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

const SFX_GRASS     = 'SFX_TALL_GRASS'
const SFX_BUMPER    = 'SFX_LEDGE'
const SFX_COLLISION = 'SFX_COLLISION'

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
  private lastPlayerY = 0
  private grassStepCooldown = false
  private collisionSoundCooldown = false
  private bumperActive = false

  private itemGroup!:   Phaser.Physics.Arcade.StaticGroup
  private npcGroup!:    Phaser.Physics.Arcade.StaticGroup
  private trainerGroup!: Phaser.Physics.Arcade.StaticGroup

  private interactKey!: Phaser.Input.Keyboard.Key
  private npcInRange:   Phaser.GameObjects.GameObject | null = null
  private interactCooldown = false

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

  private playSfx(name: string): void {
    AudioManager.instance?.playSfx('ui', name)
  }

  // ─────────────────────────────────────────────────────────────
  // CREATE
  // ─────────────────────────────────────────────────────────────

  async create(): Promise<void> {
    // Récupérer la zone chargée par BootScene (ou mise à jour par onPortalEnter)
    this.currentZone = this.registry.get('currentZone') as ZoneDetailData
    console.log('[GameScene] create — zone:', this.currentZone.name, 'spawns:', this.currentZone.wild_spawns?.length)
    
    this.buildTilemap()
    await this.hidePickedItems()
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
    // Guard — create() est async, on attend qu'il soit terminé
    if (!this.cursors || !this.player) return

    this.npcInRange = null  // reset chaque frame — rempli par l'overlap si toujours proche
    this.handleMovement()
    this.checkBumpers()
    this.checkGrassEncounter()
    this.checkCollisionSound()
    this.checkTrainerLineOfSight()
    this.player.setDepth(this.player.y + this.player.height / 2)
    this.updateDebug()
    this.lastPlayerY = this.player.y

    // Touche interaction
    if (Phaser.Input.Keyboard.JustDown(this.interactKey)) {
      void this.tryInteract()
    }
  }

  // ─────────────────────────────────────────────────────────────
  // TILEMAP
  // ─────────────────────────────────────────────────────────────

  private buildTilemap(): void {
    this.bumperLayer = undefined
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
    const tsPokeballsPickup = mapTilesetNames.includes('../tilesets/pokeballs_pickup.png')
      ? this.map.addTilesetImage('../tilesets/pokeballs_pickup.png', 'pokeballs_pickup') : null


    const allTilesets = [
      tsKanto, tsForever,
      tsLab, tsHouse1, tsHouse2, tsHouse3, tsPokeballsPickup,
      tsCollision, tsBumper,
    ].filter(Boolean) as Phaser.Tilemaps.Tileset[]

    // ── Couches de tuiles — ordre de rendu ─────────────────────
    this.map.createLayer('Ground',       allTilesets, 0, 0)
    this.map.createLayer('Bumpers',      allTilesets, 0, 0)  // visuel falaises
    this.map.createLayer('Decoration',   allTilesets, 0, 0)
    this.map.createLayer('Decoration2',  allTilesets, 0, 0)
    this.map.createLayer('Grass',        allTilesets, 0, 0)
    this.map.createLayer('Trees',        allTilesets, 0, 0)
    if (this.map.getLayer('Trees2')) {
      this.map.createLayer('Trees2', allTilesets, 0, 0)
    }

    // ── Collision ──────────────────────────────────────────────
    this.collisionLayer = this.map.createLayer('Collision', allTilesets, 0, 0)!
    this.collisionLayer.setCollisionByProperty({ collides: true })
    this.collisionLayer.setAlpha(import.meta.env.DEV ? 0.25 : 0) // visible à 25% en mode DEV pour faciliter le debug

    // ── Bumpers logique (invisible — sens unique vers le bas) ──
    const bumperLogicLayer = this.map.createLayer('Bumpers_Logic', allTilesets, 0, 0)
    if (bumperLogicLayer) {
      this.bumperLayer = bumperLogicLayer
      this.bumperLayer.setAlpha(0)
    }

    this.physics.world.setBounds(0, 0, this.map.widthInPixels, this.map.heightInPixels)

    // ── Bâtiments (object layer — image collection tilesets) ───
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
      this.add.image(obj.x!, obj.y!, textureKey)
        .setOrigin(0, 1)
        .setDepth(obj.y! - 32)
    })

    // ── Herbes haute (Grass → physics group) ───────────────────
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

    // ── Portails ───────────────────────────────────────────────
    this.portalGroup = this.physics.add.staticGroup()
    const portalLayer = this.map.getObjectLayer('Portals')
    portalLayer?.objects.forEach((obj) => {
      const rect = this.add.rectangle(
        obj.x! + obj.width!  / 2,
        obj.y! + obj.height! / 2,
        obj.width!, obj.height!,
        0xffff00, import.meta.env.DEV ? 0.2 : 0 // légèrement visibles en DEV (0.2 alpha) — invisible en prod
      )
      this.physics.add.existing(rect, true)
      const zoneName = (obj.properties as Array<{name: string; value: unknown}>)
        ?.find(p => p.name === 'zone_name')?.value as string
      rect.setData('zoneName', zoneName)
      this.portalGroup.add(rect)
    })

    // ── Items au sol ────────────────────────────────────────────
    this.itemGroup = this.physics.add.staticGroup()
    const itemsLayer = this.map.getObjectLayer('Items')

    // firstgid du tileset pokeballs_pickup — lu dynamiquement depuis la map
    const pokeballsFirstGid = this.map.tilesets.find(ts => ts.name === 'pokeballs_pickup')?.firstgid ?? 9749

    itemsLayer?.objects.forEach((obj) => {
      const props    = obj.properties as Array<{name: string; value: unknown}> ?? []
      const itemName = props.find(p => p.name === 'item_name')?.value as string
      const quantity = (props.find(p => p.name === 'quantity')?.value as number) ?? 1
      const itemId   = (props.find(p => p.name === 'item_id')?.value as number) ?? null

      // Calculer le frame depuis le GID (gid - firstgid = index dans le spritesheet)
      const frame = obj.gid ? obj.gid - pokeballsFirstGid : 0

      // obj.y pointe vers le bas de l'objet dans Tiled — on remonte de 8px pour centrer
      const sprite = this.add.sprite(obj.x! + 8, obj.y! - 8, 'pokeballs_pickup', frame)
        .setDepth(obj.y!)
        .setScale(0.5)  // 32px → 16px pour correspondre à la grille 16px
      this.physics.add.existing(sprite, true)
      sprite.setData('itemName', itemName)
      sprite.setData('quantity', quantity)
      sprite.setData('itemId',   itemId)
      sprite.setData('objId',    obj.id)
      this.itemGroup.add(sprite)

      // Bob vertical pour attirer l'attention
      this.tweens.add({
        targets: sprite,
        y: obj.y! - 11,
        duration: 800,
        ease: 'Sine.easeInOut',
        yoyo: true,
        repeat: -1,
      })
    })

    // ── NPCs ────────────────────────────────────────────────────
    this.npcGroup = this.physics.add.staticGroup()
    const npcsLayer = this.map.getObjectLayer('NPCs')
    npcsLayer?.objects.forEach((obj) => {
      const props   = obj.properties as Array<{name: string; value: unknown}> ?? []
      const npcCode = props.find(p => p.name === 'npc_code')?.value  as string
      const npcName = props.find(p => p.name === 'npc_name')?.value  as string
      const dialog  = props.find(p => p.name === 'dialog')?.value    as string

      const sprite = this.add.sprite(obj.x!, obj.y!, 'player')
        .setDepth(obj.y!)
      this.physics.add.existing(sprite, true)
      sprite.setData('npcCode', npcCode)
      sprite.setData('npcName', npcName)
      sprite.setData('dialog',  dialog)
      this.npcGroup.add(sprite)
    })

    // ── Dresseurs ───────────────────────────────────────────────
    this.trainerGroup = this.physics.add.staticGroup()
    const trainersLayer = this.map.getObjectLayer('Trainers')
    trainersLayer?.objects.forEach((obj) => {
      const props      = obj.properties as Array<{name: string; value: unknown}> ?? []
      const npcCode    = props.find(p => p.name === 'npc_code')?.value    as string
      const direction  = (props.find(p => p.name === 'direction')?.value  as string) ?? 'down'
      const sightRange = (props.find(p => p.name === 'sight_range')?.value as number) ?? 3

      const sprite = this.add.sprite(obj.x!, obj.y!, 'player')
        .setDepth(obj.y!)
        .setTint(0xff8800)
      this.physics.add.existing(sprite, true)
      sprite.setData('npcCode',    npcCode)
      sprite.setData('direction',  direction)
      sprite.setData('sightRange', sightRange)
      sprite.setData('defeated',   false)
      this.trainerGroup.add(sprite)
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
        obj.name === `from_${key}` || obj.name === `from${key}`
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
      up:    this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.Z),
      down:  this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.S),
      left:  this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.Q),
      right: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.D),
    }

    // Touche interaction : A (AZERTY) ou clic gauche
    this.interactKey = this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.A)
    this.input.on('pointerdown', (p: Phaser.Input.Pointer) => {
      if (p.leftButtonDown()) void this.tryInteract()
    })
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
  // BUMPERS — sens unique vers le bas + SFX_LEDGE
  // ─────────────────────────────────────────────────────────────

  private checkBumpers(): void {
    if (!this.bumperLayer) return

    const tile = this.bumperLayer.getTileAtWorldXY(
      this.player.x,
      this.player.y + 4
    )

    if (tile?.properties?.bumper_down) {
      const body = this.player.body as Phaser.Physics.Arcade.Body

      // Son uniquement si le joueur vient d'entrer sur le bumper depuis le haut
      // = était au-dessus du bumper la frame précédente (lastPlayerY < tile.pixelY)
      const tileTopY = tile.pixelY
      const wasAbove = this.lastPlayerY + 4 < tileTopY
      
      if (!this.bumperActive && wasAbove && body.velocity.y > 0) {
        this.bumperActive = true
        this.playSfx(SFX_BUMPER)
      }

      if (body.velocity.y < 0) this.player.setVelocityY(0)
      if (body.velocity.x !== 0) this.player.setVelocityX(0)

    } else {
      this.bumperActive = false
    }
  }



  // ─────────────────────────────────────────────────────────────
  // SON COLLISION MUR — SFX_COLLISION
  // ─────────────────────────────────────────────────────────────

  private checkCollisionSound(): void {
    if (this.collisionSoundCooldown) return

    const body = this.player.body as Phaser.Physics.Arcade.Body

    const pressingUp    = this.cursors.up.isDown    || this.wasd.up.isDown
    const pressingDown  = this.cursors.down.isDown  || this.wasd.down.isDown
    const pressingLeft  = this.cursors.left.isDown  || this.wasd.left.isDown
    const pressingRight = this.cursors.right.isDown || this.wasd.right.isDown

    // Vérifier si le joueur pousse contre un mur dans la direction où il appuie
    const blocked =
      (pressingUp    && body.blocked.up)    ||
      (pressingDown  && body.blocked.down)  ||
      (pressingLeft  && body.blocked.left)  ||
      (pressingRight && body.blocked.right)

    if (blocked) {
      this.playSfx(SFX_COLLISION)
      this.collisionSoundCooldown = true
      this.time.delayedCall(400, () => { this.collisionSoundCooldown = false })
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

    // NPCs — détecter la proximité pour afficher indicateur interaction
    this.physics.add.overlap(
      this.player,
      this.npcGroup,
      (_p, npc) => {
        this.npcInRange = npc as Phaser.GameObjects.GameObject
      }
    )

  }

  // ─────────────────────────────────────────────────────────────
  // RENCONTRE SAUVAGE — par pas + SFX_RUN dans l'herbe
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

    // Son de pas dans l'herbe (1 fois tous les 2 pas)
    if (!this.grassStepCooldown) {
      this.playSfx(SFX_GRASS)
      this.grassStepCooldown = true
      this.time.delayedCall(300, () => { this.grassStepCooldown = false })
    }

    // Lancer le dé — ~10% par pas
    if (Math.random() * 100 < ENCOUNTER_RATE) {
      void this.onGrassEncounter()
    }
  }

  // ─────────────────────────────────────────────────────────────
  // INTERACTION (touche A / clic gauche)
  // ─────────────────────────────────────────────────────────────

  private async tryInteract(): Promise<void> {
    if (this.interactCooldown || this.isMoving) return

    if (this.scene.isActive('DialogScene')) {
      this.scene.stop('DialogScene')
      return
    }

    const REACH = 28

    // ── Chercher un item proche ────────────────────────────────
    let closestItem: Phaser.GameObjects.Sprite | null = null
    let closestItemDist = REACH

    this.itemGroup.getChildren().forEach((obj) => {
      const item = obj as Phaser.GameObjects.Sprite
      if (!item.active) return
      const dist = Phaser.Math.Distance.Between(this.player.x, this.player.y, item.x, item.y)
      if (dist < closestItemDist) {
        closestItemDist = dist
        closestItem = item
      }
    })

    if (closestItem) {
      void this.onItemPickup(closestItem)
      return
    }

    // ── Chercher un NPC proche ─────────────────────────────────
    if (this.npcInRange) {
      const npc = this.npcInRange
      this.npcInRange = null
      void this.onNpcDialog(npc as Phaser.GameObjects.Sprite)
      return
    }

    let closestNpc: Phaser.GameObjects.Sprite | null = null
    let closestNpcDist = REACH

    this.npcGroup.getChildren().forEach((obj) => {
      const npc = obj as Phaser.GameObjects.Sprite
      const dist = Phaser.Math.Distance.Between(this.player.x, this.player.y, npc.x, npc.y)
      if (dist < closestNpcDist) {
        closestNpcDist = dist
        closestNpc = npc
      }
    })

    if (closestNpc) {
      void this.onNpcDialog(closestNpc)
    }
  }

  // ─────────────────────────────────────────────────────────────
  // ITEMS DÉJÀ RAMASSÉS — masquer au chargement
  // ─────────────────────────────────────────────────────────────

  private async hidePickedItems(): Promise<void> {
    try {
      const { picked_tiled_obj_ids } = await mapApi.getPickedItems(this.currentZone.id)
      if (!picked_tiled_obj_ids?.length) return

      const pickedSet = new Set<number>(picked_tiled_obj_ids)

      this.itemGroup.getChildren().forEach((obj) => {
        const sprite = obj as Phaser.GameObjects.Sprite
        const objId  = sprite.getData('objId') as number
        if (pickedSet.has(objId)) {
          // Masquer + retirer collision
          sprite.setActive(false).setVisible(false)
          this.tweens.killTweensOf(sprite)
          this.itemGroup.remove(sprite, false, false)
          const tileX = sprite.getData('tileX') as number
          const tileY = sprite.getData('tileY') as number
          if (this.collisionLayer && tileX !== undefined && tileY !== undefined) {
            this.collisionLayer.removeTileAt(tileX, tileY)
          }
        }
      })

      console.log(`[Items] ${pickedSet.size} item(s) déjà ramassés masqués`)
    } catch (err) {
      console.warn('[Items] Impossible de charger les items ramassés:', err)
    }
  }

  // ─────────────────────────────────────────────────────────────
  // RAMASSAGE ITEM
  // ─────────────────────────────────────────────────────────────

  private async onItemPickup(item: Phaser.GameObjects.Sprite): Promise<void> {
    if (!item.active) return

    // ⚠️  Lire les data AVANT de détruire le sprite
    const itemName = item.getData('itemName') as string
    const quantity = item.getData('quantity') as number
    const objId    = item.getData('objId')    as number
    const tileX    = item.getData('tileX')    as number
    const tileY    = item.getData('tileY')    as number

    console.log(`[Pickup] itemName=${itemName} objId=${objId} zone=${this.currentZone.id}`)

    // Détruire le sprite
    item.setActive(false).setVisible(false)
    this.tweens.killTweensOf(item)
    this.itemGroup.remove(item, true, true)

    // Retirer la tile de collision à cet emplacement
    if (this.collisionLayer && tileX !== undefined && tileY !== undefined) {
      this.collisionLayer.removeTileAt(tileX, tileY)
    }

    // Flash + son
    this.cameras.main.flash(120, 255, 255, 200)
    AudioManager.instance?.playSfx('ui', 'SFX_GET_ITEM_1')

    // Afficher message
    this.scene.launch('DialogScene', {
      text: `Vous avez obtenu\n${itemName ?? '?'} ×${quantity} !`,
      autoClose: 1800,
    })

    // Appel Django
    try {
      await mapApi.pickupItem(this.currentZone.id, objId)
      console.log(`[Pickup] OK — zone=${this.currentZone.id} tiled_obj_id=${objId}`)
    } catch (err) {
      console.error('[Pickup] Erreur API:', err)
    }
  }

  // ─────────────────────────────────────────────────────────────
  // DIALOGUE NPC
  // ─────────────────────────────────────────────────────────────

  private async onNpcDialog(npc: Phaser.GameObjects.Sprite): Promise<void> {
    if (this.interactCooldown) return
    this.interactCooldown = true

    const npcCode = npc.getData('npcCode') as string | undefined

    if (npcCode) {
      // Charger le dialogue depuis Django
      try {
        const result = await mapApi.getNpcDialog(npcCode)
        this.scene.launch('DialogScene', {
          text: `${result.name}:\n${result.dialog}`,
          autoClose: 0,  // attendre input joueur
        })
      } catch (err) {
        console.error('[GameScene] Erreur dialogue NPC:', err)
      }
    } else {
      // Fallback — dialog hardcodé dans Tiled
      const dialog = npc.getData('dialog') as string
      const npcName = npc.getData('npcName') as string
      if (dialog) {
        this.scene.launch('DialogScene', {
          text: npcName ? `${npcName}:\n${dialog}` : dialog,
          autoClose: 0,
        })
      }
    }

    this.time.delayedCall(500, () => { this.interactCooldown = false })
  }

  // ─────────────────────────────────────────────────────────────
  // LINE OF SIGHT — Dresseurs adverses
  // ─────────────────────────────────────────────────────────────

  private trainerAggroCooldown = false

  private checkTrainerLineOfSight(): void {
    if (this.trainerAggroCooldown || this.isMoving || this.grassCooldown) return

    this.trainerGroup.getChildren().forEach((obj) => {
      const trainer = obj as Phaser.GameObjects.Sprite
      if (!trainer.active || trainer.getData('defeated')) return

      const direction  = trainer.getData('direction')  as string ?? 'down'
      const sightRange = (trainer.getData('sightRange') as number ?? 3) * TILE_SIZE

      // Calculer la zone de vision selon la direction du dresseur
      let inSight = false

      const dx = this.player.x - trainer.x
      const dy = this.player.y - trainer.y
      const dist = Math.sqrt(dx * dx + dy * dy)

      if (dist > sightRange) return

      // Vérifier alignement axial selon la direction
      const TOLERANCE = TILE_SIZE * 0.8  // tolérance latérale d'1 tile

      switch (direction) {
        case 'down':
          inSight = dy > 0 && Math.abs(dx) < TOLERANCE
          break
        case 'up':
          inSight = dy < 0 && Math.abs(dx) < TOLERANCE
          break
        case 'left':
          inSight = dx < 0 && Math.abs(dy) < TOLERANCE
          break
        case 'right':
          inSight = dx > 0 && Math.abs(dy) < TOLERANCE
          break
      }

      if (inSight) {
        void this.onTrainerAggro(trainer)
      }
    })
  }

  private async onTrainerAggro(trainer: Phaser.GameObjects.Sprite): Promise<void> {
    if (this.trainerAggroCooldown) return
    this.trainerAggroCooldown = true
    this.isMoving = true

    const npcCode = trainer.getData('npcCode') as string

    // Exclamation mark au-dessus du dresseur
    const excl = this.add.text(trainer.x, trainer.y - 20, '!', {
      fontSize: '16px', color: '#ff0000',
      fontFamily: '"Press Start 2P"',
    }).setDepth(999).setOrigin(0.5)

    AudioManager.instance?.playSfx('ui', 'SFX_MEET_01')

    await new Promise<void>(r => this.time.delayedCall(800, r))
    excl.destroy()

    await this.fadeOut()

    try {
      const result = await mapApi.trainerBattle(npcCode)
      if (!result.success) {
        this.scene.launch('DialogScene', { text: result.message ?? 'Combat impossible.', autoClose: 2000 })
        await this.fadeIn()
        this.isMoving = false
        this.trainerAggroCooldown = false
        return
      }

      // Afficher intro_text du dresseur si présent
      if (result.intro_text) {
        await this.fadeIn()
        this.scene.launch('DialogScene', { text: result.intro_text, autoClose: 0 })
        // Attendre que le DialogScene soit fermé
        await new Promise<void>(resolve => {
          const check = setInterval(() => {
            if (!this.scene.isActive('DialogScene')) {
              clearInterval(check)
              resolve()
            }
          }, 100)
        })
        await this.fadeOut()
      }

      // Snapshot avant combat
      await new Promise<void>((resolve) => {
        this.game.renderer.snapshot((image: HTMLImageElement | Phaser.Display.Color) => {
          if (image instanceof HTMLImageElement) this.registry.set('overworldSnapshot', image.src)
          resolve()
        })
      })

      this.scene.pause('GameScene')
      this.scene.launch('BattleScene', { battleId: result.battle_id })

    } catch (err) {
      console.error('[GameScene] Erreur aggro dresseur:', err)
      await this.fadeIn()
      this.isMoving = false
      this.trainerAggroCooldown = false
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
    this.itemGroup?.destroy(true)
    this.npcGroup?.destroy(true)
    this.trainerGroup?.destroy(true)

    // Détruire l'ancienne map
    this.map?.destroy()

    // Vider les colliders/overlaps
    this.physics.world.colliders.destroy()

    // Reconstruire tilemap + groupes
    this.buildTilemap()
    await this.hidePickedItems()

    // Repositionner le joueur
    const spawn = this.findSpawnPoint()
    this.player.setPosition(spawn.x, spawn.y)
    this.player.setVelocity(0, 0)
    this.lastStepX = spawn.x
    this.lastStepY = spawn.y

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