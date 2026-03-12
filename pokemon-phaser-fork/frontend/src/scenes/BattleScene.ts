// ============================================================
// scenes/BattleScene.ts
// Style legacy Django — background zone, 4 boutons principaux,
// vrais sprites gen5, barres HP, log séquentiel.
// ============================================================

import Phaser from 'phaser'
import { battleApi } from '@api/djangoClient'
import { AudioManager } from './AudioManager'
import { BattleAnimator } from './BattleAnimator'
import type { BattleType } from './AudioManager'
import type { BattleItem } from '@api/djangoClient'
import { emit } from '@utils/EventBus'
import type { BattleResponse, PokemonData, MoveData } from '@/types'

interface BattleSceneData {
  battleId: number
}

interface PendingEvolution {
  evolution_id:    number
  pokemon_id:      number
  from_name:       string
  from_species_id: number
  to_name:         string
  to_species_id:   number
  is_shiny:        boolean
  stats_before:    Record<string, number>
}

// ── Couleurs types → teinte bouton move ───────────────────────
const TYPE_COLORS: Record<string, number> = {
  normal:   0xa8a878, fire:     0xf08030, water:    0x6890f0,
  grass:    0x78c850, electric: 0xf8d030, ice:      0x98d8d8,
  fighting: 0xc03028, poison:   0xa040a0, ground:   0xe0c068,
  flying:   0xa890f0, psychic:  0xf85888, bug:      0xa8b820,
  rock:     0xb8a038, ghost:    0x705898, dragon:   0x7038f8,
  dark:     0x705848, steel:    0xb8b8d0,
}

// ── Table d'efficacité des types (Gen 2+) ────────────────────
// TYPE_CHART[moveType][defenderType] = multiplicateur
const TYPE_CHART: Record<string, Record<string, number>> = {
  normal:   { rock: 0.5, ghost: 0, steel: 0.5 },
  fire:     { fire: 0.5, water: 0.5, grass: 2, ice: 2, bug: 2, rock: 0.5, dragon: 0.5, steel: 2 },
  water:    { fire: 2, water: 0.5, grass: 0.5, ground: 2, rock: 2, dragon: 0.5 },
  electric: { water: 2, electric: 0.5, grass: 0.5, ground: 0, flying: 2, dragon: 0.5 },
  grass:    { fire: 0.5, water: 2, grass: 0.5, poison: 0.5, ground: 2, flying: 0.5, bug: 0.5, rock: 2, dragon: 0.5, steel: 0.5 },
  ice:      { water: 0.5, grass: 2, ice: 0.5, ground: 2, flying: 2, dragon: 2, steel: 0.5 },
  fighting: { normal: 2, ice: 2, poison: 0.5, flying: 0.5, psychic: 0.5, bug: 0.5, rock: 2, ghost: 0, dark: 2, steel: 2 },
  poison:   { grass: 2, poison: 0.5, ground: 0.5, rock: 0.5, ghost: 0.5, steel: 0 },
  ground:   { fire: 2, electric: 2, grass: 0.5, poison: 2, flying: 0, bug: 0.5, rock: 2, steel: 2 },
  flying:   { electric: 0.5, grass: 2, fighting: 2, bug: 2, rock: 0.5, steel: 0.5 },
  psychic:  { fighting: 2, poison: 2, psychic: 0.5, dark: 0, steel: 0.5 },
  bug:      { fire: 0.5, grass: 2, fighting: 0.5, flying: 0.5, psychic: 2, ghost: 0.5, dark: 2, steel: 0.5 },
  rock:     { fire: 2, ice: 2, fighting: 0.5, ground: 0.5, flying: 2, bug: 2, steel: 0.5 },
  ghost:    { normal: 0, psychic: 2, ghost: 2, dark: 0.5 },
  dragon:   { dragon: 2, steel: 0.5 },
  dark:     { fighting: 0.5, psychic: 2, ghost: 2, dark: 0.5, steel: 0.5 },
  steel:    { fire: 0.5, water: 0.5, electric: 0.5, ice: 2, rock: 2, steel: 0.5 },
}

/** Calcule le multiplicateur d'efficacité d'un move contre des types défenseurs */
function getTypeEffectiveness(moveType: string, defenderTypes: string[]): number {
  const chart = TYPE_CHART[moveType.toLowerCase()] ?? {}
  return defenderTypes.reduce((mult, dt) => mult * (chart[dt.toLowerCase()] ?? 1), 1)
}

// ── Mapping zone_type → background Django ────────────────────
const ZONE_BG: Record<string, string> = {
  forest:   'bg-forest',
  cave:     'bg-dampcave',
  water:    'bg-river',
  route:    'bg-route',
  city:     'bg-city',
  building: 'bg-city',
}

export class BattleScene extends Phaser.Scene {

  private battleId!: number
  private state!: BattleResponse

  // ── Sprites Pokémon ──────────────────────────────────────────
  private opponentSprite!: Phaser.GameObjects.Image
  private playerSprite!:   Phaser.GameObjects.Image

  // ── UI info-bars ─────────────────────────────────────────────
  private opponentHpBar!:    Phaser.GameObjects.Graphics
  private playerHpBar!:      Phaser.GameObjects.Graphics
  private playerExpBar!:     Phaser.GameObjects.Graphics
  private opponentNameText!: Phaser.GameObjects.Text
  private playerNameText!:   Phaser.GameObjects.Text
  private opponentHpText!:   Phaser.GameObjects.Text
  private playerHpText!:     Phaser.GameObjects.Text
  private opponentGenderText!: Phaser.GameObjects.Text
  private playerGenderText!:   Phaser.GameObjects.Text
  private opponentStatusBadge!: Phaser.GameObjects.Container
  private playerStatusBadge!:   Phaser.GameObjects.Container
  private opponentStatBadges:  Phaser.GameObjects.Container[] = []
  private playerStatBadges:    Phaser.GameObjects.Container[] = []

  // ── UI bas ───────────────────────────────────────────────────
  private logContainer!:   Phaser.GameObjects.Container
  private logMask!:        Phaser.Display.Masks.GeometryMask
  private logHistory:      string[] = []
  private logTextObjects:  Phaser.GameObjects.Text[] = []
  private logScrollBtnUp!:   Phaser.GameObjects.Text
  private logScrollBtnDown!: Phaser.GameObjects.Text
  private actionPanel!:   Phaser.GameObjects.Container
  private movesPanel!:    Phaser.GameObjects.Container
  private bagPanel!:      Phaser.GameObjects.Container
  private switchPanel!:   Phaser.GameObjects.Container
  private moveTooltip!:   Phaser.GameObjects.Container
  private moveButtons:    Phaser.GameObjects.Container[] = []

  private waitingForInput = false

  // ── Animations ───────────────────────────────────────────────────────────
  private animator!:         BattleAnimator
  private opponentIdleTween: Phaser.Tweens.Tween | null = null
  private playerIdleTween:   Phaser.Tweens.Tween | null = null
  private prevPlayerLevel   = 0
  private prevOpponentLevel = 0
  private prevOpponentHp    = 0
  private prevPlayerHp      = 0

  constructor() {
    super({ key: 'BattleScene' })
  }

  init(data: BattleSceneData): void {
    this.battleId    = data.battleId
    this.moveButtons = []
    this.logHistory  = []
    this.logScrollOffset = 0
  }

  // Trainer id depuis le registry
  private get trainerId(): number {
    return this.registry.get('trainerId') as number
  }

  // ─────────────────────────────────────────────────────────────
  // CREATE
  // ─────────────────────────────────────────────────────────────

  async create(): Promise<void> {
    this.state = await battleApi.getState(this.battleId)
    this.animator = new BattleAnimator(this)

    await this.loadBackground()

    // Musique de combat — démarre AVANT les animations d'intro
    const battleType = (this.state.battle_type ?? 'wild') as BattleType
    AudioManager.instance?.playBattle(battleType)

    await this.loadAndPlaceSprites()
    this.buildInfoBars()
    this.buildBottomPanel()

    // Init niveaux et EXP AVANT renderState — évite le SFX exp_gain au chargement
    this.prevPlayerLevel   = this.state.player_pokemon.level
    this.prevOpponentLevel = this.state.opponent_pokemon.level
    this.prevOpponentHp    = this.state.opponent_pokemon.current_hp
    this.prevPlayerHp      = this.state.player_pokemon.current_hp
    this.animator.initExpPct(this.state.player_pokemon.exp_percent ?? 0)

    this.renderState()
    this.showActionPanel()
    this.setupKeyboardShortcuts()

    // Cri du Pokémon adverse juste après son apparition (loadAndPlaceSprites est déjà terminé)
    const oppDex = this.state.opponent_pokemon.dex_number
    if (oppDex) AudioManager.instance?.playCry(oppDex)
  }

  // ─────────────────────────────────────────────────────────────
  // BACKGROUND — depuis Django static
  // ─────────────────────────────────────────────────────────────

  private async loadBackground(): Promise<void> {
    const W = this.cameras.main.width
    const H = this.cameras.main.height

    // Récupérer le type de zone depuis le registry (chargé par BootScene)
    const zone = this.registry.get('currentZone')
    const zoneType: string = zone?.zone_type ?? 'route'
    const bgKey = ZONE_BG[zoneType] ?? 'bg-meadow'
    const bgUrl = `/static/img/battle_backgrounds/${bgKey}.png`
    const texKey = `battle-bg-${bgKey}`

    // Charger le background si pas déjà en cache
    if (!this.textures.exists(texKey)) {
      await new Promise<void>((resolve) => {
        this.load.image(texKey, bgUrl)
        this.load.once('complete', resolve)
        this.load.once('loaderror', resolve) // fallback si image manquante
        this.load.start()
      })
    }

    if (this.textures.exists(texKey)) {
      // Background plein écran, maintient les proportions
      const bg = this.add.image(W / 2, H * 0.42, texKey).setDepth(0)
      const scaleX = W / bg.width
      const scaleY = (H * 0.65) / bg.height
      bg.setScale(Math.max(scaleX, scaleY))
    } else {
      // Fallback couleur si image absente
      this.add.rectangle(W / 2, H * 0.42 / 2, W, H * 0.65, 0x1b4332).setDepth(0)
    }

    // Bande sombre — hauteur fixe calée sur le contenu
    const panelH = 112
    const panelY = H - panelH
    this.add.rectangle(W / 2, panelY + panelH / 2, W, panelH, 0x1a1a2e, 0.92)
      .setDepth(1)
  }

  // ─────────────────────────────────────────────────────────────
  // SPRITES
  // ─────────────────────────────────────────────────────────────

