"""
services/capture_service.py
============================
Système de capture et rencontres sauvages.

Exports publics :
    calculate_capture_rate(pokemon, ball, hp_percent, status)  → float 0-1
    calculate_shake_count(capture_rate_0_1)                    → (shakes, success)
    attempt_pokemon_capture(battle, ball_item, trainer)        → dict
    get_random_wild_pokemon(zone, encounter_type)              → (Pokemon, int) | (None, None)
    get_encounter_chance(encounter_type)                       → bool
"""

import math
import random
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# SECTION 7 — CAPTURE
# =============================================================================

def calculate_capture_rate(pokemon, ball, pokemon_hp_percent, pokemon_status=None):
    """
    Calcule le taux de capture selon la formule Gen 1.

    Args:
        pokemon:            PlayablePokemon adversaire
        ball:               Item (pokeball)
        pokemon_hp_percent: float 0.0-1.0 (HP actuels / HP max)
        pokemon_status:     str ou None ('sleep', 'freeze', ...)

    Returns:
        float 0.0-1.0
    """
    from myPokemonApp.models.CaptureSystem import PokeballItem

    # Master Ball → capture garantie
    try:
        pokeball_stats = PokeballItem.objects.get(item=ball)
        if pokeball_stats.guaranteed_capture:
            return 1.0
    except PokeballItem.DoesNotExist:
        pokeball_stats = None

    base_rate = (
        pokemon.species.catch_rate if hasattr(pokemon, 'species') else pokemon.catch_rate
    ) or 45

    ball_mult = ball.catch_rate_modifier or 1.0

    # Bonus spécifiques à certaines balls (type / statut)
    if pokeball_stats:
        if pokeball_stats.bonus_on_type:
            poke_types = (
                pokemon.species.types.all() if hasattr(pokemon, 'species')
                else pokemon.types.all()
            )
            if pokeball_stats.bonus_on_type in poke_types:
                ball_mult *= 1.5
        if (pokeball_stats.bonus_on_status
                and pokemon_status == pokeball_stats.bonus_on_status):
            ball_mult *= 1.5

    hp_mod     = max(0.1, min(1.0, (3 - 2 * pokemon_hp_percent) / 3))
    status_mod = (2.0 if pokemon_status in ('sleep', 'freeze')
                  else 1.5 if pokemon_status in ('burn', 'poison', 'paralysis')
                  else 1.0)

    return min(1.0, ((hp_mod * base_rate * ball_mult) / 255) * status_mod)


def calculate_shake_count(capture_rate_0_1):
    """
    Calcule le nombre de shakes selon la formule officielle Gen 3 (FireRed/LeafGreen).

    La formule Gen 3 utilise un seul seuil 'b' calculé depuis le taux de capture,
    puis effectue 4 tests indépendants (random 0-65535).
    Chaque test réussi = 1 shake supplémentaire.
    Si les 4 tests réussissent → capture (3 shakes + succès).
    Sinon → le Pokémon s'échappe après le nombre de shakes réussis (0-3).

    Source: Bulbapedia — Catch rate mechanics Gen III

    Args:
        capture_rate_0_1: float 0.0-1.0 (sortie de calculate_capture_rate)
    Returns:
        tuple (shakes: int 0-3, success: bool)
    """
    modified_rate = int(capture_rate_0_1 * 255)
    modified_rate = max(1, min(255, modified_rate))

    b = int(65536 * (modified_rate / 255) ** (3 / 16))
    b = max(1, min(65535, b))

    shakes = 0
    for _ in range(4):
        if random.randint(0, 65535) < b:
            shakes += 1
        else:
            break

    success = (shakes == 4)
    return (min(shakes, 3), success)


def attempt_pokemon_capture(battle, ball_item, trainer):
    """
    Tente de capturer le Pokémon adverse — formule Gen 3 (FireRed/LeafGreen).

    Calcule les shakes ET le résultat EN UNE SEULE FOIS ici, pour que
    le frontend puisse animer exactement ce qui s'est passé.

    Returns:
        dict: {
            'success', 'capture_rate', 'shakes', 'message',
            'captured_pokemon', 'is_first_catch', 'achievement_notifications'
        }
    """
    from myPokemonApp.models.CaptureSystem import CaptureAttempt, PokeballItem

    opponent     = battle.opponent_pokemon
    hp_percent   = opponent.current_hp / opponent.max_hp
    capture_rate = calculate_capture_rate(
        opponent, ball_item, hp_percent, opponent.status_condition
    )

    attempt = CaptureAttempt.objects.create(
        trainer=trainer,
        pokemon_species=opponent.species,
        ball_used=ball_item,
        pokemon_level=opponent.level,
        pokemon_hp_percent=hp_percent,
        pokemon_status=opponent.status_condition,
        capture_rate=capture_rate,
        battle=battle,
        success=False,
        shakes=0,
    )

    # Master Ball → capture garantie, 3 shakes
    try:
        if PokeballItem.objects.get(item=ball_item).guaranteed_capture:
            return _capture_success(battle, opponent, ball_item, trainer, attempt, shakes=3)
    except PokeballItem.DoesNotExist:
        pass

    shakes, success = calculate_shake_count(capture_rate)

    if not success:
        attempt.shakes = shakes
        attempt.save()
        return {
            'success':          False,
            'capture_rate':     capture_rate,
            'shakes':           shakes,
            'message':          f"{opponent.species.name} s'est échappé après {shakes} shake(s) !",
            'captured_pokemon': None,
        }

    return _capture_success(battle, opponent, ball_item, trainer, attempt, shakes=shakes)


