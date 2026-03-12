// ============================================================
// main.ts
// Point d'entrée : instancie Phaser avec la config.
// ============================================================

import Phaser from 'phaser'
import { gameConfig } from '@config/gameConfig'

// Lancer le jeu
const game = new Phaser.Game(gameConfig)

// Exposer en dev pour debug console
if (import.meta.env.DEV) {
  // @ts-expect-error — debug global
  window.__POKEMON_GAME__ = game
}
