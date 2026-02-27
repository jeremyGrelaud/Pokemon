#!/usr/bin/python3
"""
Views Django pour les combats Pokemon Gen 1.
"""

import logging
import random
import traceback

from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.contrib import messages

from ..models import *

from myPokemonApp.questEngine import trigger_quest_event
from myPokemonApp.views.AchievementViews import (
    trigger_achievements_after_battle,
    trigger_achievements_after_gym_win,
)
from myPokemonApp.gameUtils import (
    # Pokemon / trainer
    get_first_alive_pokemon,
    get_or_create_wild_trainer,
    get_player_trainer,
    get_or_create_player_trainer,
    create_wild_pokemon,
    # Combats
    start_battle,
    get_opponent_ai_action,
    check_battle_end,
    opponent_switch_pokemon,
    calculate_exp_gain,
    apply_exp_gain,
    apply_ev_gains,
    # Capture
    attempt_pokemon_capture,
    calculate_capture_rate,
    # Serialisation
    build_battle_response,
    serialize_pokemon,
    serialize_pokemon_moves,
    # Utilitaires
    heal_team,
    learn_moves_up_to_level,
)

logger = logging.getLogger(__name__)


# =============================================================================
# LISTES ET DETAILS
# =============================================================================

@method_decorator(login_required, name='dispatch')
class BattleListView(generic.ListView):
    """Liste des combats du joueur connecté."""
    model               = Battle
    template_name       = 'battle/battle_list.html'
    context_object_name = 'battles'
    paginate_by         = 20

    def get_queryset(self):
        trainer = get_or_create_player_trainer(self.request.user)
        qs = Battle.objects.filter(
            Q(player_trainer=trainer) | Q(opponent_trainer=trainer)
        ).order_by('-created_at')

        result = self.request.GET.get('result', 'all')
        if result == 'win':
            qs = qs.filter(winner=trainer)
        elif result == 'loss':
            qs = qs.exclude(winner=trainer).exclude(winner__isnull=True)
        elif result == 'active':
            qs = qs.filter(is_active=True)

        battle_type = self.request.GET.get('type', 'all')
        if battle_type in ('wild', 'trainer', 'gym', 'elite_four'):
            qs = qs.filter(battle_type=battle_type)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer = get_or_create_player_trainer(self.request.user)
        all_battles = Battle.objects.filter(
            Q(player_trainer=trainer) | Q(opponent_trainer=trainer)
        )
        context['stat_total']    = all_battles.count()
        context['stat_win']      = all_battles.filter(winner=trainer).count()
        context['stat_loss']     = all_battles.exclude(winner=trainer).exclude(winner__isnull=True).count()
        context['stat_active']   = all_battles.filter(is_active=True).count()
        context['result_filter'] = self.request.GET.get('result', 'all')
        context['type_filter']   = self.request.GET.get('type', 'all')
        return context


@method_decorator(login_required, name='dispatch')
class BattleDetailView(generic.DetailView):
    """Details d'un combat termine."""
    model               = Battle
    template_name       = 'battle/battle_detail.html'
    context_object_name = 'battle'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        battle  = self.object

        viewer     = get_player_trainer(self.request.user)
        player_won = (battle.winner == battle.player_trainer) if battle.winner else None

        bs                = battle.battle_state if isinstance(battle.battle_state, dict) else {}
        player_used_ids   = bs.get('player_used_ids', [])
        opponent_used_ids = bs.get('opponent_used_ids', [])
        hp_snapshot       = bs.get('hp_snapshot', {})

        # ── Équipe joueur : filtrer par player_used_ids si disponible ─────────
        if player_used_ids:
            player_team = list(
                battle.player_trainer.pokemon_team
                .filter(id__in=player_used_ids)
                .select_related('species', 'species__primary_type', 'species__secondary_type')
            )
        else:
            # Fallback legacy : équipe complète en party
            player_team = list(
                battle.player_trainer.pokemon_team
                .filter(is_in_party=True)
                .select_related('species', 'species__primary_type', 'species__secondary_type')
            )

        # ── Équipe adversaire ─────────────────────────────────────────────────
        if battle.battle_type == 'wild' or not battle.opponent_trainer:
            opponent_team = [battle.opponent_pokemon] if battle.opponent_pokemon else []
        elif opponent_used_ids:
            opponent_team = list(
                battle.opponent_trainer.pokemon_team
                .filter(id__in=opponent_used_ids)
                .select_related('species', 'species__primary_type', 'species__secondary_type')
            )
        else:
            opponent_team = list(
                battle.opponent_trainer.pokemon_team
                .filter(is_in_party=True)
                .select_related('species', 'species__primary_type', 'species__secondary_type')
            )

        # Argent gagné depuis l'historique
        money_earned = 0
        try:
            history = TrainerBattleHistory.objects.get(
                battle=battle, player=battle.player_trainer
            )
            money_earned = history.money_earned
        except (TrainerBattleHistory.DoesNotExist, Exception):
            pass

        context.update({
            'viewer':        viewer,
            'player_won':    player_won,
            'player_team':   player_team,
            'opponent_team': opponent_team,
            'money_earned':  money_earned,
            'hp_snapshot':   hp_snapshot,
        })
        return context

