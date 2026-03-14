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
// probabilité de déclencher un wild combat
const ENCOUNTER_RATE    = 10   // % de chance par pas (comme dans les vrais jeux : ~10-15%)
const TILE_STEP_PX      = 16   // distance en px = 1 pas (1 tile)

type Direction = 'up' | 'down' | 'left' | 'right'

export class GameScene extends Phaser.Scene {

  private map!: Phaser.Tilemaps.Tilemap
  private collisionLayer!: Phaser.Tilemaps.TilemapLayer
  private bumperLayer?: Phaser.Tilemaps.TilemapLayer
  private player!: Phaser.Physics.Arcade.Sprite

  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys
  private wasd!: Record<Direction, Phaser.Input.Keyboard.Key>

  private facingDirection: Direction = 'down'
  private isMoving = false
  private grassCooldown = false
  private portalCooldown = false  // évite re-déclenchement immédiat après transition

  private grassGroup!: Phaser.Physics.Arcade.StaticGroup
  private portalGroup!: Phaser.Physics.Arcade.StaticGroup

  private debugText!: Phaser.GameObjects.Text

  // Zone courante (chargée depuis le registry au démarrage)
  private currentZone!: ZoneDetailData

  private lastStepX = 0
  private lastStepY = 0

  constructor() {
    super({ key: 'GameScene' })
  }

  // ─────────────────────────────────────────────────────────────
  // HELPERS
  // ─────────────────────────────────────────────────────────────

