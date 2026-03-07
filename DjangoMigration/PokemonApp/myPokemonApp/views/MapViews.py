"""
Vues pour le système de carte et navigation
"""

import logging
import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

from myPokemonApp.models.Battle import Battle
from myPokemonApp.models.GameSave import GameSave
from myPokemonApp.models.Item import Item
from myPokemonApp.models.PokemonCenter import PokemonCenter
from myPokemonApp.models.ShopModel import Shop
from myPokemonApp.models.Trainer import GymLeader, Trainer, TrainerInventory
from myPokemonApp.models.Zone import Zone, ZoneConnection
from myPokemonApp.gameUtils import (
    get_random_wild_pokemon, get_player_trainer, get_player_location,
    get_defeated_trainer_ids, ZONE_TRANSLATIONS,
    create_wild_pokemon, get_first_alive_pokemon,
    cleanup_orphan_wild_pokemon, start_battle,
)
from myPokemonApp.questEngine import trigger_quest_event, check_rival_encounter, get_active_quests, can_access_floor
from myPokemonApp.views.AchievementViews import trigger_achievements_after_zone_visit

logger = logging.getLogger(__name__)

# ============================================================================
# MAP OVERVIEW
# ============================================================================

@login_required
def map_view(request):
    """Vue de la carte Kanto avec zones"""
    trainer         = get_player_trainer(request.user)
    player_location = get_player_location(trainer)   # crée si absent

    all_zones = Zone.objects.all()

    # Zones ayant une arène : on croise GymLeader.gym_city avec le dict de traductions
    gym_cities      = set(GymLeader.objects.values_list('gym_city', flat=True))
    zones_with_gym  = {fr for fr, en in ZONE_TRANSLATIONS.items() if en in gym_cities}

    # IDs des zones directement connectées à la zone courante (pour le bouton "Voyager")
    current_zone    = player_location.current_zone
    outgoing_ids    = set(ZoneConnection.objects.filter(from_zone=current_zone).values_list('to_zone_id', flat=True))
    incoming_ids    = set(ZoneConnection.objects.filter(to_zone=current_zone, is_bidirectional=True).values_list('from_zone_id', flat=True))
    connected_zone_ids = list(outgoing_ids | incoming_ids)

    accessible_zones = [
        {
            'zone':       zone,
            'accessible': can_access,
            'reason':     reason,
            'visited':    player_location.visited_zones.filter(id=zone.id).exists(),
            'has_gym':    zone.name in zones_with_gym,
        }
        for zone in all_zones
        for can_access, reason in [zone.is_accessible_by(trainer)]
    ]

    return render(request, 'map/map_overview.html', {
        'current_zone':       player_location.current_zone,
        'zones':              accessible_zones,
        'player_location':    player_location,
        'connected_zone_ids': connected_zone_ids,
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

    wild_spawns      = zone.wild_spawns.all()
    defeated_ids     = get_defeated_trainer_ids(trainer)

    # ── Dresseurs : plat pour zones normales, par étage pour bâtiments ──
    if zone.has_floors:
        floors_data = []
        for floor in zone.floors.all().order_by('floor_number'):
            accessible, floor_reason = can_access_floor(trainer, floor)
            floor_key = f"{zone.name}-{floor.floor_number}"
            floor_trainers = Trainer.objects.filter(is_npc=True, location=floor_key).exclude(trainer_type="rival")
            floors_data.append({
                'floor':      floor,
                'accessible': accessible,
                'reason':     floor_reason,
                'trainers': [
                    {
                        'npc':          npc,
                        'is_defeated':  npc.id in defeated_ids,
                        'can_rebattle': npc.can_rebattle,
                    }
                    for npc in floor_trainers
                ],
            })
        # Fallback : dresseurs avec location=zone.name sans numéro d'étage
        # (données non migrées vers le format "Zone-N")
        unassigned = Trainer.objects.filter(
            is_npc=True, location=zone.name
        ).exclude(trainer_type="rival")
        unassigned_with_status = [
            {
                'npc':          npc,
                'is_defeated':  npc.id in defeated_ids,
                'can_rebattle': npc.can_rebattle,
            }
            for npc in unassigned
        ]
        trainers_with_status = []   # non utilisé côté template pour les bâtiments
    else:
        floors_data = []
        unassigned_with_status = []
        trainers_in_zone = Trainer.objects.filter(
            is_npc=True, location=zone.name
        ).exclude(trainer_type="rival")
        trainers_with_status = [
            {
                'npc':          npc,
                'is_defeated':  npc.id in defeated_ids,
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

    english_zone_name = ZONE_TRANSLATIONS.get(zone.name, zone.name).strip()

    gym_leader = GymLeader.objects.filter(gym_city__icontains=english_zone_name).first()

    # Si la zone est une arène (building "Arène de X"), chercher le gym_leader via la ville connectée
    if not gym_leader and zone.zone_type == 'building' and zone.name.startswith('Arène'):
        from myPokemonApp.models.Zone import ZoneConnection as ZC
        # Trouver la ville connectée
        city_conn = ZC.objects.filter(
            to_zone=zone, from_zone__zone_type='city'
        ).select_related('from_zone').first()
        if not city_conn:
            city_conn = ZC.objects.filter(
                from_zone=zone, to_zone__zone_type='city',
                is_bidirectional=True
            ).select_related('to_zone').first()
        if city_conn:
            city_zone = city_conn.from_zone if city_conn.to_zone == zone else city_conn.to_zone
            city_en = ZONE_TRANSLATIONS.get(city_zone.name, city_zone.name).strip()
            gym_leader = GymLeader.objects.filter(gym_city__icontains=city_en).first()

    # Gym Leader : défaite per-joueur via la save
    gym_leader_defeated = gym_leader and gym_leader.trainer.id in defeated_ids

    # Zone arène associée à cette ville (building "Arène de X")
    gym_zone = None
    if gym_leader and zone.zone_type == 'city':
        # Convention : la zone arène est une connexion directe de type building
        from myPokemonApp.models.Zone import ZoneConnection as ZC
        arena_connections = ZC.objects.filter(
            from_zone=zone, to_zone__zone_type='building',
            to_zone__name__startswith='Arène'
        ).select_related('to_zone')
        if not arena_connections.exists():
            arena_connections = ZC.objects.filter(
                to_zone=zone, is_bidirectional=True,
                from_zone__zone_type='building',
                from_zone__name__startswith='Arène'
            ).select_related('from_zone')
            gym_zone = arena_connections.first().from_zone if arena_connections.exists() else None
        else:
            gym_zone = arena_connections.first().to_zone

    # Rival présent dans cette zone ?
    rival_encounter = check_rival_encounter(trainer, zone)

    # Quêtes actives pour sidebar
    active_quests = get_active_quests(trainer)[:3]

    return render(request, 'map/zone_detail.html', {
        'zone':               zone,
        'can_access':         can_access,
        'access_reason':      reason,
        'is_current':         is_current,
        'connections':        connections,
        'wild_spawns':        wild_spawns,
        'trainers':           trainers_with_status,
        'floors_data':        floors_data,
        'unassigned_trainers': unassigned_with_status,
        'current_zone':       player_location.current_zone,
        'pokemon_center':     pokemon_center,
        'zone_shop':          zone_shop,
        'gym_leader':         gym_leader,
        'gym_leader_defeated': gym_leader_defeated,
        'gym_zone':           gym_zone,
        'player_trainer':     trainer,
        'rival_encounter':    rival_encounter,
        'active_quests':      active_quests,
    })

@login_required
def travel_to_zone_view(request, zone_id):
    """Voyager vers une zone"""
    trainer         = get_player_trainer(request.user)
    zone            = get_object_or_404(Zone, pk=zone_id)
    player_location = get_player_location(trainer)
    current_zone    = player_location.current_zone

    # ── Dresseur obligatoire non vaincu dans la zone actuelle ? ────────────
    if not current_zone.is_safe_zone:
        defeated_ids = get_defeated_trainer_ids(trainer)

        # Chercher uniquement les dresseurs marqués is_battle_required
        required_qs = Trainer.objects.filter(
            is_npc=True,
            is_battle_required=True,
            location=current_zone.name,
        ).exclude(id__in=defeated_ids)

        # Même logique pour les étages accessibles
        if current_zone.has_floors:
            for floor in current_zone.floors.all():
                accessible, _ = can_access_floor(trainer, floor)
                if accessible:
                    floor_key = f"{current_zone.name}-{floor.floor_number}"
                    required_qs = required_qs | Trainer.objects.filter(
                        is_npc=True,
                        is_battle_required=True,
                        location=floor_key,
                    ).exclude(id__in=defeated_ids)

        blocker = required_qs.first()
        if blocker:
            messages.warning(
                request,
                f"⚠️ {blocker.get_full_title()} vous barre le passage !"
            )
            return redirect('battle_create_trainer', trainer_id=blocker.id)

    success, message = player_location.travel_to(zone)
    if success:
        messages.success(request, message)

        # Achievements exploration (Explorateur 10 zones, Globe-Trotter 30 zones)
        for notif in trigger_achievements_after_zone_visit(trainer):
            messages.success(request, f"🏆 {notif['title']} : {notif['message']}")

        # ── Déclencher quêtes visit_zone ──────────────────────────────────
        quest_notifications = trigger_quest_event(trainer, 'visit_zone', zone=zone)
        for notif in quest_notifications:
            msg = f"✅ Quête terminée : « {notif['title']} »"
            if notif.get('reward_money'):
                msg += f" (+{notif['reward_money']}₽)"
            if notif.get('reward_item'):
                msg += f" · Objet reçu : {notif['reward_item']}"
            messages.success(request, msg)

        # ── Remise du colis à Bourg Palette ───────────────────────────────
        if 'bourg' in zone.name.lower() or 'palette' in zone.name.lower():
            try:
                from myPokemonApp.questEngine import get_quest_progress, trigger_quest_event as tqe
                parcel = Item.objects.filter(name='Colis de Chen').first()
                if parcel:
                    has_parcel = TrainerInventory.objects.filter(
                        trainer=trainer, item=parcel, quantity__gt=0
                    ).exists()
                    if has_parcel:
                        prog = get_quest_progress(trainer, 'give_parcel_to_oak')
                        if prog and prog.state in ('active', 'available'):
                            parcel_notifs = tqe(trainer, 'give_item', item=parcel)
                            for notif in parcel_notifs:
                                msg = f"✅ Quête terminée : « {notif['title']} »"
                                if notif.get('reward_item'):
                                    msg += f" · Vous recevez : {notif['reward_item']}"
                                messages.success(request, msg)
            except Exception as e:
                logger.warning("Erreur trigger give_item Bourg Palette : %s", e)

        try:
            save = GameSave.objects.filter(trainer=trainer, is_active=True).first()
            if save:
                save.current_location = zone.name
                save.save(update_fields=['current_location'])
        except Exception as exc:
            logger.warning("Impossible de mettre à jour la position dans la save : %s", exc)

        # ── Wild battle aléatoire en traversant (20%) ─────────────────────
        if not zone.is_safe_zone and zone.wild_spawns.exists() and random.random() < 0.20:

            active_battle = Battle.objects.filter(player_trainer=trainer, is_active=True).first()
            if not active_battle:
                player_pokemon = get_first_alive_pokemon(trainer)
                wild_species, level = get_random_wild_pokemon(zone, 'grass')
                if wild_species and player_pokemon:
                    cleanup_orphan_wild_pokemon()
                    wild_pokemon = create_wild_pokemon(wild_species, level, location=zone.name)

                    battle, msg = start_battle(trainer, wild_pokemon=wild_pokemon)
                    if battle:
                        messages.warning(
                            request,
                            f"⚡ En traversant la route, un {wild_species.name} sauvage (Niv.{level}) surgit !"
                        )
                        return redirect('BattleGameView', pk=battle.id)

    else:
        messages.error(request, message)

    return redirect('zone_detail', zone_id=zone.id)


@login_required
def wild_encounter_view(request, zone_id):
    """Déclencher une rencontre sauvage dans une zone"""

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

    cleanup_orphan_wild_pokemon()
    wild_pokemon = create_wild_pokemon(wild_species, level, location=zone.name)

    battle, msg = start_battle(trainer, wild_pokemon=wild_pokemon)
    if not battle:
        messages.error(request, msg)
        return redirect('zone_detail', zone_id=zone.id)

    messages.success(request, f"Un {wild_species.name} sauvage de niveau {level} apparaît !")
    return redirect('BattleGameView', pk=battle.id)