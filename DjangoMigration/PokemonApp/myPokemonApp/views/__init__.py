"""
myPokemonApp/views/__init__.py
"""

# ── Vues génériques / dashboard ───────────────────────────────────────────────
from myPokemonApp.views.Views import (
    GenericOverview,
    DashboardView,
    choose_starter_view,
)

# ── Pokédex ────────────────────────────────────────────────────────────────────
from myPokemonApp.views.PokedexViews import (
    PokemonOverView,
    PokemonDetailView,
)

# ── Équipe ─────────────────────────────────────────────────────────────────────
from myPokemonApp.views.TeamViews import (
    MyTeamView,
    heal_pokemon_api,
    send_to_pc_api,
    add_to_party_api,
    swap_move_api,
    get_pokemon_moves_api,
    reorder_party_api,
    reorder_moves_api,
    rename_pokemon_api
)

# ── Objets tenus ───────────────────────────────────────────────────────────────
from myPokemonApp.views.HeldItemViews import (
    EquipHeldItemView,
    PokemonHeldItemsView,
)

# ── Moves ──────────────────────────────────────────────────────────────────────
from myPokemonApp.views.PokemonMovesViews import (
    PokemonMoveOverView,
    PokemonMoveDetailView,
)

# ── Carte / zones ──────────────────────────────────────────────────────────────
from myPokemonApp.views.MapViews import (
    map_view,
    zone_detail_view,
    travel_to_zone_view,
    wild_encounter_view,
    fly_view
)

# ── Étages ─────────────────────────────────────────────────────────────────────
from myPokemonApp.views.FloorViews import (
    building_redirect_view,
    floor_detail_view,
    floor_wild_encounter_view,
)

# ── Centres Pokémon ────────────────────────────────────────────────────────────
from myPokemonApp.views.PokemonCenterViews import (
    PokemonCenterListView,
    PokemonCenterDetailView,
    heal_team_api,
    center_history_view,
    access_pc_from_center_api,
)

# ── Shops ──────────────────────────────────────────────────────────────────────
from myPokemonApp.views.ShopViews import (
    ShopListView,
    ShopDetailView,
    buy_item_api,
    sell_item_api,
    transaction_history_view,
)

# ── Items ──────────────────────────────────────────────────────────────────────
from myPokemonApp.views.ItemViews import (
    ItemListView,
    UseTMView,
    TMCompatibilityView,
)

# ── Gym Leaders ────────────────────────────────────────────────────────────────
from myPokemonApp.views.GymLeaderViews import (
    GymLeaderListView,
    GymLeaderDetailView,
    BadgeBoxView,
)

# ── Sauvegardes ────────────────────────────────────────────────────────────────
from myPokemonApp.views.SaveViews import (
    save_select_view,
    save_create_view,
    save_load_view,
    save_game_view,
    auto_save_view,
    save_slots_list_view,
    save_create_quick_view,
)

# ── Quêtes ─────────────────────────────────────────────────────────────────────
from myPokemonApp.views.QuestViews import (
    quest_log_view,
    quest_widget_view,
    quest_detail_view,
)

# ── Captures ───────────────────────────────────────────────────────────────────
from myPokemonApp.views.CaptureViews import (
    capture_journal_view,
)

# ── Achievements ───────────────────────────────────────────────────────────────
from myPokemonApp.views.AchievementViews import (
    achievements_list_view,
    achievements_widget_view,
)

# ── Combat : lecture (liste, détail) ──────────────────────────────────────────
from myPokemonApp.views.BattleListViews import (
    BattleListView,
    BattleDetailView,
)

# ── Combat : vue graphique ────────────────────────────────────────────────────
from myPokemonApp.views.BattleGameViews import (
    BattleGameView,
)

# ── Combat : actions (API POST) + apprentissage de move ───────────────────────
from myPokemonApp.views.BattleActionViews import (
    battle_action_view,
    battle_learn_move_view,
)

# ── Combat : création + écran de fin dresseur ─────────────────────────────────
from myPokemonApp.views.BattleCreateViews import (
    battle_create_view,
    battle_create_wild_view,
    battle_create_trainer_view,
    battle_create_gym_view,
    battle_challenge_gym_view,
    battle_trainer_complete_view,
)

# ── Combat : APIs JSON utilitaires ────────────────────────────────────────────
from myPokemonApp.views.BattleApiViews import (
    GetTrainerTeam,
    GetTrainerItems,
)