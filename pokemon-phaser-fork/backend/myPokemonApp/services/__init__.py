"""
myPokemonApp/services
======================
Couche service extraite de gameUtils.py.

Les imports depuis gameUtils.py continuent de fonctionner sans modification
(gameUtils conserve les mêmes noms publics, qui délèguent ici).
On peut importer directement depuis services pour le nouveau code :

    from myPokemonApp.services import serialize_pokemon, get_player_trainer
"""
from .serializers import serialize_pokemon, serialize_pokemon_moves, build_battle_response
from .player_service import (
    get_player_trainer,
    get_or_create_player_trainer,
    get_player_location,
    get_defeated_trainer_ids,
    trainer_is_at_zone_with,
    has_pokedex,
    grant_pokedex,
    auto_reorganize_party,
    organize_party,
    ZONE_TRANSLATIONS,
)

__all__ = [
    # serializers
    'serialize_pokemon',
    'serialize_pokemon_moves',
    'build_battle_response',
    # player_service
    'get_player_trainer',
    'get_or_create_player_trainer',
    'get_player_location',
    'get_defeated_trainer_ids',
    'trainer_is_at_zone_with',
    'has_pokedex',
    'grant_pokedex',
    'auto_reorganize_party',
    'organize_party',
    'ZONE_TRANSLATIONS',
]