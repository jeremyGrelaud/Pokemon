#!/usr/bin/python3
"""
Vues Django — création de combats et écran de fin dresseur.

Vues exposées :
  battle_create_view          — page de création (superuser uniquement, 3 onglets)
  battle_create_wild_view     — lancer un combat sauvage
  battle_create_trainer_view  — lancer un combat contre un dresseur NPC
  battle_create_gym_view      — lancer un combat contre un Champion d'Arène (POST)
  battle_challenge_gym_view   — lancer un combat contre un Champion depuis zone_detail (GET)
  battle_trainer_complete_view— écran de fin après un combat dresseur/gym
"""

import logging
import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from myPokemonApp.models.Battle import Battle
from myPokemonApp.models.GameSave import GameSave, TrainerBattleHistory
from myPokemonApp.models.Pokemon import Pokemon
from myPokemonApp.models.Trainer import GymLeader, Trainer
from myPokemonApp.models.Zone import PlayerLocation, Zone, ZoneConnection
from myPokemonApp.gameUtils import (
    get_first_alive_pokemon,
    get_player_trainer,
    create_wild_pokemon,
    start_battle,
    heal_team,
)
from myPokemonApp.questEngine import trigger_quest_event
from myPokemonApp.views.AchievementViews import (
    trigger_achievements_after_battle,
    trigger_achievements_after_gym_win,
)

logger = logging.getLogger(__name__)

# Correspondance gym_city (anglais Bulbapedia) → nom de zone (français du projet)
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


# =============================================================================
# PAGE DE CRÉATION (superuser uniquement)
# =============================================================================

@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def battle_create_view(request):
    """
    Page de création de combat avec 3 onglets (superuser uniquement) :
      1. Pokémon Sauvage
      2. Dresseurs NPC
      3. Champions d'Arène
    """
    player_trainer = get_player_trainer(request.user)
    save           = GameSave.objects.filter(trainer=player_trainer, is_active=True).first()

    npc_trainers      = Trainer.objects.filter(is_npc=True, trainer_type='trainer').order_by('location', 'username')
    trainer_locations = list(npc_trainers.values_list('location', flat=True).distinct())
    trainer_classes   = [c for c in npc_trainers.values_list('npc_class', flat=True).distinct() if c]

    fightable_gym_leaders = [
        gl for gl in GymLeader.objects.all()
        if gl.isChallengableByPlayer(player_trainer=player_trainer)
    ]

    context = {
        'all_pokemon':       Pokemon.objects.all().order_by('pokedex_number'),
        'npc_trainers':      npc_trainers,
        'trainer_locations': trainer_locations,
        'trainer_classes':   trainer_classes,
        'gym_leaders':       fightable_gym_leaders,
        'save':              save,
    }
    return render(request, 'battle/battle_create.html', context)


# =============================================================================
# COMBAT SAUVAGE
# =============================================================================

@login_required
def battle_create_wild_view(request):
    """
    Crée un combat contre un Pokémon sauvage aléatoire (ou spécifique en mode debug).

    POST params :
      pokemon_id (optionnel) : forcer une espèce précise (debug)
      level      (optionnel) : forcer le niveau (défaut : autour du joueur +-3)
    """
    if request.method != 'POST':
        return redirect('BattleCreateView')

    player_trainer = get_player_trainer(request.user)
    player_pokemon = get_first_alive_pokemon(player_trainer)

    if not player_pokemon:
        messages.error(request, "Vous n'avez pas de Pokémon en état de combattre !")
        return redirect('PokemonCenterListView')

    pokemon_id = request.POST.get('pokemon_id')
    if pokemon_id:
        wild_species = get_object_or_404(Pokemon, pk=pokemon_id)
        level        = int(request.POST.get('level', 5))
    else:
        all_pokemon = Pokemon.objects.all()
        if not all_pokemon.exists():
            messages.error(request, "Aucun Pokémon sauvage disponible !")
            return redirect('BattleCreateView')
        wild_species = all_pokemon.order_by('?').first()
        level        = max(1, player_pokemon.level + random.randint(-3, 3))

    wild_pokemon = create_wild_pokemon(wild_species, level)

    battle, msg = start_battle(player_trainer, wild_pokemon=wild_pokemon)
    if not battle:
        messages.error(request, msg)
        return redirect('BattleCreateView')

    messages.success(request, f"Un {wild_species.name} sauvage de niveau {level} apparaît !")
    return redirect('BattleGameView', pk=battle.id)


