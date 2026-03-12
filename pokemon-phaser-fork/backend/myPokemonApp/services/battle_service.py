"""
services/battle_service.py
===========================
Logique de combat : démarrage, IA, XP/EVs, fin de combat, switch.

Exports publics :
    start_battle(player_trainer, opponent_trainer, wild_pokemon, battle_type)
        → (Battle, str)
    get_opponent_ai_action(battle)
        → dict
    calculate_exp_gain(defeated_pokemon, battle_type, winner_pokemon)
        → int
    apply_exp_gain(pokemon, exp_amount)
        → dict
    apply_ev_gains(winner, defeated_pokemon)
        → None
    check_battle_end(battle)
        → (bool, Trainer|None, str)
    opponent_switch_pokemon(battle)
        → PlayablePokemon | None
"""

import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


# =============================================================================
# HELPERS INTERNES
# =============================================================================

def _snapshot_pokemon(p):
    """Sérialise un PlayablePokemon en dict JSON-safe pour battle_snapshot."""
    return {
        'id':               p.id,
        'nickname':         p.nickname,
        'species_name':     p.species.name,
        'species_id':       p.species.id,
        'primary_type':     p.species.primary_type.name  if p.species.primary_type  else 'normal',
        'secondary_type':   p.species.secondary_type.name if p.species.secondary_type else None,
        'level':            p.level,
        'is_shiny':         p.is_shiny,
        'attack':           p.attack,
        'defense':          p.defense,
        'speed':            p.speed,
        'max_hp':           p.max_hp,
        'current_hp':       p.current_hp,
        'ko':               p.current_hp == 0,
        'status_condition': p.status_condition or '',
    }


def _snapshot_team(trainer, wild_pokemon=None):
    """Snapshot de l'équipe active d'un dresseur (ou d'un Pokémon sauvage)."""
    if wild_pokemon:
        return [_snapshot_pokemon(wild_pokemon)]
    return [
        _snapshot_pokemon(p)
        for p in trainer.pokemon_team
            .filter(is_in_party=True)
            .order_by('party_position')
            .select_related('species', 'species__primary_type', 'species__secondary_type')
    ]


# =============================================================================
# DÉMARRAGE DU COMBAT
# =============================================================================

def start_battle(player_trainer, opponent_trainer=None, wild_pokemon=None,
                 battle_type='trainer'):
    """
    Démarre un nouveau combat et retourne (Battle, message_intro).

    Cas d'usage :
        battle, msg = start_battle(trainer, opponent_trainer=npc)
        battle, msg = start_battle(trainer, wild_pokemon=wild)
    """
    from myPokemonApp.models.Battle import Battle
    from myPokemonApp.services.trainer_service import (
        get_first_alive_pokemon, _reset_team_stages
    )

    player_pokemon = get_first_alive_pokemon(player_trainer)
    if not player_pokemon:
        return None, "Aucun Pokémon disponible pour combattre !"

    if wild_pokemon:
        opponent_pokemon = wild_pokemon
        battle_type = 'wild'
    elif opponent_trainer:
        opponent_pokemon = get_first_alive_pokemon(opponent_trainer)
        if not opponent_pokemon:
            return None, "L'adversaire n'a pas de Pokémon disponible !"
    else:
        return None, "Pas d'adversaire défini !"

    # Reset les stages de TOUTE l'équipe avant le combat.
    _reset_team_stages(player_trainer)
    if wild_pokemon:
        _reset_team_stages(None, wild=wild_pokemon)
    elif opponent_trainer:
        _reset_team_stages(opponent_trainer)

    battle = Battle.objects.create(
        battle_type=battle_type,
        player_trainer=player_trainer,
        opponent_trainer=opponent_trainer,
        player_pokemon=player_pokemon,
        opponent_pokemon=opponent_pokemon,
        is_active=True,
        battle_state={
            'player_used_ids':   [player_pokemon.id],
            'opponent_used_ids': [opponent_pokemon.id],
        },
        battle_snapshot={
            'player_team':   _snapshot_team(player_trainer),
            'opponent_team': _snapshot_team(
                opponent_trainer,
                wild_pokemon=wild_pokemon if battle_type == 'wild' else None,
            ),
        },
    )

    msg = (
        f"Un {opponent_pokemon.species.name} sauvage apparaît !"
        if battle_type == 'wild'
        else (opponent_trainer.intro_text or f"{opponent_trainer.username} veut combattre !")
    )
    battle.add_to_log(msg)
    if battle_type == 'wild' and opponent_pokemon.is_shiny:
        battle.add_to_log(f"✨ Oh ! Un {opponent_pokemon.species.name} chromatique !")
    battle.add_to_log(f"{player_trainer.username} envoie {player_pokemon} !")
    opponent_label = opponent_trainer.username if opponent_trainer else 'Wild'
    battle.add_to_log(f"{opponent_label} envoie {opponent_pokemon} !")

    return battle, msg