def _capture_success(battle, opponent, ball_item, trainer, attempt, shakes):
    """Gère la capture réussie d'un Pokémon (helper privé)."""
    from myPokemonApp.models.CaptureSystem import CaptureJournal
    from myPokemonApp.views.AchievementViews import trigger_achievements_after_capture

    # Mettre à jour battle_snapshot avec les HP finaux AVANT le transfert
    try:
        snap = battle.battle_snapshot if isinstance(battle.battle_snapshot, dict) else {}
        for entry in snap.get('player_team', []):
            try:
                poke = battle.player_trainer.pokemon_team.get(id=entry['id'])
                entry.update({
                    'current_hp':       poke.current_hp,
                    'max_hp':           poke.max_hp,
                    'ko':               poke.current_hp == 0,
                    'status_condition': poke.status_condition or ''
                })
            except Exception:
                pass
        for entry in snap.get('opponent_team', []):
            if entry['id'] == opponent.id:
                entry.update({
                    'current_hp':       opponent.current_hp,
                    'max_hp':           opponent.max_hp,
                    'ko':               False,
                    'status_condition': opponent.status_condition or ''
                })
        battle.battle_snapshot = snap
        battle.save(update_fields=['battle_snapshot'])
    except Exception as exc:
        logger.warning("battle_snapshot capture update: %s", exc)

    # Transférer le Pokémon sauvage existant (conserve IVs/EVs/nature/moves)
    party_count = trainer.pokemon_team.filter(is_in_party=True).count()
    opponent.trainer          = trainer
    opponent.original_trainer = trainer.username
    opponent.pokeball_used    = ball_item.name
    opponent.friendship       = 70
    opponent.is_in_party      = party_count < 6
    opponent.party_position   = party_count + 1 if party_count < 6 else None
    opponent.save()
    captured = opponent

    is_first = not trainer.pokemon_team.filter(
        species=opponent.species
    ).exclude(id=captured.id).exists()

    CaptureJournal.objects.create(
        trainer=trainer,
        pokemon=captured,
        ball_used=ball_item,
        level_at_capture=opponent.level,
        hp_at_capture=opponent.current_hp,
        is_first_catch=is_first,
        is_critical_catch=(shakes == 0),
        attempts_before_success=1,
    )

    attempt.success = True
    attempt.shakes  = shakes
    attempt.save()

    battle.is_active = False
    battle.winner    = trainer
    battle.save()

    message = f"Vous avez capturé {opponent.species.name} !"
    if is_first:
        message += " (Première capture !)"

    return {
        'success':                   True,
        'capture_rate':              attempt.capture_rate,
        'shakes':                    shakes,
        'message':                   message,
        'captured_pokemon':          {'name': captured.species.name, 'level': captured.level},
        'is_first_catch':            is_first,
        'achievement_notifications': trigger_achievements_after_capture(trainer),
    }


# =============================================================================
# SECTION 8 — RENCONTRES SAUVAGES
# =============================================================================

def get_random_wild_pokemon(zone, encounter_type='grass'):
    """
    Génère un Pokémon sauvage aléatoire selon les spawn rates d'une zone.

    Returns:
        (Pokemon species, level) ou (None, None) si aucun spawn configuré.
    """
    from myPokemonApp.models.Zone import WildPokemonSpawn

    spawns = WildPokemonSpawn.objects.filter(zone=zone, encounter_type=encounter_type)
    if not spawns.exists():
        return None, None

    total = sum(s.spawn_rate for s in spawns)
    if total == 0:
        return None, None

    roll, cumulative = random.uniform(0, total), 0
    for spawn in spawns:
        cumulative += spawn.spawn_rate
        if roll <= cumulative:
            return spawn.pokemon, random.randint(spawn.level_min, spawn.level_max)

    # Fallback (ne devrait jamais arriver si total > 0)
    first = spawns.first()
    return first.pokemon, random.randint(first.level_min, first.level_max)


def get_encounter_chance(encounter_type='grass'):
    """
    Détermine s'il y a une rencontre aléatoire lors d'un déplacement.
    Returns: bool
    """
    base_rates = {'grass': 10.0, 'water': 20.0, 'fishing': 40.0, 'cave': 15.0}
    return random.random() * 100 < base_rates.get(encounter_type, 10.0)