  private async loadAndPlaceSprites(): Promise<void> {
    const W = this.cameras.main.width
    const H = this.cameras.main.height

    const op = this.state.opponent_pokemon
    const pp = this.state.player_pokemon

    const opFolder = op.is_shiny ? 'shiny'      : 'normal'
    const ppFolder = pp.is_shiny ? 'back-shiny'  : 'back'
    const opName   = this._spriteFileName(op.species_name)
    const ppName   = this._spriteFileName(pp.species_name)
    const opKey    = `sprite-front-${op.is_shiny ? 'shiny-' : ''}${opName}`
    const ppKey    = `sprite-back-${pp.is_shiny ? 'shiny-' : ''}${ppName}`

    await this.loadSpriteIfNeeded(opKey, opFolder, opName)
    await this.loadSpriteIfNeeded(ppKey, ppFolder, ppName)

    // Ombre adversaire
    this.add.ellipse(W * 0.75, H * 0.40, 70, 14, 0x000000, 0.25).setDepth(2)
    // Ombre joueur
    this.add.ellipse(W * 0.28, H * 0.68, 90, 18, 0x000000, 0.25).setDepth(2)

    // Sprite adversaire — invisible au départ, l'animation d'intro le fera apparaître
    this.opponentSprite = this.add.image(W * 0.75, H * 0.48, opKey)
        .setDepth(5).setScale(0).setAlpha(0).setOrigin(0.5, 1)

    // Sprite joueur — invisible au départ
    this.playerSprite = this.add.image(W * 0.28, H * 0.72, ppKey)
      .setDepth(5).setScale(0).setAlpha(0).setOrigin(0.5, 1)

    const battleType  = this.state.battle_type ?? 'wild'
    const isWild      = battleType === 'wild'
    const ballUrl     = '/static/img/items_sprites/ball/poke.png'

    // Hauteurs naturelles des sprites (à lire AVANT de mettre scale=0)
    // On restaure temporairement scale=1 pour lire displayHeight, puis on remet 0
    this.opponentSprite.setScale(1.6)
    const oppSpriteH = this.opponentSprite.displayHeight
    this.opponentSprite.setScale(0)

    this.playerSprite.setScale(2.2)
    const ppSpriteH = this.playerSprite.displayHeight
    this.playerSprite.setScale(0)

    const oppFinalX   = W * 0.75
    const oppFinalY   = H * 0.48
    const ppFinalX    = W * 0.28
    const ppFinalY    = H * 0.72

    if (isWild) {
      // ── Wild : adversaire slide-in depuis la droite, rendu visible avant le tween
      this.opponentSprite.setScale(1.6).setAlpha(1).setX(W + 100)
      this.tweens.add({
        targets: this.opponentSprite, x: oppFinalX, duration: 500, ease: 'Back.out',
        onComplete: () => {
          this.opponentIdleTween = this.animator.startIdle(this.opponentSprite)
        },
      })

      // Joueur : pokeball lancée depuis le bas (position dresseur hors-écran)
      await new Promise<void>(res => this.time.delayedCall(300, res))   // attendre slide adversaire

      AudioManager.instance?.playUiSfx('SFX_BALL_POOF')
      await this.animator.animateIntroEntry(
        this.playerSprite,
        2.2,
        { x: ppFinalX - 60, y: H + 20 },
        { x: ppFinalX, y: ppFinalY - ppSpriteH * 0.5 },
        ballUrl,
        -160,
      )
      this.playerIdleTween = this.animator.startIdle(this.playerSprite)

    } else {
      // ── Trainer / Gym / Elite4 / Rival : pokeball pour les deux

      AudioManager.instance?.playUiSfx('SFX_BALL_POOF')
      await this.animator.animateIntroEntry(
        this.opponentSprite,
        1.6,
        { x: W + 60, y: H * 0.25 },
        { x: oppFinalX, y: oppFinalY - oppSpriteH * 0.5 },
        ballUrl,
        -120,
      )
      this.opponentIdleTween = this.animator.startIdle(this.opponentSprite)

      await new Promise<void>(res => this.time.delayedCall(300, res))

      AudioManager.instance?.playUiSfx('SFX_BALL_POOF')
      await this.animator.animateIntroEntry(
        this.playerSprite,
        2.2,
        { x: ppFinalX - 60, y: H + 20 },
        { x: ppFinalX, y: ppFinalY - ppSpriteH * 0.5 },
        ballUrl,
        -160,
      )
      this.playerIdleTween = this.animator.startIdle(this.playerSprite)
    }
  }

  /** Normalise un nom d'espèce pour le nom de fichier sprite.
   *  Ex: "nidoran♂" → "nidoranm", "nidoran♀" → "nidoranf" */
  private _spriteFileName(speciesName: string): string {
    return speciesName.toLowerCase()
      .replace(/♂/g, 'm')
      .replace(/♀/g, 'f')
  }

  private loadSpriteIfNeeded(key: string, folder: string, name: string): Promise<void> {
    if (this.textures.exists(key)) return Promise.resolve()
    return new Promise((resolve) => {
      this.load.image(key, `/static/img/sprites_gen5/${folder}/${name}.png`)
      this.load.once('complete', resolve)
      this.load.once('loaderror', resolve)
      this.load.start()
    })
  }

  // ─────────────────────────────────────────────────────────────
  // INFO-BARS style Django legacy
  // ─────────────────────────────────────────────────────────────

  private buildInfoBars(): void {
    const W = this.cameras.main.width
    const H = this.cameras.main.height

    // ── Boîte adversaire (haut gauche) ───────────────────────
    const ox = 10, oy = 10, ow = W * 0.38, oh = 60
    this.drawInfoBox(ox, oy, ow, oh)

    this.opponentNameText = this.add.text(ox + 10, oy + 8, '', {
      fontSize: '9px', color: '#1a1a1a',
      fontFamily: '"Press Start 2P"', fontStyle: 'bold',
    }).setDepth(10)

    this.opponentGenderText = this.add.text(0, oy + 8, '', {
      fontSize: '11px', fontFamily: '"Inter", "Segoe UI", sans-serif', fontStyle: 'bold',
    }).setDepth(10)

    this.opponentHpBar = this.add.graphics().setDepth(10)
    this.opponentHpText = this.add.text(ox + 10, oy + 38, '', {
      fontSize: '9px', color: '#555', fontFamily: '"Inter", "Segoe UI", sans-serif',
    }).setDepth(10)
    this.opponentStatusBadge = this.add.container(0, 0).setDepth(11)

    // ── Boîte joueur (milieu droite) ──────────────────────────
    const px = W * 0.58, py = H * 0.50, pw = W * 0.38, ph = 82
    this.drawInfoBox(px, py, pw, ph)

    this.playerNameText = this.add.text(px + 10, py + 8, '', {
      fontSize: '9px', color: '#1a1a1a',
      fontFamily: '"Press Start 2P"', fontStyle: 'bold',
    }).setDepth(10)

    this.playerGenderText = this.add.text(0, py + 8, '', {
      fontSize: '11px', fontFamily: '"Inter", "Segoe UI", sans-serif', fontStyle: 'bold',
    }).setDepth(10)

    this.playerHpBar = this.add.graphics().setDepth(10)
    this.playerExpBar = this.add.graphics().setDepth(10)
    this.playerHpText = this.add.text(px + 10, py + 44, '', {
      fontSize: '9px', color: '#555', fontFamily: '"Inter", "Segoe UI", sans-serif',
    }).setDepth(10)
    this.playerStatusBadge = this.add.container(0, 0).setDepth(11)
  }

  private drawInfoBox(x: number, y: number, w: number, h: number): void {
    const g = this.add.graphics().setDepth(8)
    g.fillStyle(0xffffff, 0.93)
    g.fillRoundedRect(x, y, w, h, 8)
    g.lineStyle(2, 0x333333, 0.7)
    g.strokeRoundedRect(x, y, w, h, 8)
  }

  // ─────────────────────────────────────────────────────────────
  // PANEL BAS — Log + 4 boutons style legacy
  // ─────────────────────────────────────────────────────────────

  private buildBottomPanel(): void {
    const W = this.cameras.main.width
    const H = this.cameras.main.height
    const panelH = 112
    const panelY = H - panelH

    // ── Log scrollable (gauche) ──────────────────────────────
    const logW  = W * 0.33
    const logX  = 10
    const logY  = panelY + 8
    const logH  = panelH - 12

    // Fond arrondi derrière le log
    const logBg = this.add.graphics().setDepth(9)
    logBg.fillStyle(0x0d0d1a, 0.85)
    logBg.fillRoundedRect(logX - 4, logY - 4, logW - 6, logH + 8, 8)
    logBg.lineStyle(1, 0x3a3a6a, 0.6)
    logBg.strokeRoundedRect(logX - 4, logY - 4, logW - 6, logH + 8, 8)

    // Container masqué pour le texte
    this.logContainer = this.add.container(logX, logY).setDepth(10)
    const maskShape = this.add.graphics()
    maskShape.fillStyle(0xffffff)
    maskShape.fillRect(logX, logY, logW - 14, logH)
    this.logMask = maskShape.createGeometryMask()
    this.logContainer.setMask(this.logMask)

    // Boutons scroll ▲/▼ — HORS du masque, toujours visibles
    this.logScrollBtnUp = this.add.text(logX + logW - 12, logY + 2, '▲', {
      fontSize: '9px', color: '#ffffff99',
      fontFamily: 'sans-serif', backgroundColor: '#ffffff11',
      padding: { x: 2, y: 1 },
    }).setDepth(15).setInteractive({ useHandCursor: true })
      .on('pointerover',  () => this.logScrollBtnUp.setColor('#ffffff'))
      .on('pointerout',   () => this.logScrollBtnUp.setColor('#ffffff99'))
      .on('pointerdown',  () => this.scrollLog(-1))

    this.logScrollBtnDown = this.add.text(logX + logW - 12, logY + logH - 14, '▼', {
      fontSize: '9px', color: '#ffffff99',
      fontFamily: 'sans-serif', backgroundColor: '#ffffff11',
      padding: { x: 2, y: 1 },
    }).setDepth(15).setInteractive({ useHandCursor: true })
      .on('pointerover',  () => this.logScrollBtnDown.setColor('#ffffff'))
      .on('pointerout',   () => this.logScrollBtnDown.setColor('#ffffff99'))
      .on('pointerdown',  () => this.scrollLog(1))

    // Scroll molette DOM
    const canvas = this.game.canvas
    const onWheel = (e: WheelEvent) => {
      const rect   = canvas.getBoundingClientRect()
      const scaleX = canvas.width  / rect.width
      const scaleY = canvas.height / rect.height
      const cx = (e.clientX - rect.left) * scaleX
      const cy = (e.clientY - rect.top)  * scaleY
      if (cx >= logX && cx <= logX + logW && cy >= logY && cy <= logY + logH) {
        e.preventDefault()
        this.scrollLog(e.deltaY > 0 ? 1 : -1)
      }
    }
    canvas.addEventListener('wheel', onWheel, { passive: false })
    this.events.once('shutdown', () => canvas.removeEventListener('wheel', onWheel))

    // ── Panel ACTION (4 boutons) ──────────────────────────────
    this.actionPanel = this.buildActionButtons(W, H, panelY, panelH)

    // ── Panel MOVES (grille attaques + retour) ────────────────
    this.movesPanel = this.buildMovesButtons(W, H, panelY, panelH)
    this.movesPanel.setVisible(false)

    // ── Panel SAC et SWITCH (construits à la demande) ─────────
    this.bagPanel    = this.add.container(0, 0).setDepth(12).setVisible(false)
    this.switchPanel = this.add.container(0, 0).setDepth(12).setVisible(false)
    this.moveTooltip = this.add.container(0, 0).setDepth(30).setVisible(false)
  }

  // 4 boutons : Combat / Pokémon / Sac / Fuite
  private buildActionButtons(
    W: number, H: number, panelY: number, panelH: number
  ): Phaser.GameObjects.Container {
    const startX = W * 0.36
    const btnW   = (W * 0.62) / 2 - 5
    const btnH   = 44   // identique au plafond des move buttons
    const gap    = 4

    const defs = [
      { label: 'Combat',  icon: '⚔️',  color: 0xc0392b, hover: 0xe74c3c, cb: () => { this.sfxConfirm(); this.showMoves() } },
      { label: 'Pokémon', icon: '🔵',  color: 0x2980b9, hover: 0x3498db, cb: () => { this.sfxConfirm(); void this.showSwitchPanel() } },
      { label: 'Sac',     icon: '🎒',  color: 0x27ae60, hover: 0x2ecc71, cb: () => { this.sfxConfirm(); void this.showBagPanel() } },
      { label: 'Fuite',   icon: '💨',  color: 0x7f8c8d, hover: 0x95a5a6, cb: () => { this.sfxCancel();  void this.executeFlee() } },
    ]

    const items: Phaser.GameObjects.GameObject[] = []

    defs.forEach((def, i) => {
      const col = i % 2
      const row = Math.floor(i / 2)
      const x = startX + col * (btnW + gap)
      const totalH = 2 * btnH + gap; const offsetY = (panelH - totalH) / 2; const y = panelY + offsetY + row * (btnH + gap)

      const bg = this.add.graphics()
      const draw = (c: number) => {
        bg.clear()
        bg.fillStyle(c, 1)
        bg.fillRoundedRect(0, 0, btnW, btnH, 6)
        bg.lineStyle(2, 0xffffff, 0.15)
        bg.strokeRoundedRect(0, 0, btnW, btnH, 6)
      }
      draw(def.color)

      const label = this.add.text(btnW / 2, btnH / 2 - 4, def.label, {
        fontSize: '8px', color: '#ffffff',
        fontFamily: '"Press Start 2P"', align: 'center',
      }).setOrigin(0.5)

      // Hint touche — coin bas-droit
      const hint = this.add.text(btnW - 5, btnH - 5, `${i + 1}`, {
        fontSize: '7px', color: 'rgba(255,255,255,0.45)',
        fontFamily: '"Press Start 2P"',
      }).setOrigin(1, 1)

      const zone = this.add.zone(0, 0, btnW, btnH).setOrigin(0)
        .setInteractive({ useHandCursor: true })
        .on('pointerover',  () => draw(def.hover))
        .on('pointerout',   () => draw(def.color))
        .on('pointerdown',  def.cb)

      const container = this.add.container(x, y, [bg, label, hint, zone]).setDepth(12)
      items.push(container)
    })

    return this.add.container(0, 0, items).setDepth(12)
  }

