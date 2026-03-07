#!/usr/bin/python3
"""
gameUtils.py 
Ce fichier ne contient pas de logique métier mais les importe depuis myPokemonApp/services/
"""

# ───  trainer_service ────────────────────────────────────────
from myPokemonApp.services.trainer_service import (
    get_first_alive_pokemon,
    get_or_create_wild_trainer,
    _reset_team_stages,
    heal_team,
    cleanup_orphan_wild_pokemon,
    deposit_pokemon,
    withdraw_pokemon,
    get_nature_modifiers,
    calculate_pokemon_stats_with_nature,
)

# ─── pokemon_factory ─────────────────────────────────────
from myPokemonApp.services.pokemon_factory import (
    learn_moves_up_to_level,
    ensure_has_moves,
    exp_at_level_for_species,
    generate_random_nature,
    assign_ability,
    create_wild_pokemon,
    create_starter_pokemon,
    create_gym_leader,
    create_npc_trainer,
    create_rival,
)

# ─── battle_service ──────────────────────────────────────────────
from myPokemonApp.services.battle_service import (
    start_battle,
    get_opponent_ai_action,
    calculate_exp_gain,
    apply_exp_gain,
    apply_ev_gains,
    check_battle_end,
    opponent_switch_pokemon,
)

# ─── serializers ────────────────────────────────────
from myPokemonApp.services.serializers import (
    serialize_pokemon,
    serialize_pokemon_moves,
    build_battle_response,
)

# ─── capture_service ─────────────────────────────────────────
from myPokemonApp.services.capture_service import (
    calculate_capture_rate,
    calculate_shake_count,
    attempt_pokemon_capture,
    get_random_wild_pokemon,
    get_encounter_chance,
)

# ─── inventory_service ───────────────────────────────────────────
from myPokemonApp.services.inventory_service import (
    give_item_to_trainer,
    remove_item_from_trainer,
    use_item_in_battle,
)

# ─── player_service ────────────────────────────────
from myPokemonApp.services.player_service import (
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