# =============================================================================
# VUE DE COMBAT GRAPHIQUE
# =============================================================================

@method_decorator(login_required, name='dispatch')
class BattleGameView(generic.DetailView):
    """Vue du combat en mode graphique (template battle_game_v2)."""
    model               = Battle
    template_name       = 'battle/battle_game_v2.html'
    context_object_name = 'battle'

    def get_queryset(self):
        trainer = get_player_trainer(self.request.user)
        return Battle.objects.filter(player_trainer=trainer)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        battle  = self.object
        if not battle.player_pokemon or not battle.opponent_pokemon:
            context['error'] = "Combat invalide : Pokemon manquant"

        # Zone actuelle du joueur (pour les boutons "Retour" des modals)
        try:
            player_location = PlayerLocation.objects.get(trainer=battle.player_trainer)
            context['current_zone'] = player_location.current_zone
        except PlayerLocation.DoesNotExist:
            context['current_zone'] = None

        # Rival : trainer_type == 'rival' → musique spéciale
        context['is_rival'] = (
            battle.opponent_trainer is not None
            and battle.opponent_trainer.trainer_type == 'rival'
        )

        # Pourcentage EXP correct (relatif au niveau actuel, pas cumulatif)
        pp = battle.player_pokemon
        if pp:
            exp_at_current = pp.exp_at_level(pp.level)
            exp_at_next    = pp.exp_for_next_level()
            exp_in_level   = max(0, (pp.current_exp or 0) - exp_at_current)
            exp_needed     = max(1, exp_at_next - exp_at_current)
            context['initial_exp_percent'] = int(min(100, (exp_in_level / exp_needed) * 100))
        else:
            context['initial_exp_percent'] = 0

        return context


# =============================================================================
# API — ACTIONS DE COMBAT
# =============================================================================


# =============================================================================
# HANDLERS D'ACTIONS DE COMBAT  (un handler = une action, testable isolément)
# =============================================================================

def _handle_attack(request, battle, trainer, response_data):
    """Attaque avec un move choisi par le joueur."""
    move         = get_object_or_404(PokemonMove, pk=request.POST.get('move_id'))
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