  // Grille des attaques
  private buildMovesButtons(
    W: number, H: number, panelY: number, panelH: number
  ): Phaser.GameObjects.Container {
    const items: Phaser.GameObjects.GameObject[] = []
    const moves  = this.state.player_pokemon.moves ?? []
    const startX = W * 0.36
    const cols   = 2
    const btnW   = (W - startX - 8) / 2 - 2
    const btnH   = Math.min(44, (panelH - 28) / 2 - 3)
    const gap    = 4

    // Bouton retour
    const backBg = this.add.graphics()
    const drawBack = (c: number) => {
      backBg.clear(); backBg.fillStyle(c, 1)
      backBg.fillRoundedRect(0, 0, (btnW * 2 + gap), 18, 4)
    }
    drawBack(0x34495e)
    const backLabel = this.add.text((btnW * 2 + gap) / 2, 9, '← RETOUR', {
      fontSize: '8px', color: '#ccc', fontFamily: '"Press Start 2P"',
    }).setOrigin(0.5)
    const backZone = this.add.zone(0, 0, btnW * 2 + gap, 18).setOrigin(0)
      .setInteractive({ useHandCursor: true })
      .on('pointerover', () => drawBack(0x4a6278))
      .on('pointerout',  () => drawBack(0x34495e))
      .on('pointerdown', () => { this.sfxCancel(); this._hideMoveTooltip(); this.showActionPanel() })
    items.push(this.add.container(startX, panelY + 4, [backBg, backLabel, backZone]).setDepth(12))

    // Grille 2×2
    moves.slice(0, 4).forEach((move, i) => {
      const col = i % cols
      const row = Math.floor(i / cols)
      const x   = startX + col * (btnW + gap)
      const y   = panelY + 26 + row * (btnH + gap)

      const typeKey    = move.type?.toLowerCase() ?? ''
      const baseColor  = TYPE_COLORS[typeKey] ?? 0x607d8b
      const hoverColor = Phaser.Display.Color.IntegerToColor(baseColor).lighten(18).color
      const noPP       = move.current_pp === 0

      const bg = this.add.graphics()
      const draw = (c: number) => {
        bg.clear()
        bg.fillStyle(noPP ? 0x3a2020 : c, 1)
        bg.fillRoundedRect(0, 0, btnW, btnH, 5)
        bg.lineStyle(1, noPP ? 0xe74c3c : 0xffffff, noPP ? 0.4 : 0.2)
        bg.strokeRoundedRect(0, 0, btnW, btnH, 5)
      }
      draw(baseColor)

      // btnH ≈ 39px — 4 bandes proportionnelles
      // ┌─────────────────────────────────┐
      // │ 1                               │  ← ~12% = y≈5
      // │   40  [cat]         100 %       │  ← ~35% = y≈14
      // │           EMBER                 │  ← ~60% = y≈23
      // │ [FIRE]              PP 5/25     │  ← ~84% = y≈33
      // └─────────────────────────────────┘

      const ROW1_MID = Math.round(btnH * 0.12)
      const ROW2_MID = Math.round(btnH * 0.35)
      const ROW3_MID = Math.round(btnH * 0.60)
      const ROW4_MID = Math.round(btnH * 0.84)

      // ── LIGNE 1 : hint seul (haut gauche) ─────────────────────
      const hint = this.add.text(4, ROW1_MID, `${i + 1}`, {
        fontSize: '6px', color: 'rgba(255,255,255,0.28)',
        fontFamily: '"Press Start 2P"',
      }).setOrigin(0, 0.5)

      // ── LIGNE 2 : puissance + catIcon + précision ─────────────
      const powerStr = move.power != null ? `${move.power}` : '—'
      const powerTxt = this.add.text(8, ROW2_MID, powerStr, {
        fontSize: '6px', color: 'rgba(255,255,255,0.65)',
        fontFamily: '"Press Start 2P"',
      }).setOrigin(0, 0.5)

      const accStr = move.accuracy != null ? `${move.accuracy} %` : '—'
      const accTxt = this.add.text(btnW - 4, ROW2_MID, accStr, {
        fontSize: '6px', color: 'rgba(255,255,255,0.65)',
        fontFamily: '"Press Start 2P"',
      }).setOrigin(1, 0.5)

      const catKey = `cat-icon-${move.category}`
      const catUrl = `/static/img/movesTypesSprites/move-${move.category}.png`
      const catImg = this.add.image(btnW / 2, ROW2_MID, '__DEFAULT')
        .setDisplaySize(14, 8).setOrigin(0.5)
      if (!this.textures.exists(catKey)) {
        this.load.image(catKey, catUrl)
        this.load.once('complete', () => {
          catImg.setTexture(catKey)
          this.textures.get(catKey).setFilter(Phaser.Textures.FilterMode.LINEAR)
        })
        this.load.start()
      } else {
        catImg.setTexture(catKey)
        this.textures.get(catKey).setFilter(Phaser.Textures.FilterMode.LINEAR)
      }

      // ── LIGNE 3 : efficacité (gauche) + nom du move (centré) ──
      const oppTypes = this.state.opponent_pokemon.types ?? []
      const moveType = move.type?.toLowerCase() ?? ''
      const effectiveness = move.category !== 'status' && oppTypes.length > 0
        ? getTypeEffectiveness(moveType, oppTypes)
        : null

      // Badge efficacité — affiché seulement si ≠ 1× et move offensif
      let effBadge: Phaser.GameObjects.Container | null = null
      if (effectiveness !== null && effectiveness !== 1) {
        const { label, color } =
          effectiveness === 0    ? { label: '0×',    color: 0x555555 } :
          effectiveness >= 4     ? { label: '4×',    color: 0xe74c3c } :
          effectiveness >= 2     ? { label: '2×',    color: 0xe67e22 } :
          effectiveness <= 0.25  ? { label: '¼×',    color: 0x2980b9 } :
                                   { label: '½×',    color: 0x3498db }

        const BADGE_H = 10, PAD = 3
        const badgeW  = label.length * 5 + PAD * 2

        const effBg = this.add.graphics()
        effBg.fillStyle(color, 1)
        effBg.fillRoundedRect(0, -BADGE_H / 2, badgeW, BADGE_H, 3)

        const effTxt = this.add.text(badgeW / 2, 0, label, {
          fontSize: '6px', color: '#fff', fontFamily: '"Press Start 2P"',
        }).setOrigin(0.5, 0.5)

        effBadge = this.add.container(4, ROW3_MID, [effBg, effTxt])
      }

      const maxChars = Math.floor((btnW - 8) / 6.5)
      const moveName = move.name.length > maxChars
        ? move.name.slice(0, maxChars - 1) + '…'
        : move.name
      const nameTxt = this.add.text(btnW / 2, ROW3_MID, moveName, {
        fontSize: '8px', color: noPP ? '#aa6666' : '#ffffff',
        fontFamily: '"Press Start 2P"',
      }).setOrigin(0.5, 0.5)

      // ── LIGNE 4 : badge type (gauche) + PP (droite) ───────────
      const TYPE_BADGE_W = 34
      const TYPE_BADGE_H = 10

      const typeBg = this.add.graphics()
      typeBg.fillStyle(baseColor, 1)
      typeBg.fillRoundedRect(4, ROW4_MID - TYPE_BADGE_H / 2, TYPE_BADGE_W, TYPE_BADGE_H, 3)
      typeBg.lineStyle(1, 0xffffff, 0.25)
      typeBg.strokeRoundedRect(4, ROW4_MID - TYPE_BADGE_H / 2, TYPE_BADGE_W, TYPE_BADGE_H, 3)
      const typeLbl = this.add.text(4 + TYPE_BADGE_W / 2, ROW4_MID,
        (move.type ?? '').toUpperCase(), {
          fontSize: '6px', color: '#fff', fontFamily: '"Press Start 2P"',
        }).setOrigin(0.5)

      const ppColor = move.current_pp === 0                 ? '#e74c3c'
                    : move.current_pp <= move.max_pp * 0.25 ? '#f39c12'
                    : 'rgba(255,255,255,0.85)'

      const ppTxt = this.add.text(btnW - 4, ROW4_MID,
        `PP ${move.current_pp}/${move.max_pp}`, {
          fontSize: '6px', color: ppColor,
          fontFamily: '"Press Start 2P"',
        }).setOrigin(1, 0.5)

      const zone = this.add.zone(0, 0, btnW, btnH).setOrigin(0)
        .setInteractive({ useHandCursor: !noPP })
        .on('pointerover',  () => {
          if (!noPP) draw(hoverColor)
          this._showMoveTooltip(move, x, y, btnW, btnH)
        })
        .on('pointerout',   () => { draw(baseColor); this._hideMoveTooltip() })
        .on('pointerdown',  () => {
          if (!this.waitingForInput || noPP) return
          this.sfxConfirm(); this._hideMoveTooltip(); void this.executeMove(move.id)
        })

      const children: Phaser.GameObjects.GameObject[] = [bg, hint, catImg, powerTxt, accTxt, nameTxt, typeBg, typeLbl, ppTxt, zone]
      if (effBadge) children.splice(5, 0, effBadge)

      const container = this.add.container(x, y, children).setDepth(12)
      items.push(container)
      this.moveButtons.push(container)
    })

    return this.add.container(0, 0, items).setDepth(12)
  }


  // ─────────────────────────────────────────────────────────────
  // RACCOURCIS CLAVIER  1/2/3/4  (= &/é/"/'  sur AZERTY)
  // Même keyCode physique (49-52) sur les deux layouts.
  // ─────────────────────────────────────────────────────────────

  private setupKeyboardShortcuts(): void {
    const KEYS = [49, 50, 51, 52]

    this.input.keyboard!.on('keydown', (e: KeyboardEvent) => {
      const idx = KEYS.indexOf(e.keyCode)

      // Échap — retour au panel action depuis moves/sac/switch
      if (e.keyCode === 27 && this.waitingForInput && !this.actionPanel.visible) {
        this.sfxCancel()
        this.showActionPanel()
        return
      }

      if (idx === -1 || !this.waitingForInput) return

      if (this.actionPanel.visible) {
        const actions = [
          () => { this.sfxConfirm(); this.showMoves() },
          () => { this.sfxConfirm(); void this.showSwitchPanel() },
          () => { this.sfxConfirm(); void this.showBagPanel() },
          () => { this.sfxCancel();  void this.executeFlee() },
        ]
        actions[idx]?.()

      } else if (this.movesPanel.visible) {
        const moves = this.state.player_pokemon.moves ?? []
        const move  = moves[idx]
        if (move) { this.sfxConfirm(); void this.executeMove(move.id) }
      }
    })
  }

  // ── Tooltip moves — affiche uniquement l'effet au survol ──────
  private _showMoveTooltip(move: MoveData, btnX: number, btnY: number, btnW: number, _btnH: number): void {
    this.moveTooltip.removeAll(true)

    const effectText = move.effect
      ? (move.effect_chance && move.effect_chance > 0
          ? `${move.effect} (${move.effect_chance}%)`
          : move.effect)
      : null

    // Pas d'effet connu → on n'affiche rien
    if (!effectText) return

    const W    = this.cameras.main.width
    const TW   = 160
    const PAD  = 7

    // Calcul hauteur selon le texte (wordWrap ~22 chars par ligne, 10px/ligne)
    const charsPerLine = Math.floor((TW - PAD * 2) / 5.5)
    const lines        = Math.ceil(effectText.length / charsPerLine)
    const TH           = PAD * 2 + 8 + lines * 10

    let tx = btnX + btnW / 2 - TW / 2
    tx = Phaser.Math.Clamp(tx, 4, W - TW - 4)
    const ty = btnY - TH - 8

    const bg = this.add.graphics()
    bg.fillStyle(0x0d0d1a, 0.95)
    bg.fillRoundedRect(0, 0, TW, TH, 5)
    bg.lineStyle(1, 0x4a4a8a, 0.9)
    bg.strokeRoundedRect(0, 0, TW, TH, 5)
    // Flèche vers le bas
    bg.fillStyle(0x0d0d1a, 0.95)
    bg.fillTriangle(TW / 2 - 5, TH, TW / 2 + 5, TH, TW / 2, TH + 6)
    bg.lineStyle(1, 0x4a4a8a, 0.9)
    bg.strokeTriangle(TW / 2 - 5, TH, TW / 2 + 5, TH, TW / 2, TH + 6)

    const txt = this.add.text(PAD, PAD, effectText, {
      fontSize: '8px', color: '#ccccff',
      fontFamily: '"Press Start 2P"',
      wordWrap: { width: TW - PAD * 2 },
      lineSpacing: 2,
    })

    this.moveTooltip.add([bg, txt])
    this.moveTooltip.setPosition(tx, ty)
    this.moveTooltip.setVisible(true)
  }

