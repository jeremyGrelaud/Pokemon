"""
services/trainer_service.py
============================
Helpers orientés dresseur et gestion de l'équipe PC.

  - Helpers Trainer / premier Pokémon vivant
  - get_or_create_wild_trainer() — mise en cache module-level (évite un get_or_create DB à chaque rencontre sauvage)
  - Reset des stat-stages entre combats
  - Soins d'équipe, dépôt / retrait PC
  - Natures et stats avec nature
  - Nettoyage des Pokémon sauvages orphelins

Exports publics :
    get_first_alive_pokemon(trainer)                 → PlayablePokemon | None
    get_or_create_wild_trainer()                     → Trainer          (mis en cache)
    heal_team(trainer)                               → None
    cleanup_orphan_wild_pokemon()                    → None
    deposit_pokemon(pokemon)                         → None
    withdraw_pokemon(pokemon, position)              → (bool, str)
    get_nature_modifiers(nature)                     → (str|None, str|None)
    calculate_pokemon_stats_with_nature(pokemon)     → None
    _reset_team_stages(trainer, wild=None)           → None             (semi-privé)
"""

import logging

logger = logging.getLogger(__name__)

# =============================================================================
# Cache module-level pour le Trainer "Wild"
# =============================================================================
# get_or_create_wild_trainer() est appelé à chaque création de Pokémon sauvage.
# Le Trainer "Wild" ne change jamais → on évite un aller-retour DB à chaque
# rencontre en le mémorisant après le premier appel.
#
# Thread-safety : CPython GIL suffit pour un simple assignment de référence.
# Reset possible via _reset_wild_trainer_cache() pour les tests.
_wild_trainer_cache = None


def get_or_create_wild_trainer():
    """
    Récupère ou crée le Trainer 'Wild' utilisé pour les Pokémon sauvages.
    Le résultat est mis en cache au niveau du module après le premier appel.
    """
    global _wild_trainer_cache
    if _wild_trainer_cache is None:
        from myPokemonApp.models.Trainer import Trainer
        _wild_trainer_cache, _ = Trainer.objects.get_or_create(
            username='Wild',
            defaults={'trainer_type': 'wild'}
        )
    return _wild_trainer_cache


def _reset_wild_trainer_cache():
    """Vide le cache du Trainer Wild — à appeler uniquement dans les tests."""
    global _wild_trainer_cache
    _wild_trainer_cache = None


# =============================================================================
# SECTION 1 — HELPERS TRAINER / POKEMON
# =============================================================================

# Champs de stat-stages réinitialisés entre chaque combat.
_STAGE_FIELDS = [
    'attack_stage', 'defense_stage',
    'special_attack_stage', 'special_defense_stage',
    'speed_stage', 'accuracy_stage', 'evasion_stage',
]


def get_first_alive_pokemon(trainer):
    """
    Retourne le premier Pokémon vivant de l'équipe active d'un dresseur.
    Pattern récurrent centralisé ici pour éviter de le réécrire partout.
    """
    return trainer.pokemon_team.filter(
        is_in_party=True,
        current_hp__gt=0
    ).order_by('party_position').first()


def _reset_team_stages(trainer, wild=None):
    """
    Réinitialise les stat_stages de combat de toute l'équipe d'un dresseur.
    Si wild est fourni (Pokémon sauvage sans Trainer), reset ce seul Pokémon.

    Utilise bulk_update pour n'émettre qu'une seule requête SQL pour toute l'équipe.

    Appelé AVANT et APRÈS chaque combat pour garantir qu'aucun stage résiduel
    (attack_stage, speed_stage, etc.) ne persiste d'un combat à l'autre.
    """
    from myPokemonApp.models.PlayablePokemon import PlayablePokemon

    if wild is not None:
        for f in _STAGE_FIELDS:
            setattr(wild, f, 0)
        wild.save(update_fields=_STAGE_FIELDS)
        return
    if trainer is None:
        return
    team = list(trainer.pokemon_team.filter(is_in_party=True))
    for p in team:
        for f in _STAGE_FIELDS:
            setattr(p, f, 0)
    if team:
        PlayablePokemon.objects.bulk_update(team, _STAGE_FIELDS)


# =============================================================================
# SECTION 10 — UTILITAIRES DIVERS
# =============================================================================

