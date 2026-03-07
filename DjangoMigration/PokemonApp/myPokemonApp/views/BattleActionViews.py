#!/usr/bin/python3
"""
Vues Django — actions de combat (API POST) et apprentissage de moves.

Endpoint principal : battle_action_view (POST /battle/<pk>/action/)
Actions supportées : attack, flee, switch, item, confirm_capture, confirm_evolution

Endpoint secondaire : battle_learn_move_view (POST /battle/<pk>/learn-move/)
"""

import logging
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from myPokemonApp.models.Battle import Battle
from myPokemonApp.models.PlayablePokemon import PlayablePokemon, PokemonMoveInstance
from myPokemonApp.models.PokemonEvolution import PokemonEvolution
from myPokemonApp.models.PokemonMove import PokemonMove
from myPokemonApp.models.Trainer import TrainerInventory
from myPokemonApp.gameUtils import (
    get_player_trainer,
    get_opponent_ai_action,
    check_battle_end,
    opponent_switch_pokemon,
    calculate_exp_gain,
    apply_exp_gain,
    apply_ev_gains,
    attempt_pokemon_capture,
    calculate_capture_rate,
    build_battle_response,
    serialize_pokemon_moves,
)
from myPokemonApp.views.AchievementViews import (
    trigger_achievements_after_level_up,
)

logger = logging.getLogger(__name__)


# =============================================================================
# UTILITAIRE INTERNE
# =============================================================================

def _save_hp_snapshot(battle):
    """
    Met à jour battle_snapshot avec les HP/statut finaux de chaque Pokémon.
    Appelé juste avant de marquer le combat comme terminé.
    """
    try:
        snap = battle.battle_snapshot if isinstance(battle.battle_snapshot, dict) else {}

        for entry in snap.get('player_team', []):
            try:
                poke = battle.player_trainer.pokemon_team.get(id=entry['id'])
                entry.update({
                    'current_hp':        poke.current_hp,
                    'max_hp':            poke.max_hp,
                    'ko':                poke.current_hp == 0,
                    'status_condition':  poke.status_condition or '',
                })
            except Exception:
                pass

        bs = battle.battle_state if isinstance(battle.battle_state, dict) else {}
        opponent_used_ids = bs.get('opponent_used_ids', [])
        for entry in snap.get('opponent_team', []):
            poke = None
            if battle.opponent_trainer and opponent_used_ids:
                try:
                    poke = battle.opponent_trainer.pokemon_team.get(id=entry['id'])
                except Exception:
                    pass
            elif battle.opponent_pokemon and battle.opponent_pokemon.id == entry['id']:
                poke = battle.opponent_pokemon
            if poke:
                entry.update({
                    'current_hp':        poke.current_hp,
                    'max_hp':            poke.max_hp,
                    'ko':                poke.current_hp == 0,
                    'status_condition':  poke.status_condition or '',
                })

        battle.battle_snapshot = snap
        battle.save(update_fields=['battle_snapshot'])
    except Exception as exc:
        logger.warning("Impossible de mettre à jour battle_snapshot : %s", exc)


# =============================================================================
# HANDLERS D'ACTIONS  (un handler = une action, testable isolément)
# =============================================================================

def _handle_attack(request, battle, trainer, response_data):
    """Attaque avec un move choisi par le joueur."""
    move            = get_object_or_404(PokemonMove, pk=request.POST.get('move_id'))
    player_action   = {'type': 'attack', 'move': move}
    opponent_action = get_opponent_ai_action(battle)

    battle.execute_turn(player_action, opponent_action)

    if battle.opponent_pokemon.current_hp == 0:
        btype      = 'trainer' if battle.opponent_trainer else 'wild'
        exp_amount = calculate_exp_gain(
            battle.opponent_pokemon, btype,
            winner_pokemon=battle.player_pokemon
        )
        exp_result = apply_exp_gain(battle.player_pokemon, exp_amount)
        apply_ev_gains(battle.player_pokemon, battle.opponent_pokemon)

        response_data['log'].append(f"+{exp_amount} EXP")
        if exp_result['level_up']:
            response_data['log'].append(f"Level {exp_result['new_level']} !")
            lv_notifs = trigger_achievements_after_level_up(
                battle.player_trainer, exp_result['new_level']
            )
            for notif in lv_notifs:
                response_data['log'].append(f"🏆 {notif['title']}")
        for move_name in exp_result.get('learned_moves', []):
            response_data['log'].append(
                f"{battle.player_pokemon.species.name} apprend {move_name} !"
            )

        if exp_result.get('pending_moves'):
            response_data['pending_moves'] = exp_result['pending_moves']
        if exp_result.get('pending_evolution'):
            response_data['pending_evolution'] = exp_result['pending_evolution']

        if battle.opponent_trainer:
            new_opponent = opponent_switch_pokemon(battle)
            if new_opponent:
                response_data['log'].append(
                    f"Adversaire envoie {new_opponent.species.name} !"
                )
            else:
                _save_hp_snapshot(battle)
                battle.is_active = False
                battle.winner    = battle.player_trainer
                battle.save(update_fields=['is_active', 'winner', 'battle_state'])
                response_data['battle_ended'] = True
                response_data['result']       = 'victory'
        else:
            _save_hp_snapshot(battle)
            battle.is_active = False
            battle.winner    = battle.player_trainer
            battle.save(update_fields=['is_active', 'winner', 'battle_state'])
            response_data['battle_ended'] = True
            response_data['result']       = 'victory'


