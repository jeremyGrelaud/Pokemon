"""
views/api/phaser_api.py
=======================
Nouveaux endpoints JSON purs pour le frontend Phaser.
Ces vues remplacent les render() HTML des MapViews pour le fork.

À ajouter dans urls.py :
    path('api/phaser/', include('myPokemonApp.views.api.phaser_urls')),
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

from myPokemonApp.gameUtils import get_player_trainer, get_player_location, get_defeated_trainer_ids
from myPokemonApp.models.Zone import Zone, ZoneConnection
from myPokemonApp.models.Trainer import GymLeader, Trainer
from myPokemonApp.questEngine import can_access_zone, trainer_has_hm
from django.shortcuts import get_object_or_404

# ─────────────────────────────────────────────────────────────
# HELPERS DE SÉRIALISATION
# ─────────────────────────────────────────────────────────────

def _serialize_zone(zone: Zone) -> dict:
    """Sérialise une Zone en dict JSON."""
    return {
        'id':                      zone.id,
        'name':                    zone.name,
        'zone_type':               zone.zone_type,
        'description':             zone.description,
        'recommended_level_min':   zone.recommended_level_min,
        'recommended_level_max':   zone.recommended_level_max,
        'is_safe_zone':            zone.is_safe_zone,
        'has_pokemon_center':      zone.has_pokemon_center,
        'has_shop':                zone.has_shop,
        'has_floors':              zone.has_floors,
        'music':                   zone.music,
        'image':                   zone.image,
    }


def _serialize_wild_spawns(zone: Zone) -> list:
    """Sérialise les spawns sauvages d une zone."""
    return [
        {
            'pokemon_name':   spawn.pokemon.name,
            'pokemon_id':     spawn.pokemon.id,
            'spawn_rate':     spawn.spawn_rate,
            'level_min':      spawn.level_min,
            'level_max':      spawn.level_max,
            'encounter_type': spawn.encounter_type,
        }
        for spawn in zone.wild_spawns.select_related('pokemon').all()
    ]


def _serialize_connection(conn: ZoneConnection, trainer: Trainer, from_zone: Zone) -> dict:
    """Sérialise une ZoneConnection du point de vue du trainer."""
    # Résoudre la zone de destination (connexion peut être inversée)
    if conn.from_zone == from_zone:
        dest = conn.to_zone
    else:
        dest = conn.from_zone

    passable, reason = conn.is_passable_by(trainer)

    return {
        'to_zone_id':       dest.id,
        'to_zone_name':     dest.name,
        'is_bidirectional': conn.is_bidirectional,
        'required_hm':      conn.required_hm,
        'is_passable':      passable,
        'block_reason':     reason if not passable else '',
    }


# ─────────────────────────────────────────────────────────────
# ENDPOINT : Vue d'ensemble de la carte
# GET /api/phaser/map/
# ─────────────────────────────────────────────────────────────

@login_required
@require_GET
def phaser_map_overview(request):
    """
    Retourne toutes les zones avec leur statut d'accessibilité.
    Utilisé par GameScene au démarrage.
    """
    trainer         = get_player_trainer(request.user)
    player_location = get_player_location(trainer)
    current_zone    = player_location.current_zone

    all_zones = Zone.objects.select_related(
        'required_badge', 'required_item', 'required_quest'
    ).all()

    # IDs des zones connectées à la position actuelle
    outgoing_ids = set(
        ZoneConnection.objects.filter(from_zone=current_zone)
        .values_list('to_zone_id', flat=True)
    )
    incoming_ids = set(
        ZoneConnection.objects.filter(to_zone=current_zone, is_bidirectional=True)
        .values_list('from_zone_id', flat=True)
    )
    connected_zone_ids = list(outgoing_ids | incoming_ids)

    zones = []
    for zone in all_zones:
        can_access, reason = zone.is_accessible_by(trainer)
        visited = player_location.visited_zones.filter(id=zone.id).exists()

        zones.append({
            'zone':       _serialize_zone(zone),
            'accessible': can_access,
            'reason':     reason if not can_access else '',
            'visited':    visited,
            'has_gym':    False,  # TODO : enrichir si nécessaire
        })

    return JsonResponse({
        'current_zone_id':    current_zone.id,
        'zones':              zones,
        'connected_zone_ids': connected_zone_ids,
    })


# ─────────────────────────────────────────────────────────────
# ENDPOINT : Détail d'une zone
# GET /api/phaser/map/zone/<zone_id>/
# ─────────────────────────────────────────────────────────────

@login_required
@require_GET
def phaser_zone_detail(request, zone_id: int):
    """
    Retourne le détail d'une zone : connexions, spawns sauvages, accès.
    """
    try:
        zone = Zone.objects.select_related(
            'required_badge', 'required_item', 'required_quest'
        ).get(pk=zone_id)
    except Zone.DoesNotExist:
        return JsonResponse({'error': 'Zone introuvable'}, status=404)

    trainer         = get_player_trainer(request.user)
    player_location = get_player_location(trainer)
    can_access, reason = zone.is_accessible_by(trainer)

    # Connexions
    outgoing = ZoneConnection.objects.filter(from_zone=zone).select_related('to_zone')
    incoming = ZoneConnection.objects.filter(
        to_zone=zone, is_bidirectional=True
    ).select_related('from_zone')

    connections = []
    seen_ids = set()
    for conn in outgoing:
        connections.append(_serialize_connection(conn, trainer, zone))
        seen_ids.add(conn.to_zone_id)
    for conn in incoming:
        if conn.from_zone_id not in seen_ids:
            connections.append(_serialize_connection(conn, trainer, zone))

    # Spawns sauvages
    wild_spawns = [
        {
            'pokemon_name':   spawn.pokemon.name,
            'pokemon_id':     spawn.pokemon.id,
            'spawn_rate':     spawn.spawn_rate,
            'level_min':      spawn.level_min,
            'level_max':      spawn.level_max,
            'encounter_type': spawn.encounter_type,
        }
        for spawn in zone.wild_spawns.select_related('pokemon').all()
    ]

    data = _serialize_zone(zone)
    data.update({
        'connections': connections,
        'wild_spawns': wild_spawns,
        'can_access':  can_access,
        'access_reason': reason if not can_access else '',
        'is_current':  player_location.current_zone_id == zone.id,
    })

    return JsonResponse(data)


# ─────────────────────────────────────────────────────────────
# ENDPOINT : Position du joueur
# GET /api/phaser/player/location/
# ─────────────────────────────────────────────────────────────

@login_required
@require_GET
def phaser_player_location(request):
    """Retourne la position courante du joueur."""
    trainer         = get_player_trainer(request.user)
    player_location = get_player_location(trainer)

    visited_ids = list(
        player_location.visited_zones.values_list('id', flat=True)
    )

    return JsonResponse({
        'trainer_id':             trainer.id,
        'current_zone_id':        player_location.current_zone_id,
        'current_zone_name':      player_location.current_zone.name,
        'visited_zone_ids':       visited_ids,
        'last_pokemon_center_id': player_location.last_pokemon_center_id,
    })


# ─────────────────────────────────────────────────────────────
# ENDPOINT : Rencontre sauvage
# POST /api/phaser/map/encounter/<zone_id>/?type=grass|water
# ─────────────────────────────────────────────────────────────

@login_required
def phaser_wild_encounter(request, zone_id: int):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)

    from myPokemonApp.models.Battle import Battle
    from myPokemonApp.gameUtils import (
        get_random_wild_pokemon, get_player_trainer, get_player_location,
        create_wild_pokemon, get_first_alive_pokemon,
        cleanup_orphan_wild_pokemon, start_battle,
    )

    trainer         = get_player_trainer(request.user)
    zone            = get_object_or_404(Zone, pk=zone_id)
    player_location = get_player_location(trainer)

    # Vérifier combat déjà actif
    active_battle = Battle.objects.filter(player_trainer=trainer, is_active=True).first()
    if active_battle:
        return JsonResponse({'battle_id': active_battle.id})

    encounter_type = request.GET.get('type', 'grass')
    wild_species, level = get_random_wild_pokemon(zone, encounter_type)
    if not wild_species:
        return JsonResponse({'error': 'Aucun Pokémon dans cette zone'}, status=404)

    player_pokemon = get_first_alive_pokemon(trainer)
    if not player_pokemon:
        return JsonResponse({'error': 'Aucun Pokémon en état de combattre'}, status=400)

    cleanup_orphan_wild_pokemon()
    wild_pokemon = create_wild_pokemon(wild_species, level, location=zone.name)
    battle, msg = start_battle(trainer, wild_pokemon=wild_pokemon)

    if not battle:
        return JsonResponse({'error': msg}, status=400)

    return JsonResponse({'battle_id': battle.id, 'pokemon_name': wild_species.name, 'level': level})


# ─────────────────────────────────────────────────────────────
# ENDPOINT : Travel → JSON
# POST /api/phaser/map/travel/<zone_id>/
# ─────────────────────────────────────────────────────────────

@login_required
def phaser_travel(request, zone_id: int):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)

    from myPokemonApp.questEngine import trigger_quest_event

    trainer         = get_player_trainer(request.user)
    player_location = get_player_location(trainer)
    target_zone     = get_object_or_404(Zone, pk=zone_id)

    can_travel, reason = player_location.can_travel_to(target_zone)
    if not can_travel:
        return JsonResponse({'success': False, 'message': reason})

    player_location.travel_to(target_zone)
    trigger_quest_event(trainer, 'visit_zone', zone=target_zone)

    return JsonResponse({
        'success': True,
        'message': f'Arrivée à {target_zone.name}',
        'zone': _serialize_zone(target_zone) | {
            'connections': [],
            'wild_spawns': _serialize_wild_spawns(target_zone),
            'can_access':  True,
            'access_reason': '',
            'is_current':  True,
        },
    })


# ─────────────────────────────────────────────────────────────
# ENDPOINT : Travel → JSON
# POST /api/phaser/map/travel/by-name/<zone_name>/
# ─────────────────────────────────────────────────────────────

@login_required
def phaser_travel_by_name(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)

    import json
    from myPokemonApp.questEngine import trigger_quest_event

    try:
        body = json.loads(request.body)
        zone_name = body.get('zone_name', '').strip()
    except Exception:
        return JsonResponse({'error': 'JSON invalide'}, status=400)

    if not zone_name:
        return JsonResponse({'error': 'zone_name requis'}, status=400)

    try:
        target_zone = Zone.objects.get(name=zone_name)
    except Zone.DoesNotExist:
        return JsonResponse({'success': False, 'message': f'Zone "{zone_name}" introuvable.'})

    trainer         = get_player_trainer(request.user)
    player_location = get_player_location(trainer)

    can_travel, reason = player_location.can_travel_to(target_zone)
    if not can_travel:
        return JsonResponse({'success': False, 'message': reason})

    player_location.travel_to(target_zone)
    trigger_quest_event(trainer, 'visit_zone', zone=target_zone)

    return JsonResponse({
        'success': True,
        'message': f'Arrivée à {target_zone.name}',
        'zone': _serialize_zone(target_zone) | {
            'connections': [],
            'wild_spawns': _serialize_wild_spawns(target_zone),
            'can_access':  True,
            'access_reason': '',
            'is_current':  True,
        },
    })

# ─────────────────────────────────────────────────────────────
# ENDPOINT : État initial d'un combat
# GET /api/battle/state/<battle_id>/
# ─────────────────────────────────────────────────────────────

@login_required
@require_GET
def phaser_battle_state(request, battle_id: int):
    """
    Retourne l'état complet d'un combat (même format que build_battle_response).
    Utilisé par BattleScene au démarrage.
    """
    from myPokemonApp.models.Battle import Battle
    from myPokemonApp.services.serializers import build_battle_response

    trainer = get_player_trainer(request.user)

    try:
        battle = Battle.objects.select_related(
            'player_pokemon', 'opponent_pokemon'
        ).get(pk=battle_id, player_trainer=trainer)
    except Battle.DoesNotExist:
        return JsonResponse({'error': 'Combat introuvable'}, status=404)

    return JsonResponse(build_battle_response(battle))

# ─────────────────────────────────────────────────────────────
# ENDPOINT : Dialogue NPC
# GET /api/phaser/npc/<npc_code>/dialog/
# ─────────────────────────────────────────────────────────────

@login_required
@require_GET
def phaser_npc_dialog(request, npc_code: str):
    """
    Retourne les textes de dialogue d'un NPC identifié par son npc_code stable.
    Le NPC peut être un simple PNJ (pas d'équipe) ou un dresseur non encore battu.
    """
    from myPokemonApp.models.Trainer import Trainer
    from myPokemonApp.models.DefeatedTrainer import DefeatedTrainer
    from myPokemonApp.models.GameSave import GameSave

    try:
        npc = Trainer.objects.get(npc_code=npc_code, is_npc=True)
    except Trainer.DoesNotExist:
        return JsonResponse({'error': f'NPC "{npc_code}" introuvable.'}, status=404)

    trainer = get_player_trainer(request.user)

    # Vérifier si ce dresseur a déjà été battu par ce joueur
    game_save = GameSave.objects.filter(trainer=trainer, is_active=True).only('id').first()
    is_defeated = npc.is_defeated_by_player(trainer, game_save=game_save)

    # Choisir le bon texte selon l'état
    if is_defeated and npc.defeat_text:
        dialog_text = npc.defeat_text
    else:
        dialog_text = npc.intro_text or f"{npc.get_full_title()} n'a rien à dire."

    return JsonResponse({
        'npc_code':    npc_code,
        'name':        npc.get_full_title(),
        'npc_class':   npc.npc_class,
        'sprite_name': npc.sprite_name,
        'dialog':      dialog_text,
        'is_defeated': is_defeated,
        'can_battle':  npc.has_available_pokemon() and not is_defeated,
    })


# ─────────────────────────────────────────────────────────────
# ENDPOINT : Ramasser un objet au sol
# POST /api/phaser/map/pickup-item/
# Body : { "zone_id": int, "tiled_obj_id": int }
# ─────────────────────────────────────────────────────────────

@login_required
def phaser_pickup_item(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)

    import json
    from myPokemonApp.models.FieldItem import FieldItem, PickedUpItem
    from myPokemonApp.models.Trainer import TrainerInventory

    try:
        body = json.loads(request.body)
        zone_id      = int(body['zone_id'])
        tiled_obj_id = int(body['tiled_obj_id'])
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'zone_id et tiled_obj_id requis'}, status=400)

    try:
        field_item = FieldItem.objects.select_related('item').get(
            zone_id=zone_id, tiled_obj_id=tiled_obj_id
        )
    except FieldItem.DoesNotExist:
        return JsonResponse({'error': 'Objet introuvable sur cette map.'}, status=404)

    trainer = get_player_trainer(request.user)

    # Idempotent — impossible de ramasser deux fois
    _, created = PickedUpItem.objects.get_or_create(
        trainer=trainer,
        field_item=field_item,
    )
    if not created:
        return JsonResponse({'success': False, 'message': 'Objet déjà ramassé.'})

    # Ajouter à l'inventaire du joueur
    inv, _ = TrainerInventory.objects.get_or_create(
        trainer=trainer,
        item=field_item.item,
        defaults={'quantity': 0},
    )
    inv.quantity += field_item.quantity
    inv.save(update_fields=['quantity'])

    return JsonResponse({
        'success':   True,
        'item_name': field_item.item.name,
        'quantity':  field_item.quantity,
        'message':   f"Vous avez obtenu {field_item.item.name} ×{field_item.quantity} !",
    })


# ─────────────────────────────────────────────────────────────
# ENDPOINT : Démarrer un combat dresseur
# POST /api/phaser/trainer/<npc_code>/battle/
# ─────────────────────────────────────────────────────────────

@login_required
def phaser_trainer_battle(request, npc_code: str):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)

    from myPokemonApp.models.Trainer import Trainer
    from myPokemonApp.models.Battle import Battle
    from myPokemonApp.models.DefeatedTrainer import DefeatedTrainer
    from myPokemonApp.models.GameSave import GameSave
    from myPokemonApp.gameUtils import get_first_alive_pokemon, start_battle

    try:
        npc = Trainer.objects.get(npc_code=npc_code, is_npc=True)
    except Trainer.DoesNotExist:
        return JsonResponse({'error': f'Dresseur "{npc_code}" introuvable.'}, status=404)

    trainer = get_player_trainer(request.user)

    # Vérifier si déjà battu
    game_save = GameSave.objects.filter(trainer=trainer, is_active=True).only('id').first()
    if npc.is_defeated_by_player(trainer, game_save=game_save):
        return JsonResponse({'success': False, 'message': f'{npc.get_full_title()} a déjà été battu.'})

    # Vérifier combat déjà actif
    active_battle = Battle.objects.filter(player_trainer=trainer, is_active=True).first()
    if active_battle:
        return JsonResponse({'battle_id': active_battle.id, 'success': True})

    # Vérifier que le dresseur a des Pokémon
    if not npc.has_available_pokemon():
        return JsonResponse({'error': 'Ce dresseur n\'a aucun Pokémon.'}, status=400)

    # Vérifier que le joueur a des Pokémon
    player_pokemon = get_first_alive_pokemon(trainer)
    if not player_pokemon:
        return JsonResponse({'error': 'Aucun Pokémon en état de combattre.'}, status=400)

    # Démarrer le combat
    battle, msg = start_battle(trainer, opponent_trainer=npc)
    if not battle:
        return JsonResponse({'error': msg}, status=400)

    return JsonResponse({
        'success':    True,
        'battle_id':  battle.id,
        'trainer_name': npc.get_full_title(),
        'intro_text': npc.intro_text or '',
    })


# ─────────────────────────────────────────────────────────────
# ENDPOINT : Items déjà ramassés dans une zone
# GET /api/phaser/map/picked-items/?zone_id=<id>
# Utilisé par GameScene pour masquer les items déjà pris au chargement
# ─────────────────────────────────────────────────────────────

@login_required
@require_GET
def phaser_picked_items(request):
    """Retourne les tiled_obj_id des items déjà ramassés par le joueur dans une zone."""
    from myPokemonApp.models.FieldItem import PickedUpItem

    zone_id = request.GET.get('zone_id')
    if not zone_id:
        return JsonResponse({'error': 'zone_id requis'}, status=400)

    trainer = get_player_trainer(request.user)

    picked_ids = list(
        PickedUpItem.objects.filter(
            trainer=trainer,
            field_item__zone_id=zone_id,
        ).values_list('field_item__tiled_obj_id', flat=True)
    )

    return JsonResponse({'picked_tiled_obj_ids': picked_ids})