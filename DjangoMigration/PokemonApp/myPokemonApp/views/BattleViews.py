#!/usr/bin/python3
"""
Views Django pour les combats Pokemon Gen 1.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.contrib import messages
from ..models import *
# Zone/location models needed for defeat redirect
from myPokemonApp.models import Zone, ZoneConnection, PlayerLocation

from myPokemonApp.views.AchievementViews import trigger_achievements_after_battle
from myPokemonApp.gameUtils import (
    # Pokemon / trainer
    get_first_alive_pokemon,
    get_or_create_wild_trainer,
    create_wild_pokemon,
    # Combats
    start_battle,
    get_opponent_ai_action,
    check_battle_end,
    opponent_switch_pokemon,
    calculate_exp_gain,
    apply_exp_gain,
    # Capture
    attempt_pokemon_capture,
    calculate_capture_rate,
    # Serialisation
    build_battle_response,
    serialize_pokemon,
    # Utilitaires
    heal_team,
    learn_moves_up_to_level,
)


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
        trainer = Trainer.objects.get(username=self.request.user.username)
        return Battle.objects.filter(
            Q(player_trainer=trainer) | Q(opponent_trainer=trainer)
        ).order_by('-created_at')


@method_decorator(login_required, name='dispatch')
class BattleDetailView(generic.DetailView):
    """Details d'un combat termine."""
    model               = Battle
    template_name       = 'battle/battle_detail.html'
    context_object_name = 'battle'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        battle  = self.object

        viewer = get_object_or_404(Trainer, username=self.request.user.username)
        player_won = (battle.winner == battle.player_trainer) if battle.winner else None

        # Équipe complète du joueur (depuis le trainer du combat)
        player_team = battle.player_trainer.pokemon_team.filter(
            is_in_party=True
        ).select_related('species', 'species__primary_type', 'species__secondary_type')

        # Équipe complète de l'adversaire
        # Pour les combats sauvages : toujours utiliser opponent_pokemon (le pokemon unique
        # du combat), même si opponent_trainer est renseigné (données corrompues legacy).
        if battle.battle_type == 'wild' or not battle.opponent_trainer:
            opponent_team = [battle.opponent_pokemon] if battle.opponent_pokemon else []
        else:
            opponent_team = list(battle.opponent_trainer.pokemon_team.filter(
                is_in_party=True
            ).select_related('species', 'species__primary_type', 'species__secondary_type'))

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
        trainer = get_object_or_404(Trainer, username=self.request.user.username)
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

        return context


# =============================================================================
# API — ACTIONS DE COMBAT
# =============================================================================

