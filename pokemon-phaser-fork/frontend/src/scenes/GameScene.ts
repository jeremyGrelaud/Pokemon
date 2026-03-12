// ============================================================
// scenes/GameScene.ts
// Connecté à Django — portails et rencontres appellent l'API.
// ============================================================

import Phaser from 'phaser'
import { TILE_SIZE } from '@config/gameConfig'
import { mapApi } from '@api/djangoClient'
import type { ZoneDetailData } from '@/types'
import { AudioManager } from './AudioManager'

const PLAYER_SPEED   = 160
const ENCOUNTER_RATE = 0.02  // ~2% par frame soit ~1 rencontre/3s en marchant

type Direction = 'up' | 'down' | 'left' | 'right'

export class GameScene extends Phaser.Scene {

  private map!: Phaser.Tilemaps.Tilemap
  private collisionLayer!: Phaser.Tilemaps.TilemapLayer
  private player!: Phaser.Physics.Arcade.Sprite

  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys
  private wasd!: Record<Direction, Phaser.Input.Keyboard.Key>

  private facingDirection: Direction = 'down'
  private isMoving = false
  private grassCooldown = false

  private grassGroup!: Phaser.Physics.Arcade.StaticGroup
  private portalGroup!: Phaser.Physics.Arcade.StaticGroup

  private debugText!: Phaser.GameObjects.Text

  // Zone courante (chargée depuis le registry au démarrage)
  private currentZone!: ZoneDetailData

  constructor() {
    super({ key: 'GameScene' })
  }

  // ─────────────────────────────────────────────────────────────
  // CREATE
  // ─────────────────────────────────────────────────────────────

  create(): void {
    // Récupérer la zone chargée par BootScene
    this.currentZone = this.registry.get('currentZone') as ZoneDetailData

    this.buildTilemap()
    this.createPlayer()
    this.setupInput()
    this.setupOverlaps()
    this.cameras.main.setZoom(2)  // tiles 16px → affichés en 32px
    this.setupCamera()
    this.createDebugUI()

    // Notifier UIScene du nom de zone réel
    this.events.emit('zone-entered', this.currentZone)

    // Musique de la zone courante
    if (this.currentZone.music) {
      AudioManager.instance?.playZone(this.currentZone.music)
    }
  }

  // ─────────────────────────────────────────────────────────────
  // UPDATE
  // ─────────────────────────────────────────────────────────────

  update(): void {
    this.handleMovement()
    this.player.setDepth(this.player.y + this.player.height / 2)// Dynamic player depth use feet as reference
    this.updateDebug()
  }