# =============================================================================
# COMBAT DRESSEUR NPC
# =============================================================================

@login_required
def battle_create_trainer_view(request, trainer_id):
    """Crée un combat contre un dresseur NPC."""
    player_trainer   = get_player_trainer(request.user)
    opponent_trainer = get_object_or_404(Trainer, pk=trainer_id, is_npc=True)

    # Vérifier que le joueur est bien dans la zone (et l'étage) du dresseur
    try:
        player_location   = PlayerLocation.objects.get(trainer=player_trainer)
        current_zone_name = player_location.current_zone.name
        trainer_loc       = opponent_trainer.location

        if trainer_loc:
            in_zone = (
                trainer_loc == current_zone_name
                or trainer_loc.startswith(current_zone_name + "-")
            )

            if not in_zone:
                if "-" in trainer_loc:
                    parts = trainer_loc.rsplit("-", 1)
                    display_loc = f"{parts[0]} (étage {parts[1]})"
                else:
                    display_loc = trainer_loc
                messages.error(
                    request,
                    f"{opponent_trainer.get_full_title()} se trouve à {display_loc}, "
                    f"mais vous êtes à {current_zone_name} !",
                )
                return redirect('zone_detail', zone_id=player_location.current_zone.id)

            # Vérifier l'étage exact si applicable
            if trainer_loc.startswith(current_zone_name + "-"):
                floor_number = trainer_loc.rsplit("-", 1)[1]
                referer = request.META.get('HTTP_REFERER', '')
                if referer and f"/floor/{floor_number}" not in referer:
                    messages.error(
                        request,
                        f"Vous devez vous trouver à l'étage {floor_number} "
                        f"de {current_zone_name} pour affronter ce dresseur.",
                    )
                    return redirect('zone_detail', zone_id=player_location.current_zone.id)

    except PlayerLocation.DoesNotExist:
        messages.error(request, "Position introuvable. Veuillez voyager vers une zone.")
        return redirect('map_view')

    heal_team(opponent_trainer)

    save = GameSave.objects.filter(trainer=player_trainer, is_active=True).first()
    if save and save.is_trainer_defeated(opponent_trainer.id) and not opponent_trainer.can_rebattle:
        messages.warning(request, f"Vous avez déjà battu {opponent_trainer.get_full_title()}")
        return redirect('zone_detail', zone_id=player_location.current_zone.id)

    player_pokemon   = get_first_alive_pokemon(player_trainer)
    opponent_pokemon = get_first_alive_pokemon(opponent_trainer)

    if not player_pokemon:
        messages.error(request, "Vous n'avez pas de Pokémon en état de combattre !")
        return redirect('PokemonCenterListView')
    if not opponent_pokemon:
        messages.error(request, "Ce dresseur n'a pas d'équipe configurée !")
        return redirect('BattleCreateView')

    player_pokemon.reset_combat_stats()
    opponent_pokemon.reset_combat_stats()

    battle, msg = start_battle(player_trainer, opponent_trainer=opponent_trainer)
    if not battle:
        messages.error(request, msg)
        return redirect('BattleCreateView')

    messages.info(request, opponent_trainer.intro_text or f"Vous affrontez {opponent_trainer.get_full_title()} !")
    return redirect('BattleGameView', pk=battle.id)


# =============================================================================
# COMBAT GYM LEADER (POST depuis page de création)
# =============================================================================