  private _hideMoveTooltip(): void {
    this.moveTooltip.setVisible(false)
    this.moveTooltip.removeAll(true)
  }

  private showActionPanel(): void {
    this.actionPanel.setVisible(true)
    this.movesPanel.setVisible(false)
    this.bagPanel.setVisible(false)
    this.switchPanel.setVisible(false)
    this.showLog(`Que doit faire\n${this.state.player_pokemon.name} ?`)
    this.waitingForInput = true
  }

  private sfxConfirm(): void { AudioManager.instance?.playUiSfx('confirm') }
  private sfxCancel():  void { AudioManager.instance?.playUiSfx('cancel')  }

  private showMoves(): void {
    this.sfxConfirm()
    this.actionPanel.setVisible(false)
    this.movesPanel.setVisible(true)
    this.showLog('Choisissez\nune capacité.')
    this.waitingForInput = true
  }

  // ─────────────────────────────────────────────────────────────
  // RENDU DE L'ÉTAT
  // ─────────────────────────────────────────────────────────────

  private renderState(): void {
    this._renderNames(this.state)
    this._renderStatuses(this.state)
    this._renderOpponentHp(this.state)
    this._renderPlayerHp(this.state)
  }

  private drawHpBar(
    g: Phaser.GameObjects.Graphics,
    pokemon: PokemonData,
    x: number, y: number, maxW: number
  ): void {
    const ratio = Math.max(0, pokemon.current_hp / pokemon.max_hp)
    const color = ratio > 0.5 ? 0x2ecc71 : ratio > 0.25 ? 0xf39c12 : 0xe74c3c

    g.clear()
    // Fond barre
    g.fillStyle(0xbdc3c7)
    g.fillRoundedRect(x, y, maxW, 7, 3)
    // Barre colorée
    g.fillStyle(color)
    g.fillRoundedRect(x, y, maxW * ratio, 7, 3)
    // Label HP
    g.fillStyle(0x666666)
  }

  // ─────────────────────────────────────────────────────────────
  // ACTIONS
  // ─────────────────────────────────────────────────────────────

  private async executeMove(moveId: number): Promise<void> {
    if (!this.waitingForInput) return
    this.waitingForInput = false

    const moveData = this.state.player_pokemon.moves?.find(m => m.id === moveId)
    const W = this.cameras.main.width, H = this.cameras.main.height
    const playerPos   = { x: W * 0.28, y: H * 0.57 }
    const opponentPos = { x: W * 0.75, y: H * 0.38 }

    try {
      // 1. Appel API
      const response = await battleApi.useMove(this.battleId, moveId)
      this.prevOpponentHp = this.state.opponent_pokemon.current_hp
      this.prevPlayerHp   = this.state.player_pokemon.current_hp
      this.state = response

      // 2. Découper le log en phases
      const splitIdx     = this._findLogSplit(response.log)
      const playerLogs   = response.log.slice(0, splitIdx)
      const opponentLogs = response.log.slice(splitIdx)

      // Séparer ligne d'action et lignes de détail pour chaque phase
      const { actionLine: playerActionLine, detailLines: playerDetailLines } = this._splitActionFromDetails(playerLogs)
      const { actionLine: oppActionLine,    detailLines: oppDetailLines }    = this._splitActionFromDetails(opponentLogs)

      // Lignes fin de tour : EXP, level-up, achievements (en queue des logs joueur)
      const EOT_KEYWORDS = ['+', 'Level', '🏆', 'évolue', 'Bravo']
      const eotLines    = playerDetailLines.filter(l => EOT_KEYWORDS.some(k => l.startsWith(k)))
      const combatLines = playerDetailLines.filter(l => !EOT_KEYWORDS.some(k => l.startsWith(k)))

      const onKoLine = (line: string) => {
        if (line.toLowerCase().includes('k.o.') || line.toLowerCase().includes('est mis k')) {
          this.animateHit()
        }
      }

      // ── PHASE JOUEUR ──────────────────────────────────────────
      // a. Afficher "X utilise Y !"
      if (playerActionLine) await this.showLogSequence([playerActionLine])

      // b. Animation attaque joueur
      const playerMissed = playerLogs.some(l => l.includes("L'attaque a raté"))
      if (moveData && !playerMissed) {
        this.animator.playMoveAnimation(
          moveData.name, playerPos, opponentPos,
          this.playerSprite, this.opponentSprite, true,
          (moveData.type ?? 'normal').toLowerCase(),
          (moveData.category ?? '').toLowerCase(),
          this.playerIdleTween, this.opponentIdleTween,
        )
        AudioManager.instance?.playMoveSfx(moveData.name)
        await new Promise<void>(r => this.time.delayedCall(1200, r))
      }

      // c. Barre HP adversaire + détails du tour joueur
      this._renderOpponentHp(response)
      await this.showLogSequence(combatLines, onKoLine)

      // ── PHASE ADVERSAIRE ──────────────────────────────────────
      if (!response.turn_info.second_skipped && opponentLogs.length > 0
          && response.player_pokemon.current_hp > 0) {

        // a. Afficher "Adversaire utilise Z !"
        if (oppActionLine) await this.showLogSequence([oppActionLine])

        // b. Animation attaque adversaire
        const oppMissed = opponentLogs.some(l => l.includes("L'attaque a raté"))
        if (!oppMissed) {
          const oppMove = this._extractOpponentMove(opponentLogs, response.opponent_pokemon.name)
          this.animator.playMoveAnimation(
            oppMove.name, opponentPos, playerPos,
            this.opponentSprite, this.playerSprite, false,
            oppMove.type, oppMove.category,
            this.opponentIdleTween, this.playerIdleTween,
          )
          if (oppMove.sfxName) AudioManager.instance?.playMoveSfx(oppMove.sfxName)
          await new Promise<void>(r => this.time.delayedCall(1200, r))
        }

        // c. Barre HP joueur + détails
        this._renderPlayerHp(response)
        await this.showLogSequence(oppDetailLines, onKoLine)
      } else {
        // Pas de tour adverse — mettre quand même à jour la barre joueur (soins, etc.)
        this._renderPlayerHp(response)
      }

      // ── FIN DE TOUR : EXP, level-up, achievements ─────────────
      this._renderNames(response)
      this._renderStatuses(response)
      this._checkLevelUp(response)
      if (eotLines.length > 0) await this.showLogSequence(eotLines)

      // K.O. fallback
      this.animateHit()
      if (this.opponentFainted || this.playerFainted) {
        await new Promise<void>(r => this.time.delayedCall(850, r))
      }

      if (response.battle_ended) {
        const evo = (response as any).pending_evolution as PendingEvolution | undefined
        if (evo) await this._launchEvolution(evo)
        await this.handleBattleEnd()
      } else {
        const evo = (response as any).pending_evolution as PendingEvolution | undefined
        if (evo) await this._launchEvolution(evo)
        if (response.player_pokemon.current_hp <= 0) {
          await this.showForcedSwitchPanel()
        } else {
          this.showActionPanel()
        }
      }
    } catch (err) {
      console.error('Erreur de combat:', err)
      this.showLog('Erreur — réessaie.')
      this.waitingForInput = true
    }
  }

  /**
   * Sépare la ligne d'action ("X utilise Y !") des lignes de détail qui suivent.
   */
  private _splitActionFromDetails(lines: string[]): { actionLine: string | null; detailLines: string[] } {
    if (!lines.length) return { actionLine: null, detailLines: [] }
    const ACTION_KEYWORDS = ['utilise', 'lance', 'emploie']
    const firstIsAction = ACTION_KEYWORDS.some(k => lines[0].toLowerCase().includes(k))
    if (firstIsAction) {
      return { actionLine: lines[0], detailLines: lines.slice(1) }
    }
    return { actionLine: null, detailLines: lines }
  }

  // ── Helpers séquençage ─────────────────────────────────────────

  /**
   * Cherche l'index dans le log où commence le tour adversaire.
   * Stratégie : trouver la 2ème occurrence d'un mot-clé d'action.
   * Si introuvable → tout le log = phase joueur (adversaire K.O. / skip).
   */
  private _findLogSplit(log: string[]): number {
    // Mots-clés qui indiquent une attaque lancée (conjugaisons FR)
    const ACTION_KEYWORDS = ['utilise', 'lance', 'emploie']
    let firstFound = -1
    for (let i = 0; i < log.length; i++) {
      const lower = log[i].toLowerCase()
      if (ACTION_KEYWORDS.some(k => lower.includes(k))) {
        if (firstFound === -1) {
          firstFound = i
        } else {
          return i   // 2ème action trouvée = début tour adverse
        }
      }
    }
    return log.length  // tout appartient au joueur (adversaire K.O. ou skip)
  }

  /**
   * Extrait le nom du move adverse depuis les lignes de log qui le concernent.
   * Retourne un objet compatible avec playMoveAnimation.
   */
  private _extractOpponentMove(
    lines: string[],
    opponentName: string,
  ): { name: string; type: string; category: string; sfxName: string | null } {
    for (const line of lines) {
      // Pattern : "{nom} utilise {move} !" ou "{nom} lance {move} !"
      const m = line.match(/utilise\s+(.+?)[\s!]/) ?? line.match(/lance\s+(.+?)[\s!]/)
      if (m) {
        const moveName = m[1].trim()
        return { name: moveName, type: 'normal', category: 'physical', sfxName: moveName }
      }
    }
    // Fallback générique si parsing échoue
    return { name: '', type: 'normal', category: 'physical', sfxName: null }
  }

  // ── Rendus partiels (appelés au bon moment dans la séquence) ───

  private _renderOpponentHp(r: BattleResponse): void {
    const W  = this.cameras.main.width
    const ow = W * 0.38 - 20
    this.animator.animateHpBar(this.opponentHpBar, r.opponent_pokemon.current_hp, r.opponent_pokemon.max_hp, 20, 28, ow, false)
    this.opponentHpText?.setText('')
    if (r.opponent_pokemon.current_hp < this.prevOpponentHp && r.opponent_pokemon.current_hp > 0) {
      this.animator.flashHit(this.opponentSprite)
    }
    this.prevOpponentHp = r.opponent_pokemon.current_hp
    if (r.opponent_pokemon.current_hp <= 0) this.animateHit()
  }

  private _renderPlayerHp(r: BattleResponse): void {
    const W  = this.cameras.main.width
    const H  = this.cameras.main.height
    const pw = W * 0.38 - 20
    const px = W * 0.58
    const py = H * 0.50
    this.playerHpText.setText(`PV  ${r.player_pokemon.current_hp}/${r.player_pokemon.max_hp}`)
    this.animator.animateHpBar(this.playerHpBar, r.player_pokemon.current_hp, r.player_pokemon.max_hp, px + 10, py + 32, pw, true)
    this.animator.animateExpBar(
      this.playerExpBar,
      r.player_pokemon.exp_percent ?? 0,
      px, py, pw,
      () => AudioManager.instance?.playUiSfx('exp_gain'),
    )
    if (r.player_pokemon.current_hp < this.prevPlayerHp && r.player_pokemon.current_hp > 0) {
      this.animator.flashHit(this.playerSprite)
    }
    this.prevPlayerHp = r.player_pokemon.current_hp
    if (r.player_pokemon.current_hp <= 0) this.animateHit()
  }

  private _renderNames(r: BattleResponse): void {
    const genderSymbol = (g?: string) => g === 'M' ? '♂' : g === 'F' ? '♀' : ''
    const genderColor  = (g?: string) => g === 'M' ? '#4a90d9' : g === 'F' ? '#d94a7a' : '#888'

    const opShiny  = r.opponent_pokemon.is_shiny ? ' ✨' : ''
    const ppShiny  = r.player_pokemon.is_shiny   ? ' ✨' : ''

    this.opponentNameText.setText(`${r.opponent_pokemon.name.toUpperCase()}${opShiny}  Nv.${r.opponent_pokemon.level}`)
    this.playerNameText.setText(`${r.player_pokemon.name.toUpperCase()}${ppShiny}  Nv.${r.player_pokemon.level}`)

    // Symbole genre — positionné juste après le texte du nom (police système pour ♂/♀)
    const opGender = genderSymbol(r.opponent_pokemon.gender)
    this.opponentGenderText
      .setText(opGender)
      .setColor(genderColor(r.opponent_pokemon.gender))
      .setX(this.opponentNameText.x + this.opponentNameText.width + 3)

    const ppGender = genderSymbol(r.player_pokemon.gender)
    this.playerGenderText
      .setText(ppGender)
      .setColor(genderColor(r.player_pokemon.gender))
      .setX(this.playerNameText.x + this.playerNameText.width + 3)
  }