def _handle_flee(request, battle, trainer, response_data):
    """Tentative de fuite."""
    success = battle.attempt_flee()
    response_data['fled'] = success
    if success:
        _save_hp_snapshot(battle)
        battle.is_active = False
        battle.winner    = battle.player_trainer
        battle.save(update_fields=['is_active', 'winner', 'battle_state'])
        response_data['log']          = ['Vous avez réussi à fuir !']
        response_data['battle_ended'] = True
        response_data['result']       = 'fled'
    else:
        response_data['log'] = ['Échec dans la fuite !']


def _handle_switch(request, battle, trainer, response_data):
    """Switch de Pokémon (normal ou forcé après KO)."""
    new_pokemon   = get_object_or_404(
        PlayablePokemon, pk=request.POST.get('pokemon_id'), trainer=trainer
    )
    player_action = {'type': 'switch', 'pokemon': new_pokemon}

    # Track player used pokemon IDs
    bs   = battle.battle_state if isinstance(battle.battle_state, dict) else {}
    used = bs.get('player_used_ids', [])
    if new_pokemon.id not in used:
        used.append(new_pokemon.id)
    bs['player_used_ids'] = used
    battle.battle_state   = bs
    battle.save(update_fields=['battle_state'])

    # Switch forcé (après KO) : l'adversaire ne joue pas ce tour
    if request.POST.get('type') == 'forcedSwitch':
        opponent_action = {}
    else:
        opponent_action = get_opponent_ai_action(battle)

    battle.execute_turn(player_action, opponent_action)


def _handle_item(request, battle, trainer, response_data):
    """
    Utilisation d'un objet.
    Pokeball → pré-calcul shakes + stockage session (confirm_capture finalise).
    Autre    → soin/antidote exécuté immédiatement.

    Retourne True → early return (réponse déjà prête dans response_data).
    """
    from myPokemonApp.gameUtils import calculate_shake_count
    from myPokemonApp.models import PokeballItem

    inv  = get_object_or_404(TrainerInventory, pk=request.POST.get('item_id'))
    item = inv.item

    if item.item_type == 'pokeball':
        if battle.battle_type != 'wild':
            response_data['log'] = ["Vous ne pouvez pas capturer le Pokémon d'un dresseur !"]
            return True  # early return

        opponent   = battle.opponent_pokemon
        hp_percent = opponent.current_hp / opponent.max_hp
        cap_rate   = calculate_capture_rate(
            opponent, item, hp_percent, opponent.status_condition
        )

        guaranteed = False
        try:
            guaranteed = PokeballItem.objects.get(item=item).guaranteed_capture
        except PokeballItem.DoesNotExist:
            pass

        if guaranteed:
            shakes, success = 3, True
        else:
            shakes, success = calculate_shake_count(cap_rate)

        request.session['pending_capture'] = {
            'item_id': inv.pk,
            'success': success,
            'shakes':  shakes,
            'message': (
                f"{opponent.species.name} a été capturé !" if success
                else f"{opponent.species.name} s'est échappé après {shakes} shake(s) !"
            ),
        }
        request.session.modified = True

        response_data['capture_attempt'] = {
            'pokemon':         {'species_name': opponent.species.name, 'level': opponent.level},
            'ball_type':       item.name.lower().replace(' ', ''),
            'capture_rate':    cap_rate,
            'shakes':          shakes,
            'success':         success,
            'start_animation': True,
            'is_shiny':        opponent.is_shiny,
        }
        return True  # early return

    # Objet normal (potion, antidote, …)
    player_action   = {'type': 'item', 'item': item, 'target': battle.player_pokemon}
    opponent_action = get_opponent_ai_action(battle)
    battle.execute_turn(player_action, opponent_action)

    if item.is_consumable:
        inv.quantity -= 1
        if inv.quantity <= 0:
            inv.delete()
        else:
            inv.save(update_fields=['quantity'])

    return False


