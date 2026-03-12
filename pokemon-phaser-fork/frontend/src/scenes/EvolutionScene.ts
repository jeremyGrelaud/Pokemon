// ============================================================
// scenes/EvolutionScene.ts
// Scène d'évolution Pokémon — lancée depuis BattleScene
// après la fin du combat (ou pendant si level-up mid-combat).
//
// Données reçues via scene.launch('EvolutionScene', data) :
//   battleId, evolution_id, from_name, to_name,
//   from_species_id, to_species_id, is_shiny
//
// Séquence :
//   1. Fondu noir depuis BattleScene
//   2. Musique évolution (static/sounds/bgm/kanto/pokemon-evolution-sound-effect.mp3)
//   3. Sprite "from" visible en bas de l'écran
//   4. Flash blanc accéléré (8 cycles)
//   5. Silhouette blanche → swap texture "to"
//   6. Révélation couleur progressive
//   7. Bounce + cri du nouveau Pokémon
//   8. confirm_evolution → backend
//   9. Log "{from} évolue en {to} !"
//  10. Fondu sortie → signal 'evolution-done' → BattleScene reprend
// ============================================================

import Phaser from 'phaser'
import { AudioManager } from './AudioManager'
import { battleApi }    from '@api/djangoClient'

interface EvolutionData {
  battleId:      number
  evolution_id:  number
  from_name:     string
  to_name:       string
  from_species_id: number
  to_species_id:   number
  is_shiny:      boolean
}

const SPRITE_BASE = '/static/img/sprites_gen5'

export class EvolutionScene extends Phaser.Scene {

  constructor() {
    super({ key: 'EvolutionScene' })
  }

  // ─────────────────────────────────────────────────────────────
  // HELPERS
  // ─────────────────────────────────────────────────────────────

  private delay(ms: number): Promise<void> {
    return new Promise(r => this.time.delayedCall(ms, r))
  }

  private spriteFileName(name: string): string {
    return name.toLowerCase().replace(/♂/g, 'm').replace(/♀/g, 'f')
  }

  private loadSprite(key: string, folder: string, name: string): Promise<void> {
    if (this.textures.exists(key)) return Promise.resolve()
    return new Promise(resolve => {
      this.load.image(key, `${SPRITE_BASE}/${folder}/${name}.png`)
      this.load.once('complete',   resolve)
      this.load.once('loaderror', resolve)
      this.load.start()
    })
  }

  // ─────────────────────────────────────────────────────────────
  // CREATE
  // ─────────────────────────────────────────────────────────────

