// ============================================================
// scenes/PreloadScene.ts
// VERSION TEST — charge les assets minimalistes de test.
// ============================================================

import Phaser from 'phaser'

export class PreloadScene extends Phaser.Scene {
  private progressBar!: Phaser.GameObjects.Graphics
  private progressBox!: Phaser.GameObjects.Graphics

  constructor() {
    super({ key: 'PreloadScene' })
  }

  preload(): void {
    this.createLoadingBar()

    this.load.on('progress', (value: number) => {
      this.progressBar.clear()
      this.progressBar.fillStyle(0xffffff, 1)
      this.progressBar.fillRect(
        this.cameras.main.width / 4,
        this.cameras.main.height / 2 - 10,
        (this.cameras.main.width / 2) * value,
        20
      )
    })

    // ── Tilemap de test ───────────────────────────────────────
    // Le JSON référence tileset_test.json qui doit être
    // dans le même dossier que kanto_test.json
    this.load.tilemapTiledJSON('kanto', '/assets/tilemaps/kanto_test.json')
    this.load.image('tileset_test', '/assets/tilesets/tileset_test.png')

    // ── Spritesheet joueur (32×32, 3 cols × 4 rows) ───────────
    this.load.spritesheet('player', '/assets/sprites/player_test.png', {
      frameWidth:  32,
      frameHeight: 32,
    })
  }

  create(): void {
    this.progressBar.destroy()
    this.progressBox.destroy()

    this.createAnimations()

    // GameScene + UIScene en parallèle
    this.scene.start('GameScene')
    this.scene.launch('UIScene')
    this.scene.launch('AudioManager')
  }

  private createAnimations(): void {
    const anims = this.anims

    // Spritesheet : 3 frames × 4 directions
    // Row 0 = bas, Row 1 = gauche, Row 2 = droite, Row 3 = haut
    const dirs: Array<{ key: string; row: number }> = [
      { key: 'down',  row: 0 },
      { key: 'left',  row: 1 },
      { key: 'right', row: 2 },
      { key: 'up',    row: 3 },
    ]

    dirs.forEach(({ key, row }) => {
      anims.create({
        key: `walk-${key}`,
        frames: anims.generateFrameNumbers('player', {
          start: row * 3,
          end:   row * 3 + 2,
        }),
        frameRate: 8,
        repeat: -1,
      })

      anims.create({
        key: `idle-${key}`,
        frames: [{ key: 'player', frame: row * 3 }],
        frameRate: 1,
        repeat: 0,
      })
    })
  }

  private createLoadingBar(): void {
    const { width, height } = this.cameras.main

    this.progressBox = this.add.graphics()
    this.progressBox.fillStyle(0x222222, 0.8)
    this.progressBox.fillRect(width / 4 - 5, height / 2 - 15, width / 2 + 10, 30)

    this.progressBar = this.add.graphics()

    this.add.text(width / 2, height / 2 - 40, 'Chargement...', {
      fontSize: '10px',
      color: '#ffffff',
    }).setOrigin(0.5)
  }
}