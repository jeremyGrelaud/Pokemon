// ============================================================
// scenes/DialogScene.ts
// Boîte de dialogue générique (messages NPC, notifications).
// ============================================================

import Phaser from 'phaser'

interface DialogData {
  text: string
  autoClose?: number   // ms, 0 = attendre input
}

export class DialogScene extends Phaser.Scene {

  constructor() {
    super({ key: 'DialogScene' })
  }

  create(data: DialogData): void {
    const W = this.cameras.main.width
    const H = this.cameras.main.height

    // Fond de la boîte
    const box = this.add.graphics()
    box.fillStyle(0xffffff, 1)
    box.fillRoundedRect(8, H - 64, W - 16, 56, 4)
    box.lineStyle(2, 0x000000, 1)
    box.strokeRoundedRect(8, H - 64, W - 16, 56, 4)
    box.setDepth(200)

    // Texte
    const text = this.add.text(16, H - 56, data.text, {
      fontSize: '7px',
      color: '#000000',
      fontFamily: '"Press Start 2P"',
      wordWrap: { width: W - 32 },
    }).setDepth(201)

    // Fermeture
    const close = (): void => this.scene.stop('DialogScene')

    if (data.autoClose && data.autoClose > 0) {
      this.time.delayedCall(data.autoClose, close)
    } else {
      // Fermer sur espace / Z / clic
      this.input.keyboard!.once('keydown-SPACE', close)
      this.input.keyboard!.once('keydown-Z',     close)
      this.input.once('pointerdown', close)
    }
  }
}
