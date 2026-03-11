// ============================================================
// api/djangoClient.ts
// Client HTTP vers le backend Django.
// - Requêtes JSON par défaut
// - Form data pour les actions de combat (Django lit request.POST)
// ============================================================

import type {
  MapOverviewData,
  ZoneDetailData,
  PlayerLocationData,
  BattleResponse,
  PokemonData,
} from '@/types'

export interface BattleItem {
  id: number
  name: string
  quantity: number
  item_type: string
  description: string
}

export interface TeamResponse  { success: boolean; team: PokemonData[] }
export interface ItemsResponse { success: boolean; items: BattleItem[] }

// ── CSRF ──────────────────────────────────────────────────────

function getCsrfToken(): string {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : ''
}

// ── Fetch générique ───────────────────────────────────────────

async function request<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const customHeaders = (options.headers as Record<string, string>) ?? {}

  const headers: Record<string, string> = {
    'X-CSRFToken': getCsrfToken(),
    // Content-Type JSON par défaut, sauf si déjà défini (ex: form data)
    ...(!customHeaders['Content-Type'] && { 'Content-Type': 'application/json' }),
    ...customHeaders,
  }

  const res = await fetch(url, {
    credentials: 'include', // Envoie le cookie de session Django
    ...options,
    headers,
  })

  if (res.status === 401 || res.status === 403) {
    window.location.href = '/login/?next=/'
    throw new Error('Session expirée')
  }

  if (!res.ok) {
    const errorText = await res.text()
    throw new Error(`API ${res.status}: ${errorText}`)
  }

  return res.json() as Promise<T>
}

// ── Helper form data ──────────────────────────────────────────

function formRequest<T>(url: string, params: Record<string, string>): Promise<T> {
  return request<T>(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams(params).toString(),
  })
}

// ── API Map ───────────────────────────────────────────────────

export const mapApi = {
  /** Récupère la vue d'ensemble de la carte Kanto */
  getOverview(): Promise<MapOverviewData> {
    return request<MapOverviewData>('/api/phaser/map/')
  },

  /** Détail d'une zone (connexions, spawns, accès) */
  getZone(zoneId: number): Promise<ZoneDetailData> {
    return request<ZoneDetailData>(`/api/phaser/map/zone/${zoneId}/`)
  },

  /** Déplace le joueur vers une zone — endpoint Phaser JSON */
  travelTo(zoneId: number): Promise<{ success: boolean; message: string; zone: ZoneDetailData }> {
    return request(`/api/phaser/map/travel/${zoneId}/`, { method: 'POST' })
  },

  /** Déclenche une rencontre sauvage — endpoint Phaser JSON */
  wildEncounter(zoneId: number, type: string = 'grass'): Promise<{ battle_id: number; pokemon_name?: string; level?: number }> {
    return request(`/api/phaser/map/encounter/${zoneId}/?type=${type}`, { method: 'POST' })
  },

  /** Récupère la position actuelle du joueur */
  getPlayerLocation(): Promise<PlayerLocationData> {
    return request<PlayerLocationData>('/api/phaser/player/location/')
  },
}

// ── API Battle ────────────────────────────────────────────────

export const battleApi = {
  /** État initial du combat */
  getState(battleId: number): Promise<BattleResponse> {
    return request<BattleResponse>(`/api/battle/state/${battleId}/`)
  },

  /** Attaque — Django lit request.POST → form data */
  useMove(battleId: number, moveId: number): Promise<BattleResponse> {
    return formRequest<BattleResponse>(`/battle/${battleId}/action/`, {
      action:  'attack',
      move_id: String(moveId),
    })
  },

  /** Utiliser un objet — form data */
  useItem(battleId: number, itemId: number, pokemonId?: number): Promise<BattleResponse> {
    const params: Record<string, string> = {
      action:  'item',
      item_id: String(itemId),
    }
    if (pokemonId !== undefined) params.pokemon_id = String(pokemonId)
    return formRequest<BattleResponse>(`/battle/${battleId}/action/`, params)
  },

  /** Fuir — form data */
  flee(battleId: number): Promise<BattleResponse> {
    return formRequest<BattleResponse>(`/battle/${battleId}/action/`, {
      action: 'flee',
    })
  },

  /** Changer de Pokémon — form data */
  switchPokemon(battleId: number, pokemonId: number): Promise<BattleResponse> {
    return formRequest<BattleResponse>(`/battle/${battleId}/action/`, {
      action:     'switch',
      pokemon_id: String(pokemonId),
    })
  },

  /** Lancer une Poké Ball — form data (action='item', Django détecte le type pokeball) */
  throwBall(battleId: number, itemId: number): Promise<BattleResponse> {
    return formRequest<BattleResponse>(`/battle/${battleId}/action/`, {
      action:  'item',
      item_id: String(itemId),
    })
  },

  /** Confirmer la capture après animation shakes — form data */
  confirmCapture(battleId: number, itemId: number): Promise<BattleResponse> {
    return formRequest<BattleResponse>(`/battle/${battleId}/action/`, {
      action:  'confirm_capture',
      item_id: String(itemId),
    })
  },

  /** Confirmer une évolution après animation — form data */
  confirmEvolution(battleId: number, evolutionId: number): Promise<BattleResponse> {
    return formRequest<BattleResponse>(`/battle/${battleId}/action/`, {
      action:       'confirm_evolution',
      evolution_id: String(evolutionId),
    })
  },

  /** Récupère l'équipe du dresseur */
  getTeam(trainerId: number): Promise<TeamResponse> {
    return request<TeamResponse>(`/api/battle/team/?trainer_id=${trainerId}`)
  },

  /** Récupère les objets du dresseur */
  getItems(trainerId: number): Promise<ItemsResponse> {
    return request<ItemsResponse>(`/api/battle/items/?trainer_id=${trainerId}`)
  },
}

// ── API Player ────────────────────────────────────────────────

export const playerApi = {
  /** Sauvegarde rapide */
  autoSave(saveId: number): Promise<{ success: boolean }> {
    return formRequest(`/saves/${saveId}/auto-save/`, {})
  },
}