def _handle_confirm_capture(request, battle, trainer, response_data):
    """
    Finalise la capture après que l'animation client est terminée.
    Utilise le résultat pré-calculé en session (pas de nouveau random).
    Retourne True → early return.
    """
    from myPokemonApp.services.capture_service import _capture_success
    from myPokemonApp.models.CaptureSystem import CaptureAttempt

    pending = request.session.pop('pending_capture', None)

    if pending is None:
        # Session expirée : fallback avec un nouveau tirage
        inv    = get_object_or_404(TrainerInventory, pk=request.POST.get('item_id'))
        result = attempt_pokemon_capture(battle, ball_item=inv.item, trainer=trainer)
        inv    = get_object_or_404(TrainerInventory, pk=request.POST.get('item_id'))
    else:
        inv  = get_object_or_404(TrainerInventory, pk=pending['item_id'])
        item = inv.item
        if pending['success']:
            opponent   = battle.opponent_pokemon
            hp_percent = opponent.current_hp / opponent.max_hp
            cap_rate   = calculate_capture_rate(
                opponent, item, hp_percent, opponent.status_condition
            )
            attempt = CaptureAttempt.objects.create(
                trainer=trainer,
                pokemon_species=opponent.species,
                ball_used=item,
                pokemon_level=opponent.level,
                pokemon_hp_percent=hp_percent,
                pokemon_status=opponent.status_condition,
                capture_rate=cap_rate,
                battle=battle,
                success=False,
                shakes=pending['shakes'],
            )
            result = _capture_success(
                battle, opponent, item, trainer, attempt, shakes=pending['shakes']
            )
        else:
            result = {
                'success':          False,
                'capture_rate':     0,
                'shakes':           pending['shakes'],
                'message':          pending['message'],
                'captured_pokemon': None,
            }

    # Consommer la ball
    inv.quantity -= 1
    if inv.quantity == 0:
        inv.delete()
    else:
        inv.save(update_fields=['quantity'])

    if not result['success']:
        turn_before     = battle.current_turn
        opponent_action = get_opponent_ai_action(battle)
        battle.execute_turn({'type': 'PokeBall'}, opponent_action)
        # Rebuild response_data avec les HP à jour après l'attaque adverse.
        battle.refresh_from_db()
        fresh = build_battle_response(battle)
        response_data.update(fresh)

        # Récupérer les messages du battle_log générés par execute_turn
        # (dégâts, statut, etc. infligés par l'adversaire ce tour).
        opponent_logs = [
            entry['message'] for entry in battle.battle_log
            if entry.get('turn') in (turn_before, turn_before + 1)
        ]
        if not opponent_logs:
            opponent_logs = [entry['message'] for entry in battle.battle_log[-5:]]
        
        opponent_logs = [
            m.get('message', str(m)) if isinstance(m, dict) else m
            for m in opponent_logs
        ]
        # Le message d'échec de capture est ajouté en premier, suivi des dégâts adverses.
        response_data['log'] = [result['message']] + opponent_logs
    else:
        response_data['log'] = [result['message']]

    response_data['capture_result'] = result
    response_data['battle_ended']   = result['success']
    if result['success']:
        response_data['result'] = 'capture'
    return True  # early return


def _handle_confirm_evolution(request, battle, trainer, response_data):
    """
    Applique l'évolution après que l'animation client est terminée.
    Retourne un dict JSON prêt à l'envoi, ou None si l'évolution est invalide.
    """
    evolution_id = request.POST.get('evolution_id')
    evolution    = get_object_or_404(PokemonEvolution, pk=evolution_id)
    pokemon      = battle.player_pokemon

    if evolution.pokemon != pokemon.species:
        return None  # le caller renverra un 400

    new_species = evolution.evolves_to
    evolve_msg  = pokemon.evolve_to(new_species)

    battle.refresh_from_db()
    resp = build_battle_response(battle)
    resp['log']         = [evolve_msg]
    resp['evolved']     = True
    resp['new_species'] = new_species.name
    resp['stats_after'] = {
        'hp':              pokemon.max_hp,
        'attack':          pokemon.attack,
        'defense':         pokemon.defense,
        'special_attack':  pokemon.special_attack,
        'special_defense': pokemon.special_defense,
        'speed':           pokemon.speed,
    }
    return resp  # caller retourne JsonResponse(resp)


# Dispatch table — mappe action_type → handler
_ACTION_HANDLERS = {
    'attack':            _handle_attack,
    'flee':              _handle_flee,
    'switch':            _handle_switch,
    'item':              _handle_item,
    'confirm_capture':   _handle_confirm_capture,
    'confirm_evolution': _handle_confirm_evolution,
}


# =============================================================================
# ENDPOINTS
# =============================================================================

