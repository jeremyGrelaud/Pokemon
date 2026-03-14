"""
services/pokemon_factory.py
============================
Création et initialisation des Pokémon et des dresseurs NPC.

  - Gestion des moves (learn, ensure)
  - Calcul d'XP, IVs, natures, ability
  - Création de Pokémon (sauvage, starter, NPC)
  - Création de dresseurs NPC (gym leaders, trainers, rival)

Exports publics :
    # Moves
    learn_moves_up_to_level(pokemon, level)         → None
    ensure_has_moves(pokemon)                        → None

    # Stats / génération
    exp_at_level_for_species(species, level)         → int
    generate_random_nature()                         → str
    assign_ability(pokemon, allow_hidden=True)       → None

    # Création Pokémon
    create_wild_pokemon(species, level, location)    → PlayablePokemon
    create_starter_pokemon(species, trainer, ...)    → PlayablePokemon

    # Création NPC
    create_gym_leader(username, gym_name, ...)       → (Trainer, GymLeader)
    create_npc_trainer(username, trainer_type, ...)  → Trainer
    create_rival(username, player_trainer)           → Trainer
"""

import random
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# HELPERS INTERNES
# =============================================================================

def _build_ivs(iv_min=0, iv_max=31):
    """Génère un dict d'IVs aléatoires entre iv_min et iv_max."""
    iv_stats = ('iv_hp', 'iv_attack', 'iv_defense',
                'iv_special_attack', 'iv_special_defense', 'iv_speed')
    return {stat: random.randint(iv_min, iv_max) for stat in iv_stats}


def _finalize_pokemon(pokemon, level):
    """
    Calcule les stats, fixe les HP à leur maximum, apprend les moves.
    Factorise le pattern commun à toutes les créations de Pokémon.
    """
    pokemon.calculate_stats()
    pokemon.current_hp = pokemon.max_hp
    pokemon.save()
    learn_moves_up_to_level(pokemon, level)
    return pokemon


def _create_npc_pokemon(species, trainer, level, username, party_position,
                        iv_min=0, iv_max=20,
                        fixed_ivs=None, fixed_nature=None):
    """
    Crée et sauvegarde un PlayablePokemon pour un NPC avec ses stats calculées.
    Helper interne partagé entre create_gym_leader et create_npc_trainer.

    Args:
        fixed_ivs   : dict optionnel {'iv_hp':10, ...} — bypasse iv_min/iv_max.
        fixed_nature: str optionnel (ex: 'Hardy') — bypasse generate_random_nature().
    """
    from myPokemonApp.models.PlayablePokemon import PlayablePokemon

    ivs    = fixed_ivs if fixed_ivs is not None else _build_ivs(iv_min, iv_max)
    nature = fixed_nature if fixed_nature is not None else generate_random_nature()

    pokemon = PlayablePokemon(
        species=species,
        trainer=trainer,
        level=level,
        original_trainer=username,
        is_in_party=True,
        party_position=party_position,
        nature=nature,
        gender=generate_gender(species),
        **ivs
    )
    pokemon.calculate_stats()
    pokemon.current_hp = pokemon.max_hp
    assign_ability(pokemon, allow_hidden=False)  # NPCs : talents normaux seulement
    pokemon.save()
    return pokemon


def _assign_npc_moves(pokemon, moves):
    """
    Assigne une liste de moves à un Pokémon NPC.
    get_or_create + déduplification pour éviter les violations UNIQUE constraint.
    """
    from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance

    seen = set()
    for move in moves:
        if move.id in seen:
            continue
        seen.add(move.id)
        PokemonMoveInstance.objects.get_or_create(
            pokemon=pokemon,
            move=move,
            defaults={'current_pp': move.pp}
        )


# =============================================================================
# SECTION 2 — GESTION DES MOVES
# =============================================================================

