// ============================================================
// scenes/BattleAnimator.ts
// Moteur d'animations de combat Phaser 3
// Inspiré de battle-effects.js (sprites PS FX, barres animées, lunge/shake/faint)
//
// Sprites FX chargés depuis : /static/img/fx/<name>.png
// Compatible avec la bibliothèque PS (electroball, fireball, lightning…)
// ============================================================

import Phaser from 'phaser'
import { AudioManager } from './AudioManager'

const FX_BASE = '/static/img/fx/'

// ── Flash de fond par type ───────────────────────────────────────────────────
const TYPE_FLASH: Record<string, number> = {
  fire:     0xff6600, water:    0x4488ff, grass:    0x44cc44,
  electric: 0xffdd00, ice:      0x88eeff, psychic:  0xff44aa,
  ghost:    0x8844cc, dragon:   0x7744ff, rock:     0xccaa44,
  ground:   0xaa8833, poison:   0xaa44aa, bug:      0x88aa44,
  fighting: 0xcc4422, flying:   0x8899ff, dark:     0x553311,
  steel:    0xaaaacc, normal:   0xffffff,
}

type XY = { x: number; y: number }
type MoveAnimFn = (a: BattleAnimator, atk: XY, def: XY, isPlayer?: boolean) => void

function toEase(t: string): string {
  const map: Record<string, string> = {
    decel:     'Quad.easeOut',
    accel:     'Quad.easeIn',
    ballistic: 'Cubic.easeOut',
    swing:     'Sine.easeInOut',
    linear:    'Linear',
  }
  return map[t] ?? 'Linear'
}

export class BattleAnimator {
  private scene:   Phaser.Scene
  private fxLayer: Phaser.GameObjects.Container

  // Ratios précédents pour l'animation des barres
  private prevPlayerHpRatio   = 1
  private prevOpponentHpRatio = 1
  private prevExpPct          = 0

  constructor(scene: Phaser.Scene) {
    this.scene   = scene
    this.fxLayer = scene.add.container(0, 0).setDepth(50)
  }

  /** Initialise le % EXP de départ pour éviter l'animation depuis 0 au premier tour. */
  initExpPct(pct: number): void {
    this.prevExpPct = pct
  }

  // ── Idle bounce ─────────────────────────────────────────────────────────────

  startIdle(sprite: Phaser.GameObjects.Image, delay = 0): Phaser.Tweens.Tween {
    return this.scene.tweens.add({
      targets: sprite, y: sprite.y - 10,
      duration: 1200, ease: 'Sine.easeInOut', yoyo: true, repeat: -1, delay,
    })
  }

  // ── Background flash ─────────────────────────────────────────────────────────

  backgroundEffect(color: number, duration: number, opacity = 1.0, delay = 0): void {
    const W = this.scene.cameras.main.width
    const H = this.scene.cameras.main.height
    const rect = this.scene.add.rectangle(W / 2, H * 0.32, W, H * 0.65, color, 0).setDepth(6)
    const fadeDur = Math.min(180, Math.floor(duration / 3))
    this.scene.time.delayedCall(delay, () => {
      this.scene.tweens.add({
        targets: rect, fillAlpha: opacity, duration: fadeDur,
        onComplete: () => {
          this.scene.time.delayedCall(duration - fadeDur * 2, () => {
            this.scene.tweens.add({
              targets: rect, fillAlpha: 0, duration: fadeDur,
              onComplete: () => rect.destroy(),
            })
          })
        },
      })
    })
  }

  // ── PS FX sprite ─────────────────────────────────────────────────────────────

  showEffect(
    name: string,
    start: { x: number; y: number; scale?: number; opacity?: number; time?: number },
    end:   { x: number; y: number; scale?: number; opacity?: number; time?: number },
    transition = 'decel',
    after?: 'fade' | 'explode',
  ): void {
    const key      = `fx-${name}`
    const delay    = start.time ?? 0
    const duration = Math.max(50, (end.time ?? delay + 400) - delay)
    const ss = start.scale   ?? 1,  es = end.scale   ?? ss
    const sa = start.opacity ?? 1,  ea = end.opacity ?? sa
    const ease = toEase(transition)

    const run = () => {
      if (!this.scene.textures.exists(key)) {
        this.scene.load.image(key, `${FX_BASE}${name}.png`)
        this.scene.load.once('complete', () =>
          this._spawnEffect(key, start.x, start.y, end.x, end.y, ss, es, sa, ea, duration, ease, after))
        this.scene.load.once('loaderror', () => {/* sprite absent — pas d'effet */})
        this.scene.load.start()
      } else {
        this._spawnEffect(key, start.x, start.y, end.x, end.y, ss, es, sa, ea, duration, ease, after)
      }
    }
    delay > 0 ? this.scene.time.delayedCall(delay, run) : run()
  }

  private _spawnEffect(
    key: string,
    sx: number, sy: number, ex: number, ey: number,
    ss: number, es: number, sa: number, ea: number,
    duration: number, ease: string, after?: 'fade' | 'explode',
  ): void {
    if (!this.scene.textures.exists(key)) return
    const img = this.scene.add.image(sx, sy, key).setScale(ss).setAlpha(sa).setDepth(50)
    this.fxLayer.add(img)

    this.scene.tweens.add({
      targets: img, x: ex, y: ey, scaleX: es, scaleY: es, alpha: ea,
      duration, ease,
      onComplete: () => {
        if (after === 'fade') {
          this.scene.tweens.add({
            targets: img, alpha: 0, duration: 100,
            onComplete: () => this.fxLayer.remove(img, true),
          })
        } else if (after === 'explode') {
          this.scene.tweens.add({
            targets: img, scaleX: es * 2.5, scaleY: es * 2.5, alpha: 0,
            duration: 180, ease: 'Quad.easeOut',
            onComplete: () => this.fxLayer.remove(img, true),
          })
        } else {
          this.fxLayer.remove(img, true)
        }
      },
    })
  }