  // ─────────────────────────────────────────────────────────────
  // TILEMAP
  // ─────────────────────────────────────────────────────────────

private buildTilemap(): void {
    this.map = this.make.tilemap({ key: 'pallet_town' })

    // ── Tilesets ───────────────────────────────────────────────
    const tsKanto   = this.map.addTilesetImage('full_kanto',                          'full_kanto')!
    const tsForever = this.map.addTilesetImage('style_forever',                       'style_forever')!
    const tsLab     = this.map.addTilesetImage('../tilesets/pallet_lab.png',          'pallet_lab')!
    const tsHouse1  = this.map.addTilesetImage('../tilesets/pallet_house_green1.png', 'pallet_house_green1')!
    const tsHouse2  = this.map.addTilesetImage('../tilesets/pallet_house_green2.png', 'pallet_house_green2')!
    const tsHouse3  = this.map.addTilesetImage('../tilesets/pallet_house_green3.png', 'pallet_house_green3')!

    const allTilesets = [tsKanto, tsForever, tsLab, tsHouse1, tsHouse2, tsHouse3]

    // ── Couches de tuiles ──────────────────────────────────────
    this.map.createLayer('Ground',     allTilesets, 0, 0)
    this.map.createLayer('Decoration', allTilesets, 0, 0)
    this.map.createLayer('Grass',      allTilesets, 0, 0)

    this.collisionLayer = this.map.createLayer('Collision', allTilesets, 0, 0)!
    this.collisionLayer.setCollisionByProperty({ collides: true })
    this.collisionLayer.setAlpha(0)

    this.physics.world.setBounds(0, 0, this.map.widthInPixels, this.map.heightInPixels)

    // ── Bâtiments (object layer — image collection tilesets) ───
    // Tiled positionne les objets depuis le coin bas-gauche → setOrigin(0, 1)
    // depth = y pour un rendu pseudo-3D correct (les bâtiments plus bas = devant)
    const GID_TO_KEY: Record<number, string> = {
      9747: 'pallet_lab',
      9753: 'pallet_house_green1',
      9754: 'pallet_house_green2',
      9755: 'pallet_house_green3',
    }

    const buildingsLayer = this.map.getObjectLayer('Buildings')
    buildingsLayer?.objects.forEach((obj) => {
      const textureKey = obj.gid ? GID_TO_KEY[obj.gid] : undefined
      if (!textureKey) return
      // Après — depth = bas du bâtiment (obj.y) mais on soustrait une marge
      // pour que le joueur passe devant quand il est sous le bâtiment
      // La "ligne de sol" du bâtiment = bas du sprite - ~32px d'ombre
      const groundLine = obj.y! - 32
      this.add.image(obj.x!, obj.y!, textureKey)
        .setOrigin(0, 1)
        .setDepth(groundLine)
    })

    // ── Herbes depuis la couche Grass ──────────────────────────
    this.grassGroup = this.physics.add.staticGroup()
    const grassLayer = this.map.getLayer('Grass')
    if (grassLayer) {
      grassLayer.data.forEach((row) => {
        row.forEach((tile) => {
          if (tile.index > 0) {
            const rect = this.add.rectangle(
              tile.pixelX + TILE_SIZE / 2,
              tile.pixelY + TILE_SIZE / 2,
              TILE_SIZE, TILE_SIZE,
              0x00ff00, 0
            )
            this.physics.add.existing(rect, true)
            this.grassGroup.add(rect)
          }
        })
      })
    }

    // ── Portails depuis l'object layer Portals ─────────────────
    this.portalGroup = this.physics.add.staticGroup()
    const portalLayer = this.map.getObjectLayer('Portals')
    portalLayer?.objects.forEach((obj) => {
      const rect = this.add.rectangle(
        obj.x! + obj.width! / 2,
        obj.y! + obj.height! / 2,
        obj.width!, obj.height!,
        0xffff00, 0.3
      )
      this.physics.add.existing(rect, true)
      const zoneId = (obj.properties as Array<{name: string; value: unknown}>)
        ?.find(p => p.name === 'zone_id')?.value as number
      rect.setData('zoneId', zoneId)
      rect.setData('zoneName', obj.name)
      this.portalGroup.add(rect)
    })
  }
  // private buildTilemap(): void {
  //   this.map = this.make.tilemap({ key: 'pallet_town' })
  //   const tileset = this.map.addTilesetImage('full_kanto', 'full_kanto')!

  //   this.map.createLayer('Ground', tileset, 0, 0)
  //   this.map.createLayer('Decoration', tileset, 0, 0)
  //   this.map.createLayer('Grass', tileset, 0, 0)

  //   this.collisionLayer = this.map.createLayer('Collision', tileset, 0, 0)!
  //   this.collisionLayer.setCollisionByProperty({ collides: true })
  //   this.collisionLayer.setAlpha(0)  // invisible en jeu

  //   // this.physics.world.setBounds(0, 0, this.map.widthInPixels, this.map.heightInPixels)

  //   // this.map = this.make.tilemap({ key: 'kanto' })
  //   // const tileset = this.map.addTilesetImage('tileset_test', 'tileset_test')!

  //   // this.map.createLayer('Ground', tileset, 0, 0)!
  //   // this.map.createLayer('Grass', tileset, 0, 0)!

  //   // this.collisionLayer = this.map.createLayer('Collision', tileset, 0, 0)!
  //   // this.collisionLayer.setCollisionByProperty({ collides: true })
  //   // this.collisionLayer.setAlpha(0)

  //   // this.physics.world.setBounds(0, 0, this.map.widthInPixels, this.map.heightInPixels)

  //   // ── Herbes depuis la couche Grass ─────────────────────────
  //   this.grassGroup = this.physics.add.staticGroup()
  //   const grassLayer = this.map.getLayer('Grass')
  //   if (grassLayer) {
  //     grassLayer.data.forEach((row) => {
  //       row.forEach((tile) => {
  //         if (tile.index > 0) {
  //           const rect = this.add.rectangle(
  //             tile.pixelX + TILE_SIZE / 2,
  //             tile.pixelY + TILE_SIZE / 2,
  //             TILE_SIZE, TILE_SIZE,
  //             0x00ff00, 0
  //           )
  //           this.physics.add.existing(rect, true)
  //           this.grassGroup.add(rect)
  //         }
  //       })
  //     })
  //   }