def _save_hp_snapshot(battle):
    """
    Enregistre les HP actuels de TOUS les Pokémon de l'équipe du joueur
    (pas seulement ceux envoyés en combat) ainsi que ceux de l'adversaire.
    Appelé juste avant de marquer un combat comme terminé.
    Format : { str(pokemon_id): {'hp': int, 'max_hp': int, 'ko': bool} }
    """
    try:
        bs = battle.battle_state if isinstance(battle.battle_state, dict) else {}
        snapshot = {}

        # Toute l'équipe du joueur (in party), qu'ils aient combattu ou non
        for poke in battle.player_trainer.pokemon_team.filter(is_in_party=True):
            snapshot[str(poke.id)] = {
                'hp':     poke.current_hp,
                'max_hp': poke.max_hp,
                'ko':     poke.current_hp == 0,
            }

        # Pokémon adverses qui ont participé
        opponent_used_ids = bs.get('opponent_used_ids', [])
        if battle.opponent_trainer and opponent_used_ids:
            for poke in battle.opponent_trainer.pokemon_team.filter(id__in=opponent_used_ids):
                snapshot[str(poke.id)] = {
                    'hp':     poke.current_hp,
                    'max_hp': poke.max_hp,
                    'ko':     poke.current_hp == 0,
                }
        elif battle.opponent_pokemon:
            p = battle.opponent_pokemon
            snapshot[str(p.id)] = {
                'hp':     p.current_hp,
                'max_hp': p.max_hp,
                'ko':     p.current_hp == 0,
            }

        bs['hp_snapshot'] = snapshot
        battle.battle_state = bs
        battle.save(update_fields=['battle_state'])
    except Exception as exc:
        logger.warning("Impossible de sauvegarder hp_snapshot : %s", exc)


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
    bs = battle.battle_state if isinstance(battle.battle_state, dict) else {}
    used = bs.get('player_used_ids', [])
    if new_pokemon.id not in used:
        used.append(new_pokemon.id)
    bs['player_used_ids'] = used
    battle.battle_state = bs
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

    Retourne (response, early_return) où early_return=True signifie qu'on
    doit renvoyer la réponse immédiatement sans rebuild.
    """
    from myPokemonApp.gameUtils import calculate_capture_rate, calculate_shake_count
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

    # Consommer l'objet si consommable (pokéball déjà gérée dans confirm_capture)
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
    from myPokemonApp.gameUtils import _capture_success, calculate_capture_rate
    from myPokemonApp.models import CaptureAttempt

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
        opponent_action = get_opponent_ai_action(battle)
        battle.execute_turn({'type': 'PokeBall'}, opponent_action)

    response_data['capture_result'] = result
    response_data['battle_ended']   = result['success']
    response_data['log']            = [result['message']]
    if result['success']:
        response_data['result'] = 'capture'
    return True  # early return


def _handle_confirm_evolution(request, battle, trainer, response_data):
    """
    Applique l'évolution après que l'animation client est terminée.
    Retourne True → early return.
    """
    from myPokemonApp.models.PokemonEvolution import PokemonEvolution

    evolution_id = request.POST.get('evolution_id')
    evolution    = get_object_or_404(PokemonEvolution, pk=evolution_id)
    pokemon      = battle.player_pokemon

    if evolution.pokemon != pokemon.species:
        return None  # will raise 400 in caller

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
    return resp  # caller returns JsonResponse(resp)


# Dispatch table — mappe action_type → handler
_ACTION_HANDLERS = {
    'attack':           _handle_attack,
    'flee':             _handle_flee,
    'switch':           _handle_switch,
    'item':             _handle_item,
    'confirm_capture':  _handle_confirm_capture,
    'confirm_evolution': _handle_confirm_evolution,
}


@login_required
def battle_action_view(request, pk):
    """
    API POST pour exécuter une action de combat.
    Retourne du JSON pour mise à jour en temps réel par le client.

    Actions supportées :
      attack           : attaquer avec un move
      flee             : tenter de fuir
      switch           : changer de Pokémon (normal ou forcé après KO)
      item             : utiliser un objet (pokeball → pré-animation capture)
      confirm_capture  : finaliser la capture après l'animation côté client
      confirm_evolution: appliquer l'évolution après l'animation côté client
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

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

        # ── Cas spéciaux : early return ou réponse pré-construite ───────────
        if action_type == 'confirm_evolution':
            if result is None:
                return JsonResponse({'error': 'Evolution invalide'}, status=400)
            if isinstance(result, dict):
                return JsonResponse(result)

        if action_type in ('confirm_capture', 'item') and result is True:
            return JsonResponse(response_data)

        # ── Rebuild de la réponse après exécution du tour ───────────────────
        # Capturer le numéro de tour AVANT refresh pour filtrer les bons logs
        turn_before = battle.current_turn
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

        # Logs du tour actuel uniquement (filtrés par turn_before et turn_before+1
        # car current_turn est incrémenté en fin de execute_turn)
        if battle.battle_log:
            turn_logs = [
                entry['message'] for entry in battle.battle_log
                if entry.get('turn') in (turn_before, turn_before + 1)
            ]
            # Fallback : si aucun log trouvé par turn, prendre les 5 derniers
            if not turn_logs:
                turn_logs = [entry['message'] for entry in battle.battle_log[-5:]]
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
        traceback.print_exc()
        response_data['success'] = False
        response_data['error']   = str(exc)
        response_data['log']     = [f'Erreur : {exc}']

    return JsonResponse(response_data)