@login_required
def battle_create_gym_view(request):
    """Crée un combat contre un Champion d'Arène (POST depuis battle_create)."""
    if request.method != 'POST':
        return redirect('BattleCreateView')

    player_trainer = get_player_trainer(request.user)
    gym_leader_id  = request.POST.get('gym_leader_id')

    try:
        gym_leader = GymLeader.objects.select_related('trainer').get(pk=gym_leader_id)
    except GymLeader.DoesNotExist:
        messages.error(request, "Champion d'Arène introuvable !")
        return redirect('BattleCreateView')

    opponent_trainer = gym_leader.trainer
    heal_team(opponent_trainer)

    if not gym_leader.isChallengableByPlayer(player_trainer):
        messages.warning(
            request,
            f"Vous devez avoir au moins {gym_leader.badge_order - 1} badge(s) "
            f"pour défier {opponent_trainer.username}"
        )
        return redirect('BattleCreateView')

    player_pokemon   = get_first_alive_pokemon(player_trainer)
    opponent_pokemon = get_first_alive_pokemon(opponent_trainer)

    if not player_pokemon:
        messages.error(request, "Vous n'avez pas de Pokémon en état de combattre !")
        return redirect('PokemonCenterListView')
    if not opponent_pokemon:
        messages.error(request, "Le Champion n'a pas d'équipe configurée !")
        return redirect('BattleCreateView')

    player_pokemon.reset_combat_stats()
    opponent_pokemon.reset_combat_stats()

    battle, msg = start_battle(player_trainer, opponent_trainer=opponent_trainer, battle_type='gym')
    if not battle:
        messages.error(request, msg)
        return redirect('BattleCreateView')

    messages.info(
        request,
        opponent_trainer.intro_text
        or f"Vous défiez {opponent_trainer.username}, Champion d'Arène de {gym_leader.gym_city} !"
    )
    return redirect('BattleGameView', pk=battle.id)


# =============================================================================
# COMBAT GYM LEADER (GET depuis zone_detail)
# =============================================================================

@login_required
def battle_challenge_gym_view(request, gym_leader_id):
    """
    Lance un combat contre un Champion d'Arène directement depuis zone_detail.
    GET /battle/gym/<id>/challenge/
    Vérifie que le joueur est bien dans la ville de l'arène.
    """
    player_trainer = get_player_trainer(request.user)

    try:
        gym_leader = GymLeader.objects.select_related('trainer').get(pk=gym_leader_id)
    except GymLeader.DoesNotExist:
        messages.error(request, "Champion d'Arène introuvable !")
        return redirect('GymLeaderListView')

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

    player_pokemon.reset_combat_stats()
    opponent_pokemon.reset_combat_stats()

    battle, msg = start_battle(player_trainer, opponent_trainer=opponent_trainer, battle_type='gym')
    if not battle:
        messages.error(request, msg)
        return redirect('GymLeaderDetailView', pk=gym_leader.id)

    messages.info(
        request,
        opponent_trainer.intro_text
        or f"Vous défiez {opponent_trainer.username}, Champion d'Arène de {gym_leader.gym_city} !",
    )
    return redirect('BattleGameView', pk=battle.id)


# =============================================================================
# ÉCRAN DE FIN (après un combat dresseur / gym)
# =============================================================================