@login_required
@require_http_methods(['POST'])
def battle_action_view(request, pk):
    """
    API POST pour exécuter une action de combat.
    Retourne du JSON pour mise à jour en temps réel par le client.
    """
    battle  = get_object_or_404(Battle, pk=pk)
    trainer = get_player_trainer(request.user)

    if battle.player_trainer != trainer:
        return JsonResponse({'error': 'Not your battle'}, status=403)

    action_type = request.POST.get('action')

    if not battle.is_active and action_type not in ('confirm_evolution', 'confirm_capture'):
        return JsonResponse({'error': 'Battle already ended'}, status=400)

    handler = _ACTION_HANDLERS.get(action_type)
    if handler is None:
        return JsonResponse({'error': f'Unknown action: {action_type}'}, status=400)

    response_data = build_battle_response(battle)

    try:
        result = handler(request, battle, trainer, response_data)

        # ── Cas spéciaux : early return ou réponse pré-construite ────────────
        if action_type == 'confirm_evolution':
            if result is None:
                return JsonResponse({'error': 'Evolution invalide'}, status=400)
            if isinstance(result, dict):
                return JsonResponse(result)

        if action_type in ('confirm_capture', 'item') and result is True:
            return JsonResponse(response_data)

        # ── Rebuild de la réponse après exécution du tour ────────────────────
        turn_before       = battle.current_turn
        battle.refresh_from_db()
        ended_before      = response_data.get('battle_ended', False)
        result_before     = response_data.get('result')
        extra_logs        = list(response_data.get('log', []))
        pending_evolution = response_data.get('pending_evolution')
        pending_moves     = response_data.get('pending_moves')

        response_data = build_battle_response(battle)

        if ended_before:
            response_data['battle_ended'] = True
        if result_before:
            response_data['result'] = result_before
        if pending_evolution:
            response_data['pending_evolution'] = pending_evolution
        if pending_moves:
            response_data['pending_moves'] = pending_moves

        # Logs du tour actuel uniquement
        if battle.battle_log:
            turn_logs = [
                entry['message'] for entry in battle.battle_log
                if entry.get('turn') in (turn_before, turn_before + 1)
            ]
            if not turn_logs:
                turn_logs = [entry['message'] for entry in battle.battle_log[-5:]]
            turn_logs = [m.get('message', str(m)) if isinstance(m, dict) else m for m in turn_logs]
            seen   = set(turn_logs)
            merged = turn_logs + [m for m in extra_logs if m not in seen]
            response_data['log'] = merged
        elif extra_logs:
            response_data['log'] = extra_logs

        # Vérification finale de fin de combat
        if not response_data.get('battle_ended'):
            is_ended, winner, end_message = check_battle_end(battle)
            if is_ended:
                _save_hp_snapshot(battle)
                response_data['battle_ended'] = True
                response_data['winner']       = winner.username if winner else 'Draw'
                response_data['result']       = 'victory' if winner == battle.player_trainer else 'defeat'
                response_data['log'].append(end_message)

    except Exception as exc:
        logger.exception("Erreur inattendue dans battle_action_view pk=%s action=%s", pk, action_type)
        response_data['success'] = False
        response_data['error']   = "Une erreur est survenue. Veuillez réessayer."
        response_data['log']     = ["Erreur serveur. Réessayez dans un instant."]

    return JsonResponse(response_data)


@login_required
@require_http_methods(['POST'])
def battle_learn_move_view(request, pk):
    """
    Gère la décision du joueur lors de l'apprentissage d'un move (modal de sélection).

    POST params :
      new_move_id      : ID du move à apprendre
      replaced_move_id : ID du move à oublier (ou 'skip' pour ne pas apprendre)
      pokemon_id       : ID du PlayablePokemon concerné
    """
    battle  = get_object_or_404(Battle, pk=pk)
    trainer = get_player_trainer(request.user)

    if battle.player_trainer != trainer:
        return JsonResponse({'error': 'Not your battle'}, status=403)

    new_move_id      = request.POST.get('new_move_id')
    replaced_move_id = request.POST.get('replaced_move_id')
    pokemon_id       = request.POST.get('pokemon_id')

    pokemon  = get_object_or_404(PlayablePokemon, pk=pokemon_id, trainer=trainer)
    new_move = get_object_or_404(PokemonMove, pk=new_move_id)

    if replaced_move_id and replaced_move_id != 'skip':
        PokemonMoveInstance.objects.filter(
            pokemon=pokemon, move_id=replaced_move_id
        ).delete()
        PokemonMoveInstance.objects.get_or_create(
            pokemon=pokemon,
            move=new_move,
            defaults={'current_pp': new_move.pp}
        )
        message = f"{pokemon.species.name} oublie et apprend {new_move.name} !"
    else:
        message = f"{pokemon.species.name} n'apprend pas {new_move.name}."

    moves = serialize_pokemon_moves(pokemon)
    for m in moves:
        m.setdefault('max_pp', m['pp'])

    return JsonResponse({'success': True, 'message': message, 'moves': moves})