# =============================================================================
# VUE DE CREATION DE COMBAT (page avec 3 onglets)
# =============================================================================

@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def battle_create_view(request):
    """
    Page de creation de combat avec 3 onglets (super_user uniquement) :
      1. Pokemon Sauvage
      2. Dresseurs NPC
      3. Champions d'Arene
    """
    player_trainer = get_player_trainer(request.user)

    save = GameSave.objects.filter(trainer=player_trainer, is_active=True).first()

    npc_trainers       = Trainer.objects.filter(is_npc=True, trainer_type='trainer').order_by('location', 'username')
    trainer_locations  = list(npc_trainers.values_list('location', flat=True).distinct())
    trainer_classes    = [c for c in npc_trainers.values_list('npc_class', flat=True).distinct() if c]

    fightable_gym_leaders = [
        gl for gl in GymLeader.objects.all()
        if gl.isChallengableByPlayer(player_trainer=player_trainer)
    ]

    context = {
        'all_pokemon':      Pokemon.objects.all().order_by('pokedex_number'),
        'npc_trainers':     npc_trainers,
        'trainer_locations': trainer_locations,
        'trainer_classes':  trainer_classes,
        'gym_leaders':      fightable_gym_leaders,
        'save':             save,
    }
    return render(request, 'battle/battle_create.html', context)


# =============================================================================
# WILD BATTLE
# =============================================================================

@login_required
def battle_create_wild_view(request):
    """
    Cree un combat contre un Pokemon sauvage aleatoire (ou specifique en mode debug).

    POST params :
      pokemon_id (optionnel) : forcer une espece precise (debug)
      level      (optionnel) : forcer le niveau (defaut : autour du joueur +-3)
    """
    if request.method != 'POST':
        return redirect('BattleCreateView')

    player_trainer = get_player_trainer(request.user)
    player_pokemon = get_first_alive_pokemon(player_trainer)

    if not player_pokemon:
        messages.error(request, "Vous n'avez pas de Pokemon en etat de combattre !")
        return redirect('PokemonCenterListView')

    # Choisir l'espece et le niveau
    pokemon_id = request.POST.get('pokemon_id')
    if pokemon_id:
        wild_species = get_object_or_404(Pokemon, pk=pokemon_id)
        level        = int(request.POST.get('level', 5))
    else:
        all_pokemon = Pokemon.objects.all()
        if not all_pokemon.exists():
            messages.error(request, "Aucun Pokemon sauvage disponible !")
            return redirect('BattleCreateView')
        wild_species = all_pokemon.order_by('?').first()
        level        = max(1, player_pokemon.level + random.randint(-3, 3))

    # Creer le Pokemon sauvage (stats + moves + fallback Tackle) via gameUtils
    wild_pokemon = create_wild_pokemon(wild_species, level)

    # Réinitialiser les stages des deux Pokémon avant le combat
    player_pokemon.reset_combat_stats()
    wild_pokemon.reset_combat_stats()

    battle = Battle.objects.create(
        player_trainer=player_trainer,
        opponent_trainer=None,
        player_pokemon=player_pokemon,
        opponent_pokemon=wild_pokemon,
        battle_type='wild',
        is_active=True,
    )

    messages.success(request, f"Un {wild_species.name} sauvage de niveau {level} apparait !")
    return redirect('BattleGameView', pk=battle.id)


# =============================================================================
# TRAINER BATTLE
# =============================================================================

