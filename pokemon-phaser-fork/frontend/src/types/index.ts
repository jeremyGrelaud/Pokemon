// ============================================================
// types/index.ts
// Types TypeScript qui reflètent les serializers Django.
// À maintenir en sync avec serializers.py et les modèles Django.
// ============================================================

// ── Zone ─────────────────────────────────────────────────────

export type ZoneType = 'route' | 'city' | 'cave' | 'forest' | 'water' | 'building'
export type EncounterType = 'grass' | 'water' | 'fishing' | 'cave'

export interface ZoneData {
  id: number
  name: string
  zone_type: ZoneType
  description: string
  recommended_level_min: number
  recommended_level_max: number
  is_safe_zone: boolean
  has_pokemon_center: boolean
  has_shop: boolean
  has_floors: boolean
  music: string
  image: string
  // Coordonnées pixel sur la tilemap Kanto (à remplir lors du mapping)
  map_x?: number
  map_y?: number
}

export interface ZoneConnectionData {
  to_zone_id: number
  to_zone_name: string
  is_bidirectional: boolean
  required_hm: string
  is_passable: boolean
  block_reason: string
}

export interface WildSpawnData {
  pokemon_name: string
  pokemon_id: number
  spawn_rate: number
  level_min: number
  level_max: number
  encounter_type: EncounterType
}

export interface ZoneDetailData extends ZoneData {
  connections: ZoneConnectionData[]
  wild_spawns: WildSpawnData[]
  can_access: boolean
  access_reason: string
  is_current: boolean
}

// ── Player / Location ─────────────────────────────────────────

export interface PlayerLocationData {
  trainer_id: number   
  current_zone_id: number
  current_zone_name: string
  visited_zone_ids: number[]
  last_pokemon_center_id: number | null
}

// ── Pokémon ───────────────────────────────────────────────────

export interface MoveData {
  id: number
  name: string
  type: string
  category: 'physical' | 'special' | 'status'
  power: number | null
  accuracy: number | null
  effect: string | null
  effect_chance: number | null
  current_pp: number
  max_pp: number
}

export interface PokemonData {
  id: number
  name: string
  species_name: string
  level: number
  current_hp: number
  max_hp: number
  status: string | null
  is_shiny: boolean
  dex_number?: number
  moves?: MoveData[]
  // Champs XP (présents dans build_battle_response)
  current_exp?: number
  exp_for_next_level?: number
  exp_percent?: number
}

// ── Combat ────────────────────────────────────────────────────

export interface StatStages {
  atk: number
  def: number
  spatk: number
  spdef: number
  speed: number
  acc: number
  eva: number
}

export interface ScreenState {
  light_screen: number
  reflect: number
}

export interface BattleState {
  weather: string | null
  weather_turns: number

  player_confused: boolean
  player_leech_seed: boolean
  player_trapped: boolean
  player_badly_poisoned: boolean
  player_charging: string | null
  player_recharge: boolean
  player_protected: boolean
  player_screens: ScreenState

  opponent_confused: boolean
  opponent_leech_seed: boolean
  opponent_trapped: boolean
  opponent_badly_poisoned: boolean
  opponent_charging: string | null
  opponent_recharge: boolean
  opponent_protected: boolean
  opponent_screens: ScreenState

  player_atk_stage: number
  player_def_stage: number
  player_spatk_stage: number
  player_spdef_stage: number
  player_speed_stage: number
  player_acc_stage: number
  player_eva_stage: number

  opponent_atk_stage: number
  opponent_def_stage: number
  opponent_spatk_stage: number
  opponent_spdef_stage: number
  opponent_speed_stage: number
  opponent_acc_stage: number
  opponent_eva_stage: number
}

export interface TurnInfo {
  player_first: boolean
  second_skipped: boolean
}

export interface BattleResponse {
  success: boolean
  log: string[]
  player_pokemon: PokemonData
  opponent_pokemon: PokemonData
  player_hp: number
  player_max_hp: number
  opponent_hp: number
  opponent_max_hp: number
  battle_ended: boolean
  battle_type?: 'wild' | 'trainer' | 'gym' | 'elite_four' | 'rival'
  battle_state: BattleState
  turn_info: TurnInfo
  hp_before_eot: { player: number; opponent: number } | null
  pending_evolution?: {
    evolution_id:    number
    pokemon_id:      number
    from_name:       string
    from_species_id: number
    to_name:         string
    to_species_id:   number
    is_shiny:        boolean
    stats_before:    Record<string, number>
  }
}

// ── Map overview ──────────────────────────────────────────────

export interface MapZoneEntry {
  zone: ZoneData
  accessible: boolean
  reason: string
  visited: boolean
  has_gym: boolean
}

export interface MapOverviewData {
  current_zone_id: number
  zones: MapZoneEntry[]
  connected_zone_ids: number[]
}

// ── Événements Phaser (EventBus) ──────────────────────────────

export type GameEvent =
  | 'zone-changed'
  | 'zone-entered'
  | 'battle-started'
  | 'battle-ended'
  | 'player-healed'
  | 'save-loaded'
  | 'quest-completed'
  | 'pokemon-caught'