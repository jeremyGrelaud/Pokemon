"""
Vues pour les bâtiments multi-étages (Tour Pokémon, Sylphe SARL, etc.)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from myPokemonApp.models import Zone, ZoneFloor, Battle, WildPokemonSpawn, Trainer
from myPokemonApp.gameUtils import (
    get_player_trainer, get_player_location, get_defeated_trainer_ids,
    get_random_wild_pokemon, create_wild_pokemon, get_first_alive_pokemon,
)
from myPokemonApp.questEngine import (
    can_access_floor, check_rival_encounter, trigger_quest_event
)


@login_required
def building_redirect_view(request, zone_id):
    """
    building_view est désormais intégré dans zone_detail.
    On redirige proprement pour conserver la compatibilité des anciens liens.
    """
    return redirect('zone_detail', zone_id=zone_id)


@login_required
def floor_detail_view(request, zone_id, floor_number):
    """
    Vue détaillée d'un étage spécifique.
    Affiche dresseurs, Pokémon sauvages, rival éventuel.
    """
    trainer         = get_player_trainer(request.user)
    zone            = get_object_or_404(Zone, pk=zone_id, has_floors=True)
    floor           = get_object_or_404(ZoneFloor, zone=zone, floor_number=floor_number)
    player_location = get_player_location(trainer)
    is_current      = player_location.current_zone == zone

    # Vérifier l'accès à l'étage
    accessible, reason = can_access_floor(trainer, floor)
    if not accessible:
        messages.error(request, reason)
        return redirect('building_view', zone_id=zone_id)

    # Dresseurs sur cet étage
    # Convention : Trainer.location = "<zone_name>-<floor_number>"
    floor_location_key = f"{zone.name}-{floor_number}"
    trainers_on_floor = Trainer.objects.filter(
        is_npc=True, location=floor_location_key
    )
    defeated_ids = get_defeated_trainer_ids(trainer)
    trainers_with_status = [
        {
            'npc':          npc,
            'is_defeated':  npc.id in defeated_ids,
            'can_rebattle': npc.can_rebattle,
        }
        for npc in trainers_on_floor
    ]

    # Wild spawns sur cet étage (on filtre ceux sans floor OU qui ont le bon floor)
    wild_spawns = WildPokemonSpawn.objects.filter(
        zone=zone, encounter_type='cave'
    ).select_related('pokemon')

    # Rival sur cet étage ?
    rival_encounter = check_rival_encounter(trainer, zone, floor=floor)

    # Étages adjacents (navigation)
    all_floors = list(zone.floors.order_by('floor_number'))
    current_idx = next((i for i, f in enumerate(all_floors) if f.floor_number == floor_number), 0)
    floor_below = all_floors[current_idx - 1] if current_idx > 0 else None
    floor_above = all_floors[current_idx + 1] if current_idx < len(all_floors) - 1 else None

    return render(request, 'map/floor_detail.html', {
        'zone':             zone,
        'floor':            floor,
        'is_current':       is_current,
        'trainers':         trainers_with_status,
        'wild_spawns':      wild_spawns,
        'rival_encounter':  rival_encounter,
        'floor_below':      floor_below,
        'floor_above':      floor_above,
        'all_floors':       all_floors,
        'current_zone':     player_location.current_zone,
    })


@login_required
def floor_wild_encounter_view(request, zone_id, floor_number):
    """Déclencher une rencontre sauvage sur un étage."""
    trainer         = get_player_trainer(request.user)
    zone            = get_object_or_404(Zone, pk=zone_id, has_floors=True)
    floor           = get_object_or_404(ZoneFloor, zone=zone, floor_number=floor_number)
    player_location = get_player_location(trainer)

    if player_location.current_zone != zone:
        messages.error(request, "Vous n'êtes pas dans ce bâtiment !")
        return redirect('map_view')

    accessible, reason = can_access_floor(trainer, floor)
    if not accessible:
        messages.error(request, reason)
        return redirect('building_view', zone_id=zone_id)

    active_battle = Battle.objects.filter(player_trainer=trainer, is_active=True).first()
    if active_battle:
        return redirect('BattleGameView', pk=active_battle.id)

    wild_species, level = get_random_wild_pokemon(zone, 'cave')
    if not wild_species:
        messages.warning(request, "Aucun Pokémon ici.")
        return redirect('floor_detail', zone_id=zone_id, floor_number=floor_number)

    player_pokemon = get_first_alive_pokemon(trainer)
    if not player_pokemon:
        messages.error(request, "Vous n'avez pas de Pokémon en état de combattre !")
        return redirect('PokemonCenterListView')

    wild_pokemon = create_wild_pokemon(wild_species, level, location=zone.name)
    battle = Battle.objects.create(
        player_trainer=trainer,
        opponent_trainer=None,
        player_pokemon=player_pokemon,
        opponent_pokemon=wild_pokemon,
        battle_type='wild',
        is_active=True,
    )
    messages.success(request, f"Un {wild_species.name} sauvage (Niv.{level}) apparaît !")
    return redirect('BattleGameView', pk=battle.id)