@login_required
def battle_trainer_complete_view(request, battle_id):
    """
    Appelé après un combat contre un dresseur NPC.
    Distribue les récompenses, enregistre l'historique, déclenche les achievements.
    """
    battle         = get_object_or_404(Battle, pk=battle_id)
    player_trainer = get_player_trainer(request.user)

    if battle.player_trainer != player_trainer:
        return redirect('home')

    player_won = battle.winner == player_trainer
    opponent   = battle.opponent_trainer

    # ── Victoire ──────────────────────────────────────────────────────────────
    money_earned = 0
    badge_earned = None

    if player_won:
        notifications = trigger_achievements_after_battle(
            player_trainer,
            {'won': True, 'opponent_type': opponent.trainer_type if opponent else 'wild'}
        )
        for notif in notifications:
            messages.success(request, f"{notif['title']} : {notif['message']}")

        if opponent and opponent.trainer_type != 'wild':
            money_earned = opponent.get_reward()
            player_trainer.money += money_earned
            player_trainer.save()

        if opponent:
            try:
                gym_info = GymLeader.objects.get(trainer=opponent)
                if player_trainer.badges < gym_info.badge_order:
                    player_trainer.badges = gym_info.badge_order
                    player_trainer.save()
                    badge_earned = gym_info
                    messages.success(request, f"🏅 Vous avez obtenu le {gym_info.badge_name} !")

                    gym_notifications = trigger_achievements_after_gym_win(
                        player_trainer, player_trainer.badges
                    )
                    for notif in gym_notifications:
                        messages.success(request, f"{notif['title']} : {notif['message']}")

                    if player_trainer.badges >= 8:
                        try:
                            from myPokemonApp.questEngine import set_story_flag_and_trigger
                            set_story_flag_and_trigger(player_trainer, 'all_badges_obtained')
                            messages.info(
                                request,
                                "🎖️ Vous possédez les 8 badges de Kanto ! "
                                "Les gardes de la Ligue vous ouvrent désormais la Route 23."
                            )
                        except Exception as e:
                            logger.warning("Erreur flag all_badges_obtained: %s", e)
            except GymLeader.DoesNotExist:
                pass

    # ── Historique ────────────────────────────────────────────────────────────
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
        game_save = GameSave.objects.filter(trainer=player_trainer, is_active=True).first()
        if game_save  and player_won and opponent:
            game_save.add_defeated_trainer(opponent.id)
    except Exception as exc:
        logger.warning("Impossible de marquer le dresseur %s comme battu : %s", opponent, exc)

    # ── Quêtes ────────────────────────────────────────────────────────────────
    if player_won and opponent:
        try:
            quest_notifs = trigger_quest_event(
                player_trainer, 'defeat_trainer',
                trainer_id=opponent.id,
                player_trainer=player_trainer,
            )
            for notif in quest_notifs:
                msg = f"✅ Quête terminée : « {notif['title']} »"
                if notif.get('reward_money'):
                    msg += f" (+{notif['reward_money']}₽)"
                if notif.get('reward_item'):
                    msg += f" · Objet reçu : {notif['reward_item']}"
                messages.success(request, msg)

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

    # ── Défaite → soigner et rediriger vers le Centre Pokémon ─────────────────
    if not player_won:
        try:
            player_location = PlayerLocation.objects.get(trainer=player_trainer)
            current_zone    = player_location.current_zone

            if current_zone.has_pokemon_center:
                center_zone = current_zone
            else:
                connected_ids = ZoneConnection.objects.filter(
                    from_zone=current_zone
                ).values_list('to_zone_id', flat=True)
                reverse_ids = ZoneConnection.objects.filter(
                    to_zone=current_zone, is_bidirectional=True
                ).values_list('from_zone_id', flat=True)
                all_ids = list(connected_ids) + list(reverse_ids)

                center_zone = Zone.objects.filter(
                    id__in=all_ids, has_pokemon_center=True
                ).first()

                if not center_zone:
                    center_zone = Zone.objects.filter(has_pokemon_center=True).first()

            if center_zone:
                player_location.current_zone = center_zone
                if center_zone.has_pokemon_center:
                    player_location.last_pokemon_center = center_zone
                player_location.save()

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
        (opponent.defeat_text  or "Vous avez gagné...") if player_won
        else (opponent.victory_text or "J'ai gagné !") if opponent
        else ""
    )

    try:
        player_location = PlayerLocation.objects.get(trainer=player_trainer)
        current_zone = player_location.current_zone
    except PlayerLocation.DoesNotExist:
        current_zone = None

    return render(request, 'battle/battle_trainer_complete.html', {
        'battle':       battle,
        'opponent':     opponent,
        'player_won':   player_won,
        'money_earned': money_earned,
        'badge_earned': badge_earned,
        'dialogue':     dialogue,
        'current_zone': current_zone,
    })