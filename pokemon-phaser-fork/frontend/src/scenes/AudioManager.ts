// ============================================================
// scenes/AudioManager.ts
// Scène Phaser parallèle — gère toute la BGM + SFX du jeu.
// Lancée une seule fois depuis PreloadScene.
//
// Chemins réels du projet :
//   BGM zones   : /static/sounds/bgm/kanto/<track>.mp3
//   BGM combat  : /static/sounds/bgm/<file>.mp3
//   Cris        : /static/sounds/cries/<NNN>.wav  (ex: 006.wav)
//   SFX moves   : /static/sounds/sfx/attacks/<move>.wav
//   SFX UI      : /static/sounds/sfx/ui/<file>.wav
//   SFX battle  : /static/sounds/sfx/battle/<file>.wav
//   SFX capture : /static/sounds/sfx/capture/<file>.wav
// ============================================================

import Phaser from 'phaser'

export type BattleType = 'wild' | 'trainer' | 'gym' | 'elite_four' | 'rival'

const BATTLE_BGM: Record<BattleType, string> = {
  wild:       'battle_wild',
  trainer:    'battle_trainer',
  gym:        'battle_gym',
  elite_four: 'battle_elite4',
  rival:      'battle_rival',
}

const BGM_ZONE_BASE   = '/static/sounds/bgm/kanto/'
const BGM_BATTLE_BASE = '/static/sounds/bgm/'
const CRIES_BASE      = '/static/sounds/cries/'
const SFX_BASE        = '/static/sounds/sfx/'
const FADE_MS         = 600
const DEFAULT_VOL     = 0.45

export class AudioManager extends Phaser.Scene {

  static instance: AudioManager

  private bgmCurrent: Phaser.Sound.BaseSound | null = null
  private bgmCurrentKey = ''
  private bgmZoneKey    = ''

  private masterVol  = DEFAULT_VOL
  private muted      = false
  private activeSfx  = new Set<Phaser.Sound.BaseSound>()

  constructor() {
    super({ key: 'AudioManager', active: false })
    AudioManager.instance = this
  }

  create(): void {
    this.game.events.on('audio-volume', (v: number) => this.setVolume(v))
    this.game.events.on('audio-mute',   ()           => this.toggleMute())
    this._unlockAudioContext()
  }

  // ── Unlock AudioContext (politique autoplay navigateur) ────

  private _unlockAudioContext(): void {
    const ctx = (this.sound as Phaser.Sound.WebAudioSoundManager)?.context
    if (!ctx || ctx.state === 'running') return

    const resume = () => {
      ctx.resume().then(() => {
        // L'AudioContext est débloqué : relancer la BGM de zone si elle
        // était prête mais silencieuse faute de geste utilisateur.
        if (this.bgmZoneKey && !this.bgmCurrent?.isPlaying) {
          this._playBgm(this.bgmZoneKey, undefined, true)
        }
        document.removeEventListener('keydown',  resume)
        document.removeEventListener('pointerdown', resume)
      })
    }

    document.addEventListener('keydown',    resume, { once: true })
    document.addEventListener('pointerdown', resume, { once: true })
  }

  // ── BGM ────────────────────────────────────────────────────

  playZone(musicFile: string): void {
    if (!musicFile) return
    const key = `bgm-zone-${musicFile}`
    this.bgmZoneKey = key
    this._playBgm(key, `${BGM_ZONE_BASE}${musicFile}.mp3`, true)
  }

  playBattle(type: BattleType = 'wild'): void {
    const file = BATTLE_BGM[type] ?? BATTLE_BGM.wild
    const key  = `bgm-battle-${file}`
    this._stopBgm(false)
    this._playBgm(key, `${BGM_BATTLE_BASE}${file}.mp3`, true)
  }

  resumeZone(): void {
    if (!this.bgmZoneKey) return
    this._stopBgm(false)
    this._playBgm(this.bgmZoneKey, undefined, true)
  }

  /**
   * Joue une BGM temporaire (ex: évolution) SANS écraser bgmZoneKey.
   * resumeZone() reprendra la musique de zone correcte après.
   */
  playBgmOneShot(musicFile: string): void {
    if (!musicFile) return
    const key = `bgm-oneshot-${musicFile}`
    this._stopBgm(false)
    this._playBgm(key, `${BGM_ZONE_BASE}${musicFile}.mp3`, true)
    // bgmZoneKey intentionnellement non modifié
  }

