// ============================================================
// config/gameConfig.ts
// Configuration centrale de Phaser.
// ============================================================

import Phaser from 'phaser'
import { BootScene }    from '@scenes/BootScene'
import { PreloadScene } from '@scenes/PreloadScene'
import { GameScene }    from '@scenes/GameScene'
import { BattleScene }    from '@scenes/BattleScene'
import { EvolutionScene } from '@scenes/EvolutionScene'
import { UIScene }        from '@scenes/UIScene'
import { DialogScene }  from '@scenes/DialogScene'
import { AudioManager } from '@scenes/AudioManager'

export const GAME_WIDTH  = 640   // 20 tuiles × 32px
export const GAME_HEIGHT = 480   // 15 tuiles × 32px
export const TILE_SIZE   = 32    // px par tuile (peut passer à 16 si nécessaire)

export const gameConfig: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,             // WebGL si dispo, sinon Canvas
  width:  GAME_WIDTH,
  height: GAME_HEIGHT,
  parent: 'game-container',
  pixelArt: true,                // Désactive l'antialiasing — crucial pour le pixel art
  roundPixels: true,
  backgroundColor: '#000000',
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { x: 0, y: 0 },
      debug: import.meta.env.DEV,  // hitbox visibles en dev
    },
  },
  scene: [
    BootScene,     // 1. Boot : injecte le CSRF cookie, charge config JSON
    PreloadScene,  // 2. Preload : charge tous les assets (sprites, tilemaps, audio)
    GameScene,     // 3. GameScene : carte + déplacement joueur
    UIScene,       // 4. UIScene (parallèle) : HUD, menu, inventaire
    BattleScene,     // 5. BattleScene : combat au tour par tour
    EvolutionScene,  // 6. EvolutionScene : animation d'évolution Pokémon
    DialogScene,     // 7. DialogScene : boîtes de dialogue NPC
    AudioManager,    // 8. AudioManager : BGM + SFX
  ],
}