  clearEffects(): void {
    this.fxLayer.removeAll(true)
  }

  // ── Sprite animations ─────────────────────────────────────────────────────────

  attackLunge(
    sprite:    Phaser.GameObjects.Image,
    isPlayer:  boolean,
    idleTween?: Phaser.Tweens.Tween | null,
  ): void {
    const dx    = isPlayer ? -85 : 85
    const origX = sprite.x
    idleTween?.pause()
    this.scene.tweens.killTweensOf(sprite)
    this.scene.tweens.add({
      targets: sprite, x: origX + dx,
      duration: 200, ease: 'Quad.easeOut',
      onComplete: () => {
        this.scene.tweens.add({
          targets: sprite, x: origX,
          duration: 180, ease: 'Quad.easeIn',
          onComplete: () => idleTween?.resume(),
        })
      },
    })
  }

  damageShake(
    sprite:    Phaser.GameObjects.Image,
    delayMs  = 0,
    idleTween?: Phaser.Tweens.Tween | null,
  ): void {
    this.scene.time.delayedCall(delayMs, () => {
      idleTween?.pause()
      const origX = sprite.x
      // Flash blanc via tint
      sprite.setTint(0xffffff)
      this.scene.time.delayedCall(60, () => sprite.clearTint())
      // Vibration
      const proxy = { t: 0 }
      this.scene.tweens.killTweensOf(sprite)
      this.scene.tweens.add({
        targets: proxy, t: 1, duration: 480, ease: 'Linear',
        onUpdate: () => { sprite.x = origX + Math.sin(proxy.t * Math.PI * 7) * 8 },
        onComplete: () => { sprite.x = origX; idleTween?.resume() },
      })
    })
  }

  faintAnim(sprite: Phaser.GameObjects.Image, isPlayer: boolean): void {
    this.scene.tweens.killTweensOf(sprite)
    this.scene.tweens.add({
      targets: sprite,
      y:     sprite.y + 130,
      angle: isPlayer ? 30 : -30,
      alpha: 0,
      duration: 800, ease: 'Quad.easeIn',
    })
  }

  // ── Barre HP animée + shine ───────────────────────────────────────────────────

  animateHpBar(
    g:        Phaser.GameObjects.Graphics,
    currentHp: number,
    maxHp:     number,
    x: number, y: number, maxW: number,
    isPlayer: boolean,
  ): void {
    const newRatio = Math.max(0, currentHp / maxHp)
    const oldRatio = isPlayer ? this.prevPlayerHpRatio : this.prevOpponentHpRatio
    if (isPlayer) this.prevPlayerHpRatio   = newRatio
    else          this.prevOpponentHpRatio = newRatio

    if (Math.abs(newRatio - oldRatio) < 0.001) {
      this._drawHpRatio(g, newRatio, x, y, maxW)
      return
    }

    const proxy = { r: oldRatio }
    this.scene.tweens.add({
      targets: proxy, r: newRatio, duration: 700, ease: 'Cubic.easeOut',
      onUpdate:  () => this._drawHpRatio(g, proxy.r, x, y, maxW),
      onComplete: () => {
        this._drawHpRatio(g, newRatio, x, y, maxW)
        if (newRatio < oldRatio) this._hpShine(x, y, maxW * newRatio, 7)
      },
    })
  }

  private _drawHpRatio(g: Phaser.GameObjects.Graphics, ratio: number, x: number, y: number, maxW: number): void {
    const color = ratio > 0.5 ? 0x2ecc71 : ratio > 0.25 ? 0xf39c12 : 0xe74c3c
    g.clear()
    // Fond
    g.fillStyle(0x2c3e50);  g.fillRoundedRect(x, y, maxW, 7, 3)
    // Barre colorée
    g.fillStyle(color);     g.fillRoundedRect(x, y, maxW * ratio, 7, 3)
    // Liseret brillant en haut de la barre
    if (ratio > 0.02) {
      g.fillStyle(0xffffff, 0.18)
      g.fillRect(x + 2, y + 1, maxW * ratio - 4, 2)
    }
  }

  private _hpShine(x: number, y: number, fillW: number, h: number): void {
    if (fillW < 4) return
    const shine = this.scene.add.graphics().setDepth(11)
    shine.fillStyle(0xffffff, 0.6)
    shine.fillRoundedRect(x, y, 10, h, 2)
    this.scene.tweens.add({
      targets: shine, x: fillW - 4, alpha: 0,
      duration: 280, ease: 'Quad.easeOut',
      onComplete: () => shine.destroy(),
    })
  }

  // ── Barre EXP animée + shimmer ────────────────────────────────────────────────

  /**
   * Anime la barre EXP de oldPct → newPct.
   * @param onExpGain  Callback appelé dès le début de l'animation si l'EXP a augmenté.
   *                   Utilisé pour jouer le SFX exp_gain en sync.
   */
  animateExpBar(
    g:      Phaser.GameObjects.Graphics,
    newPct: number,
    px: number, py: number, pw: number,
    onExpGain?: () => void,
  ): void {
    const oldFrac = this.prevExpPct / 100
    const newFrac = newPct        / 100
    this.prevExpPct = newPct

    // Déclencher le SFX dès que l'EXP progresse réellement
    if (newFrac > oldFrac && onExpGain) onExpGain()

    const proxy = { f: oldFrac }
    this.scene.tweens.add({
      targets: proxy, f: newFrac, duration: 900, ease: 'Quad.easeOut',
      onUpdate: () => {
        g.clear()
        // Barre EXP bleue
        g.fillStyle(0x4080f0); g.fillRect(px + 10, py + 64, pw * proxy.f, 3)
        // Fond gris
        g.fillStyle(0x1a3a6a); g.fillRect(px + 10 + pw * proxy.f, py + 64, pw * (1 - proxy.f), 3)
        // Shimmer statique (trait brillant en haut)
        if (proxy.f > 0.02) {
          g.fillStyle(0xffffff, 0.3)
          g.fillRect(px + 10, py + 64, pw * proxy.f, 1)
        }
      },
      onComplete: () => this._expShimmer(px + 10, py + 64, pw * newFrac),
    })
  }

