// ============================================================
// scenes/UIScene.ts
// HUD : zone actuelle, mini-map, menu, etc.
// Tourne en parallèle de GameScene.
// ============================================================

import Phaser from 'phaser'
import { EventBus } from '@utils/EventBus'
import { AudioManager } from './AudioManager'
import type { ZoneDetailData } from '@/types'

export class UIScene extends Phaser.Scene {

  private zoneText!: Phaser.GameObjects.Text
  private menuVisible = false

  constructor() {
    super({ key: 'UIScene' })
  }

  create(): void {
    const W = this.cameras.main.width

    // ── Bandeau de zone (en haut) ─────────────────────────────
    this.add.rectangle(0, 0, W, 18, 0x000000, 0.6)
      .setOrigin(0, 0).setDepth(100)

    this.zoneText = this.add.text(W / 2, 9, '...', {
      fontSize: '7px',
      color: '#ffffff',
      fontFamily: '"Press Start 2P"',
    }).setOrigin(0.5).setDepth(101)

    // ── Touche menu ───────────────────────────────────────────
    this.input.keyboard!.on('keydown-ESC', () => this.toggleMenu())
    this.input.keyboard!.on('keydown-ENTER', () => this.toggleMenu())

    // ── Bouton mute (coin haut droit) ────────────────────────
    const muteBtn = this.add.text(W - 8, 9, '🔊', {
      fontSize: '10px', fontFamily: 'sans-serif',
    }).setOrigin(1, 0.5).setDepth(102).setInteractive({ useHandCursor: true })

    muteBtn.on('pointerdown', () => {
      const muted = AudioManager.instance?.toggleMute()
      muteBtn.setText(muted ? '🔇' : '🔊')
    })

    // ── Écouter les changements de zone ───────────────────────
    EventBus.on('zone-changed', (zone: ZoneDetailData) => {
      this.zoneText.setText(zone.name)
    }, this)

    EventBus.on('zone-entered', (zone: ZoneDetailData) => {
      this.zoneText.setText(zone.name)
    }, this)
  }

  private toggleMenu(): void {
    this.menuVisible = !this.menuVisible
    // TODO : lancer une scène MenuScene ou afficher un overlay
    console.log('Menu:', this.menuVisible ? 'ouvert' : 'fermé')
  }

  destroy(): void {
    EventBus.off('zone-changed', undefined, this)
    EventBus.off('zone-entered', undefined, this)
  }
}