  private _renderStatuses(r: BattleResponse): void {
    const W = this.cameras.main.width
    const H = this.cameras.main.height
    const ox = 10, oy = 10, ow = W * 0.38
    const px = W * 0.58, py = H * 0.50, pw = W * 0.38
    this._drawStatusBadge(this.opponentStatusBadge, r.opponent_pokemon.status ?? null, ox + ow - 6, oy + 38)
    this._drawStatusBadge(this.playerStatusBadge,   r.player_pokemon.status   ?? null, px + pw - 6, py + 44)
    this._renderStatBadges(r)
  }

  // ── Badge statut arrondi coloré ───────────────────────────────────────────
  private _drawStatusBadge(
    container: Phaser.GameObjects.Container,
    status: string | null,
    rightX: number,   // bord droit du badge
    centerY: number,
  ): void {
    container.removeAll(true)
    if (!status) return

    // Couleur + libellé par statut
    const STATUS_STYLES: Record<string, { bg: number; border: number; label: string }> = {
      burn:      { bg: 0xc0392b, border: 0xff6b6b, label: 'BRÛ' },
      poison:    { bg: 0x8e44ad, border: 0xc39bd3, label: 'PSN' },
      paralysis: { bg: 0xf39c12, border: 0xfde68a, label: 'PAR' },
      sleep:     { bg: 0x5d6d7e, border: 0xaeb6bf, label: 'SOM' },
      freeze:    { bg: 0x2980b9, border: 0x7fb3d3, label: 'GEL' },
    }
    const style = STATUS_STYLES[status] ?? { bg: 0x555555, border: 0x999999, label: status.slice(0, 3).toUpperCase() }

    const BADGE_H  = 13
    const PAD_X    = 5
    const label    = style.label

    // Mesure approx du texte (6px par char à fontSize 8px)
    const textW    = label.length * 5.5
    const BADGE_W  = textW + PAD_X * 2

    const bg = this.add.graphics()
    bg.fillStyle(style.bg, 1)
    bg.fillRoundedRect(-BADGE_W, -BADGE_H / 2, BADGE_W, BADGE_H, 4)
    bg.lineStyle(1, style.border, 0.8)
    bg.strokeRoundedRect(-BADGE_W, -BADGE_H / 2, BADGE_W, BADGE_H, 4)

    const txt = this.add.text(-BADGE_W / 2, 0, label, {
      fontSize: '8px',
      color: '#ffffff',
      fontFamily: '"Press Start 2P"',
      fontStyle: 'bold',
    }).setOrigin(0.5, 0.5)

    container.add([bg, txt])
    container.setPosition(rightX, centerY)
  }

  // ── Stat stage badges ─────────────────────────────────────────────────────

  private _stageToMult(stage: number): number {
    // Table officielle Pokémon : stage -6→+6
    const table: Record<number, number> = {
      '-6': 0.25, '-5': 0.29, '-4': 0.33, '-3': 0.4, '-2': 0.5, '-1': 0.67,
      '0': 1, '1': 1.5, '2': 2, '3': 2.5, '4': 3, '5': 3.5, '6': 4,
    }
    return table[stage] ?? 1
  }

  private _renderStatBadges(r: BattleResponse): void {
    const bs = r.battle_state as any
    if (!bs) return

    this.opponentStatBadges.forEach(c => c.destroy())
    this.playerStatBadges.forEach(c => c.destroy())
    this.opponentStatBadges = []
    this.playerStatBadges   = []

    const STAT_DEFS = [
      { label: 'ATQ', playerField: 'player_atk_stage',   oppField: 'opponent_atk_stage'   },
      { label: 'DEF', playerField: 'player_def_stage',   oppField: 'opponent_def_stage'   },
      { label: 'SpA', playerField: 'player_spatk_stage', oppField: 'opponent_spatk_stage' },
      { label: 'SpD', playerField: 'player_spdef_stage', oppField: 'opponent_spdef_stage' },
      { label: 'VIT', playerField: 'player_speed_stage', oppField: 'opponent_speed_stage' },
      { label: 'PRÉ', playerField: 'player_acc_stage',   oppField: 'opponent_acc_stage'   },
      { label: 'ESQ', playerField: 'player_eva_stage',   oppField: 'opponent_eva_stage'   },
    ]

    const W = this.cameras.main.width
    const H = this.cameras.main.height

    const ox = 10, oy = 10, oh = 60
    const px  = W * 0.58, py = H * 0.50, ph = 82

    // Style Showdown : pills sous la boîte, alignés à gauche
    // Format : "×0.67 ATQ" en rouge, "×1.5 ATQ" en bleu
    const makeBadges = (
      stageField: 'playerField' | 'oppField',
      startX: number, belowY: number,
      store: Phaser.GameObjects.Container[],
    ) => {
      const PILL_H = 13, GAP = 3
      let bx = startX

      STAT_DEFS.forEach(def => {
        const stage = bs[def[stageField]] ?? 0
        if (stage === 0) return

        const mult   = this._stageToMult(stage)
        const isUp   = stage > 0
        const bgCol  = isUp ? 0x1565c0 : 0xb71c1c
        const txtCol = isUp ? '#90caf9' : '#ef9a9a'

        const multStr = mult < 1
          ? `×${mult.toFixed(2).replace(/0+$/, '').replace(/\.$/, '')}`
          : `×${Number.isInteger(mult) ? mult : mult.toFixed(1)}`
        const label = `${multStr} ${def.label}`

        // Mesurer la largeur du texte (approx 6px/char pour 8px font)
        const pillW = label.length * 5.8 + 8

        const bg = this.add.graphics().setDepth(12)
        bg.fillStyle(bgCol, 0.88)
        bg.fillRoundedRect(0, 0, pillW, PILL_H, 3)

        const txt = this.add.text(pillW / 2, PILL_H / 2, label, {
          fontSize: '8px', color: txtCol,
          fontFamily: '"Inter", "Segoe UI", sans-serif', fontStyle: 'bold',
        }).setOrigin(0.5, 0.5).setDepth(13)

        const container = this.add.container(bx, belowY + 2, [bg, txt]).setDepth(12)
        store.push(container)
        bx += pillW + GAP
      })
    }

    // Adversaire : sous sa boîte (oy + oh)
    makeBadges('oppField',    ox,  oy + oh,  this.opponentStatBadges)
    // Joueur : sous sa boîte (py + ph)
    makeBadges('playerField', px,  py + ph,  this.playerStatBadges)
  }

  private _checkLevelUp(r: BattleResponse): void {
    const W  = this.cameras.main.width
    const H  = this.cameras.main.height
    const px = W * 0.58
    const py = H * 0.50
    if (r.player_pokemon.level > this.prevPlayerLevel && this.prevPlayerLevel > 0) {
      this.animator.levelUpFlash(px, py, W * 0.38, 82)
    }
    this.prevPlayerLevel   = r.player_pokemon.level
    this.prevOpponentLevel = r.opponent_pokemon.level
  }

  private async executeFlee(): Promise<void> {
    if (!this.waitingForInput) return
    this.waitingForInput = false
    this.showLog('Vous tentez\nde fuir...')

    const W = this.cameras.main.width, H = this.cameras.main.height
    const playerPos   = { x: W * 0.28, y: H * 0.57 }
    const opponentPos = { x: W * 0.75, y: H * 0.38 }

    try {
      const response = await battleApi.flee(this.battleId)
      this.prevOpponentHp = this.state.opponent_pokemon.current_hp
      this.prevPlayerHp   = this.state.player_pokemon.current_hp
      this.state = response

      if (response.battle_ended) {
        await this.showLogSequence(response.log)
        await this.handleBattleEnd()
        return
      }

      // ── Fuite échouée : pipeline adverse identique à executeMove ──
      // Premier log = "Impossible de fuir !", le reste = logs d'attaque adverse
      const [fleeLine, ...opponentLogs] = response.log
      await this.showLogSequence([fleeLine])

      const onKoLine = (line: string) => {
        if (line.toLowerCase().includes('k.o.') || line.toLowerCase().includes('est mis k')) {
          this.animateHit()
        }
      }

      // Animation + SFX attaque adverse
      if (opponentLogs.length > 0 && response.player_pokemon.current_hp >= 0) {
        const oppMissed = opponentLogs.some(l => l.includes("L'attaque a raté"))
        if (!oppMissed) {
          const oppMove = this._extractOpponentMove(opponentLogs, response.opponent_pokemon.name)
          this.animator.playMoveAnimation(
            oppMove.name,
            opponentPos, playerPos,
            this.opponentSprite, this.playerSprite,
            false,
            oppMove.type,
            oppMove.category,
            this.opponentIdleTween, this.playerIdleTween,
          )
          if (oppMove.sfxName) AudioManager.instance?.playMoveSfx(oppMove.sfxName)
          await new Promise<void>(r => this.time.delayedCall(1100, r))
        }
      }

      // Mise à jour HP joueur après délai
      await new Promise<void>(r => this.time.delayedCall(1200, r))
      this._renderPlayerHp(response)

      // Logs adversaires
      await this.showLogSequence(opponentLogs, onKoLine)

      this._renderNames(response)
      this._renderStatuses(response)
      this.animateHit()   // fallback K.O.

      if (this.playerFainted) {
        await new Promise<void>(r => this.time.delayedCall(850, r))
        await this.showForcedSwitchPanel()
      } else {
        this.showActionPanel()
      }
    } catch (err) {
      console.error('Erreur fuite:', err)
      this.showActionPanel()
    }
  }

  // ─────────────────────────────────────────────────────────────
  // ANIMATIONS
  // ─────────────────────────────────────────────────────────────

  private opponentFainted = false
  private playerFainted   = false

  private animateHit(): void {
    // K.O. adversaire → faint animé (une seule fois)
    if (this.state.opponent_pokemon.current_hp <= 0 && this.opponentSprite && !this.opponentFainted) {
      this.opponentFainted = true
      AudioManager.instance?.playSfx('battle', 'faint')
      this.opponentIdleTween?.stop()
      this.animator.faintAnim(this.opponentSprite, false)
    }
    // K.O. joueur → faint animé (une seule fois)
    if (this.state.player_pokemon.current_hp <= 0 && this.playerSprite && !this.playerFainted) {
      this.playerFainted = true
      AudioManager.instance?.playSfx('battle', 'faint')
      this.playerIdleTween?.stop()
      this.animator.faintAnim(this.playerSprite, true)
    }
  }

  // ─────────────────────────────────────────────────────────────
  // LOG SÉQUENTIEL
  // ─────────────────────────────────────────────────────────────

  private logScrollOffset = 0   // nb de lignes scrollées depuis le bas

  private showLog(text: string): void {
    // Ajoute au log sans vider l'historique
    text.split('\n').filter(Boolean).forEach(line => this.appendLog(line))
  }

  private appendLog(line: string): void {
    if (line.trim()) this.logHistory.push(line)
    this.logScrollOffset = 0   // retour en bas à chaque nouveau message
    this.renderLogLines()
  }

  private scrollLog(dir: number): void {
    const maxScroll = Math.max(0, this.logHistory.length - 1)
    this.logScrollOffset = Math.max(0, Math.min(maxScroll, this.logScrollOffset + dir))
    this.renderLogLines()
  }

  private renderLogLines(): void {
    this.logTextObjects.forEach(t => t.destroy())
    this.logTextObjects = []

    const W      = this.cameras.main.width
    const logW   = W * 0.33
    const logH   = 112 - 12

    // ── Style boîte de dialogue Pokémon DS ───────────────────────
    // On affiche uniquement les 2 dernières lignes (+ scroll manuel)
    const MAX_VISIBLE = 2
    const total       = this.logHistory.length
    const endIdx      = total - this.logScrollOffset
    const startIdx    = Math.max(0, endIdx - MAX_VISIBLE)
    const visible     = this.logHistory.slice(startIdx, endIdx)

    // Deux slots fixes en bas du log
    const SLOT_H    = (logH - 4) / MAX_VISIBLE
    visible.forEach((text, i) => {
      const isLast   = (i === visible.length - 1)
      const color    = isLast ? '#ffffff' : '#8899bb'  // ligne active en blanc, précédente atténuée
      const yPos     = 4 + i * SLOT_H

      const t = this.add.text(6, yPos, text, {
        fontSize: '10px',
        color,
        fontFamily: '"Inter", "Segoe UI", sans-serif',
        wordWrap: { width: logW - 24 },
        lineSpacing: 2,
      }).setDepth(10)
      this.logContainer.add(t)
      this.logTextObjects.push(t)
    })

    // Indicateur "▼ suite" si l'historique a plus de lignes (scroll disponible)
    const canScrollUp = this.logScrollOffset < total - MAX_VISIBLE
    if (this.logScrollBtnUp && this.logScrollBtnDown) {
      this.logScrollBtnUp.setVisible(canScrollUp)
      this.logScrollBtnDown.setVisible(this.logScrollOffset > 0)
    }
  }