@login_required
def battle_create_trainer_view(request, trainer_id):
    """Cree un combat contre un dresseur NPC."""
    player_trainer   = get_player_trainer(request.user)
    opponent_trainer = get_object_or_404(Trainer, pk=trainer_id, is_npc=True)

    # Vérifier que le joueur est bien dans la zone du dresseur
    try:
        player_location = PlayerLocation.objects.get(trainer=player_trainer)
        if opponent_trainer.location and player_location.current_zone.name != opponent_trainer.location:
            messages.error(
                request,
                f"{opponent_trainer.get_full_title()} se trouve à {opponent_trainer.location}, "
                f"mais vous êtes à {player_location.current_zone.name} !",
            )
            return redirect('zone_detail', zone_id=player_location.current_zone.id)
    except PlayerLocation.DoesNotExist:
        messages.error(request, "Position introuvable. Veuillez voyager vers une zone.")
        return redirect('map_view')

    heal_team(opponent_trainer)

    # Vérifie si le dresseur a déjà été battu dans la save
    save = GameSave.objects.filter(trainer=player_trainer, is_active=True).first()
    if save and save.is_trainer_defeated(opponent_trainer.id) and not opponent_trainer.can_rebattle:
        messages.warning(request, f"Vous avez deja battu {opponent_trainer.get_full_title()}")
        return redirect('zone_detail', zone_id=player_location.current_zone.id)

    player_pokemon   = get_first_alive_pokemon(player_trainer)
    opponent_pokemon = get_first_alive_pokemon(opponent_trainer)

    if not player_pokemon:
        messages.error(request, "Vous n'avez pas de Pokemon en etat de combattre !")
        return redirect('PokemonCenterListView')
    if not opponent_pokemon:
        messages.error(request, "Ce dresseur n'a pas d'equipe configuree !")
        return redirect('BattleCreateView')
    
    # Réinitialiser les stages des deux Pokémon avant le combat
    player_pokemon.reset_combat_stats()
    opponent_pokemon.reset_combat_stats()

    battle = Battle.objects.create(
        player_trainer=player_trainer,
        opponent_trainer=opponent_trainer,
        player_pokemon=player_pokemon,
        opponent_pokemon=opponent_pokemon,
        battle_type='trainer',
        is_active=True,
    )

    messages.info(request, opponent_trainer.intro_text or f"Vous affrontez {opponent_trainer.get_full_title()} !")
    return redirect('BattleGameView', pk=battle.id)


# =============================================================================
# GYM LEADER BATTLE
# =============================================================================

@login_required
def battle_create_gym_view(request):
    """Cree un combat contre un Champion d'Arene."""
    if request.method != 'POST':
        return redirect('BattleCreateView')

    player_trainer = get_player_trainer(request.user)
    gym_leader_id  = request.POST.get('gym_leader_id')

    try:
        gym_leader = GymLeader.objects.select_related('trainer').get(pk=gym_leader_id)
    except GymLeader.DoesNotExist:
        messages.error(request, "Champion d'Arene introuvable !")
        return redirect('BattleCreateView')

    opponent_trainer = gym_leader.trainer
    heal_team(opponent_trainer)

    if not gym_leader.isChallengableByPlayer(player_trainer):
        messages.warning(
            request,
            f"Vous devez avoir au moins {gym_leader.badge_order - 1} badge(s) "
            f"pour defier {opponent_trainer.username}"
        )
        return redirect('BattleCreateView')

    player_pokemon   = get_first_alive_pokemon(player_trainer)
    opponent_pokemon = get_first_alive_pokemon(opponent_trainer)

    if not player_pokemon:
        messages.error(request, "Vous n'avez pas de Pokemon en etat de combattre !")
        return redirect('PokemonCenterListView')
    if not opponent_pokemon:
        messages.error(request, "Le Champion n'a pas d'equipe configuree !")
        return redirect('BattleCreateView')

    # Réinitialiser les stages des deux Pokémon avant le combat
    player_pokemon.reset_combat_stats()
    opponent_pokemon.reset_combat_stats()

    battle = Battle.objects.create(
        player_trainer=player_trainer,
        opponent_trainer=opponent_trainer,
        player_pokemon=player_pokemon,
        opponent_pokemon=opponent_pokemon,
        battle_type='gym',
        is_active=True,
    )

    messages.info(
        request,
        opponent_trainer.intro_text
        or f"Vous defiez {opponent_trainer.username}, Champion d'Arene de {gym_leader.gym_city} !"
    )
    return redirect('BattleGameView', pk=battle.id)

# =============================================================================
# GYM LEADER BATTLE depuis la zone (GET)
# =============================================================================