def learn_moves_up_to_level(pokemon, level):
    """
    Synchronise les PokemonMoveInstance avec les 4 dernières capacités
    apprises jusqu'au niveau donné.

    - Déduplique (si un move apparaît à plusieurs niveaux, garde le plus récent).
    - Supprime les moves hors du set final (utile après level-up ou relance).
    - Ajoute les moves manquants via get_or_create (idempotent).
    - Hard cap à 4 moves (règle Gen 1).
    """
    from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance

    learnable = pokemon.species.learnable_moves.filter(
        learn_method='level',
        level_learned__gt=0,
        level_learned__lte=level,
    ).order_by('level_learned')

    seen_moves = {}
    for lm in learnable:
        seen_moves[lm.move_id] = lm  # garde la dernière occurrence par move_id

    all_moves   = list(seen_moves.values())
    final_moves = all_moves[-4:] if len(all_moves) > 4 else all_moves
    final_ids   = {lm.move_id for lm in final_moves}

    # Ne supprimer QUE les moves appris par niveau (source='level').
    # Les TM (source='tm'), CS (source='hm'), tuteurs etc. sont préservés.
    PokemonMoveInstance.objects.filter(
        pokemon=pokemon, source='level'
    ).exclude(move_id__in=final_ids).delete()

    for lm in final_moves:
        PokemonMoveInstance.objects.get_or_create(
            pokemon=pokemon,
            move=lm.move,
            defaults={'current_pp': lm.move.pp, 'source': 'level'}
        )


def ensure_has_moves(pokemon):
    """
    Garantit qu'un Pokémon a au moins un move.
    Fallback sur Charge (Tackle) pour les Pokémon sans learnset configuré.
    """
    from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance
    from myPokemonApp.models.PokemonMove import PokemonMove

    if not pokemon.pokemonmoveinstance_set.exists():
        tackle = (
            PokemonMove.objects.filter(name__icontains='Charge').first()
            or PokemonMove.objects.first()
        )
        if tackle:
            PokemonMoveInstance.objects.get_or_create(
                pokemon=pokemon,
                move=tackle,
                defaults={'current_pp': tackle.pp}
            )


# =============================================================================
# SECTION 3 — CRÉATION DE POKÉMON
# =============================================================================

