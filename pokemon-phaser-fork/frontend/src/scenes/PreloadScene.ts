// ============================================================
// scenes/PreloadScene.ts
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

    // ── Tilemap de la zone courante (chargée dynamiquement) ───
    // Le joueur peut démarrer sur n'importe quelle zone (Django)
    // On charge toujours la map de la zone courante + bourg_palette par défaut
    const currentZoneName: string = this.registry.get('currentZoneName') ?? 'Bourg Palette'
    const currentMapKey = this.zoneNameToKey(currentZoneName)

    this.load.tilemapTiledJSON(currentMapKey, `/assets/tilemaps/${currentMapKey}.json`)

    // Charger aussi bourg_palette si ce n'est pas déjà la zone courante
    if (currentMapKey !== 'bourg_palette') {
      this.load.tilemapTiledJSON('bourg_palette', '/assets/tilemaps/bourg_palette.json')
    }

    // ── Tilesets standard (grilles) ───────────────────────────
    this.load.image('full_kanto',    '/assets/tilesets/full_kanto.png')
    this.load.image('style_forever', '/assets/tilesets/style_forever.png')

    // ── Tilesets "image collection" ───────────────────────────
    this.load.image('pallet_lab',          '/assets/tilesets/pallet_lab.png')
    this.load.image('pallet_house_green1', '/assets/tilesets/pallet_house_green1.png')
    this.load.image('pallet_house_green2', '/assets/tilesets/pallet_house_green2.png')
    this.load.image('pallet_house_green3', '/assets/tilesets/pallet_house_green3.png')

    this.load.spritesheet('pokeballs_pickup', '/assets/tilesets/pokeballs_pickup.png', {
      frameWidth: 32,
      frameHeight: 32,
    })

    this.load.image('collision',   '/assets/tilesets/collision.png')
    this.load.image('bumper_down', '/assets/tilesets/bumper_down.png')

    // ── Spritesheet joueur (20×32) ────────────────────────────
    this.load.spritesheet('player', '/assets/sprites/player.png', {
      frameWidth:  20,
      frameHeight: 32,
    })
  }

  create(): void {
    this.progressBar.destroy()
    this.progressBox.destroy()

    this.createAnimations()

    this.scene.start('GameScene')
    this.scene.launch('UIScene')
    this.scene.launch('AudioManager')
  }

  // Même logique que GameScene.zoneNameToKey — dupliquée ici
  // pour éviter une dépendance circulaire
  private zoneNameToKey(name: string): string {
    return name
      .toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_|_$/g, '')
  }

  private createAnimations(): void {
    const anims = this.anims

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