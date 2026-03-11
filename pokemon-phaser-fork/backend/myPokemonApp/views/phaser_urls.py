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
)

urlpatterns = [
    path('map/',                              phaser_map_overview,    name='phaser_map_overview'),
    path('map/zone/<int:zone_id>/',           phaser_zone_detail,     name='phaser_zone_detail'),
    path('map/travel/<int:zone_id>/',         phaser_travel,          name='phaser_travel'),
    path('map/encounter/<int:zone_id>/',      phaser_wild_encounter,  name='phaser_wild_encounter'),
    path('player/location/',                  phaser_player_location, name='phaser_player_location'),
    path('battle/state/<int:battle_id>/',     phaser_battle_state,   name='phaser_battle_state'),
]