@login_required
def battle_action_view(request, pk):
    """
    API POST pour executer une action de combat.
    Retourne du JSON pour mise a jour en temps reel par le client.

    Actions supportees :
      attack          : attaquer avec un move
      flee            : tenter de fuir
      switch          : changer de Pokemon (normal ou force apres KO)
      item            : utiliser un objet (pokeball -> pre-animation capture)
      confirm_capture : effectuer la capture apres l'animation cote client
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    battle  = get_object_or_404(Battle, pk=pk)
    trainer = get_object_or_404(Trainer, username=request.user.username)

    if battle.player_trainer != trainer:
        return JsonResponse({'error': 'Not your battle'}, status=403)

    if not battle.is_active:
        # confirm_evolution peut arriver après la fin du combat (animation côté client)
        action_type = request.POST.get('action')
        if action_type != 'confirm_evolution':
            return JsonResponse({'error': 'Battle already ended'}, status=400)

    action_type   = request.POST.get('action')
    response_data = build_battle_response(battle)

    try:
        # ------------------------------------------------------------------
        if action_type == 'attack':
            move         = get_object_or_404(PokemonMove, pk=request.POST.get('move_id'))
            player_action   = {'type': 'attack', 'move': move}
            opponent_action = get_opponent_ai_action(battle)

            battle.execute_turn(player_action, opponent_action)

            if battle.opponent_pokemon.current_hp == 0:
                btype      = 'trainer' if battle.opponent_trainer else 'wild'
                exp_amount = calculate_exp_gain(battle.opponent_pokemon, btype)
                exp_result = apply_exp_gain(battle.player_pokemon, exp_amount)

                response_data['log'].append(f"+{exp_amount} EXP")
                if exp_result['level_up']:
                    response_data['log'].append(f"Level {exp_result['new_level']} !")
                for move_name in exp_result.get('learned_moves', []):
                    response_data['log'].append(f"{battle.player_pokemon.species.name} apprend {move_name} !")

                # Moves en attente d'apprentissage (pokemon a deja 4 moves)
                if exp_result.get('pending_moves'):
                    response_data['pending_moves'] = exp_result['pending_moves']

                # Évolution en attente (prioritaire sur la fin de combat)
                if exp_result.get('pending_evolution'):
                    response_data['pending_evolution'] = exp_result['pending_evolution']

                # Switch adversaire si dresseur avec d'autres Pokemon
                if battle.opponent_trainer:
                    new_opponent = opponent_switch_pokemon(battle)
                    if new_opponent:
                        response_data['log'].append(
                            f"Adversaire envoie {new_opponent.species.name} !"
                        )
                    else:
                        battle.is_active = False
                        battle.winner    = battle.player_trainer
                        battle.save()
                        response_data['battle_ended'] = True
                        response_data['result']       = 'victory'
                else:
                    battle.is_active = False
                    battle.winner    = battle.player_trainer
                    battle.save()
                    response_data['battle_ended'] = True
                    response_data['result']       = 'victory'

        # ------------------------------------------------------------------
        elif action_type == 'flee':
            success = battle.attempt_flee()
            response_data['fled'] = success
            if success:
                # Le joueur fuit = victoire morale, on marque le combat terminé
                battle.is_active = False
                battle.winner = battle.player_trainer
                battle.save()
                response_data['log']          = ['Vous avez reussi a fuir !']
                response_data['battle_ended'] = True
                response_data['result']       = 'fled'
            else:
                response_data['log'] = ['Echec dans la fuite !']

        # ------------------------------------------------------------------
        elif action_type == 'switch':
            new_pokemon = get_object_or_404(
                PlayablePokemon, pk=request.POST.get('pokemon_id'), trainer=trainer
            )
            player_action = {'type': 'switch', 'pokemon': new_pokemon}

            # Switch force (apres KO) : l'adversaire ne joue pas ce tour
            if request.POST.get('type') == 'forcedSwitch':
                opponent_action = {}
            else:
                opponent_action = get_opponent_ai_action(battle)

            battle.execute_turn(player_action, opponent_action)

        # ------------------------------------------------------------------
        elif action_type == 'item':
            inv  = get_object_or_404(TrainerInventory, pk=request.POST.get('item_id'))
            item = inv.item

            if item.item_type == 'pokeball':
                # if battle.opponent_trainer:
                if battle.battle_type != "wild":
                    response_data['log'] = ["Vous ne pouvez pas capturer le Pokemon d'un dresseur !"]
                    return JsonResponse(response_data)

                # Preparer les donnees pour l'animation cote client.
                # La vraie capture se fait via 'confirm_capture' apres l'animation.
                hp_percent   = battle.opponent_pokemon.current_hp / battle.opponent_pokemon.max_hp
                capture_rate = calculate_capture_rate(
                    battle.opponent_pokemon, item, hp_percent,
                    battle.opponent_pokemon.status_condition
                )
                response_data['capture_attempt'] = {
                    'pokemon': {
                        'species_name': battle.opponent_pokemon.species.name,
                        'level':        battle.opponent_pokemon.level,
                    },
                    'ball_type':      item.name.lower().replace(' ', ''),
                    'capture_rate':   capture_rate,
                    'start_animation': True,
                }
                return JsonResponse(response_data)

            else:
                # Soin / antidote sur le Pokemon du joueur
                player_action   = {'type': 'item', 'item': item, 'target': battle.player_pokemon}
                opponent_action = get_opponent_ai_action(battle)
                battle.execute_turn(player_action, opponent_action)

        # ------------------------------------------------------------------
        elif action_type == 'confirm_capture':
            # Le client a termine l'animation, on effectue la vraie capture.
            inv    = get_object_or_404(TrainerInventory, pk=request.POST.get('item_id'))
            item   = inv.item
            result = attempt_pokemon_capture(battle, ball_item=item, trainer=trainer)

            # Consommer la ball dans l'inventaire
            inv.quantity -= 1
            if inv.quantity == 0:
                inv.delete()
            else:
                inv.save()

            # L'adversaire attaque si la capture echoue
            if not result['success']:
                opponent_action = get_opponent_ai_action(battle)
                battle.execute_turn({'type': 'PokeBall'}, opponent_action)
            else:
                # Capture réussie → marquer le combat comme gagné par le joueur
                battle.is_active = False
                battle.winner = trainer
                battle.save()

            response_data['capture_result'] = result
            response_data['battle_ended']   = result['success']
            response_data['log']            = [result['message']]
            if result['success']:
                response_data['result'] = 'capture'

            return JsonResponse(response_data)

        # ------------------------------------------------------------------
        elif action_type == 'confirm_evolution':
            # Le client a termine l'animation, on applique l'evolution.
            from myPokemonApp.models.PokemonEvolution import PokemonEvolution
            from myPokemonApp.models import Pokemon as PokemonSpecies

            evolution_id = request.POST.get('evolution_id')
            evolution    = get_object_or_404(PokemonEvolution, pk=evolution_id)
            pokemon      = battle.player_pokemon

            # Sécurité : vérifier que l'évolution concerne bien ce pokémon
            if evolution.pokemon != pokemon.species:
                return JsonResponse({'error': 'Evolution invalide'}, status=400)

            old_name    = pokemon.species.name
            new_species = evolution.evolves_to
            evolve_msg  = pokemon.evolve_to(new_species)

            battle.refresh_from_db()
            response_data = build_battle_response(battle)
            response_data['log']         = [evolve_msg]
            response_data['evolved']     = True
            response_data['new_species'] = new_species.name
            # Stats après évolution pour les afficher dans le modal
            response_data['stats_after'] = {
                'hp':              pokemon.max_hp,
                'attack':          pokemon.attack,
                'defense':         pokemon.defense,
                'special_attack':  pokemon.special_attack,
                'special_defense': pokemon.special_defense,
                'speed':           pokemon.speed,
            }
            return JsonResponse(response_data)
        battle.refresh_from_db()
        ended_before       = response_data.get('battle_ended', False)
        result_before      = response_data.get('result')
        extra_logs         = response_data.get('log', [])
        pending_evolution  = response_data.get('pending_evolution')   # ← sauvegarder
        pending_moves      = response_data.get('pending_moves')       # ← sauvegarder

        response_data = build_battle_response(battle)

        if ended_before:
            response_data['battle_ended'] = True
        if result_before:
            response_data['result'] = result_before
        if pending_evolution:                                          # ← réinjecter
            response_data['pending_evolution'] = pending_evolution
        if pending_moves:                                              # ← réinjecter
            response_data['pending_moves'] = pending_moves

        # Logs recents depuis le journal de combat
        if battle.battle_log:
            battle_log_messages = [entry['message'] for entry in battle.battle_log[-5:]]
            # Fusionner : d'abord les messages du journal, puis les extras (EXP/level-up)
            # qui ne sont pas déjà dans le journal
            seen = set(battle_log_messages)
            merged = battle_log_messages + [m for m in extra_logs if m not in seen]
            response_data['log'] = merged
        elif extra_logs:
            response_data['log'] = extra_logs

        # Verification finale de fin de combat (seulement si pas deja termine)
        if not response_data.get('battle_ended'):
            is_ended, winner, end_message = check_battle_end(battle)
            if is_ended:
                response_data['battle_ended'] = True
                response_data['winner']       = winner.username if winner else 'Draw'
                response_data['result']       = 'victory' if winner == battle.player_trainer else 'defeat'
                response_data['log'].append(end_message)

    except Exception as e:
        import traceback
        traceback.print_exc()
        response_data['success'] = False
        response_data['error']   = str(e)
        response_data['log']     = [f'Erreur : {str(e)}']

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
    player_trainer = get_object_or_404(Trainer, username=request.user.username)

    save = GameSave.objects.filter(trainer=player_trainer, is_active=True).first()

    npc_trainers       = Trainer.objects.filter(is_npc=True, trainer_type='trainer').order_by('location', 'username')
    trainer_locations  = list(npc_trainers.values_list('location', flat=True).distinct())
    trainer_classes    = [c for c in npc_trainers.values_list('npc_class', flat=True).distinct() if c]

    fightable_gym_leaders = [
        gl for gl in GymLeader.objects.all()
        if gl.isChallengableByPlayer(player=player_trainer)
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
    import random
    """
    Cree un combat contre un Pokemon sauvage aleatoire (ou specifique en mode debug).

    POST params :
      pokemon_id (optionnel) : forcer une espece precise (debug)
      level      (optionnel) : forcer le niveau (defaut : autour du joueur +-3)
    """
    if request.method != 'POST':
        return redirect('BattleCreateView')

    player_trainer = get_object_or_404(Trainer, username=request.user.username)
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
    player_trainer   = get_object_or_404(Trainer, username=request.user.username)
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

    player_trainer = get_object_or_404(Trainer, username=request.user.username)
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
    player_trainer = get_object_or_404(Trainer, username=request.user.username)

    try:
        gym_leader = GymLeader.objects.select_related('trainer').get(pk=gym_leader_id)
    except GymLeader.DoesNotExist:
        messages.error(request, "Champion d'Arène introuvable !")
        return redirect('GymLeaderListView')

    # Vérifier que le joueur est dans la bonne ville
    try:
        player_location = PlayerLocation.objects.get(trainer=player_trainer)
        current_zone    = player_location.current_zone
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
    player_trainer = get_object_or_404(Trainer, username=request.user.username)

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
    except Exception:
        pass

    try:
        save = GameSave.objects.filter(trainer=player_trainer, is_active=True).first()
        if save and player_won and opponent:
            save.add_defeated_trainer(opponent.id)
    except Exception:
        pass

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

    return render(request, 'battle/battle_trainer_complete.html', {
        'battle':       battle,
        'opponent':     opponent,
        'player_won':   player_won,
        'money_earned': money_earned,
        'badge_earned': badge_earned,
        'dialogue':     dialogue,
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
    inventory = TrainerInventory.objects.filter(trainer=trainer, quantity__gt=0)

    items_data = [
        {'id': inv.id, 'name': inv.item.name, 'quantity': inv.quantity}
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
    trainer = get_object_or_404(Trainer, username=request.user.username)

    if battle.player_trainer != trainer:
        return JsonResponse({'error': 'Not your battle'}, status=403)

    new_move_id      = request.POST.get('new_move_id')
    replaced_move_id = request.POST.get('replaced_move_id')  # 'skip' = ne pas apprendre
    pokemon_id       = request.POST.get('pokemon_id')

    pokemon  = get_object_or_404(PlayablePokemon, pk=pokemon_id, trainer=trainer)
    new_move = get_object_or_404(PokemonMove, pk=new_move_id)

    if replaced_move_id and replaced_move_id != 'skip':
        # Oublier le move choisi et apprendre le nouveau
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
        # Joueur decide de ne pas apprendre le move
        message = f"{pokemon.species.name} n'apprend pas {new_move.name}."

    # Retourner les moves mis a jour
    moves = [
        {
            'id':         mi.move.id,
            'name':       mi.move.name,
            'type':       mi.move.type.name if mi.move.type else '',
            'power':      mi.move.power,
            'accuracy':   mi.move.accuracy,
            'pp':         mi.move.pp,
            'current_pp': mi.current_pp,
            'max_pp':     mi.move.pp,
        }
        for mi in PokemonMoveInstance.objects.filter(
            pokemon=pokemon
        ).select_related('move', 'move__type')
    ]

    return JsonResponse({'success': True, 'message': message, 'moves': moves})