def exp_at_level_for_species(species, level):
    """
    Retourne l'XP totale cumulée requise pour ATTEINDRE `level`.

    Standalone — utilisable avant que l'instance PlayablePokemon soit
    sauvegardée en base.

    Exemples (medium_fast = n³) :
        level 3  →    27
        level 5  →   125
        level 10 →  1000
    """
    n = max(1, min(level, 100))
    if n <= 1:
        return 0

    rate = getattr(species, 'growth_rate', 'medium_fast')

    if rate == 'fast':
        return int(4 * n ** 3 / 5)
    elif rate == 'medium_slow':
        return max(0, int(6 * n ** 3 / 5) - 15 * n ** 2 + 100 * n - 140)
    elif rate == 'slow':
        return int(5 * n ** 3 / 4)
    elif rate == 'erratic':
        if n <= 50:   return int(n ** 3 * (100 - n) / 50)
        elif n <= 68: return int(n ** 3 * (150 - n) / 100)
        elif n <= 98: return int(n ** 3 * ((1911 - 10 * n) // 3) / 500)
        else:         return int(n ** 3 * (160 - n) / 100)
    elif rate == 'fluctuating':
        if n <= 15:   return int(n ** 3 * ((n + 1) // 3 + 24) / 50)
        elif n <= 36: return int(n ** 3 * (n + 14) / 50)
        else:         return int(n ** 3 * ((n // 2) + 32) / 50)
    else:  # medium_fast (défaut)
        return n ** 3


def generate_random_nature():
    """Génère une nature aléatoire parmi les 25 natures."""
    return random.choice([
        'Hardy', 'Lonely', 'Brave',   'Adamant', 'Naughty',
        'Bold',  'Docile', 'Relaxed', 'Impish',  'Lax',
        'Timid', 'Hasty',  'Serious', 'Jolly',   'Naive',
        'Modest','Mild',   'Quiet',   'Bashful',  'Rash',
        'Calm',  'Gentle', 'Sassy',   'Careful',  'Quirky',
    ])


def generate_gender(species):
    """
    Tire le genre d'un Pokémon selon le gender_ratio de son espèce.

    species.gender_ratio :
        -1   → sans genre  ('N')
         0.0 → toujours femelle ('F')
         1.0 → toujours mâle   ('M')
         0.875 → starters / plupart des pseudo-légendaires
         0.5   → majorité des espèces
    """
    ratio = getattr(species, 'gender_ratio', 0.5)
    if ratio < 0:
        return 'N'
    return 'M' if random.random() < ratio else 'F'


def assign_ability(pokemon, allow_hidden=True):
    """
    Assigne un talent (Ability) à un PlayablePokemon en tirant au sort
    parmi les slots définis sur son espèce.

    Poids de tirage (voir Pokemon.get_ability_pool) :
      - Talent 1 seul                -> 100 %
      - Talent 1 + Talent 2          -> 50 % / 50 %
      - Talent 1 + Talent 2 + Cache  -> 45 % / 45 % / 10 %
      - Talent 1 + Cache             -> 90 % / 10 %

    Args:
        pokemon      : PlayablePokemon (non encore sauvegardé ou déjà en base)
        allow_hidden : False pour les starters / créations sans talent caché
    """
    pool = pokemon.species.get_ability_pool(allow_hidden=allow_hidden)
    if not pool:
        return  # espèce sans talent défini

    total = sum(weight for _, weight in pool)
    roll  = random.uniform(0, total)
    cumul = 0
    for ability, weight in pool:
        cumul += weight
        if roll <= cumul:
            pokemon.ability           = ability
            pokemon.is_hidden_ability = (ability == pokemon.species.hidden_ability)
            return


def create_wild_pokemon(species, level, location=None):
    """
    Crée un Pokémon sauvage avec des IVs aléatoires (0-31) et garantit
    au moins un move via ensure_has_moves().

    Args:
        species:  Pokemon (espèce)
        level:    int
        location: str optionnel (nom de la zone de capture)

    Returns:
        PlayablePokemon sauvegardé avec stats et moves
    """
    from myPokemonApp.models.PlayablePokemon import PlayablePokemon
    from myPokemonApp.services.trainer_service import get_or_create_wild_trainer

    is_shiny = random.randint(1, 8192) == 1  # Probabilité Gen 1 : 1/8192

    pokemon = PlayablePokemon(
        species=species,
        trainer=get_or_create_wild_trainer(),
        level=level,
        current_exp=exp_at_level_for_species(species, level),
        original_trainer='Wild',
        caught_location=location,
        is_in_party=True,
        is_shiny=is_shiny,
        nature=generate_random_nature(),
        gender=generate_gender(species),
        **_build_ivs(0, 31)
    )
    assign_ability(pokemon, allow_hidden=True)  # sauvages peuvent avoir le talent caché
    _finalize_pokemon(pokemon, level)
    ensure_has_moves(pokemon)
    return pokemon


def create_starter_pokemon(species, trainer, nickname=None, is_shiny=False):
    """
    Crée un Pokémon de départ pour un joueur (niveau 5, IVs favorables 10-31).
    is_shiny est pré-rollé dans la vue de sélection.
    """
    from myPokemonApp.models.PlayablePokemon import PlayablePokemon

    pokemon = PlayablePokemon(
        species=species,
        trainer=trainer,
        nickname=nickname,
        level=5,
        current_exp=exp_at_level_for_species(species, 5),
        original_trainer=trainer.username,
        caught_location='Pallet Town',
        party_position=1,
        is_shiny=is_shiny,
        nature=generate_random_nature(),
        gender=generate_gender(species),
        **_build_ivs(10, 31)
    )
    assign_ability(pokemon, allow_hidden=False)  # starters : talents normaux seulement
    return _finalize_pokemon(pokemon, 5)


# =============================================================================
# SECTION 4 — CRÉATION DE NPCs ET DRESSEURS
# =============================================================================

def create_gym_leader(username, gym_name, city, badge_name,
                      specialty_type, badge_order, team_data):
    """
    Crée un Champion d'Arène avec son équipe. Idempotent (get_or_create).

    team_data = [
        {'species': Pokemon, 'level': 14, 'moves': [move1, move2]},
        ...
    ]
    """
    from myPokemonApp.models.Trainer import Trainer, GymLeader

    trainer, created = Trainer.objects.get_or_create(
        username=username,
        defaults={
            'trainer_type': 'gym_leader',
            'location': city,
            'intro_text': f"Bienvenue à l'arène de {city} ! Je suis {username} !",
            'defeat_text': f"Tu m'as battu... Tu mérites le badge {badge_name} !",
            'victory_text': "Tu n'es pas encore prêt pour mon badge !",
            'can_rebattle': True,
            'is_npc': True,
            'npc_class': 'GymLeader',
        }
    )

    if not created:
        logger.info("  [skip] Gym Leader '%s' existe déjà", username)
        gym, _ = GymLeader.objects.get_or_create(trainer=trainer)
        return trainer, gym

    gym, _ = GymLeader.objects.get_or_create(
        trainer=trainer,
        defaults={
            'gym_name':       gym_name,
            'gym_city':       city,
            'badge_name':     badge_name,
            'specialty_type': specialty_type,
            'badge_order':    badge_order,
        }
    )

    for i, poke_data in enumerate(team_data, 1):
        # IVs élevés pour les champions (20-31)
        pokemon = _create_npc_pokemon(
            poke_data['species'], trainer, poke_data['level'],
            username, i, iv_min=20, iv_max=31
        )
        _assign_npc_moves(pokemon, poke_data.get('moves', []))

    return trainer, gym


def create_npc_trainer(username, trainer_type, location, team_data,
                       intro_text=None, npc_class='Gamin', sprite_name='',
                       can_rebattle=False, money=None,
                       defeat_text=None, victory_text=None,
                       is_battle_required=False,
                       fixed_ivs=None, fixed_nature=None,
                       iv_min=0, iv_max=20,
                       ai_flags=None,
                       npc_code=None):
    """
    Crée un dresseur NPC générique avec son équipe. Idempotent via npc_code.

    npc_code : clé stable et lisible utilisée par Tiled (ex: 'route_1_youngster_ben').
               Si non fourni, auto-généré depuis location + username.
               C'est la clé d'idempotence — remplace (username, location).
    """
    import unicodedata, re

    def slugify(s):
        s = unicodedata.normalize('NFD', (s or '').lower())
        s = s.encode('ascii', 'ignore').decode()
        return re.sub(r'[^a-z0-9]+', '_', s).strip('_')

    # Générer npc_code si non fourni
    if not npc_code:
        npc_code = f"{slugify(location)}_{slugify(username)}"

    from myPokemonApp.models.Trainer import Trainer

    final_intro   = intro_text   or f"{username} veut combattre !"
    final_defeat  = defeat_text  or "J'ai perdu..."
    final_victory = victory_text or "J'ai gagné !"

    trainer, created = Trainer.objects.update_or_create(
        npc_code=npc_code,
        defaults={
            'username':           username,
            'trainer_type':       trainer_type,
            'location':           location,
            'intro_text':         final_intro,
            'defeat_text':        final_defeat,
            'victory_text':       final_victory,
            'can_rebattle':       can_rebattle,
            'money':              money if money is not None else 500,
            'is_npc':             True,
            'npc_class':          npc_class,
            'sprite_name':        sprite_name,
            'is_battle_required': is_battle_required,
            'ai_flags':           ai_flags or [],
        }
    )

    if not created:
        logger.info("  [skip] NPC '%s' (code: %s) existe déjà", username, npc_code)
        return trainer

    for i, poke_data in enumerate(team_data, 1):
        pokemon = _create_npc_pokemon(
            poke_data['species'], trainer, poke_data['level'],
            username, i,
            iv_min=iv_min, iv_max=iv_max,
            fixed_ivs=fixed_ivs,
            fixed_nature=fixed_nature,
        )
        _assign_npc_moves(pokemon, poke_data.get('moves', []))

    return trainer


def create_rival(username, player_trainer):
    """Crée un rival lié au joueur."""
    from myPokemonApp.models.Trainer import Trainer

    return Trainer.objects.create(
        username=username,
        trainer_type='rival',
        intro_text=f"Salut {player_trainer.username} ! On fait un combat ?",
        defeat_text="Tu t'améliores... Mais je serai toujours meilleur !",
        victory_text="Haha ! J'ai gagné comme toujours !",
        can_rebattle=True,
        money=0,
        is_npc=True,
        npc_class='Rival',
    )