  private _expShimmer(x: number, y: number, fillW: number): void {
    if (fillW < 4) return
    const shine = this.scene.add.graphics().setDepth(11)
    shine.fillStyle(0xaaccff, 0.75)
    shine.fillRect(x, y, 7, 3)
    // x de l'objet part de 0 → fillW - 5 (position relative au drawn rect)
    this.scene.tweens.add({
      targets: shine, x: fillW - 5, alpha: 0,
      duration: 400, ease: 'Quad.easeOut',
      onComplete: () => shine.destroy(),
    })
  }

  // ── Level-up flash ───────────────────────────────────────────────────────────

  levelUpFlash(boxX: number, boxY: number, boxW: number, boxH: number): void {
    AudioManager.instance?.playUiSfx('SFX_LEVEL_UP')

    const glow  = this.scene.add.graphics().setDepth(9)
    const proxy = { t: 0 }

    this.scene.tweens.add({
      targets: proxy, t: 1,
      duration: 1400, ease: 'Sine.easeInOut', yoyo: true,
      onUpdate: () => {
        const a = proxy.t
        glow.clear()
        glow.lineStyle(3, 0xffd700, a)
        glow.strokeRoundedRect(boxX, boxY, boxW, boxH, 8)
        glow.lineStyle(7, 0xffd700, a * 0.25)
        glow.strokeRoundedRect(boxX - 2, boxY - 2, boxW + 4, boxH + 4, 10)
      },
      onComplete: () => glow.destroy(),
    })

    const badge = this.scene.add.text(boxX + boxW - 8, boxY - 8, 'NIV. UP!', {
      fontSize: '8px', fontFamily: '"Press Start 2P"',
      color: '#fff', backgroundColor: '#f0932b',
      padding: { x: 4, y: 2 },
    }).setOrigin(1, 1).setDepth(20).setAlpha(0).setScale(0)

    this.scene.tweens.add({
      targets: badge, alpha: 1, scale: 1, duration: 220, ease: 'Back.easeOut',
      onComplete: () => {
        this.scene.time.delayedCall(1400, () => {
          this.scene.tweens.add({
            targets: badge, alpha: 0, y: badge.y - 12, duration: 300,
            onComplete: () => badge.destroy(),
          })
        })
      },
    })
  }

  // ── Animation Poké Ball ──────────────────────────────────────────────────────

  animateBallThrow(
    targetSprite:  Phaser.GameObjects.Image,
    throwerPos:    { x: number; y: number },
    targetPos:     { x: number; y: number },
    shakes:        number,
    success:       boolean,
    ballSpriteUrl: string,
    onShakeTick?:  () => void,
  ): Promise<void> {
    return new Promise((resolve) => {
      const scene = this.scene

      const spriteH = targetSprite.displayHeight
      const tx      = targetPos.x
      const ty      = targetPos.y - spriteH * 0.5    // centre visuel du sprite
      const groundY = targetPos.y - spriteH * 0.25   // au niveau de l'ombre, juste sous les pieds du sprite

      const sx  = throwerPos.x, sy = throwerPos.y
      const arcH = -160

      const ballKey = `__ball__${ballSpriteUrl}`

      const launch = () => {
        const ball = scene.add.image(sx, sy, ballKey)
          .setDepth(60).setOrigin(0.5, 0.5)

        // Cible ~22px à l'écran quelle que soit la taille source du sprite
        const TARGET_PX = 22
        const naturalW  = ball.width || 64
        ball.setScale(TARGET_PX / naturalW)

        const proxy = { t: 0 }
        scene.tweens.add({
          targets: proxy, t: 1, duration: 520, ease: 'Quad.easeOut',
          onUpdate: () => {
            const t    = proxy.t
            const x    = sx + (tx - sx) * t
            const yLin = sy + (ty - sy) * t
            const arc  = arcH * 4 * t * (1 - t)
            ball.setPosition(x, yLin + arc)
            ball.setAngle(ball.angle + 14)
          },
          onComplete: () => {
            this.backgroundEffect(0xffffff, 180, 0.45)
            scene.tweens.add({
              targets: targetSprite,
              scaleX: 0, scaleY: 0, alpha: 0,
              duration: 200, ease: 'Quad.easeIn',
            })
            scene.time.delayedCall(160, () => {
              const fall = { t: 0 }
              scene.tweens.add({
                targets: fall, t: 1, duration: 280, ease: 'Quad.easeIn',
                onUpdate: () => {
                  ball.setPosition(tx, ty + (groundY - ty) * fall.t)
                  ball.setAngle(ball.angle + 7)
                },
                onComplete: () => {
                  ball.setAngle(0)
                  this._doBallShakes(ball, tx, groundY, shakes, success, onShakeTick, () => {
                    ball.destroy()
                    if (!success) {
                      scene.tweens.add({
                        targets: targetSprite,
                        scaleX: 1.6, scaleY: 1.6, alpha: 1,
                        duration: 350, ease: 'Back.easeOut',
                      })
                      this.damageShake(targetSprite, 100)
                    }
                    resolve()
                  })
                },
              })
            })
          },
        })
      }

      if (!scene.textures.exists(ballKey)) {
        scene.load.image(ballKey, ballSpriteUrl)
        scene.load.once('complete', launch)
        scene.load.start()
      } else {
        launch()
      }
    })
  }

