"""
views/api/phaser_urls.py
Inclure dans urls.py principal :
    path('api/phaser/', include('myPokemonApp.views.api.phaser_urls')),
    path('api/battle/state/<int:battle_id>/', phaser_battle_state, name='phaser_battle_state'),
"""

from django.urls import path
from .phaser_api import (
    phaser_map_overview,
    phaser_zone_detail,
    phaser_player_location,
    phaser_battle_state,
    phaser_wild_encounter,
    phaser_travel,
    phaser_travel_by_name,
    phaser_npc_dialog,
    phaser_pickup_item,
    phaser_trainer_battle,
    phaser_picked_items,
)

urlpatterns = [
    # ── Map & navigation ──────────────────────────────────────
    path('map/',                              phaser_map_overview,    name='phaser_map_overview'),
    path('map/zone/<int:zone_id>/',           phaser_zone_detail,     name='phaser_zone_detail'),
    path('map/travel/<int:zone_id>/',         phaser_travel,          name='phaser_travel'),
    path('map/travel/by-name/',               phaser_travel_by_name,  name='phaser_travel_by_name'),
    path('map/encounter/<int:zone_id>/',      phaser_wild_encounter,  name='phaser_wild_encounter'),

    # ── Joueur ────────────────────────────────────────────────
    path('player/location/',                  phaser_player_location, name='phaser_player_location'),

    # ── Items au sol ──────────────────────────────────────────
    path('map/pickup-item/',                  phaser_pickup_item,     name='phaser_pickup_item'),
    path('map/picked-items/',                 phaser_picked_items,    name='phaser_picked_items'),

    # ── NPCs & Dresseurs ──────────────────────────────────────
    path('npc/<str:npc_code>/dialog/',        phaser_npc_dialog,      name='phaser_npc_dialog'),
    path('trainer/<str:npc_code>/battle/',    phaser_trainer_battle,  name='phaser_trainer_battle'),
]