# =============================================================================
# IA ADVERSAIRE
# =============================================================================

def get_opponent_ai_action(battle):
    """
    Retourne l'action de l'adversaire IA pour ce tour de combat.

    Utilise Battle.choose_enemy_move() qui implémente un scoring multi-critères :
      • Efficacité de type (immunité évitée, super-efficace privilégié)
      • STAB
      • KO potentiel détecté → priorité absolue
      • Soin d'urgence si HP < 30 %
      • Infliger un statut si la cible n'en a pas
      • Légère dose d'aléatoire pour rester imprévisible
    """
    opponent = battle.opponent_pokemon
    player   = battle.player_pokemon

    if opponent is None or opponent.is_fainted():
        return {'type': 'pass'}

    return battle.choose_enemy_move(opponent, player)


# =============================================================================
# CALCUL ET APPLICATION DE L'XP
# =============================================================================

def calculate_exp_gain(defeated_pokemon, battle_type='wild', winner_pokemon=None):
    """
    Calcule l'XP gagnée selon la formule Gen 5+ (Noire/Blanche → présent).

        exp = round( (b × Lf / 5) × ratio^2.5 + 1 ) × t

    Où :
      b     = base_experience du Pokémon vaincu
      Lf    = niveau du Pokémon vaincu
      Lp    = niveau du Pokémon vainqueur (15 par défaut si inconnu)
      ratio = (2×Lf + 10) / (Lf + Lp + 10)
      t     = 1.5 si combat de dresseur, 1.0 si sauvage

    Avantage Gen 5+ : battre un Pokémon plus fort rapporte plus d'XP ;
    battre un Pokémon beaucoup plus faible rapporte très peu.
    """
    b  = defeated_pokemon.species.base_experience or 64
    Lf = defeated_pokemon.level
    Lp = winner_pokemon.level if winner_pokemon else 15
    t  = 1.5 if battle_type in ('trainer', 'gym', 'elite_four') else 1.0

    ratio        = (2 * Lf + 10) / (Lf + Lp + 10)
    level_factor = ratio ** 2.5
    exp = int(round((b * Lf / 5) * level_factor + 1) * t)
    return max(1, exp)


def apply_exp_gain(pokemon, exp_amount):
    """
    Applique l'XP à un Pokémon et gère les level-ups avec apprentissage de moves.

    Système d'XP cumulatif :
      - current_exp = XP totale accumulée depuis le niveau 1
      - exp_for_next_level() retourne le seuil cumulatif pour atteindre level+1

    Retourne :
        {
            'exp_gained':      int,
            'level_up':        bool,
            'new_level':       int,
            'learned_moves':   [str],
            'pending_moves':   [{ move_id, move_name, move_type, move_power,
                                   move_pp, current_moves }],
            'pending_evolution': { ... }  (présent seulement si évolution disponible)
        }
    """
    from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance

    result = {
        'exp_gained':    exp_amount,
        'level_up':      False,
        'new_level':     pokemon.level,
        'learned_moves': [],
        'pending_moves': [],
    }

    pokemon.current_exp = (pokemon.current_exp or 0) + exp_amount

    while pokemon.level < 100 and pokemon.current_exp >= pokemon.exp_for_next_level():
        pokemon.level += 1
        result['level_up'] = True
        result['new_level'] = pokemon.level

        old_max_hp = pokemon.max_hp
        pokemon.calculate_stats()
        pokemon.current_hp = min(
            pokemon.current_hp + (pokemon.max_hp - old_max_hp),
            pokemon.max_hp
        )

        new_learnable = pokemon.species.learnable_moves.filter(
            learn_method='level',
            level_learned=pokemon.level,
        ).select_related('move', 'move__type')

        for lm in new_learnable:
            move = lm.move
            already_has = PokemonMoveInstance.objects.filter(
                pokemon=pokemon, move=move
            ).exists()
            if already_has:
                continue

            current_count = PokemonMoveInstance.objects.filter(pokemon=pokemon).count()

            if current_count < 4:
                PokemonMoveInstance.objects.get_or_create(
                    pokemon=pokemon,
                    move=move,
                    defaults={'current_pp': move.pp}
                )
                result['learned_moves'].append(move.name)
            else:
                current_moves = [
                    {
                        'id':    mi.move.id,
                        'name':  mi.move.name,
                        'type':  mi.move.type.name if mi.move.type else '',
                        'power': mi.move.power,
                        'pp':    mi.move.pp,
                    }
                    for mi in PokemonMoveInstance.objects.filter(
                        pokemon=pokemon
                    ).select_related('move', 'move__type')
                ]
                result['pending_moves'].append({
                    'move_id':       move.id,
                    'move_name':     move.name,
                    'move_type':     move.type.name if move.type else '',
                    'move_power':    move.power,
                    'move_pp':       move.pp,
                    'current_moves': current_moves,
                })

    if result['level_up'] and 'pending_evolution' not in result:
        evo = pokemon.check_evolution()
        if evo:
            result['pending_evolution'] = {
                'evolution_id':    evo.id,
                'pokemon_id':      pokemon.id,
                'from_name':       pokemon.species.name,
                'from_species_id': pokemon.species.id,
                'to_name':         evo.evolves_to.name,
                'to_species_id':   evo.evolves_to.id,
                'is_shiny':        pokemon.is_shiny,
                'stats_before': {
                    'hp':              pokemon.max_hp,
                    'attack':          pokemon.attack,
                    'defense':         pokemon.defense,
                    'special_attack':  pokemon.special_attack,
                    'special_defense': pokemon.special_defense,
                    'speed':           pokemon.speed,
                },
            }

    pokemon.save()
    return result