  private _doBallShakes(
    ball:     Phaser.GameObjects.Image,
    cx:       number,
    groundY:  number,
    shakes:   number,
    success:  boolean,
    onTick:   (() => void) | undefined,
    onDone:   () => void,
  ): void {
    const scene = this.scene
    let done = 0

    const doOne = (): void => {
      if (done >= shakes) {
        if (success) {
          const proxy = { t: 0 }
          scene.tweens.add({
            targets: proxy, t: 1, duration: 400, ease: 'Sine.easeInOut',
            onUpdate: () => ball.setPosition(cx + Math.sin(proxy.t * Math.PI * 5) * 3, groundY),
            onComplete: onDone,
          })
        } else {
          scene.tweens.add({
            targets: ball, alpha: 0, scaleX: 0.12, scaleY: 0.12,
            duration: 250, ease: 'Quad.easeOut',
            onComplete: onDone,
          })
        }
        return
      }

      onTick?.()

      const proxy = { t: 0 }
      scene.tweens.add({
        targets: proxy, t: 1, duration: 600, ease: 'Sine.easeInOut',
        onUpdate: () => {
          const angle   = Math.sin(proxy.t * Math.PI * 2) * 20
          const bounceY = Math.abs(Math.sin(proxy.t * Math.PI)) * -8
          ball.setAngle(angle)
          ball.setPosition(cx, groundY + bounceY)
        },
        onComplete: () => {
          ball.setAngle(0)
          ball.setPosition(cx, groundY)
          done++
          scene.time.delayedCall(150, doOne)
        },
      })
    }

    doOne()
  }

  playMoveAnimation(
    moveName:     string,
    atkPos:       XY,
    defPos:       XY,
    atkSprite:    Phaser.GameObjects.Image,
    defSprite:    Phaser.GameObjects.Image,
    isPlayer:     boolean,
    moveType    = 'normal',
    moveCategory = '',
    atkIdleTween?: Phaser.Tweens.Tween | null,
    defIdleTween?: Phaser.Tweens.Tween | null,
  ): void {
    this.clearEffects()
    this.attackLunge(atkSprite, isPlayer, atkIdleTween)

    const isStatus = moveCategory === 'status'
    if (!isStatus) this.damageShake(defSprite, 380, defIdleTween)

    const norm = moveName.toLowerCase().replace(/[^a-z0-9]/g, '')
    const fn   = MOVE_ANIMS[norm] ?? MOVE_ANIMS[`__type__${moveType}`]

    if (fn) {
      fn(this, atkPos, defPos, isPlayer)
    } else if (moveCategory === 'physical') {
      this.physicalFallback(atkPos, defPos)
    } else if (!isStatus) {
      this.genericSpecial(atkPos, defPos, moveType)
    }
  }

  // Exposés pour usage dans MOVE_ANIMS
  physicalFallback(atk: XY, def: XY): void {
    this.backgroundEffect(0xffffff, 220, 0.3)
    this.showEffect('rightslash',
      { x: def.x, y: def.y, scale: 0.2, opacity: 1 },
      { x: def.x, y: def.y, scale: 1.3, opacity: 0.6, time: 220 }, 'decel', 'explode')
  }

  genericSpecial(atk: XY, def: XY, moveType: string): void {
    const color = TYPE_FLASH[moveType] ?? 0xffffff
    this.showEffect('wisp',
      { x: atk.x, y: atk.y, scale: 0.3, opacity: 0.8 },
      { x: def.x, y: def.y, scale: 1,   opacity: 0,   time: 400 }, 'decel', 'fade')
    this.backgroundEffect(color, 300, 0.15, 370)
  }

  // ─────────────────────────────────────────────────────────────
  // INTRO ENTRY — pokeball throw + pop pour entrée en combat
  // ─────────────────────────────────────────────────────────────

  /**
   * Lance une pokeball depuis `throwFrom` vers `landPos`, flash blanc,
   * puis fait apparaître `sprite` avec un scale-in depuis 0.
   * Résout quand l'animation est terminée.
   */
  animateIntroEntry(
    sprite:     Phaser.GameObjects.Image,
    finalScale: number,
    throwFrom:  { x: number; y: number },
    landPos:    { x: number; y: number },
    ballUrl:    string,
    arcHeight   = -140,
  ): Promise<void> {
    return new Promise((resolve) => {
      const scene   = this.scene
      const ballKey = `__intro_ball__${ballUrl}`

      const launch = () => {
        const ball = scene.add.image(throwFrom.x, throwFrom.y, ballKey)
          .setDepth(60).setOrigin(0.5, 0.5)
        const TARGET_PX = 24
        ball.setScale(TARGET_PX / (ball.width || 64))

        const proxy = { t: 0 }
        scene.tweens.add({
          targets: proxy, t: 1, duration: 480, ease: 'Quad.easeOut',
          onUpdate: () => {
            const t    = proxy.t
            const x    = throwFrom.x + (landPos.x - throwFrom.x) * t
            const yLin = throwFrom.y + (landPos.y - throwFrom.y) * t
            const arc  = arcHeight * 4 * t * (1 - t)
            ball.setPosition(x, yLin + arc)
            ball.setAngle(ball.angle + 12)
          },
          onComplete: () => {
            this.backgroundEffect(0xffffff, 120, 0.5)

            scene.tweens.add({
              targets: ball,
              scaleX: ball.scaleX * 3,
              scaleY: ball.scaleY * 3,
              alpha: 0,
              duration: 220,
              ease: 'Quad.easeOut',
              onComplete: () => ball.destroy(),
            })

            scene.time.delayedCall(60, () => {
              sprite.setAlpha(1).setScale(0)
              scene.tweens.add({
                targets: sprite,
                scaleX: finalScale,
                scaleY: finalScale,
                duration: 380,
                ease: 'Back.easeOut',
                onComplete: () => resolve(),
              })
            })
          },
        })
      }

      if (!scene.textures.exists(ballKey)) {
        scene.load.image(ballKey, ballUrl)
        scene.load.once('complete', launch)
        scene.load.start()
      } else {
        launch()
      }
    })
  }