  private showLogSequence(lines: string[], onLine?: (line: string) => void): Promise<void> {
    if (!lines.length) return Promise.resolve()
    return new Promise((resolve) => {
      let i = 0
      const next = () => {
        if (i >= lines.length) { resolve(); return }
        const line = lines[i++]
        this.appendLog(line)
        onLine?.(line)
        this.time.delayedCall(1500, next)
      }
      next()
    })
  }


  // ─────────────────────────────────────────────────────────────
  // PANEL SAC
  // ─────────────────────────────────────────────────────────────

  // ── État interne du sac ──────────────────────────────────────
  private bagTab: 'heal' | 'ball' | 'battle' = 'heal'
  private bagScrollOffset = 0
  private bagAllItems: BattleItem[] = []
  private BAG_VISIBLE_ROWS = 3

  private async showBagPanel(): Promise<void> {
    if (!this.waitingForInput) return
    this.actionPanel.setVisible(false)
    this.movesPanel.setVisible(false)
    this.switchPanel.setVisible(false)
    this.showLog('Choisissez\nun objet.')

    try {
      const { items } = await battleApi.getItems(this.trainerId)
      this.bagAllItems    = items
      this.bagScrollOffset = 0
      this.bagTab         = 'heal'
      this._rebuildBagPanel()
    } catch {
      this.showLog('Erreur chargement\ndu sac.')
      this.showActionPanel()
      return
    }
  }

  private _bagTabItems(): BattleItem[] {
    return this.bagAllItems.filter(item => {
      if (this.bagTab === 'heal')   return item.item_type === 'potion' || item.item_type === 'medicine'
      if (this.bagTab === 'ball')   return item.item_type === 'pokeball'
      if (this.bagTab === 'battle') return item.item_type === 'battle'
      return false
    })
  }

  private _rebuildBagPanel(): void {
    this.bagPanel.removeAll(true)
    this.bagPanel.setVisible(true)

    const W      = this.cameras.main.width
    const H      = this.cameras.main.height
    const panelH = 112
    const panelY = H - panelH
    const startX = W * 0.36
    const panelW = W - startX - 4
    const TAB_H  = 24   // hauteur onglets — assez pour "Press Start 2P" 7px
    const itemH  = 22
    const gap    = 2

    // ── Fond du panel ──────────────────────────────────────────
    const bg = this.add.graphics()
    bg.fillStyle(0x1a1a2e, 0.97)
    bg.fillRoundedRect(startX, panelY, panelW, panelH, 6)
    bg.lineStyle(1, 0x3a3a6a, 0.8)
    bg.strokeRoundedRect(startX, panelY, panelW, panelH, 6)
    this.bagPanel.add(bg)

    // ── Onglets ────────────────────────────────────────────────
    const tabs: Array<{ key: typeof this.bagTab; label: string; color: number }> = [
      { key: 'heal',   label: '💊 Soins',  color: 0x16a085 },
      { key: 'ball',   label: '⚾ Balls',  color: 0xe74c3c },
      { key: 'battle', label: '⚔️ Combat', color: 0x8e44ad },
    ]
    const tabW = panelW / tabs.length

    tabs.forEach((tab, i) => {
      const tx     = startX + i * tabW
      const active = tab.key === this.bagTab
      const tabBg  = this.add.graphics()
      tabBg.fillStyle(active ? tab.color : 0x2c2c4a, 1)
      tabBg.fillRoundedRect(tx + 1, panelY + 1, tabW - 2, TAB_H - 1, 4)
      if (active) {
        tabBg.lineStyle(1, 0xffffff, 0.3)
        tabBg.strokeRoundedRect(tx + 1, panelY + 1, tabW - 2, TAB_H - 1, 4)
      }
      this.bagPanel.add(tabBg)

      const tabLabel = this.add.text(tx + tabW / 2, panelY + TAB_H / 2 + 1, tab.label, {
        fontSize: '7px', color: active ? '#ffffff' : '#aaaacc',
        fontFamily: '"Press Start 2P"',
      }).setOrigin(0.5).setDepth(14)
      this.bagPanel.add(tabLabel)

      const tabZone = this.add.zone(tx, panelY, tabW, TAB_H).setOrigin(0)
        .setInteractive({ useHandCursor: true })
        .on('pointerdown', () => {
          this.sfxConfirm()
          this.bagTab = tab.key
          this.bagScrollOffset = 0
          this._rebuildBagPanel()
        })
      this.bagPanel.add(tabZone)
    })

    // ── Liste d'items ──────────────────────────────────────────
    const filtered = this._bagTabItems()
    const listY    = panelY + TAB_H + 2
    const listH    = panelH - TAB_H - 2

    if (filtered.length === 0) {
      const empty = this.add.text(startX + panelW / 2, listY + listH / 2, 'Aucun objet', {
        fontSize: '8px', color: '#666688', fontFamily: '"Press Start 2P"',
      }).setOrigin(0.5).setDepth(14)
      this.bagPanel.add(empty)
    } else {
      const visible   = filtered.slice(this.bagScrollOffset, this.bagScrollOffset + this.BAG_VISIBLE_ROWS)
      const canUp     = this.bagScrollOffset > 0
      const canDown   = this.bagScrollOffset + this.BAG_VISIBLE_ROWS < filtered.length

      visible.forEach((item, i) => {
        const iy = listY + i * (itemH + gap) + 2
        this._buildBagItemRow(item, startX + 4, iy, panelW - 8, itemH)
      })

      // Flèches scroll
      if (canUp || canDown) {
        if (canUp) {
          const upBtn = this.add.text(startX + panelW - 14, listY + 2, '▲', {
            fontSize: '9px', color: '#ffffff99', fontFamily: 'sans-serif',
          }).setDepth(15).setInteractive({ useHandCursor: true })
            .on('pointerover', () => upBtn.setColor('#ffffff'))
            .on('pointerout',  () => upBtn.setColor('#ffffff99'))
            .on('pointerdown', () => {
              this.bagScrollOffset = Math.max(0, this.bagScrollOffset - 1)
              this._rebuildBagPanel()
            })
          this.bagPanel.add(upBtn)
        }
        if (canDown) {
          const downBtn = this.add.text(startX + panelW - 14, listY + listH - 14, '▼', {
            fontSize: '9px', color: '#ffffff99', fontFamily: 'sans-serif',
          }).setDepth(15).setInteractive({ useHandCursor: true })
            .on('pointerover', () => downBtn.setColor('#ffffff'))
            .on('pointerout',  () => downBtn.setColor('#ffffff99'))
            .on('pointerdown', () => {
              this.bagScrollOffset = Math.min(filtered.length - this.BAG_VISIBLE_ROWS, this.bagScrollOffset + 1)
              this._rebuildBagPanel()
            })
          this.bagPanel.add(downBtn)
        }

        // Compteur pages
        const pageText = this.add.text(startX + panelW / 2, listY + listH - 6,
          `${this.bagScrollOffset + 1}-${Math.min(this.bagScrollOffset + this.BAG_VISIBLE_ROWS, filtered.length)} / ${filtered.length}`, {
            fontSize: '6px', color: '#888899', fontFamily: '"Press Start 2P"',
          }).setOrigin(0.5).setDepth(14)
        this.bagPanel.add(pageText)
      }
    }

    // ── Bouton retour ──────────────────────────────────────────
    // Molette de scroll sur le panel sac
    const canvas = this.game.canvas
    const onBagWheel = (e: WheelEvent) => {
      const rect  = canvas.getBoundingClientRect()
      const cx    = (e.clientX - rect.left) * (canvas.width / rect.width)
      const cy    = (e.clientY - rect.top)  * (canvas.height / rect.height)
      if (cx >= startX && cy >= panelY) {
        e.preventDefault()
        const filtered2 = this._bagTabItems()
        if (e.deltaY > 0 && this.bagScrollOffset + this.BAG_VISIBLE_ROWS < filtered2.length)
          this.bagScrollOffset++
        else if (e.deltaY < 0 && this.bagScrollOffset > 0)
          this.bagScrollOffset--
        else return
        this._rebuildBagPanel()
      }
    }
    canvas.addEventListener('wheel', onBagWheel, { passive: false })
    // Retirer le listener quand on quitte le panel
    this.bagPanel.once('destroy', () => canvas.removeEventListener('wheel', onBagWheel))

    const backEl = this.makeBackButton(startX + 2, panelY + panelH - 14, 48, () => {
      canvas.removeEventListener('wheel', onBagWheel)
      this.showActionPanel()
    })
    this.bagPanel.add(backEl)
  }

  private _buildBagItemRow(item: BattleItem, x: number, y: number, w: number, h: number): void {
    const isUsable = item.item_type === 'potion' || item.item_type === 'medicine'
                  || item.item_type === 'pokeball' || item.item_type === 'battle'
    const baseColor  = isUsable ? 0x1e3a2e : 0x2a2a3a
    const hoverColor = isUsable ? 0x27ae60 : 0x2a2a3a

    const rowBg = this.add.graphics()
    const draw  = (c: number) => {
      rowBg.clear()
      rowBg.fillStyle(c, 1)
      rowBg.fillRoundedRect(0, 0, w, h, 3)
      rowBg.lineStyle(1, isUsable ? 0x27ae60 : 0x3a3a5a, 0.5)
      rowBg.strokeRoundedRect(0, 0, w, h, 3)
    }
    draw(baseColor)

    // Icône item
    const iconKey = `item-icon-${item.id}`
    const iconUrl = this.getItemSpriteUrl(item)
    const icon    = this.add.image(h / 2, h / 2, '__DEFAULT').setDisplaySize(h - 4, h - 4).setOrigin(0.5)
    if (!this.textures.exists(iconKey)) {
      this.load.image(iconKey, iconUrl)
      this.load.once('complete', () => {
        icon.setTexture(iconKey)
        this.textures.get(iconKey).setFilter(Phaser.Textures.FilterMode.LINEAR)
      })
      this.load.once('loaderror', () => {})
      this.load.start()
    } else {
      icon.setTexture(iconKey)
      this.textures.get(iconKey).setFilter(Phaser.Textures.FilterMode.LINEAR)
    }

    // Nom
    const nameText = this.add.text(h + 4, h / 2 - 3, item.name, {
      fontSize: '7px', color: isUsable ? '#ffffff' : '#666688',
      fontFamily: '"Press Start 2P"',
    }).setOrigin(0, 0.5)

    // Quantité — alignée à droite
    const qtyText = this.add.text(w - 14, h / 2, `×${item.quantity}`, {
      fontSize: '8px', color: isUsable ? '#f1c40f' : '#555566',
      fontFamily: '"Press Start 2P"',
    }).setOrigin(1, 0.5)

    const hitZone = this.add.zone(0, 0, w, h).setOrigin(0)
      .setInteractive({ useHandCursor: isUsable })
      .on('pointerover',  () => { if (isUsable) draw(hoverColor) })
      .on('pointerout',   () => draw(baseColor))
      .on('pointerdown',  () => {
        if (!this.waitingForInput || !isUsable) return
        this.sfxConfirm()
        if (item.item_type === 'pokeball') void this.executeBallThrow(item)
        else void this.executeUseItem(item)
      })

    const row = this.add.container(x, y, [rowBg, icon, nameText, qtyText, hitZone]).setDepth(13)
    this.bagPanel.add(row)
  }

  private getItemSpriteUrl(item: BattleItem): string {
    const name = item.name.toLowerCase()
      .replace(/ ball$/, '').replace(/ /g, '-')
      .normalize('NFD').replace(/[̀-ͯ]/g, '')
    if (item.item_type === 'pokeball') return `/static/img/items_sprites/ball/${name}.png`
    if (item.item_type === 'potion')   return `/static/img/items_sprites/medicine/${name}.png`
    if (item.item_type === 'battle') {
      // X-Attack, X-Speed etc. → battle-item / sinon (Repel, Escape Rope…) → other-item
      if (name.startsWith('x-') || name.startsWith('dire') || name.startsWith('guard')) {
        return `/static/img/items_sprites/battle-item/${name}.png`
      }
      return `/static/img/items_sprites/other-item/${name}.png`
    }
    return `/static/img/items_sprites/other-item/${name}.png`
  }

