// ============================================================
// scenes/BootScene.ts
// Charge la position actuelle du joueur depuis l'api Django avant de lancer
// le jeu. Stocke les données dans le registry Phaser.
// ============================================================

import Phaser from 'phaser'
import { mapApi } from '@api/djangoClient'

export class BootScene extends Phaser.Scene {
  constructor() {
    super({ key: 'BootScene' })
  }

  async create(): Promise<void> {
    // ── Afficher un écran de chargement minimal ───────────────
    const { width, height } = this.cameras.main
    this.add.text(width / 2, height / 2, 'Connexion...', {
      fontSize: '10px',
      color: '#ffffff',
      fontFamily: '"Press Start 2P"',
    }).setOrigin(0.5)

    try {
      // ── 1. Charger la position courante du joueur ─────────
      const location = await mapApi.getPlayerLocation()

      this.registry.set('currentZoneId',   location.current_zone_id)
      this.registry.set('currentZoneName', location.current_zone_name)
      this.registry.set('visitedZoneIds',  location.visited_zone_ids)
      this.registry.set('trainerId',       location.trainer_id)

      console.log(`[Boot] Zone: ${location.current_zone_name} (id: ${location.current_zone_id})`)

      // ── 2. Charger le détail de la zone courante ──────────
      const zone = await mapApi.getZone(location.current_zone_id)
      this.registry.set('currentZone', zone)

      console.log(`[Boot] Zone chargée — connexions: ${zone.connections.length}, spawns: ${zone.wild_spawns.length}`)

      // ── 3. Lancer le jeu ──────────────────────────────────
      this.scene.start('PreloadScene')

    } catch (err) {
      // Si la session est expirée, djangoClient redirige vers /login/
      // On affiche juste l'erreur pour le debug
      console.error('[Boot] Erreur:', err)
      this.add.text(width / 2, height / 2 + 30, 'Erreur de connexion — vérifier Django', {
        fontSize: '8px',
        color: '#ff4444',
      }).setOrigin(0.5)
    }
  }
}