def heal_team(trainer):
    """
    Soigne complètement tous les Pokémon d'un dresseur (HP max + PP max).
    Utilise des UPDATE groupés : 2 requêtes quelle que soit la taille de l'équipe.
    """
    from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance
    from django.db import models as _models

    team_qs = trainer.pokemon_team.all()

    # 1) HP + statut + stages en une seule requête
    team_qs.update(
        current_hp=_models.F('max_hp'),
        status_condition=None,
        sleep_turns=0,
        attack_stage=0,
        defense_stage=0,
        special_attack_stage=0,
        special_defense_stage=0,
        speed_stage=0,
        accuracy_stage=0,
        evasion_stage=0,
    )

    # 2) PP — SQLite/Django interdit F('move__pp') dans un UPDATE (joined field).
    #    On charge toutes les instances avec select_related (1 requête),
    #    affecte current_pp = move.pp en Python, puis bulk_update (1 requête).
    move_instances = list(
        PokemonMoveInstance.objects.filter(pokemon__in=team_qs).select_related('move')
    )
    for mi in move_instances:
        mi.current_pp = mi.move.pp
    if move_instances:
        PokemonMoveInstance.objects.bulk_update(move_instances, ['current_pp'])


def cleanup_orphan_wild_pokemon():
    """
    Supprime les PlayablePokemon sauvages orphelins (trainer 'Wild' ou 'wild_pokemon')
    qui ne sont plus liés à aucun combat actif.

    À appeler avant de créer un nouveau combat sauvage pour éviter
    l'accumulation de lignes inutiles en base.
    """
    from myPokemonApp.models.Battle import Battle
    from myPokemonApp.models.PlayablePokemon import PlayablePokemon

    active_wild_ids = Battle.objects.filter(
        is_active=True
    ).values_list('opponent_pokemon_id', flat=True)

    PlayablePokemon.objects.filter(
        trainer__username__in=('Wild', 'wild_pokemon')
    ).exclude(id__in=active_wild_ids).delete()


def deposit_pokemon(pokemon):
    """Dépose un Pokémon dans le PC (retire de l'équipe active)."""
    pokemon.is_in_party    = False
    pokemon.party_position = None
    pokemon.save()


def withdraw_pokemon(pokemon, position):
    """
    Retire un Pokémon du PC et l'ajoute à l'équipe.
    Retourne (success: bool, message: str).
    """
    if pokemon.trainer.pokemon_team.filter(is_in_party=True).count() >= 6:
        return False, "L'équipe est complète !"
    pokemon.is_in_party    = True
    pokemon.party_position = position
    pokemon.save()
    return True, f"{pokemon} a été ajouté à l'équipe !"


def get_nature_modifiers(nature):
    """
    Retourne (stat_augmentée, stat_diminuée) pour une nature.
    Retourne (None, None) pour les natures neutres.
    """
    _NATURE_EFFECTS = {
        'Lonely':  ('attack',          'defense'),
        'Brave':   ('attack',          'speed'),
        'Adamant': ('attack',          'special_attack'),
        'Naughty': ('attack',          'special_defense'),
        'Bold':    ('defense',         'attack'),
        'Relaxed': ('defense',         'speed'),
        'Impish':  ('defense',         'special_attack'),
        'Lax':     ('defense',         'special_defense'),
        'Timid':   ('speed',           'attack'),
        'Hasty':   ('speed',           'defense'),
        'Jolly':   ('speed',           'special_attack'),
        'Naive':   ('speed',           'special_defense'),
        'Modest':  ('special_attack',  'attack'),
        'Mild':    ('special_attack',  'defense'),
        'Quiet':   ('special_attack',  'speed'),
        'Rash':    ('special_attack',  'special_defense'),
        'Calm':    ('special_defense', 'attack'),
        'Gentle':  ('special_defense', 'defense'),
        'Sassy':   ('special_defense', 'speed'),
        'Careful': ('special_defense', 'special_attack'),
    }
    return _NATURE_EFFECTS.get(nature, (None, None))


def calculate_pokemon_stats_with_nature(pokemon):
    """Recalcule les stats d'un Pokémon en appliquant les modificateurs de nature (+10%/-10%)."""
    pokemon.calculate_stats()
    increased, decreased = get_nature_modifiers(pokemon.nature)
    if increased:
        setattr(pokemon, increased, int(getattr(pokemon, increased) * 1.1))
    if decreased:
        setattr(pokemon, decreased, int(getattr(pokemon, decreased) * 0.9))
    pokemon.save()