  // ─────────────────────────────────────────────────────────────
  // PANEL SWITCH POKÉMON
  // ─────────────────────────────────────────────────────────────

  /** Switch forcé : le Pokémon joueur vient de tomber K.O. — pas de retour possible */
  private async showForcedSwitchPanel(): Promise<void> {
    this.waitingForInput = true
    this.actionPanel.setVisible(false)
    this.movesPanel.setVisible(false)
    this.bagPanel.setVisible(false)
    this.switchPanel.removeAll(true)

    // Message d'urgence dans le log
    this.showLog(`${this.state.player_pokemon.name}\nest K.O. !\nChoisissez un\nremplaçant !`)

    try {
      const { team } = await battleApi.getTeam(this.trainerId)
      this._buildForcedSwitchButtons(team)
    } catch {
      this.showLog('Erreur chargement\nde l\'équipe.')
    }

    this.switchPanel.setVisible(true)
  }

  private _buildForcedSwitchButtons(
    team: { id: number; name: string; species_name: string; current_hp: number; max_hp: number; level: number; status: string | null }[]
  ): void {
    const W      = this.cameras.main.width
    const H      = this.cameras.main.height
    const panelH = 112
    const panelY = H - panelH
    const startX = W * 0.36
    const totalW = W - startX - 4
    const cols   = 2
    const gap    = 3
    const btnW   = (totalW - gap) / 2

    // Bandeau d'urgence rouge en lieu du bouton retour
    const urgBg = this.add.graphics()
    urgBg.fillStyle(0x7b1c1c, 1)
    urgBg.fillRoundedRect(startX, panelY + 2, totalW, 18, 4)
    urgBg.lineStyle(1, 0xe74c3c, 0.8)
    urgBg.strokeRoundedRect(startX, panelY + 2, totalW, 18, 4)
    this.switchPanel.add(urgBg)

    const urgLabel = this.add.text(startX + totalW / 2, panelY + 11,
      '⚠ Choisissez un remplaçant !', {
        fontSize: '7px', color: '#ff6b6b',
        fontFamily: '"Press Start 2P"',
      }).setOrigin(0.5).setDepth(14)
    this.switchPanel.add(urgLabel)

    const ITEMS_Y = panelY + 24
    const ITEMS_H = panelY + panelH - ITEMS_Y - 2
    const itemH   = Math.floor((ITEMS_H - gap * 2) / 3)

    const activePokemonId = this.state.player_pokemon.id

    team.slice(0, 6).forEach((poke, i) => {
      const col = i % cols
      const row = Math.floor(i / cols)
      const x   = startX + col * (btnW + gap)
      const y   = ITEMS_Y + row * (itemH + gap)

      const isActive = poke.id === activePokemonId   // le K.O.
      const isKo     = poke.current_hp <= 0
      const disabled = isKo                           // seul critère : PV à 0

      const hpRatio   = poke.current_hp / poke.max_hp
      const hpColor   = isKo ? '#666' : hpRatio > 0.5 ? '#2ecc71' : hpRatio > 0.25 ? '#f39c12' : '#e74c3c'
      // K.O. actuel affiché en rouge foncé, K.O. autres en gris, disponibles en bleu
      const baseColor = isActive ? 0x5a1a1a : isKo ? 0x332222 : 0x2c3e7a
      const hoverColor = 0x3d5aad

      const bg = this.add.graphics()
      const draw = (c: number) => {
        bg.clear()
        bg.fillStyle(c, 1)
        bg.fillRoundedRect(0, 0, btnW, itemH, 4)
        // Bordure rouge sur le K.O. actuel, normale sinon
        bg.lineStyle(1, isActive ? 0xe74c3c : 0xffffff, disabled ? 0.1 : 0.15)
        bg.strokeRoundedRect(0, 0, btnW, itemH, 4)
      }
      draw(baseColor)

      const ICON_PX    = Math.min(20, itemH - 2)
      const fileName   = this._spriteFileName(poke.species_name)
      const speciesKey = `switch-icon-${fileName}`
      const spriteEl   = this.add.image(ICON_PX / 2 + 3, itemH / 2, '__DEFAULT')
        .setDisplaySize(ICON_PX, ICON_PX).setOrigin(0.65).setAlpha(disabled ? 0.3 : 1)

      const applyAndSmooth = (key: string) => {
        spriteEl.setTexture(key)
        this.textures.get(key).setFilter(Phaser.Textures.FilterMode.LINEAR)
      }
      if (this.textures.exists(speciesKey)) {
        applyAndSmooth(speciesKey)
      } else {
        this.load.image(speciesKey, `/static/img/sprites_icons/${fileName}.png`)
        this.load.once('complete', () => applyAndSmooth(speciesKey))
        this.load.once('loaderror', () => {
          this.load.image(speciesKey, `/static/img/sprites_gen5/normal/${fileName}.png`)
          this.load.once('complete', () => applyAndSmooth(speciesKey))
          this.load.start()
        })
        this.load.start()
      }

      const textX      = ICON_PX + 8
      const maxNameLen = Math.floor((btnW - textX - 4) / 6)
      const displayName = poke.name.length > maxNameLen ? poke.name.slice(0, maxNameLen) + '…' : poke.name

      const nameLabel = this.add.text(textX, itemH / 2 - 6,
        `${displayName}  Nv.${poke.level}`, {
          fontSize: '9px', color: disabled ? '#666' : '#fff',
          fontFamily: '"Inter", "Segoe UI", sans-serif', fontStyle: 'bold',
        }).setOrigin(0, 0.5)

      const hpLabel = this.add.text(textX, itemH / 2 + 6,
        isKo ? 'K.O.' : `PV ${poke.current_hp}/${poke.max_hp}`, {
          fontSize: '8px', color: hpColor,
          fontFamily: '"Inter", "Segoe UI", sans-serif',
        }).setOrigin(0, 0.5)

      const zone = this.add.zone(0, 0, btnW, itemH).setOrigin(0)
        .setInteractive({ useHandCursor: !disabled })
        .on('pointerover', () => { if (!disabled) draw(hoverColor) })
        .on('pointerout',  () => draw(baseColor))
        .on('pointerdown', () => {
          if (!this.waitingForInput || disabled) return
          this.sfxConfirm()
          void this.executeSwitchPokemon(poke.id)
        })

      this.switchPanel.add(
        this.add.container(x, y, [bg, spriteEl, nameLabel, hpLabel, zone]).setDepth(13)
      )
    })
  }

   private async showSwitchPanel(): Promise<void> {
    if (!this.waitingForInput) return
    this.actionPanel.setVisible(false)
    this.movesPanel.setVisible(false)
    this.bagPanel.setVisible(false)
    this.showLog('Quel Pokémon\nenvoyer ?')

    this.switchPanel.removeAll(true)

    try {
      const { team } = await battleApi.getTeam(this.trainerId)
      this.buildSwitchButtons(team)
    } catch {
      this.showLog('Erreur chargement\nde l\'équipe.')
      this.showActionPanel()
      return
    }

    this.switchPanel.setVisible(true)
  }

  private buildSwitchButtons(team: { id: number; name: string; species_name: string; current_hp: number; max_hp: number; level: number; status: string | null }[]): void {
    const W = this.cameras.main.width
    const H = this.cameras.main.height
    const panelH = 112
    const panelY = H - panelH
    const startX = W * 0.36
    const totalW = W * 0.62
    const cols   = 2
    const gap    = 3
    const btnW   = (totalW - gap) / 2
    const BACK_H  = 20
    const BACK_Y  = panelY + 4
    const ITEMS_Y = BACK_Y + BACK_H + 3
    const ITEMS_H = panelY + panelH - ITEMS_Y - 2
    const itemH   = Math.floor((ITEMS_H - gap * 2) / 3)

    const backEl = this.makeBackButton(startX, BACK_Y, totalW, () => this.showActionPanel())
    this.switchPanel.add(backEl)

    const activePokemonId = this.state.player_pokemon.id

    if (!team.length) {
      const txt = this.add.text(startX + totalW / 2, panelY + 60,
        'Équipe vide', {
          fontSize: '8px', color: '#aaa',
          fontFamily: '"Inter", "Segoe UI", sans-serif', align: 'center',
        }).setOrigin(0.5)
      this.switchPanel.add(txt)
      return
    }

    team.slice(0, 6).forEach((poke, i) => {
      const col = i % cols
      const row = Math.floor(i / cols)
      const x   = startX + col * (btnW + gap)
      const y   = ITEMS_Y + row * (itemH + gap)

      const isActive = poke.id === activePokemonId
      const isKo     = poke.current_hp <= 0
      const disabled = isActive || isKo

      const hpRatio   = poke.current_hp / poke.max_hp
      const hpColor   = isKo ? '#888' : hpRatio > 0.5 ? '#2ecc71' : hpRatio > 0.25 ? '#f39c12' : '#e74c3c'
      const baseColor = isActive ? 0x555566 : isKo ? 0x443333 : 0x2c3e7a

      const bg = this.add.graphics()
      const draw = (c: number) => {
        bg.clear()
        bg.fillStyle(c, 1)
        bg.fillRoundedRect(0, 0, btnW, itemH, 4)
        bg.lineStyle(1, 0xffffff, disabled ? 0.05 : 0.15)
        bg.strokeRoundedRect(0, 0, btnW, itemH, 4)
      }
      draw(baseColor)

      // Icône Pokémon — taille fixe garantie dans le bouton
      const ICON_PX    = Math.min(20, itemH - 2)
      const fileName   = this._spriteFileName(poke.species_name)
      const speciesKey = `switch-icon-${fileName}`
      const spriteEl   = this.add.image(ICON_PX / 2 + 3, itemH / 2, '__DEFAULT')
        .setDisplaySize(ICON_PX, ICON_PX).setOrigin(0.65).setAlpha(disabled ? 0.4 : 1)

      const applyAndSmooth = (key: string) => {
        spriteEl.setTexture(key)
        // Interpolation linéaire — évite le rendu pixelisé sur les petites icônes
        this.textures.get(key).setFilter(Phaser.Textures.FilterMode.LINEAR)
      }

      const tryLoad = (url: string, fallbackUrl?: string) => {
        if (this.textures.exists(speciesKey)) { applyAndSmooth(speciesKey); return }
        this.load.image(speciesKey, url)
        this.load.once('complete', () => applyAndSmooth(speciesKey))
        this.load.once('loaderror', () => {
          if (fallbackUrl) {
            this.load.image(speciesKey, fallbackUrl)
            this.load.once('complete', () => applyAndSmooth(speciesKey))
            this.load.start()
          }
        })
        this.load.start()
      }
      tryLoad(
        `/static/img/sprites_icons/${fileName}.png`,
        `/static/img/sprites_gen5/normal/${fileName}.png`,
      )

      const textX = ICON_PX + 8
      const maxNameLen = Math.floor((btnW - textX - 4) / 6)
      const displayName = poke.name.length > maxNameLen ? poke.name.slice(0, maxNameLen) + '…' : poke.name
      const nameColor = disabled ? '#999' : '#fff'

      const nameLabel = this.add.text(textX, itemH / 2 - 6,
        `${displayName}  Nv.${poke.level}`, {
          fontSize: '9px', color: nameColor,
          fontFamily: '"Inter", "Segoe UI", sans-serif', fontStyle: 'bold',
        }).setOrigin(0, 0.5)

      const hpLabel = this.add.text(textX, itemH / 2 + 6,
        isKo ? 'K.O.' : `PV ${poke.current_hp}/${poke.max_hp}`, {
          fontSize: '8px', color: hpColor,
          fontFamily: '"Inter", "Segoe UI", sans-serif',
        }).setOrigin(0, 0.5)

      const zone = this.add.zone(0, 0, btnW, itemH).setOrigin(0)
        .setInteractive({ useHandCursor: !disabled })
        .on('pointerover',  () => !disabled && draw(0x3d5aad))
        .on('pointerout',   () => draw(baseColor))
        .on('pointerdown',  () => {
          if (!this.waitingForInput || disabled) return
          this.sfxConfirm()
          void this.executeSwitchPokemon(poke.id)
        })

      this.switchPanel.add(this.add.container(x, y, [bg, spriteEl, nameLabel, hpLabel, zone]).setDepth(13))
    })
  }

  // ─────────────────────────────────────────────────────────────
  // HELPER — bouton retour réutilisable
  // ─────────────────────────────────────────────────────────────