  // ─────────────────────────────────────────────────────────────
  // SWITCH OUT — rétractation dans la pokeball
  // ─────────────────────────────────────────────────────────────

  /**
   * Le sprite se rétracte vers une pokeball qui apparaît en son centre,
   * puis la pokeball disparaît en poof.
   */
  animateSwitchOut(
    sprite:  Phaser.GameObjects.Image,
    ballUrl: string,
  ): Promise<void> {
    return new Promise((resolve) => {
      const scene   = this.scene
      const ballKey = `__ball__${ballUrl}`

      const cx = sprite.x
      const cy = sprite.y - sprite.displayHeight * 0.5

      const doAnim = () => {
        const ball = scene.add.image(cx, cy, ballKey)
          .setDepth(61).setOrigin(0.5)
        const TARGET_PX = 24
        ball.setScale(TARGET_PX / (ball.width || 64))

        scene.tweens.add({
          targets: sprite,
          scaleX: 0, scaleY: 0, alpha: 0,
          x: cx, y: cy,
          duration: 280,
          ease: 'Quad.easeIn',
          onComplete: () => {
            this.backgroundEffect(0xff4444, 100, 0.25)

            scene.tweens.add({
              targets: ball,
              y: cy - 8,
              duration: 120,
              ease: 'Quad.easeOut',
              yoyo: true,
              onComplete: () => {
                scene.tweens.add({
                  targets: ball,
                  scaleX: ball.scaleX * 2.5,
                  scaleY: ball.scaleY * 2.5,
                  alpha: 0,
                  duration: 200,
                  ease: 'Quad.easeOut',
                  onComplete: () => {
                    ball.destroy()
                    resolve()
                  },
                })
              },
            })
          },
        })
      }

      if (!scene.textures.exists(ballKey)) {
        scene.load.image(ballKey, ballUrl)
        scene.load.once('complete', doAnim)
        scene.load.start()
      } else {
        doAnim()
      }
    })
  }
}

// ── Catalogue des animations par move ────────────────────────────────────────