  //   // ── Portails depuis la couche Portals ─────────────────────
  //   // Pour l'instant on utilise les portails de la tilemap de test.
  //   // Quand tu auras la vraie carte Kanto, ils seront alignés avec
  //   // les vrais zone_id Django.
  //   this.portalGroup = this.physics.add.staticGroup()
  //   const portalLayer = this.map.getObjectLayer('Portals')
  //   portalLayer?.objects.forEach((obj) => {
  //     const rect = this.add.rectangle(
  //       obj.x! + obj.width! / 2,
  //       obj.y! + obj.height! / 2,
  //       obj.width!, obj.height!,
  //       0xffff00, 0.3
  //     )
  //     this.physics.add.existing(rect, true)
  //     const zoneId = (obj.properties as Array<{name:string; value:unknown}>)
  //       ?.find(p => p.name === 'zone_id')?.value as number
  //     rect.setData('zoneId', zoneId)
  //     rect.setData('zoneName', obj.name)
  //     this.portalGroup.add(rect)
  //   })
  // }

  // ─────────────────────────────────────────────────────────────
  // JOUEUR
  // ─────────────────────────────────────────────────────────────

  private createPlayer(): void {
    const spawn = this.map.findObject(
      'Spawns',
      (obj) => obj.name === 'PlayerSpawn'
    ) as { x: number; y: number; width: number; height: number } | undefined

    const x = spawn ? spawn.x + spawn.width / 2  : this.map.widthInPixels / 2
    const y = spawn ? spawn.y + spawn.height / 2 : this.map.heightInPixels / 2

    this.player = this.physics.add.sprite(x, y, 'player', 0)
    this.player.setCollideWorldBounds(true)
    //this.player.setDepth(10)  // will be set dynamically
    // hitbox centrée sur les pieds du sprite 20×32
    this.player.body!.setSize(12, 10)
    this.player.body!.setOffset(4, 22)

    this.physics.add.collider(this.player, this.collisionLayer)
    this.player.anims.play('idle-down')
  }

  // ─────────────────────────────────────────────────────────────
  // INPUT
  // ─────────────────────────────────────────────────────────────