# Correspondance gym_city (anglais) → nom de zone (français)
_GYM_CITY_TO_ZONE = {
    "Pewter City":    "Argenta",
    "Cerulean City":  "Azuria",
    "Vermilion City": "Carmin sur Mer",
    "Celadon City":   "Céladopole",
    "Saffron City":   "Safrania",
    "Fuchsia City":   "Parmanie",
    "Cinnabar Island":"Cramois'Ile",
    "Viridian City":  "Jadielle",
}


@login_required
def battle_challenge_gym_view(request, gym_leader_id):
    """
    Lance un combat contre un Champion d'Arène directement depuis zone_detail.
    Accessible via GET  /battle/gym/<id>/challenge/
    Vérifie que le joueur est bien dans la ville de l'arène.
    """
    player_trainer = get_player_trainer(request.user)

    try:
        gym_leader = GymLeader.objects.select_related('trainer').get(pk=gym_leader_id)
    except GymLeader.DoesNotExist:
        messages.error(request, "Champion d'Arène introuvable !")
        return redirect('GymLeaderListView')

    # Vérifier que le joueur est dans la bonne ville
    try:
        player_location = PlayerLocation.objects.get(trainer=player_trainer)
        current_zone    = player_location.current_zone
        print(gym_leader.gym_city)
        expected_zone   = _GYM_CITY_TO_ZONE.get(gym_leader.gym_city, gym_leader.gym_city)
        if current_zone.name != expected_zone:
            messages.error(
                request,
                f"L'arène de {gym_leader.trainer.username} se trouve à {expected_zone}, "
                f"mais vous êtes à {current_zone.name} !",
            )
            return redirect('zone_detail', zone_id=current_zone.id)
    except PlayerLocation.DoesNotExist:
        messages.error(request, "Position introuvable. Veuillez voyager vers une zone.")
        return redirect('map_view')

    # Vérification badge
    if not gym_leader.isChallengableByPlayer(player_trainer):
        messages.warning(
            request,
            f"Vous avez besoin d'au moins {gym_leader.badge_order - 1} badge(s) "
            f"pour défier {gym_leader.trainer.username} !",
        )
        return redirect('zone_detail', zone_id=current_zone.id)

    opponent_trainer = gym_leader.trainer
    heal_team(opponent_trainer)

    player_pokemon   = get_first_alive_pokemon(player_trainer)
    opponent_pokemon = get_first_alive_pokemon(opponent_trainer)

    if not player_pokemon:
        messages.error(request, "Vous n'avez pas de Pokémon en état de combattre !")
        return redirect('PokemonCenterListView')
    if not opponent_pokemon:
        messages.error(request, "Le Champion n'a pas d'équipe configurée !")
        return redirect('GymLeaderDetailView', pk=gym_leader.id)

    # Réinitialiser les stages des deux Pokémon avant le combat
    player_pokemon.reset_combat_stats()
    opponent_pokemon.reset_combat_stats()
    
    battle = Battle.objects.create(
        player_trainer=player_trainer,
        opponent_trainer=opponent_trainer,
        player_pokemon=player_pokemon,
        opponent_pokemon=opponent_pokemon,
        battle_type='gym',
        is_active=True,
    )

    messages.info(
        request,
        opponent_trainer.intro_text
        or f"Vous défiez {opponent_trainer.username}, Champion d'Arène de {gym_leader.gym_city} !",
    )
    return redirect('BattleGameView', pk=battle.id)


# =============================================================================
# BATTLE COMPLETE (apres un combat contre un dresseur)
# =============================================================================