const MOVE_ANIMS: Record<string, MoveAnimFn> = {

  // ═══ FEU ══════════════════════════════════════════════════════════════════
  flamethrower(a, atk, def) {
    a.backgroundEffect(0xff6600, 400, 0.2)
    for (let i = 0; i < 5; i++) {
      a.showEffect('fireball',
        { x: atk.x, y: atk.y, scale: 0.3, opacity: 0.9, time: i * 60 },
        { x: def.x + (i % 2 ? 10 : -10), y: def.y, scale: 0.7, opacity: 0.2, time: i * 60 + 350 },
        'decel', 'fade')
    }
  },
  fireblast(a, atk, def) {
    a.backgroundEffect(0xff4400, 600, 0.3)
    a.showEffect('flareball',
      { x: atk.x, y: atk.y, scale: 0.2, opacity: 1 },
      { x: def.x, y: def.y, scale: 1.8, opacity: 0.8, time: 500 }, 'decel', 'explode')
  },
  firespin(a, atk, def) {
    a.backgroundEffect(0xff5500, 500, 0.2)
    for (let i = 0; i < 3; i++) {
      a.showEffect('fireball',
        { x: def.x + Math.cos(i * 2.1) * 30, y: def.y + Math.sin(i * 2.1) * 20, scale: 0.3, opacity: 0.8, time: i * 80 },
        { x: def.x, y: def.y, scale: 0.9, opacity: 0.3, time: i * 80 + 350 }, 'decel', 'fade')
    }
  },

  // ═══ EAU ══════════════════════════════════════════════════════════════════
  watergun(a, atk, def) {
    a.showEffect('waterwisp',
      { x: atk.x, y: atk.y, scale: 0.2, opacity: 0.9 },
      { x: def.x, y: def.y, scale: 0.7, opacity: 0.5, time: 350 }, 'decel', 'explode')
    a.backgroundEffect(0x4488ff, 250, 0.1, 300)
  },
  hydropump(a, atk, def) {
    a.backgroundEffect(0x0044ff, 500, 0.2)
    for (let i = 0; i < 3; i++) {
      a.showEffect('waterwisp',
        { x: atk.x, y: atk.y + (i - 1) * 22, scale: 0.3, opacity: 0.9, time: i * 80 },
        { x: def.x, y: def.y + (i - 1) * 15, scale: 0.8, opacity: 0.5, time: i * 80 + 420 },
        'decel', 'explode')
    }
  },
  surf(a, atk, def) {
    a.backgroundEffect(0x2266ff, 500, 0.25)
    for (let i = 0; i < 4; i++) {
      a.showEffect('waterwisp',
        { x: atk.x - 40 + i * 20, y: def.y + 30, scale: 0.2, opacity: 0, time: i * 60 },
        { x: def.x - 20 + i * 12, y: def.y - 20, scale: 0.9, opacity: 0.5, time: i * 60 + 380 },
        'decel', 'explode')
    }
  },

  // ═══ ÉLECTRIK ═════════════════════════════════════════════════════════════
  thunderbolt(a, atk, def) {
    a.backgroundEffect(0xffff00, 350, 0.28)
    a.showEffect('lightning',
      { x: def.x, y: atk.y - 90, scale: 0.8, opacity: 1 },
      { x: def.x, y: def.y, scale: 1, opacity: 0.5, time: 200 }, 'decel', 'fade')
    a.showEffect('electroball',
      { x: def.x, y: def.y, scale: 0, opacity: 0.9, time: 160 },
      { x: def.x, y: def.y, scale: 2, opacity: 0,   time: 380 }, 'decel', 'fade')
  },
  thunder(a, atk, def) { MOVE_ANIMS.thunderbolt(a, atk, def) },
  thunderwave(a, atk, def) {
    a.showEffect('electroball',
      { x: atk.x, y: atk.y, scale: 0.2, opacity: 0.9 },
      { x: def.x, y: def.y, scale: 0.6, opacity: 0.3, time: 350 }, 'decel', 'fade')
    a.backgroundEffect(0xffdd00, 280, 0.1, 300)
  },

  // ═══ GLACE ════════════════════════════════════════════════════════════════
  icebeam(a, atk, def) {
    a.backgroundEffect(0x88eeff, 400, 0.2)
    a.showEffect('iceball',
      { x: atk.x, y: atk.y, scale: 0.2, opacity: 0.9 },
      { x: def.x, y: def.y, scale: 0.8, opacity: 0.6, time: 350 }, 'decel', 'explode')
    a.showEffect('icicle',
      { x: def.x + 20, y: def.y - 40, scale: 0.5, opacity: 0,   time: 200 },
      { x: def.x + 20, y: def.y,      scale: 0.9, opacity: 0.8, time: 420 }, 'decel', 'fade')
  },
  blizzard(a, atk, def) {
    a.backgroundEffect(0xaaeeff, 600, 0.25)
    for (let i = 0; i < 6; i++) {
      a.showEffect('icicle',
        { x: atk.x, y: atk.y + (i - 3) * 30, scale: 0.4, opacity: 0.7, time: i * 50 },
        { x: def.x, y: def.y + (i - 3) * 18, scale: 0.7, opacity: 0.3, time: i * 50 + 300 },
        'decel', 'explode')
    }
  },

  // ═══ PLANTE ═══════════════════════════════════════════════════════════════
  vinewhip(a, atk, def) {
    a.showEffect('leaf1',
      { x: atk.x, y: atk.y, scale: 0.8, opacity: 0.9 },
      { x: def.x, y: def.y, scale: 1.2, opacity: 0.6, time: 350 }, 'decel', 'explode')
    a.backgroundEffect(0x44cc44, 220, 0.1, 300)
  },
  razorleaf(a, atk, def) {
    for (let i = 0; i < 4; i++) {
      a.showEffect('leaf2',
        { x: atk.x, y: atk.y + (i - 2) * 25, scale: 0.6, opacity: 0.8, time: i * 60 },
        { x: def.x, y: def.y + (i - 2) * 14, scale: 1,   opacity: 0.4, time: i * 60 + 300 },
        'linear', 'explode')
    }
  },
  solarbeam(a, atk, def) {
    a.backgroundEffect(0xffff66, 600, 0.4)
    a.showEffect('energyball',
      { x: atk.x, y: atk.y, scale: 0, opacity: 0 },
      { x: atk.x, y: atk.y, scale: 1.6, opacity: 1, time: 400 }, 'decel', 'fade')
    a.showEffect('energyball',
      { x: atk.x, y: atk.y, scale: 0.5, opacity: 0.9, time: 450 },
      { x: def.x, y: def.y, scale: 1.5, opacity: 0.5, time: 760 }, 'decel', 'explode')
  },

  // ═══ PSY ══════════════════════════════════════════════════════════════════
  psychic(a, atk, def) {
    a.backgroundEffect(0xff44aa, 500, 0.2)
    a.showEffect('mistball',
      { x: atk.x, y: atk.y, scale: 0.3, opacity: 0.8 },
      { x: def.x, y: def.y, scale: 1,   opacity: 0.5, time: 400 }, 'decel', 'explode')
    a.showEffect('stare',
      { x: def.x, y: def.y, scale: 0.5, opacity: 0,   time: 200 },
      { x: def.x, y: def.y, scale: 1.5, opacity: 0.5, time: 500 }, 'decel', 'fade')
  },

  // ═══ SPECTRE / TÉNÈBRES ═══════════════════════════════════════════════════
  shadowball(a, atk, def) {
    a.backgroundEffect(0x330066, 400, 0.3)
    a.showEffect('shadowball',
      { x: atk.x, y: atk.y, scale: 0.3, opacity: 0.9 },
      { x: def.x, y: def.y, scale: 1,   opacity: 0.6, time: 400 }, 'decel', 'explode')
  },
  nightshade(a, atk, def) {
    a.backgroundEffect(0x220044, 400, 0.35)
    a.showEffect('blackwisp',
      { x: atk.x, y: atk.y, scale: 0.3, opacity: 0.8 },
      { x: def.x, y: def.y, scale: 1,   opacity: 0.4, time: 350 }, 'decel', 'explode')
  },

  // ═══ ROCHE / SOL ══════════════════════════════════════════════════════════
  rockthrow(a, atk, def) {
    a.showEffect('rock1',
      { x: atk.x, y: atk.y - 20, scale: 0.6, opacity: 0.9 },
      { x: def.x, y: def.y,      scale: 1,   opacity: 0.7, time: 400 }, 'ballistic', 'explode')
    a.backgroundEffect(0xccaa44, 180, 0.1, 360)
  },
  rockslide(a, atk, def) {
    for (let i = 0; i < 3; i++) {
      a.showEffect('rock2',
        { x: def.x + (i - 1) * 42, y: atk.y - 70, scale: 0.5, opacity: 0.9, time: i * 100 },
        { x: def.x + (i - 1) * 22, y: def.y,      scale: 0.9, opacity: 0.7, time: i * 100 + 350 },
        'ballistic', 'explode')
    }
    a.backgroundEffect(0x998833, 280, 0.15, 180)
  },
  earthquake(a, atk, def) {
    a.backgroundEffect(0x885522, 600, 0.3)
    for (let i = 0; i < 4; i++) {
      a.showEffect('rocks',
        { x: def.x + (i % 2 ? 30 : -30), y: def.y + 20, scale: 0,   opacity: 0,   time: i * 80 },
        { x: def.x + (i % 2 ? 30 : -30), y: def.y,      scale: 0.8, opacity: 0.5, time: i * 80 + 350 },
        'decel', 'explode')
    }
  },
  dig(a, atk, def) {
    a.backgroundEffect(0x885522, 400, 0.2)
    a.showEffect('rocks',
      { x: def.x, y: def.y + 35, scale: 0,   opacity: 0.8 },
      { x: def.x, y: def.y,      scale: 1,   opacity: 0.3, time: 350 }, 'decel', 'explode')
  },

  // ═══ PHYSIQUES ════════════════════════════════════════════════════════════
  slash(a, atk, def) {
    a.backgroundEffect(0xffffff, 200, 0.3)
    a.showEffect('rightslash',
      { x: def.x, y: def.y, scale: 0.2, opacity: 1 },
      { x: def.x, y: def.y, scale: 1.4, opacity: 0.7, time: 250 }, 'decel', 'explode')
  },
  megapunch(a, atk, def) {
    a.backgroundEffect(0xffffff, 200, 0.35)
    a.showEffect('fist1',
      { x: def.x - 30, y: def.y, scale: 0.5, opacity: 1 },
      { x: def.x + 12, y: def.y, scale: 1.2, opacity: 0.4, time: 250 }, 'decel', 'explode')
  },
  doubleedge(a, atk, def) {
    a.backgroundEffect(0xffffff, 300, 0.3)
    a.showEffect('impact',
      { x: def.x, y: def.y, scale: 0,   opacity: 0.9 },
      { x: def.x, y: def.y, scale: 1.5, opacity: 0,   time: 400 }, 'decel', 'fade')
  },
  bodyslam(a, atk, def)  { MOVE_ANIMS.doubleedge(a, atk, def) },
  tackle(a, atk, def)    { MOVE_ANIMS.doubleedge(a, atk, def) },
  hyperbeam(a, atk, def) {
    a.backgroundEffect(0xffffff, 700, 0.3)
    for (let i = 0; i < 5; i++) {
      a.showEffect('electroball',
        { x: atk.x, y: atk.y, scale: 0.4, opacity: 0.6, time: i * 60 },
        { x: def.x + (i % 2 ? 20 : -20), y: def.y, scale: 0.6, opacity: 0.3, time: i * 60 + 200 },
        'linear', 'explode')
    }
    a.showEffect('shadowball',
      { x: def.x, y: def.y, scale: 0,   opacity: 0.5, time: 600 },
      { x: def.x, y: def.y, scale: 3,   opacity: 0,   time: 900 }, 'decel', 'fade')
  },
  seedbomb(a, atk, def) {
    a.showEffect('energyball',
      { x: atk.x, y: atk.y, scale: 0.3, opacity: 0.9 },
      { x: def.x, y: def.y, scale: 0.8, opacity: 0.5, time: 400 }, 'ballistic', 'explode')
    a.backgroundEffect(0x44cc44, 200, 0.15, 360)
  },
  dragonrage(a, atk, def) {
    a.backgroundEffect(0x4400aa, 500, 0.25)
    for (let i = 0; i < 4; i++) {
      a.showEffect('flareball',
        { x: atk.x, y: atk.y, scale: 0.3, opacity: 0.7, time: i * 80 },
        { x: def.x + (i % 2 ? 20 : -20), y: def.y, scale: 0.8, opacity: 0.4, time: i * 80 + 400 },
        'decel', 'explode')
    }
  },

  // ═══ SOINS ════════════════════════════════════════════════════════════════
  recover(a, atk) {
    for (let i = 0; i < 5; i++) {
      const ox = (Math.random() - 0.5) * 60
      a.showEffect('wisp',
        { x: atk.x + ox, y: atk.y + 55, scale: 0.3, opacity: 0,   time: i * 80 },
        { x: atk.x + ox, y: atk.y - 30, scale: 0.8, opacity: 0.6, time: i * 80 + 400 },
        'decel', 'fade')
    }
    a.backgroundEffect(0x44ff44, 400, 0.1)
  },
  softboiled(a, atk, def) { MOVE_ANIMS.recover(a, atk, def) },
  moonlight(a,  atk, def) { MOVE_ANIMS.recover(a, atk, def) },

  // ═══ POISON ═══════════════════════════════════════════════════════════════
  toxic(a, atk, def) {
    a.showEffect('poisonwisp',
      { x: atk.x, y: atk.y, scale: 0.1, opacity: 0 },
      { x: def.x, y: def.y, scale: 0.6, opacity: 1, time: 450 }, 'ballistic', 'explode')
    a.backgroundEffect(0xaa44aa, 300, 0.15, 380)
  },
  poisonsting(a, atk, def) {
    a.showEffect('poisonwisp',
      { x: atk.x, y: atk.y, scale: 0.2, opacity: 0.8 },
      { x: def.x, y: def.y, scale: 0.5, opacity: 1,   time: 350 }, 'decel', 'explode')
  },

  // ═══ STATUTS ══════════════════════════════════════════════════════════════
  growl(a, atk) {
    for (let i = 0; i < 3; i++) {
      a.showEffect('electroball',
        { x: atk.x, y: atk.y, scale: 0,   opacity: 0.3, time: i * 150 },
        { x: atk.x, y: atk.y, scale: 4,   opacity: 0,   time: i * 150 + 500 },
        'decel', 'fade')
    }
  },
  tailwhip(a, atk, def)  { a.physicalFallback(atk, def) },
  stringshot(a, atk, def) {
    a.showEffect('wisp',
      { x: atk.x, y: atk.y, scale: 0.2, opacity: 0.7 },
      { x: def.x, y: def.y, scale: 0.6, opacity: 0.3, time: 400 }, 'decel', 'fade')
  },

  // ═══ FALLBACKS PAR TYPE ═══════════════════════════════════════════════════
  __type__fire    (a, atk, def) { MOVE_ANIMS.flamethrower(a, atk, def) },
  __type__water   (a, atk, def) { MOVE_ANIMS.watergun(a, atk, def) },
  __type__grass   (a, atk, def) { MOVE_ANIMS.vinewhip(a, atk, def) },
  __type__electric(a, atk, def) { MOVE_ANIMS.thunderbolt(a, atk, def) },
  __type__ice     (a, atk, def) { MOVE_ANIMS.icebeam(a, atk, def) },
  __type__psychic (a, atk, def) { MOVE_ANIMS.psychic(a, atk, def) },
  __type__ghost   (a, atk, def) { MOVE_ANIMS.shadowball(a, atk, def) },
  __type__rock    (a, atk, def) { MOVE_ANIMS.rockthrow(a, atk, def) },
  __type__ground  (a, atk, def) { MOVE_ANIMS.earthquake(a, atk, def) },
  __type__poison  (a, atk, def) { MOVE_ANIMS.poisonsting(a, atk, def) },
  __type__dragon  (a, atk, def) { MOVE_ANIMS.dragonrage(a, atk, def) },
  __type__normal  (a, atk, def) { a.physicalFallback(atk, def) },
  __type__fighting(a, atk, def) { MOVE_ANIMS.megapunch(a, atk, def) },
  __type__flying  (a, atk, def) {
    for (let i = 0; i < 4; i++) {
      a.showEffect('shine',
        { x: atk.x, y: atk.y + (i - 2) * 15, scale: 0.5, opacity: 0.8, time: i * 50 },
        { x: def.x, y: def.y + (i - 2) * 10, scale: 1,   opacity: 0.4, time: i * 50 + 300 },
        'linear', 'fade')
    }
  },
  __type__dark    (a, atk, def) { MOVE_ANIMS.nightshade(a, atk, def) },
  __type__bug     (a, atk, def) {
    a.showEffect('leaf1',
      { x: atk.x, y: atk.y, scale: 0.7, opacity: 0.8 },
      { x: def.x, y: def.y, scale: 1,   opacity: 0.5, time: 350 }, 'decel', 'explode')
  },
  __type__steel   (a, atk, def) {
    a.backgroundEffect(0xaaaacc, 300, 0.2)
    a.showEffect('rocks',
      { x: def.x, y: def.y, scale: 0.3, opacity: 0.8 },
      { x: def.x, y: def.y, scale: 1.2, opacity: 0.4, time: 300 }, 'decel', 'explode')
  },
}