# =============================================================================
# EFFORT VALUES (EVs)
# =============================================================================

_EV_CAP_PER_STAT = 252
_EV_TOTAL_CAP    = 510


def apply_ev_gains(winner, defeated_pokemon):
    """
    Accorde les EVs (Effort Values) au Pokémon vainqueur après le combat.
    Limites Gen 3+ : 252 EVs par stat, 510 EVs au total.
    Recalcule les stats si des EVs sont gagnés.
    """
    yields = defeated_pokemon.species.get_ev_yields()
    if not yields:
        return  # Pokémon sans yield défini

    current_total = (
        winner.ev_hp + winner.ev_attack + winner.ev_defense +
        winner.ev_special_attack + winner.ev_special_defense + winner.ev_speed
    )

    if current_total >= _EV_TOTAL_CAP:
        return  # Plafond déjà atteint

    gained_any = False
    for stat_field, amount in yields:
        if current_total >= _EV_TOTAL_CAP:
            break
        current_val = getattr(winner, stat_field)
        gain = min(amount, _EV_CAP_PER_STAT - current_val, _EV_TOTAL_CAP - current_total)
        if gain > 0:
            setattr(winner, stat_field, current_val + gain)
            current_total += gain
            gained_any = True

    if gained_any:
        winner.calculate_stats()
        winner.save()


# =============================================================================
# FIN DE COMBAT / SWITCH
# =============================================================================

def check_battle_end(battle):
    """
    Vérifie si le combat est terminé.
    Retourne (is_ended: bool, winner: Trainer | None, message: str).

    Note : cette fonction ne distribue PAS l'XP ni n'appelle end_battle().
    La gestion de l'XP est centralisée dans BattleViews.py (action 'attack').
    """
    from myPokemonApp.services.trainer_service import _reset_team_stages

    if not battle.is_active:
        return False, None, ""

    player_alive = battle.player_trainer.pokemon_team.filter(
        is_in_party=True, current_hp__gt=0
    ).exists()

    if battle.opponent_trainer:
        opponent_alive = battle.opponent_trainer.pokemon_team.filter(
            is_in_party=True, current_hp__gt=0
        ).exists()
    else:
        opponent_alive = battle.opponent_pokemon.current_hp > 0

    if not player_alive:
        battle.is_active = False
        battle.winner    = battle.opponent_trainer
        battle.ended_at  = timezone.now()
        battle.save()
        _reset_team_stages(battle.player_trainer)
        if battle.opponent_trainer:
            _reset_team_stages(battle.opponent_trainer)
        elif battle.opponent_pokemon:
            _reset_team_stages(None, wild=battle.opponent_pokemon)
        return True, battle.opponent_trainer, "Vous avez perdu le combat..."

    if not opponent_alive:
        battle.is_active = False
        battle.winner    = battle.player_trainer
        battle.ended_at  = timezone.now()
        battle.save()
        msg = "Vous avez gagné le combat !"
        if battle.opponent_trainer:
            msg = battle.opponent_trainer.defeat_text or msg
        _reset_team_stages(battle.player_trainer)
        if battle.opponent_trainer:
            _reset_team_stages(battle.opponent_trainer)
        elif battle.opponent_pokemon:
            _reset_team_stages(None, wild=battle.opponent_pokemon)
        return True, battle.player_trainer, msg

    return False, None, ""


def opponent_switch_pokemon(battle):
    """Fait switcher l'adversaire vers son prochain Pokémon vivant."""
    if not battle.opponent_trainer:
        return None

    bench = battle.opponent_trainer.pokemon_team.filter(
        is_in_party=True, current_hp__gt=0
    ).exclude(id=battle.opponent_pokemon.id)

    if not bench.exists():
        return None

    new_pokemon = bench.first()
    battle.opponent_pokemon = new_pokemon

    bs   = battle.battle_state if isinstance(battle.battle_state, dict) else {}
    used = bs.get('opponent_used_ids', [])
    if new_pokemon.id not in used:
        used.append(new_pokemon.id)
    bs['opponent_used_ids'] = used
    battle.battle_state = bs
    battle.save()

    return new_pokemon