  private makeBackButton(x: number, y: number, w: number, cb: () => void): Phaser.GameObjects.Container {
    const bg = this.add.graphics()
    const draw = (c: number) => {
      bg.clear()
      bg.fillStyle(c, 1)
      bg.fillRoundedRect(0, 0, w, 18, 4)
    }
    draw(0x34495e)
    const label = this.add.text(w / 2, 9, '← RETOUR', {
      fontSize: '8px', color: '#ccc', fontFamily: '"Press Start 2P"',
    }).setOrigin(0.5)
    const zone = this.add.zone(0, 0, w, 18).setOrigin(0)
      .setInteractive({ useHandCursor: true })
      .on('pointerover',  () => draw(0x4a6278))
      .on('pointerout',   () => draw(0x34495e))
      .on('pointerdown',  () => { this.sfxCancel(); cb() })
    return this.add.container(x, y, [bg, label, zone]).setDepth(13)
  }

  // ─────────────────────────────────────────────────────────────
  // ACTIONS — Switch & Item
  // ─────────────────────────────────────────────────────────────

  private async executeSwitchPokemon(pokemonId: number): Promise<void> {
    if (!this.waitingForInput) return
    this.waitingForInput = false
    this.switchPanel.setVisible(false)
    this.showLog('Changement\nde Pokémon...')

    const ballUrl = '/static/img/items_sprites/ball/poke.png'

    // ── Animation sortie du Pokémon actuel ──────────────────────
    if (this.playerSprite && !this.playerFainted) {
      this.playerIdleTween?.stop()
      this.playerIdleTween = null
      AudioManager.instance?.playUiSfx('SFX_BALL_POOF')
      await this.animator.animateSwitchOut(this.playerSprite, ballUrl)
    }

    try {
      const response = await battleApi.switchPokemon(this.battleId, pokemonId)
      this.state = response
      await this.showLogSequence(response.log)

      // Cri du Pokémon entrant
      const dex = response.player_pokemon.dex_number
      if (dex) AudioManager.instance?.playCry(dex)

      // Recharger le sprite et animer l'entrée en pokeball
      this.playerFainted = false
      await this.reloadPlayerSprite()
      this.renderState()
      this.rebuildMovesPanel()

      if (response.battle_ended) {
        await this.handleBattleEnd()
      } else {
        this.showActionPanel()
      }
    } catch (err) {
      console.error('Erreur switch:', err)
      this.showLog('Erreur — réessaie.')
      this.waitingForInput = true
      this.showActionPanel()
    }
  }

  private async executeUseItem(item: BattleItem): Promise<void> {
    if (!this.waitingForInput) return
    this.waitingForInput = false
    this.bagPanel.setVisible(false)
    this.showLog(`Utilisation\nde ${item.name}...`)

    try {
      if (item.item_type === 'pokeball') {
        await this.executeBallThrow(item)
      } else {
        const response = await battleApi.useItem(this.battleId, item.id)
        this.state = response
        await this.showLogSequence(response.log)
        this.renderState()
        if (response.battle_ended) {
          await this.handleBattleEnd()
        } else {
          this.showActionPanel()
        }
      }
    } catch (err) {
      console.error('Erreur item:', err)
      this.showLog('Erreur — réessaie.')
      this.waitingForInput = true
      this.showActionPanel()
    }
  }

  // Système Pokéball en 2 temps : throw → animation visuelle → confirm
  private async executeBallThrow(item: BattleItem): Promise<void> {
    try {
      // Étape 1 : Django pré-calcule le résultat et retourne capture_attempt
      const throwResp = await battleApi.throwBall(this.battleId, item.id)

      const attempt = (throwResp as unknown as Record<string, unknown>)['capture_attempt'] as {
        shakes: number
        success: boolean
        pokemon: { species_name: string }
      } | undefined

      if (!attempt) {
        // Pas de capture_attempt → traiter comme réponse normale
        this.state = throwResp
        await this.showLogSequence(throwResp.log)
        this.renderState()
        if (throwResp.battle_ended) await this.handleBattleEnd()
        else this.showActionPanel()
        return
      }

      // Étape 2 : Animation complète de la Pokéball
      const pokeName = attempt.pokemon?.species_name ?? 'Pokémon'
      this.appendLog(`Une Poké Ball lancée\nsur ${pokeName} !`)

      const W = this.cameras.main.width, H = this.cameras.main.height
      const throwerPos = { x: W * 0.28, y: H * 0.62 }
      const targetPos  = { x: this.opponentSprite.x, y: this.opponentSprite.y }

      // SFX lancer
      AudioManager.instance?.playUiSfx('SFX_BALL_TOSS')

      await this.animator.animateBallThrow(
        this.opponentSprite,
        throwerPos,
        targetPos,
        attempt.shakes,
        attempt.success,
        this.getItemSpriteUrl(item),
        () => AudioManager.instance?.playUiSfx('SFX_TINK'),
      )

      // SFX résultat (légèrement avant la fin pour coller à l'animation)
      if (attempt.success) {
        AudioManager.instance?.playUiSfx('SFX_CAUGHT_MON')
        this.appendLog('Capturé !')
      } else {
        AudioManager.instance?.playSfx('capture', 'failed')
        this.appendLog(`${pokeName} s'est échappé !`)
      }

      // Petit délai pour lire le message
      await new Promise(r => this.time.delayedCall(800, r))

      // Étape 3 : Confirmer la capture (Django finalise)
      const confirmResp = await battleApi.confirmCapture(this.battleId, item.id)
      this.state = confirmResp

      // Si échec : l'adversaire riposte — jouer son animation d'attaque
      if (!attempt.success) {
        const splitIdx    = this._findLogSplit(confirmResp.log)
        const playerLogs  = confirmResp.log.slice(0, splitIdx)
        const opponentLogs = confirmResp.log.slice(splitIdx)

        this._renderOpponentHp(confirmResp)
        await this.showLogSequence(playerLogs)

        if (!confirmResp.turn_info.second_skipped && opponentLogs.length > 0
            && confirmResp.player_pokemon.current_hp > 0) {
          const oppMove = this._extractOpponentMove(opponentLogs, confirmResp.opponent_pokemon.name)
          this.animator.playMoveAnimation(
            oppMove.name,
            targetPos, throwerPos,
            this.opponentSprite, this.playerSprite,
            false,
            oppMove.type,
            oppMove.category,
            this.opponentIdleTween, this.playerIdleTween,
          )
          if (oppMove.sfxName) AudioManager.instance?.playMoveSfx(oppMove.sfxName)
          await new Promise<void>(r => this.time.delayedCall(1100, r))
        }

        this._renderPlayerHp(confirmResp)
        await this.showLogSequence(opponentLogs)
        this._renderNames(confirmResp)
        this._renderStatuses(confirmResp)
        this._checkLevelUp(confirmResp)
        this.animateHit()
      } else {
        await this.showLogSequence(confirmResp.log)
        this.renderState()
      }

      if (confirmResp.battle_ended) {
        await this.handleBattleEnd()
      } else {
        this.showActionPanel()
      }
    } catch (err) {
      console.error('Erreur ball throw:', err)
      this.showLog('Erreur — réessaie.')
      this.waitingForInput = true
      this.showActionPanel()
    }
  }

  // ─────────────────────────────────────────────────────────────
  // RELOAD SPRITE JOUEUR (après switch)
  // ─────────────────────────────────────────────────────────────

  private rebuildMovesPanel(): void {
    const W = this.cameras.main.width
    const H = this.cameras.main.height
    const panelH = 112
    const panelY = H - panelH
    this.movesPanel.destroy()
    this.movesPanel = this.buildMovesButtons(W, H, panelY, panelH)
    this.movesPanel.setVisible(false)
  }

  private async reloadPlayerSprite(): Promise<void> {
    const W = this.cameras.main.width
    const H = this.cameras.main.height
    const pp = this.state.player_pokemon
    const ppName   = this._spriteFileName(pp.species_name)
    const ppFolder = pp.is_shiny ? 'back-shiny' : 'back'
    const ppKey    = `sprite-back-${pp.is_shiny ? 'shiny-' : ''}${ppName}`

    await this.loadSpriteIfNeeded(ppKey, ppFolder, ppName)

    if (this.playerSprite) this.playerSprite.destroy()

    const playerFinalX = W * 0.28
    const playerFinalY = H * 0.72
    const ballUrl      = '/static/img/items_sprites/ball/poke.png'

    this.playerSprite = this.add.image(playerFinalX, playerFinalY, ppKey)
      .setDepth(5).setScale(0).setAlpha(0).setOrigin(0.5, 1)

    // Lire la hauteur naturelle AVANT que animateIntroEntry ne mette scale=0
    this.playerSprite.setScale(2.2)
    const ppSpriteH = this.playerSprite.displayHeight
    this.playerSprite.setScale(0)

    AudioManager.instance?.playUiSfx('SFX_BALL_POOF')

    await this.animator.animateIntroEntry(
      this.playerSprite,
      2.2,
      { x: playerFinalX - 60, y: H + 20 },
      { x: playerFinalX, y: playerFinalY - ppSpriteH * 0.5 },
      ballUrl,
      -160,
    )
    if (this.playerIdleTween) this.playerIdleTween.stop()
    this.playerIdleTween = this.animator.startIdle(this.playerSprite)
  }

  // ─────────────────────────────────────────────────────────────
  // FIN DE COMBAT
  // ─────────────────────────────────────────────────────────────

  // ─────────────────────────────────────────────────────────────
  // ÉVOLUTION — délègue à EvolutionScene
  // ─────────────────────────────────────────────────────────────

  private _launchEvolution(evo: PendingEvolution): Promise<void> {
    return new Promise<void>(resolve => {
      // Masquer les panels, bloquer l'input
      this.waitingForInput = false
      this.actionPanel.setVisible(false)
      this.movesPanel.setVisible(false)
      this.bagPanel.setVisible(false)
      this.switchPanel.setVisible(false)

      // Écouter le signal de fin d'évolution
      this.events.once('evolution-done', (updatedState: unknown) => {
        // Mettre à jour le state si confirmEvolution a retourné un état frais
        if (updatedState) this.state = updatedState as typeof this.state
        // Mettre à jour le sprite joueur avec la nouvelle espèce, puis débloquer
        this._refreshPlayerSpriteAfterEvolution().then(resolve)
      })

      // Lancer la scène d'évolution par-dessus BattleScene
      this.scene.launch('EvolutionScene', {
        battleId:       this.battleId,
        evolution_id:   evo.evolution_id,
        from_name:      evo.from_name,
        to_name:        evo.to_name,
        from_species_id: evo.from_species_id,
        to_species_id:  evo.to_species_id,
        is_shiny:       evo.is_shiny,
      })
    })
  }

  private async _refreshPlayerSpriteAfterEvolution(): Promise<void> {
    // Recharger l'état depuis le state (mis à jour par confirmEvolution)
    const pp     = this.state.player_pokemon
    const folder = pp.is_shiny ? 'back-shiny' : 'back'
    const name   = this._spriteFileName(pp.species_name)
    const key    = `sprite-back-${pp.is_shiny ? 'shiny-' : ''}${name}`

    await this.loadSpriteIfNeeded(key, folder, name)

    if (this.playerSprite) this.playerSprite.destroy()
    const W = this.cameras.main.width
    const H = this.cameras.main.height
    this.playerSprite = this.add.image(W * 0.28, H * 0.72, key)
      .setDepth(5).setScale(2.2).setOrigin(0.5, 1)

    if (this.playerIdleTween) this.playerIdleTween.stop()
    this.playerIdleTween = this.animator.startIdle(this.playerSprite)

    this.renderState()
    this.rebuildMovesPanel()
  }

  private async handleBattleEnd(): Promise<void> {
    this.waitingForInput = false
    emit('battle-ended', this.battleId)

    // Couper toute BGM en cours (combat ou évolution) + SFX résiduels
    AudioManager.instance?.stopBgm()
    AudioManager.instance?.stopAllSfx()

    // SFX victoire/défaite
    const playerWon = this.state.player_pokemon.current_hp > 0
    AudioManager.instance?.playSfx('battle', playerWon ? 'victory' : 'defeat')

    await new Promise(r => setTimeout(r, 4200))

    // Couper le SFX victoire/défaite avant le retour en zone
    AudioManager.instance?.stopAllSfx()

    // Reprendre la musique de zone avec fondu enchaîné
    AudioManager.instance?.resumeZone()

    this.scene.stop('BattleScene')
    const gameScene = this.scene.get('GameScene') as { resumeFromBattle?: () => void }
    gameScene.resumeFromBattle?.()
  }
}