// Injecter aliases tirets / espaces automatiquement
;[
  ['doubleedge',  ['double-edge',  'double edge']],
  ['vinewhip',    ['vine-whip',    'vine whip']],
  ['razorleaf',   ['razor-leaf',   'razor leaf']],
  ['solarbeam',   ['solar-beam',   'solar beam']],
  ['fireblast',   ['fire-blast',   'fire blast']],
  ['firespin',    ['fire-spin',    'fire spin']],
  ['watergun',    ['water-gun',    'water gun']],
  ['hydropump',   ['hydro-pump',   'hydro pump']],
  ['icebeam',     ['ice-beam',     'ice beam']],
  ['thunderbolt', ['thunder-bolt', 'thunder bolt']],
  ['thunderwave', ['thunder-wave', 'thunder wave']],
  ['shadowball',  ['shadow-ball',  'shadow ball']],
  ['hyperbeam',   ['hyper-beam',   'hyper beam']],
  ['rockslide',   ['rock-slide',   'rock slide']],
  ['rockthrow',   ['rock-throw',   'rock throw']],
  ['bodyslam',    ['body-slam',    'body slam']],
  ['megapunch',   ['mega-punch',   'mega punch']],
  ['seedbomb',    ['seed-bomb',    'seed bomb']],
  ['dragonrage',  ['dragon-rage',  'dragon rage']],
  ['poisonsting', ['poison-sting', 'poison sting']],
  ['nightshade',  ['night-shade',  'night shade']],
  ['tailwhip',    ['tail-whip',    'tail whip']],
  ['stringshot',  ['string-shot',  'string shot']],
].forEach(([target, aliases]) => {
  ;(aliases as string[]).forEach(a => {
    const key = a.replace(/[^a-z0-9]/g, '')
    if (!MOVE_ANIMS[key] && MOVE_ANIMS[target as string]) {
      MOVE_ANIMS[key] = MOVE_ANIMS[target as string]
    }
  })
})