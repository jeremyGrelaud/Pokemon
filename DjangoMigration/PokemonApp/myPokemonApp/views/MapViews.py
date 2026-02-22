"""
Vues pour le système de carte et navigation
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from myPokemonApp.models import *
from myPokemonApp.gameUtils import get_random_wild_pokemon, get_player_trainer, get_player_location, get_defeated_trainer_ids

# ============================================================================
# MAP OVERVIEW
# ============================================================================

@login_required
def map_view(request):
    """Vue de la carte Kanto avec zones"""
    trainer         = get_player_trainer(request.user)
    player_location = get_player_location(trainer)   # crée si absent

    all_zones = Zone.objects.all()

    accessible_zones = [
        {
            'zone':       zone,
            'accessible': can_access,
            'reason':     reason,
            'visited':    player_location.visited_zones.filter(id=zone.id).exists(),
        }
        for zone in all_zones
        for can_access, reason in [zone.is_accessible_by(trainer)]
    ]

    return render(request, 'map/map_overview.html', {
        'current_zone':    player_location.current_zone,
        'zones':           accessible_zones,
        'player_location': player_location,
    })


@login_required
def zone_detail_view(request, zone_id):
    """Détail d'une zone avec options"""
    trainer         = get_player_trainer(request.user)
    zone            = get_object_or_404(Zone, pk=zone_id)
    can_access, reason = zone.is_accessible_by(trainer)
    player_location = get_player_location(trainer)
    is_current      = player_location.current_zone == zone

    outgoing = ZoneConnection.objects.filter(from_zone=zone).select_related('to_zone')
    incoming = ZoneConnection.objects.filter(
        to_zone=zone, is_bidirectional=True
    ).select_related('from_zone')

    connections    = list(outgoing)
    seen_zone_ids  = {c.to_zone_id for c in outgoing}
    for conn in incoming:
        if conn.from_zone_id not in seen_zone_ids:
            conn.to_zone = conn.from_zone
            connections.append(conn)

    wild_spawns        = zone.wild_spawns.all()
    trainers_in_zone   = Trainer.objects.filter(is_npc=True, location=zone.name)

    # Calcul des dresseurs vaincus en UNE seule requête DB
    # (évite le N+1 que produirait npc.is_defeated_by_player() dans le template)
    defeated_ids = get_defeated_trainer_ids(trainer)
    trainers_with_status = [
        {
            'npc':         npc,
            'is_defeated': npc.id in defeated_ids,
            'can_rebattle': npc.can_rebattle,
        }
        for npc in trainers_in_zone
    ]

    pokemon_center = None
    if zone.has_pokemon_center:
        pokemon_center = PokemonCenter.objects.filter(
            location__icontains=zone.name, is_available=True
        ).first()

    zone_shop = None
    if zone.has_shop:
        zone_shop = Shop.objects.filter(location__icontains=zone.name).first()

    zone_translations = {
        "Argenta": "Pewter City",
        "Azuria": "Cerulean City",
        "Carmin sur Mer": "Vermilion City",
        "Céladopole": "Celadon City",
        "Jadielle": "Viridian City",
        "Safrania": "Saffron City",
        "Parmanie": "Fuchsia City",
        "Cramois'Ile": "Cinnabar Island",
    }
    english_zone_name = zone_translations.get(zone.name, zone.name).strip()

    gym_leader = None
    try:
        gym_leader = GymLeader.objects.filter(gym_city__icontains=english_zone_name).first()
    except Exception:
        pass

    # Gym Leader : défaite per-joueur via la save
    gym_leader_defeated = gym_leader and gym_leader.trainer.id in defeated_ids

    return render(request, 'map/zone_detail.html', {
        'zone':               zone,
        'can_access':         can_access,
        'access_reason':      reason,
        'is_current':         is_current,
        'connections':        connections,
        'wild_spawns':        wild_spawns,
        'trainers':           trainers_with_status,
        'current_zone':       player_location.current_zone,
        'pokemon_center':     pokemon_center,
        'zone_shop':          zone_shop,
        'gym_leader':         gym_leader,
        'gym_leader_defeated': gym_leader_defeated,
        'player_trainer':     trainer,
    })

from myPokemonApp.views.AchievementViews import check_achievement

@login_required
def travel_to_zone_view(request, zone_id):
    """Voyager vers une zone"""
    trainer         = get_player_trainer(request.user)
    zone            = get_object_or_404(Zone, pk=zone_id)
    player_location = get_player_location(trainer)

    success, message = player_location.travel_to(zone)

    if success:
        messages.success(request, message)

        if player_location.visited_zones.count() >= 10:
            result = check_achievement(trainer, 'Explorateur')
            if result.get('newly_completed'):
                messages.success(request, f"🏆 Explorateur débloqué ! +{result['reward_money']}₽")

        try:
            save = GameSave.objects.filter(trainer=trainer, is_active=True).first()
            if save:
                save.current_location = zone.name
                save.save()
        except Exception:
            pass
    else:
        messages.error(request, message)

    return redirect('zone_detail', zone_id=zone.id)


@login_required
def wild_encounter_view(request, zone_id):
    """Déclencher une rencontre sauvage dans une zone"""
    from myPokemonApp.gameUtils import create_wild_pokemon, get_first_alive_pokemon

    trainer         = get_player_trainer(request.user)
    zone            = get_object_or_404(Zone, pk=zone_id)
    player_location = get_player_location(trainer)

    if player_location.current_zone != zone:
        messages.error(request, "Vous n'êtes pas dans cette zone !")
        return redirect('map_view')

    active_battle = Battle.objects.filter(player_trainer=trainer, is_active=True).first()
    if active_battle:
        messages.warning(request, "Un combat est déjà en cours !")
        return redirect('BattleGameView', pk=active_battle.id)

    encounter_type = request.GET.get('type', 'grass')
    wild_species, level = get_random_wild_pokemon(zone, encounter_type)
    if not wild_species:
        messages.warning(request, "Aucun Pokémon trouvé dans cette zone.")
        return redirect('zone_detail', zone_id=zone.id)

    player_pokemon = get_first_alive_pokemon(trainer)
    if not player_pokemon:
        messages.error(request, "Vous n'avez pas de Pokémon en état de combattre !")
        return redirect('PokemonCenterListView')

    # Nettoyer les vieux Pokémon sauvages orphelins
    active_wild_pokemon_ids = Battle.objects.filter(
        is_active=True
    ).values_list('opponent_pokemon_id', flat=True)
    PlayablePokemon.objects.filter(
        trainer__username__in=('Wild', 'wild_pokemon')
    ).exclude(id__in=active_wild_pokemon_ids).delete()

    wild_pokemon = create_wild_pokemon(wild_species, level, location=zone.name)

    battle = Battle.objects.create(
        player_trainer=trainer,
        opponent_trainer=None,
        player_pokemon=player_pokemon,
        opponent_pokemon=wild_pokemon,
        battle_type='wild',
        is_active=True,
    )

    messages.success(request, f"Un {wild_species.name} sauvage de niveau {level} apparaît !")
    return redirect('BattleGameView', pk=battle.id)