  /**
   * Convertit un nom de zone Django en clé tilemap Phaser.
   * "Bourg Palette" → "bourg_palette"
   * "Route 1"       → "route_1"
   */
  private zoneNameToKey(name: string): string {
    return name
      .toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '') // supprime accents
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_|_$/g, '')
  }

  /**
   * Charge une tilemap JSON dans le cache Phaser si elle n'y est pas encore.
   */
  private loadMapIfNeeded(key: string): Promise<void> {
    if (this.cache.tilemap.has(key)) return Promise.resolve()
    return new Promise<void>((resolve) => {
      this.load.tilemapTiledJSON(key, `/assets/tilemaps/${key}.json`)
      this.load.once('complete',   resolve)
      this.load.once('loaderror', () => {
        console.warn(`[GameScene] Tilemap introuvable : /assets/tilemaps/${key}.json`)
        resolve()
      })
      this.load.start()
    })
  }

  // ─────────────────────────────────────────────────────────────
  // CREATE
  // ─────────────────────────────────────────────────────────────

  create(): void {
    // Récupérer la zone chargée par BootScene (ou mise à jour par onPortalEnter)
    this.currentZone = this.registry.get('currentZone') as ZoneDetailData
    console.log('[GameScene] create — zone:', this.currentZone.name, 'spawns:', this.currentZone.wild_spawns?.length)
    
    this.buildTilemap()
    this.createPlayer()
    this.setupInput()
    this.setupOverlaps()
    this.setupCamera()
    this.createDebugUI()

    // Fondu d'entrée à chaque (re)démarrage de scène
    this.cameras.main.fadeIn(300, 0, 0, 0)

    // Cooldown portail au démarrage
    this.portalCooldown = true
    this.time.delayedCall(1000, () => { this.portalCooldown = false })

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
    this.checkBumpers()
    this.checkGrassEncounter()
    this.player.setDepth(this.player.y + this.player.height / 2)
    this.updateDebug()
  }

  // ─────────────────────────────────────────────────────────────
  // TILEMAP
  // ─────────────────────────────────────────────────────────────

  private buildTilemap(): void {
    this.bumperLayer = undefined  // reset à chaque chargement de map
    const mapKey = this.zoneNameToKey(this.currentZone.name)
    this.map = this.make.tilemap({ key: mapKey })

    // ── Tilesets toujours présents ─────────────────────────────
    const tsKanto     = this.map.addTilesetImage('full_kanto',    'full_kanto')!
    const tsForever   = this.map.addTilesetImage('style_forever', 'style_forever')!
    const tsCollision = this.map.addTilesetImage('collision',     'collision')!

    // ── Tilesets optionnels — vérifiés avant ajout ─────────────
    const mapTilesetNames = this.map.tilesets.map(ts => ts.name)

    const tsBumper = mapTilesetNames.includes('bumper_down')
      ? this.map.addTilesetImage('bumper_down', 'bumper_down') : null
    const tsLab    = mapTilesetNames.includes('../tilesets/pallet_lab.png')
      ? this.map.addTilesetImage('../tilesets/pallet_lab.png', 'pallet_lab') : null
    const tsHouse1 = mapTilesetNames.includes('../tilesets/pallet_house_green1.png')
      ? this.map.addTilesetImage('../tilesets/pallet_house_green1.png', 'pallet_house_green1') : null
    const tsHouse2 = mapTilesetNames.includes('../tilesets/pallet_house_green2.png')
      ? this.map.addTilesetImage('../tilesets/pallet_house_green2.png', 'pallet_house_green2') : null
    const tsHouse3 = mapTilesetNames.includes('../tilesets/pallet_house_green3.png')
      ? this.map.addTilesetImage('../tilesets/pallet_house_green3.png', 'pallet_house_green3') : null

    const allTilesets = [
      tsKanto, tsForever,
      tsLab, tsHouse1, tsHouse2, tsHouse3,
      tsCollision, tsBumper,
    ].filter(Boolean) as Phaser.Tilemaps.Tileset[]

    // ── Couches de tuiles — ordre = ordre de rendu ─────────────
    this.map.createLayer('Ground',      allTilesets, 0, 0)
    this.map.createLayer('Bumpers',     allTilesets, 0, 0)   // visuel falaises
    this.map.createLayer('Decoration',  allTilesets, 0, 0)
    this.map.createLayer('Decoration2', allTilesets, 0, 0)
    this.map.createLayer('Grass',       allTilesets, 0, 0)
    this.map.createLayer('Trees',       allTilesets, 0, 0)

    // Collision
    this.collisionLayer = this.map.createLayer('Collision', allTilesets, 0, 0)!
    this.collisionLayer.setCollisionByProperty({ collides: true })
    this.collisionLayer.setAlpha(0)

    // Bumpers logique (invisible — sens unique vers le bas)
    const bumperLogicLayer = this.map.createLayer('Bumpers_Logic', allTilesets, 0, 0)
    if (bumperLogicLayer) {
      this.bumperLayer = bumperLogicLayer
      this.bumperLayer.setAlpha(0)
    }

    this.physics.world.setBounds(0, 0, this.map.widthInPixels, this.map.heightInPixels)

    // ── Bâtiments (object layer) ───────────────────────────────
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
      const zoneName = (obj.properties as Array<{name: string; value: unknown}>)
        ?.find(p => p.name === 'zone_name')?.value as string
      rect.setData('zoneName', zoneName)
      this.portalGroup.add(rect)
    })
  }

  // ─────────────────────────────────────────────────────────────
  // JOUEUR
  // ─────────────────────────────────────────────────────────────

  private findSpawnPoint(): { x: number; y: number } {
    const previousZoneName = this.registry.get('previousZoneName') as string | undefined

    // Essaie d'abord un spawn directionnel basé sur la zone précédente :  from_zone_name, exemple from_bourg_palette
    if (previousZoneName) {
      const key = this.zoneNameToKey(previousZoneName)
      const directional = this.map.findObject('Spawns', obj =>
        obj.name === `from_${key}` ||
        obj.name === `from${key}`
      ) as { x: number; y: number } | undefined
      if (directional) return directional
    }

    // Spawn par défaut — cherche 'Player' ou 'PlayerSpawn'
    const defaultSpawn = this.map.findObject('Spawns', obj =>
      obj.name === 'Player' || obj.name === 'PlayerSpawn'
    ) as { x: number; y: number } | undefined

    if (defaultSpawn) return defaultSpawn

    // Fallback : centre de la map
    return { x: this.map.widthInPixels / 2, y: this.map.heightInPixels / 2 }
  }

  private createPlayer(): void {
    const spawn = this.findSpawnPoint()

    this.player = this.physics.add.sprite(spawn.x, spawn.y, 'player', 0)
    this.player.setCollideWorldBounds(true)
    this.player.body!.setSize(12, 10)
    this.player.body!.setOffset(4, 22)

    this.physics.add.collider(this.player, this.collisionLayer)
    this.player.anims.play('idle-down')

    this.lastStepX = spawn.x
    this.lastStepY = spawn.y
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
  // BUMPERS — sens unique vers le bas
  // ─────────────────────────────────────────────────────────────

  private checkBumpers(): void {
    if (!this.bumperLayer) return

    const tile = this.bumperLayer.getTileAtWorldXY(
      this.player.x,
      this.player.y + 4  // légèrement sous le centre pour les pieds
    )

    if (tile?.properties?.bumper_down) {
      const body = this.player.body as Phaser.Physics.Arcade.Body
      if (body.velocity.y < 0) this.player.setVelocityY(0)
      if (body.velocity.x !== 0) this.player.setVelocityX(0)
    }
  }

  // ─────────────────────────────────────────────────────────────
  // OVERLAPS
  // ─────────────────────────────────────────────────────────────

  private setupOverlaps(): void {
    this.physics.add.overlap(this.player, this.grassGroup)

    this.physics.add.overlap(
      this.player,
      this.portalGroup,
      (_p, portal) => {
        if (this.portalCooldown) return
        const rect = portal as Phaser.GameObjects.Rectangle
        void this.onPortalEnter(rect.getData('zoneName') as string)
      }
    )
  }

  // ─────────────────────────────────────────────────────────────
  // Probabilité de RENCONTRE SAUVAGE → TYpeScript
  // ─────────────────────────────────────────────────────────────

  private checkGrassEncounter(): void {
    if (this.grassCooldown || this.isMoving) return

    // Calculer la distance parcourue depuis le dernier pas
    const dx = Math.abs(this.player.x - this.lastStepX)
    const dy = Math.abs(this.player.y - this.lastStepY)

    // Un "pas" = 1 tile traversée
    if (dx + dy < TILE_STEP_PX) return

    // Mettre à jour la position du dernier pas
    this.lastStepX = this.player.x
    this.lastStepY = this.player.y

    // Vérifier si le joueur est sur une herbe haute
    const grassLayer = this.map.getLayer('Grass')
    if (!grassLayer) return

    const tile = this.map.getTileAtWorldXY(
      this.player.x,
      this.player.y,
      false,
      undefined,
      'Grass'
    )
    if (!tile || tile.index <= 0) return

    // Lancer le dé — ~10% par pas
    if (Math.random() * 100 < ENCOUNTER_RATE) {
      void this.onGrassEncounter()
    }
  }

  // ─────────────────────────────────────────────────────────────
  // RENCONTRE SAUVAGE → Django
  // ─────────────────────────────────────────────────────────────

  private async onGrassEncounter(): Promise<void> {
    this.grassCooldown = true
    this.cameras.main.flash(200, 255, 255, 255)

    try {
      const result = await mapApi.wildEncounter(this.currentZone.id)
      console.log(`[GameScene] Combat créé — battle_id: ${result.battle_id}`)
      this.scene.pause('GameScene')
      this.scene.launch('BattleScene', { battleId: result.battle_id })
    } catch (err) {
      console.error('[GameScene] Erreur rencontre:', err)
      this.scene.launch('DialogScene', {
        text: `Aucun Pokémon dans cette zone.`,
        autoClose: 1500,
      })
    }
  }

  // ─────────────────────────────────────────────────────────────
  // TRANSITION DE ZONE → Django
  // ─────────────────────────────────────────────────────────────

  private async onPortalEnter(zoneName: string): Promise<void> {
    if (this.isMoving || !zoneName) return
    this.isMoving = true

    await this.fadeOut()

    try {
      const result = await mapApi.travelToByName(zoneName)

      if (!result.success || !result.zone) {
        this.scene.launch('DialogScene', {
          text: result.message ?? `Impossible d'accéder à ${zoneName}.`,
          autoClose: 2500,
        })
        await this.fadeIn()
        this.isMoving = false
        return
      }

      // Mémoriser la zone de provenance pour le spawn directionnel
      this.registry.set('previousZoneName', this.currentZone.name)

      // Mettre à jour le registry
      this.registry.set('currentZone',     result.zone)
      this.registry.set('currentZoneId',   result.zone.id)
      this.registry.set('currentZoneName', result.zone.name)

      console.log(`[GameScene] Arrivée : ${result.zone.name} (id: ${result.zone.id})`)

      // Charger la tilemap si nécessaire
      const mapKey = this.zoneNameToKey(result.zone.name)
      await this.loadMapIfNeeded(mapKey)

      // Reconstruire en place — sans scene.restart() qui relance BootScene
      await this.rebuildForZone(result.zone)

    } catch (err) {
      console.error('[GameScene] Erreur portail:', err)
      this.scene.launch('DialogScene', {
        text: `Impossible d'accéder à ${zoneName}.`,
        autoClose: 2000,
      })
      await this.fadeIn()
      this.isMoving = false
    }
  }

  // ─────────────────────────────────────────────────────────────
  // RECONSTRUCTION EN PLACE (sans scene.restart)
  // ─────────────────────────────────────────────────────────────

  private async rebuildForZone(zone: ZoneDetailData): Promise<void> {
    this.currentZone = zone

    // Stopper proprement la BGM via AudioManager
    // (pas sound.stopAll qui laisse bgmCurrent invalide → crash "currentConfig is null")
    AudioManager.instance?.stopBgm()
    AudioManager.instance?.stopAllSfx()

    // Lancer la musique de la nouvelle zone immédiatement après le stop
    if (zone.music) {
      AudioManager.instance?.playZone(zone.music)
    }

    // Détruire tous les game objects sauf joueur et debugText
    this.children.list
      .filter(obj => obj !== this.player && obj !== this.debugText)
      .forEach(obj => obj.destroy())

    // Détruire groupes physics
    this.grassGroup?.destroy(true)
    this.portalGroup?.destroy(true)

    // Détruire l'ancienne map
    this.map?.destroy()

    // Vider les colliders/overlaps
    this.physics.world.colliders.destroy()

    // Reconstruire tilemap + groupes
    this.buildTilemap()

    // Repositionner le joueur
    const spawn = this.findSpawnPoint()
    this.player.setPosition(spawn.x, spawn.y)
    this.player.setVelocity(0, 0)

    // Recréer collider joueur ↔ collision
    this.physics.add.collider(this.player, this.collisionLayer)

    // Recréer overlaps
    this.setupOverlaps()

    // Mettre à jour caméra
    this.cameras.main.setBounds(0, 0, this.map.widthInPixels, this.map.heightInPixels)
    this.cameras.main.startFollow(this.player, true, 1, 1)

    // Notifier UIScene
    this.events.emit('zone-entered', zone)

    // Fondu d'entrée
    this.cameras.main.fadeIn(300, 0, 0, 0)

    // Cooldown portail — évite re-déclenchement immédiat après transition
    this.portalCooldown = true
    this.time.delayedCall(1000, () => { this.portalCooldown = false })

    this.isMoving = false
  }

  // ─────────────────────────────────────────────────────────────
  // CAMÉRA
  // ─────────────────────────────────────────────────────────────

  private setupCamera(): void {
    this.cameras.main.setRoundPixels(true)
    this.cameras.main.setBounds(0, 0, this.map.widthInPixels, this.map.heightInPixels)
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
    this.time.delayedCall(2500, () => {
      this.grassCooldown = false
    })
  }
}