@login_required
def battle_trainer_complete_view(request, battle_id):
    """
    Appele apres un combat contre un dresseur NPC.
    Distribue les recompenses, enregistre l'historique, declenche les achievements.
    """
    battle         = get_object_or_404(Battle, pk=battle_id)
    player_trainer = get_player_trainer(request.user)

    if battle.player_trainer != player_trainer:
        return redirect('home')

    player_won = battle.winner == player_trainer
    opponent   = battle.opponent_trainer

    # =========================================================
    # VICTOIRE
    # =========================================================
    money_earned = 0
    badge_earned = None

    if player_won:
        # --- Achievements ---
        notifications = trigger_achievements_after_battle(
            player_trainer,
            {'won': True, 'opponent_type': opponent.trainer_type if opponent else 'wild'}
        )
        for notif in notifications:
            messages.success(request, f"{notif['title']} : {notif['message']}")

        # --- Argent ---
        if opponent and opponent.trainer_type != 'wild':
            money_earned = opponent.get_reward()
            player_trainer.money += money_earned
            player_trainer.save()

        # --- Badge Arène ---
        if opponent:
            try:
                gym_info = GymLeader.objects.get(trainer=opponent)
                # Donner le badge si le joueur ne l'a pas encore
                if player_trainer.badges < gym_info.badge_order:
                    player_trainer.badges = gym_info.badge_order
                    player_trainer.save()
                    badge_earned = gym_info
                    messages.success(
                        request,
                        f"🏅 Vous avez obtenu le {gym_info.badge_name} !"
                    )
                    # Achievements badges
                    gym_notifications = trigger_achievements_after_gym_win(
                        player_trainer, player_trainer.badges
                    )
                    for notif in gym_notifications:
                        messages.success(request, f"{notif['title']} : {notif['message']}")
            except GymLeader.DoesNotExist:
                pass  # Pas un Champion d'Arène

    # =========================================================
    # HISTORIQUE
    # =========================================================
    try:
        TrainerBattleHistory.objects.create(
            player=player_trainer,
            opponent=opponent,
            player_won=player_won,
            battle=battle,
            money_earned=money_earned,
        )
    except Exception as exc:
        logger.warning("Impossible de créer l'historique de combat : %s", exc)

    try:
        save = GameSave.objects.filter(trainer=player_trainer, is_active=True).first()
        if save and player_won and opponent:
            save.add_defeated_trainer(opponent.id)
    except Exception as exc:
        logger.warning("Impossible de marquer le dresseur %s comme battu : %s", opponent, exc)

    # =========================================================
    # QUÊTES — defeat_trainer / defeat_gym
    # =========================================================
    if player_won and opponent:
        try:
            # Tout combat contre un dresseur
            quest_notifs = trigger_quest_event(
                player_trainer, 'defeat_trainer', trainer_id=opponent.id
            )
            for notif in quest_notifs:
                msg = f"✅ Quête terminée : « {notif['title']} »"
                if notif.get('reward_money'):
                    msg += f" (+{notif['reward_money']}₽)"
                if notif.get('reward_item'):
                    msg += f" · Objet reçu : {notif['reward_item']}"
                messages.success(request, msg)

            # Combat arène spécifiquement
            if badge_earned:
                gym_notifs = trigger_quest_event(
                    player_trainer, 'defeat_gym', gym_leader=badge_earned
                )
                for notif in gym_notifs:
                    msg = f"✅ Quête terminée : « {notif['title']} »"
                    if notif.get('reward_money'):
                        msg += f" (+{notif['reward_money']}₽)"
                    if notif.get('reward_item'):
                        msg += f" · Objet reçu : {notif['reward_item']}"
                    messages.success(request, msg)

        except Exception as exc:
            logger.warning("Erreur déclenchement quêtes post-combat : %s", exc)

    # =========================================================
    # DÉFAITE → soigner et rediriger vers le Centre Pokémon le plus proche
    # =========================================================
    if not player_won:
        try:
            # Trouver la zone avec Centre Pokémon
            player_location = PlayerLocation.objects.get(trainer=player_trainer)
            current_zone    = player_location.current_zone

            # Chercher le centre le plus proche : d'abord la zone actuelle, sinon
            # la première zone connectée avec un centre
            if current_zone.has_pokemon_center:
                center_zone = current_zone
            else:
                # Chercher parmi les connexions directes
                connected_ids = ZoneConnection.objects.filter(
                    from_zone=current_zone
                ).values_list('to_zone_id', flat=True)
                reverse_ids  = ZoneConnection.objects.filter(
                    to_zone=current_zone, is_bidirectional=True
                ).values_list('from_zone_id', flat=True)
                all_ids      = list(connected_ids) + list(reverse_ids)

                center_zone = Zone.objects.filter(
                    id__in=all_ids, has_pokemon_center=True
                ).first()

                if not center_zone:
                    # Fallback: premier centre disponible
                    center_zone = Zone.objects.filter(has_pokemon_center=True).first()

            if center_zone:
                player_location.current_zone = center_zone
                if center_zone.has_pokemon_center:
                    player_location.last_pokemon_center = center_zone
                player_location.save()

                # Sauvegarder la location dans la save active
                save = GameSave.objects.filter(trainer=player_trainer, is_active=True).first()
                if save:
                    save.current_location = center_zone.name
                    save.save()

                messages.warning(
                    request,
                    f"Vous avez été soigné au Centre Pokémon de {center_zone.name}."
                )

        except PlayerLocation.DoesNotExist:
            pass

    dialogue = (
        (opponent.defeat_text  or "Vous avez gagne...") if player_won
        else (opponent.victory_text or "J'ai gagne !") if opponent
        else ""
    )

    # Récupérer la zone courante du joueur pour les liens de navigation
    try:
        player_location = PlayerLocation.objects.get(trainer=player_trainer)
        current_zone = player_location.current_zone
    except PlayerLocation.DoesNotExist:
        current_zone = None

    return render(request, 'battle/battle_trainer_complete.html', {
        'battle':        battle,
        'opponent':      opponent,
        'player_won':    player_won,
        'money_earned':  money_earned,
        'badge_earned':  badge_earned,
        'dialogue':      dialogue,
        'current_zone':  current_zone,
    })