  // ── Cris Pokémon ───────────────────────────────────────────

  playCry(dexNumber: number): void {
    const pad = String(dexNumber).padStart(3, '0')
    this._playSfxOnce(`cry-${pad}`, `${CRIES_BASE}${pad}.wav`)
  }

  // ── SFX moves ──────────────────────────────────────────────

  playMoveSfx(moveName: string): void {
    const normalized = moveName.toLowerCase().replace(/[^a-z0-9]/g, '')
    this._playSfxOnce(`sfx-move-${normalized}`, `${SFX_BASE}attacks/${normalized}.wav`)
  }

  // ── SFX génériques ─────────────────────────────────────────

  playSfx(category: 'ui' | 'battle' | 'capture', filename: string): void {
    this._playSfxOnce(`sfx-${category}-${filename}`, `${SFX_BASE}${category}/${filename}.wav`)
  }


  playUiSfx(filename: string): void {
    this._playSfxOnce(`sfx-ui-${filename}`, `${SFX_BASE}ui/${filename}.wav`)
  }

  // ── SFX control ────────────────────────────────────────────

  /** Arrête et détruit immédiatement tous les SFX en cours (cris, moves, ui…). */
  stopAllSfx(): void {
    for (const sfx of this.activeSfx) {
      try { sfx.stop(); sfx.destroy() } catch { /* déjà détruit */ }
    }
    this.activeSfx.clear()
  }

  stopBgm(): void {
    this._stopBgm(true)   // fondu court avant le silence
  }

  // ── Volume / Mute ──────────────────────────────────────────

  setVolume(v: number): void {
    this.masterVol = Math.max(0, Math.min(1, v))
    if (this.bgmCurrent && !this.muted) {
      (this.bgmCurrent as Phaser.Sound.WebAudioSound).setVolume?.(this.masterVol)
    }
  }

  toggleMute(): boolean {
    this.muted = !this.muted
    const vol = this.muted ? 0 : this.masterVol
    ;(this.bgmCurrent as Phaser.Sound.WebAudioSound)?.setVolume?.(vol)
    return this.muted
  }

  get isMuted(): boolean { return this.muted }

  // ── Internals ──────────────────────────────────────────────

  private _playBgm(key: string, url?: string, fade = true): void {
    if (this.bgmCurrentKey === key && this.bgmCurrent?.isPlaying) return

    const startTrack = () => {
      if (!this.cache.audio.has(key)) {
        console.warn(`[AudioManager] Cache manquant: ${key}`)
        return
      }
      const track = this.sound.add(key, {
        loop:   true,
        volume: fade ? 0 : (this.muted ? 0 : this.masterVol),
      }) as Phaser.Sound.WebAudioSound

      track.play()
      this.bgmCurrent    = track
      this.bgmCurrentKey = key

      if (fade) {
        this.tweens.add({
          targets: track, volume: this.muted ? 0 : this.masterVol, duration: FADE_MS,
        })
      }
    }

    if (url && !this.cache.audio.has(key)) {
      this.load.audio(key, url)
      this.load.once('complete', startTrack)
      this.load.once('loaderror', () => console.warn(`[AudioManager] Introuvable: ${url}`))
      this.load.start()
    } else {
      startTrack()
    }
  }

  private _stopBgm(fade: boolean): void {
    const prev = this.bgmCurrent
    if (!prev) return
    if (fade) {
      this.tweens.add({
        targets: prev, volume: 0, duration: FADE_MS,
        onComplete: () => { prev.stop(); prev.destroy() },
      })
    } else {
      prev.stop()
      prev.destroy()
    }
    this.bgmCurrent    = null
    this.bgmCurrentKey = ''
  }

  private _playSfxOnce(key: string, url: string): void {
    const play = () => {
      if (!this.cache.audio.has(key)) return
      const s = this.sound.add(key, { volume: this.muted ? 0 : Math.min(1, this.masterVol * 1.4) })
      this.activeSfx.add(s)
      s.play()
      s.once('complete', () => { this.activeSfx.delete(s); s.destroy() })
    }
    if (!this.cache.audio.has(key)) {
      this.load.audio(key, url)
      this.load.once('complete', play)
      this.load.once('loaderror', () => {})
      this.load.start()
    } else {
      play()
    }
  }
}