  private setupInput(): void {
    this.cursors = this.input.keyboard!.createCursorKeys()
    this.wasd = {
      up:    this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.W),
      down:  this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.S),
      left:  this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.A),
      right: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.D),
    }
  }

  private handleMovement(): void {
    const up    = this.cursors.up.isDown    || this.wasd.up.isDown
    const down  = this.cursors.down.isDown  || this.wasd.down.isDown
    const left  = this.cursors.left.isDown  || this.wasd.left.isDown
    const right = this.cursors.right.isDown || this.wasd.right.isDown

    if (!up && !down && !left && !right) {
      this.player.setVelocity(0, 0)
      this.player.anims.play(`idle-${this.facingDirection}`, true)
      return
    }

    let vx = 0, vy = 0
    let dir: Direction = this.facingDirection

    if (up)    { vy = -PLAYER_SPEED; dir = 'up'    }
    if (down)  { vy =  PLAYER_SPEED; dir = 'down'  }
    if (left)  { vx = -PLAYER_SPEED; dir = 'left'  }
    if (right) { vx =  PLAYER_SPEED; dir = 'right' }

    if (vx !== 0 && vy !== 0) {
      vx *= 0.707
      vy *= 0.707
    }

    this.facingDirection = dir
    this.player.setVelocity(vx, vy)
    this.player.anims.play(`walk-${dir}`, true)
  }

  // ─────────────────────────────────────────────────────────────
  // OVERLAPS
  // ─────────────────────────────────────────────────────────────

  private setupOverlaps(): void {
    this.physics.add.overlap(this.player, this.grassGroup, () => {
      if (this.grassCooldown || this.isMoving) return
      if (Math.random() < ENCOUNTER_RATE) {
        void this.onGrassEncounter()
      }
    })

    this.physics.add.overlap(
      this.player,
      this.portalGroup,
      (_p, portal) => {
        const rect = portal as Phaser.GameObjects.Rectangle
        void this.onPortalEnter(
          rect.getData('zoneId') as number,
          rect.getData('zoneName') as string
        )
      }
    )
  }

  // ─────────────────────────────────────────────────────────────
  // RENCONTRE SAUVAGE → Django
  // ─────────────────────────────────────────────────────────────

  private async onGrassEncounter(): Promise<void> {
    this.grassCooldown = true
    this.cameras.main.flash(200, 255, 255, 255)

    try {
      // Appel Django : crée le combat et renvoie battle_id
      const result = await mapApi.wildEncounter(this.currentZone.id)

      console.log(`[GameScene] Combat créé — battle_id: ${result.battle_id}`)

      // Suspendre GameScene et lancer BattleScene
      this.scene.pause('GameScene')
      this.scene.launch('BattleScene', { battleId: result.battle_id })

    } catch (err) {
      console.error('[GameScene] Erreur rencontre:', err)
      // En cas d'erreur (zone sans spawns, etc.) on affiche un message
      this.scene.launch('DialogScene', {
        text: `Aucun Pokémon dans cette zone.`,
        autoClose: 1500,
      })
    }
  }

  // ─────────────────────────────────────────────────────────────
  // TRANSITION DE ZONE → Django
  // ─────────────────────────────────────────────────────────────

  private async onPortalEnter(zoneId: number, zoneName: string): Promise<void> {
    if (this.isMoving) return
    this.isMoving = true

    await this.fadeOut()

    try {
      // Appel Django : déplace le joueur vers la zone
      const result = await mapApi.travelTo(zoneId)

      if (!result.success) {
        // Django bloque le passage (badge manquant, CS requise, etc.)
        this.scene.launch('DialogScene', {
          text: result.message,
          autoClose: 2500,
        })
        await this.fadeIn()
        this.isMoving = false
        return
      }

      // Mettre à jour la zone courante
      this.currentZone = result.zone
      this.registry.set('currentZone', result.zone)
      this.registry.set('currentZoneId', result.zone.id)
      this.registry.set('currentZoneName', result.zone.name)

      console.log(`[GameScene] Arrivée : ${result.zone.name} (id: ${result.zone.id})`)

      // Nouvelle musique de zone (fondu enchaîné)
      if (result.zone.music) {
        AudioManager.instance?.playZone(result.zone.music)
      }

      // Notifier UIScene
      this.events.emit('zone-changed', this.currentZone)

      // Afficher le nom de la nouvelle zone
      this.scene.launch('DialogScene', {
        text: `📍 ${result.zone.name}`,
        autoClose: 1500,
      })

      await this.fadeIn()

    } catch (err) {
      console.error('[GameScene] Erreur portail:', err)
      this.scene.launch('DialogScene', {
        text: `Impossible d'accéder à ${zoneName}.`,
        autoClose: 2000,
      })
      await this.fadeIn()
    }

    this.isMoving = false
  }

  // ─────────────────────────────────────────────────────────────
  // CAMÉRA
  // ─────────────────────────────────────────────────────────────

  private setupCamera(): void {
    this.cameras.main.setRoundPixels(true) // to avoid blacklines due to pixels chevauchement
    this.cameras.main.setBounds(0, 0, this.map.widthInPixels, this.map.heightInPixels)
    // this.cameras.main.startFollow(this.player, true, 0.12, 0.12)
    // Après — pas de lerp, ou lerp désactivé pour pixel art
    this.cameras.main.startFollow(this.player, true, 1, 1)
    this.cameras.main.setZoom(2)
  }

  private fadeOut(duration = 300): Promise<void> {
    return new Promise((resolve) => {
      this.cameras.main.fadeOut(duration, 0, 0, 0)
      this.cameras.main.once('camerafadeoutcomplete', resolve)
    })
  }

  private fadeIn(duration = 300): Promise<void> {
    return new Promise((resolve) => {
      this.cameras.main.fadeIn(duration, 0, 0, 0)
      this.cameras.main.once('camerafadeincomplete', resolve)
    })
  }

  // ─────────────────────────────────────────────────────────────
  // DEBUG UI
  // ─────────────────────────────────────────────────────────────

  private createDebugUI(): void {
    this.debugText = this.add.text(8, 24, '', {
      fontSize: '9px',
      color: '#ffff00',
      backgroundColor: '#00000088',
      padding: { x: 4, y: 2 },
    }).setScrollFactor(0).setDepth(100)
  }

  private updateDebug(): void {
    const tx = Math.floor(this.player.x / TILE_SIZE)
    const ty = Math.floor(this.player.y / TILE_SIZE)
    this.debugText.setText(
      `Zone: ${this.currentZone?.name ?? '?'}\n` +
      `Pos: (${Math.floor(this.player.x)}, ${Math.floor(this.player.y)})\n` +
      `Tuile: (${tx}, ${ty}) | Dir: ${this.facingDirection}\n` +
      `Herbe: ${this.grassCooldown ? '⏳' : '✅'}`
    )
  }

  // ─────────────────────────────────────────────────────────────
  // APPELÉ PAR BattleScene quand combat terminé
  // ─────────────────────────────────────────────────────────────

  resumeFromBattle(): void {
    this.isMoving = false
    this.scene.resume('GameScene')
    // Délai avant de réarmer — évite une rencontre immédiate au retour du combat
    this.time.delayedCall(2500, () => {
      this.grassCooldown = false
    })
  }
}