# =============================================================================
# API — EQUIPE DU DRESSEUR
# =============================================================================

@login_required
@require_http_methods(['GET'])
def GetTrainerTeam(request):
    """
    Retourne l'equipe active du dresseur (is_in_party=True, max 6 Pokemon).
    Utilise serialize_pokemon() de gameUtils pour eviter la duplication de structure.
    """
    trainer_id         = request.GET.get('trainer_id')
    exclude_pokemon_id = request.GET.get('exclude_pokemon_id')

    trainer = get_object_or_404(Trainer, pk=trainer_id)
    team    = trainer.pokemon_team.filter(is_in_party=True)

    if exclude_pokemon_id:
        team = team.exclude(pk=exclude_pokemon_id)

    # serialize_pokemon retourne id/name/species/level/current_hp/max_hp/status.
    # On ajoute nickname et species.id pour la compatibilite avec le template existant.
    team_data = []
    for pokemon in team:
        data = serialize_pokemon(pokemon)
        data['nickname'] = pokemon.nickname
        data['species']  = {'name': pokemon.species.name, 'id': pokemon.species.id}
        data['status_condition'] = pokemon.status_condition  # alias pour le JS
        team_data.append(data)

    return JsonResponse({'success': True, 'team': team_data})


# =============================================================================
# API — INVENTAIRE DU DRESSEUR
# =============================================================================

@login_required
@require_http_methods(['GET'])
def GetTrainerItems(request):
    """Retourne les objets du dresseur avec leurs quantites."""
    trainer  = get_object_or_404(Trainer, pk=request.GET.get('trainer_id'))
    BATTLE_USABLE_TYPES = ('potion', 'pokeball', 'status', 'battle')
    inventory = TrainerInventory.objects.filter(
        trainer=trainer,
        quantity__gt=0,
        item__item_type__in=BATTLE_USABLE_TYPES,
    ).select_related('item') #avoid showing quest or key items

    items_data = [
        {'id': inv.id, 'name': inv.item.name, 'quantity': inv.quantity, 
         'item_type': inv.item.item_type, 'description': inv.item.description}
        for inv in inventory
    ]

    return JsonResponse({'success': True, 'items': items_data})


# =============================================================================
# API — APPRENTISSAGE DE MOVE (modal de selection)
# =============================================================================

@login_required
@require_http_methods(['POST'])
def battle_learn_move_view(request, pk):
    """
    Gere la decision du joueur lors de l'apprentissage d'un move (modal de selection).

    POST params :
      new_move_id      : ID du move a apprendre
      replaced_move_id : ID du move a oublier (ou 'skip' pour ne pas apprendre)
      pokemon_id       : ID du PlayablePokemon concerne
    """
    from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance

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

    # serialize_pokemon_moves remplace le rebuild inline
    moves = serialize_pokemon_moves(pokemon)
    # Ajouter max_pp pour la compatibilité avec le template existant
    for m in moves:
        m.setdefault('max_pp', m['pp'])

    return JsonResponse({'success': True, 'message': message, 'moves': moves})