  async create(data: EvolutionData): Promise<void> {
    const W = this.cameras.main.width
    const H = this.cameras.main.height

    // ── Fond noir total ──────────────────────────────────────────
    this.add.rectangle(0, 0, W, H, 0x000000, 1).setOrigin(0).setDepth(0)

    // ── Fondu depuis BattleScene ─────────────────────────────────
    this.cameras.main.setAlpha(0)
    this.tweens.add({ targets: this.cameras.main, alpha: 1, duration: 500 })
    await this.delay(500)

    // ── Musique ──────────────────────────────────────────────────
    AudioManager.instance?.stopBgm()
    await this.delay(200)
    AudioManager.instance?.playBgmOneShot('pokemon-evolution-sound-effect')

    // ── Charger les deux sprites (front) ─────────────────────────
    const folder   = data.is_shiny ? 'shiny' : 'normal'
    const fromFile = this.spriteFileName(data.from_name)
    const toFile   = this.spriteFileName(data.to_name)
    const fromKey  = `evo-from-${fromFile}`
    const toKey    = `evo-to-${toFile}`

    await this.loadSprite(fromKey, folder, fromFile)
    await this.loadSprite(toKey,   folder, toFile)

    // ── Sprite centré, légèrement au-dessus du centre ────────────
    const spriteY = H * 0.55
    const sprite  = this.add.image(W / 2, spriteY, fromKey)
      .setDepth(2).setScale(2.2).setOrigin(0.5, 0.5)

    // ── Texte bas de l'écran ─────────────────────────────────────
    const msgBox = this.add.graphics().setDepth(4)
    msgBox.fillStyle(0x111111, 0.92)
    msgBox.fillRoundedRect(10, H - 72, W - 20, 60, 8)
    msgBox.lineStyle(1, 0x444444, 1)
    msgBox.strokeRoundedRect(10, H - 72, W - 20, 60, 8)

    const msgText = this.add.text(W / 2, H - 42, `Quoi ? ${data.from_name}\névolue !`, {
      fontSize: '8px', color: '#ffffff',
      fontFamily: '"Press Start 2P"', align: 'center',
      lineSpacing: 6,
    }).setOrigin(0.5).setDepth(5)

    await this.delay(2000)   // ~2.7s écoulées

    // ── Flash blanc accéléré — 12 cycles ────────────────────────
    // + rotation légère + pulse scale pendant les flashes
    const baseScale = 2.2
    let pulseTween: Phaser.Tweens.Tween | null = this.tweens.add({
      targets: sprite,
      scaleX: baseScale * 1.06, scaleY: baseScale * 1.06,
      duration: 200, ease: 'Sine.easeInOut',
      yoyo: true, repeat: -1,
    })

    for (let i = 0; i < 12; i++) {
      const half = Math.max(28, 210 - i * 15)

      // Flip horizontal au milieu des cycles (effet miroir)
      if (i === 4) {
        this.tweens.add({ targets: sprite, scaleX: -baseScale * 1.06, duration: half, ease: 'Linear' })
      }
      if (i === 8) {
        this.tweens.add({ targets: sprite, scaleX: baseScale * 1.06, duration: half, ease: 'Linear' })
      }

      await new Promise<void>(resolve => {
        this.tweens.add({
          targets: sprite, alpha: 0,
          duration: half, ease: 'Linear',
          onComplete: () => {
            sprite.setTint(0xffffff)
            this.tweens.add({
              targets: sprite, alpha: 1,
              duration: half, ease: 'Linear',
              onComplete: () => { sprite.clearTint(); resolve() },
            })
          },
        })
      })
    }

    // Arrêter pulse + remettre scale/flip normaux
    pulseTween.stop()
    pulseTween = null
    sprite.setScale(baseScale).setFlipX(false)  // ~7.5s écoulées

    // ── Silhouette blanche fixe ──────────────────────────────────
    sprite.setTint(0xffffff).setAlpha(1)
    await this.delay(800)   // ~8.3s

    // ── Swap texture → nouveau Pokémon ───────────────────────────
    sprite.setTexture(toKey)
    sprite.setScale(baseScale)

    // ── Overlay blanc couvrant EXACTEMENT les bounds du nouveau sprite
    // Calculer après setTexture pour avoir les bonnes dimensions
    const sw = sprite.displayWidth
    const sh = sprite.displayHeight
    const sx = sprite.x - sw / 2
    const sy = sprite.y - sh / 2

    const overlay = this.add.graphics().setDepth(3)
    overlay.fillStyle(0xffffff, 1)
    overlay.fillRect(sx, sy, sw, sh)

    // ── Révélation progressive ───────────────────────────────────
    await new Promise<void>(resolve => {
      this.tweens.add({
        targets: overlay, alpha: 0, duration: 1800, ease: 'Sine.easeOut',
        onComplete: () => { overlay.destroy(); resolve() },
      })
    })
    sprite.clearTint()   // ~10.1s

    // ── Bounce d'apparition ──────────────────────────────────────
    await new Promise<void>(resolve => {
      this.tweens.add({
        targets: sprite,
        scaleX: baseScale * 1.15, scaleY: baseScale * 1.15,
        duration: 260, ease: 'Back.easeOut', yoyo: true,
        onComplete: () => { sprite.setScale(baseScale); resolve() },
      })
    })   // ~10.4s

    // ── Cri du nouveau Pokémon ───────────────────────────────────
    AudioManager.instance?.playCry(data.to_species_id)
    await this.delay(1200)   // ~11.6s

    // ── Confirmer côté backend ───────────────────────────────────
    let logLine = `${data.from_name} évolue en ${data.to_name} !`
    let updatedState: unknown = null
    try {
      const resp = await battleApi.confirmEvolution(data.battleId, data.evolution_id)
      if (resp.log?.[0]) logLine = resp.log[0]
      updatedState = resp
    } catch (err) {
      console.error('[EvolutionScene] confirm_evolution error:', err)
    }

    // ── Log résultat ─────────────────────────────────────────────
    msgText.setText(logLine).setWordWrapWidth(W - 40)

    // Idle bob sur le nouveau sprite pendant la lecture du log
    this.tweens.add({
      targets: sprite, y: spriteY - 6,
      duration: 700, ease: 'Sine.easeInOut',
      yoyo: true, repeat: -1,
    })

    await this.delay(5500)   // ~17.1s + fondu = ~20s

    // ── Fondu sortie ─────────────────────────────────────────────
    await new Promise<void>(resolve => {
      this.tweens.add({
        targets: this.cameras.main, alpha: 0, duration: 800,
        onComplete: () => resolve(),
      })
    })   // ~20s total

    // ── Signaler à BattleScene et reprendre ─────────────────────
    this.scene.stop('EvolutionScene')
    this.scene.get('BattleScene')?.events.emit('evolution-done', updatedState)
  }
}