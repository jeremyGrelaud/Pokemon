/**
 * Audio Manager
 * Centralized audio system for Pokemon battle
 */

class AudioManager {
  constructor() {
    this.bgm        = null;
    this.sfx        = {};
    this.enabled    = true;
    this.cache      = {};
    this.audioSupported = typeof Audio !== 'undefined';

    // Volume persisté entre zone → combat (même clé que le widget zone)
    const savedVol = parseFloat(
      sessionStorage.getItem('bgmVolume') ?? localStorage.getItem('zoneBgmVolume') ?? '30'
    );
    this.volume = {
      bgm:   savedVol / 100,
      sfx:   0.5,
      cries: 0.7,
    };

    // true si le navigateur a déjà accordé l'autoplay (déverrouillé depuis la zone)
    this.unlocked = sessionStorage.getItem('audioUnlocked') === '1';

    // Référence au widget BGM injecté dans la page de combat
    this._widget       = null;
    this._currentTrack = null;

    console.log('🔊 AudioManager initialized', {
      supported: this.audioSupported,
      volumes:   this.volume,
      unlocked:  this.unlocked,
    });
  }

  /** Appeler après un premier succès de lecture pour mémoriser l'autorisation */
  markUnlocked() {
    this.unlocked = true;
    sessionStorage.setItem('audioUnlocked', '1');
  }

  // ============================================================================
  // BGM (Background Music)
  // ============================================================================

  playBGM(track) {
    if (!this.audioSupported || !this.enabled) return;
    this._currentTrack = track;

    try {
      if (this.bgm) {
        this.bgm.pause();
        this.bgm.currentTime = 0;
      }

      this.bgm = new Audio(`/static/sounds/bgm/${track}.mp3`);
      this.bgm.loop   = true;
      this.bgm.volume = this.volume.bgm;

      // Mise à jour de la barre de progression du widget
      this.bgm.addEventListener('timeupdate', () => {
        const w = this._widget;
        if (w && this.bgm.duration) {
          const pct = (this.bgm.currentTime / this.bgm.duration * 100).toFixed(1);
          const bar = w.querySelector('.bgm-progress-bar');
          if (bar) bar.style.width = pct + '%';
        }
      });

      const playPromise = this.bgm.play();

      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            console.log(`🎵 Playing BGM: ${track}`);
            this.markUnlocked();
            this._widgetSetPlaying(true);
          })
          .catch(error => {
            console.warn(`❌ BGM blocked for "${track}": ${error.message}`);
            if (track === 'battle_rival') {
              console.info('🎵 Fallback: battle_rival → battle_trainer');
              this.playBGM('battle_trainer');
              return;
            }
            if (this.unlocked) {
              // L'utilisateur avait déjà autorisé — retenter après un court délai
              console.info('🔁 Retrying BGM (was unlocked)…');
              setTimeout(() => {
                this.bgm.play()
                  .then(() => { this.markUnlocked(); this._widgetSetPlaying(true); })
                  .catch(() => this._widgetPromptClick());
              }, 400);
            } else {
              this._widgetPromptClick();
            }
          });
      }

      // Fallback 404
      this.bgm.addEventListener('error', () => {
        if (track === 'battle_rival') {
          console.info('🎵 Fallback 404: battle_rival → battle_trainer');
          this.playBGM('battle_trainer');
        }
      }, { once: true });

    } catch (error) {
      console.error('BGM Error:', error);
    }
  }

  stopBGM() {
    if (this.bgm) {
      this.bgm.pause();
      this.bgm.currentTime = 0;
      console.log('🔇 BGM stopped');
    }
  }

  pauseBGM() {
    if (this.bgm) {
      this.bgm.pause();
    }
  }

  resumeBGM() {
    if (this.bgm && this.enabled) {
      this.bgm.play().catch(e => console.warn('Resume BGM failed:', e));
    }
  }

  setBGMVolume(volume) {
    this.volume.bgm = Math.max(0, Math.min(1, volume));
    if (this.bgm) this.bgm.volume = this.volume.bgm;
    // Persiste pour la prochaine page (même clé que le widget zone)
    localStorage.setItem('zoneBgmVolume', Math.round(volume * 100));
  }

  // ============================================================================
  // SFX (Sound Effects)
  // ============================================================================

  playSFX(sound) {
    if (!this.audioSupported || !this.enabled) return;
    
    try {
      const audio = new Audio(`/static/sounds/sfx/${sound}.wav`);
      audio.volume = this.volume.sfx;
      
      audio.play().catch(error => {
        console.warn(`SFX playback failed for ${sound}:`, error.message);
        // Try MP3 fallback
        this.playSFXFallback(sound);
      });
      
      // Clean up after playing
      audio.onended = () => {
        audio.remove();
      };
    } catch (error) {
      console.warn('SFX Error:', error);
    }
  }

  playSFXFallback(sound) {
    try {
      const audio = new Audio(`/static/sounds/sfx/${sound}.mp3`);
      audio.volume = this.volume.sfx;
      audio.play().catch(() => {
        console.log(`No audio file found for: ${sound}`);
      });
    } catch (error) {
      // Silent fail
    }
  }

  setSFXVolume(volume) {
    this.volume.sfx = Math.max(0, Math.min(1, volume));
  }

  // ============================================================================
  // POKEMON CRIES
  // ============================================================================

  playCry(pokemonId) {
    if (!this.audioSupported || !this.enabled) return;
    
    try {
      // Format: 001.wav, 002.wav, etc.
      const formattedId = String(pokemonId).padStart(3, '0');
      const audio = new Audio(`/static/sounds/cries/${formattedId}.wav`);
      audio.volume = this.volume.cries;
      
      audio.play().catch(error => {
        console.warn(`Cry playback failed for Pokemon ${pokemonId}:`, error.message);
      });
      
      audio.onended = () => {
        audio.remove();
      };
    } catch (error) {
      console.warn('Cry Error:', error);
    }
  }

  setCryVolume(volume) {
    this.volume.cries = Math.max(0, Math.min(1, volume));
  }

  // ============================================================================
  // PRESETS - Quick Sound Effects
  // ============================================================================

  // UI Sounds
  playSelect() {
    this.playSFX('ui/select');
  }

  playConfirm() {
    this.playSFX('ui/confirm');
  }

  playCancel() {
    this.playSFX('ui/cancel');
  }

  playError() {
    this.playSFX('ui/error');
  }

  // Battle Sounds
  playHit() {
    this.playSFX('attacks/hit');
  }

  playCritical() {
    this.playSFX('attacks/critical');
  }

  playMiss() {
    this.playSFX('attacks/miss');
  }

  playFaint() {
    this.playSFX('battle/faint');
  }

  playVictory() {
    this.playSFX('battle/victory');
  }

  playDefeat() {
    this.playSFX('battle/defeat');
  }

  playLevelUp() {
    this.playSFX('battle/levelup');
  }

  playHeal() {
    this.playSFX('items/heal');
  }

  // ============================================================================
  // SYSTEM CONTROL
  // ============================================================================

  toggleAudio() {
    this.enabled = !this.enabled;
    
    if (!this.enabled) {
      this.stopBGM();
    } else {
      this.resumeBGM();
    }
    
    console.log(`🔊 Audio ${this.enabled ? 'enabled' : 'disabled'}`);
    return this.enabled;
  }

  setMasterVolume(volume) {
    const vol = Math.max(0, Math.min(1, volume));
    this.volume.bgm = vol * 0.3;
    this.volume.sfx = vol * 0.5;
    this.volume.cries = vol * 0.7;
    
    if (this.bgm) {
      this.bgm.volume = this.volume.bgm;
    }
  }

  // ============================================================================
  // UTILITY
  // ============================================================================

  // ============================================================================
  // WIDGET BGM UNIFIÉ (combat)
  // ============================================================================

  /**
   * Initialise ou réutilise le widget BGM dans la page de combat.
   * Appelé par battle-game.js juste après new AudioManager().
   * @param {string} trackName  ex. 'battle_wild'
   */
  initBattleWidget(trackName) {
    // Chercher un widget déjà présent dans le HTML (battle_game_v2.html)
    let widget = document.getElementById('battle-bgm-player');
    if (!widget) return;

    this._widget = widget;

    const label = AudioManager._TRACK_LABELS[trackName] ?? trackName;
    const nameEl = widget.querySelector('.bgm-zone-name');
    if (nameEl) nameEl.textContent = label;

    const volEl = widget.querySelector('.bgm-volume');
    if (volEl) {
      volEl.value = Math.round(this.volume.bgm * 100);
      volEl.addEventListener('input', () => {
        const v = volEl.value / 100;
        this.setBGMVolume(v);
      });
    }

    const btn  = widget.querySelector('.bgm-btn');
    const icon = widget.querySelector('.bgm-icon');
    if (btn) {
      btn.addEventListener('click', () => {
        if (this.bgm && !this.bgm.paused) {
          this.pauseBGM();
          this._widgetSetPlaying(false);
        } else {
          this.resumeBGM();
          this._widgetSetPlaying(true);
        }
      });
    }

    widget.classList.add('bgm-idle');
  }

  /** Met à jour l'icône play/pause du widget */
  _widgetSetPlaying(playing) {
    if (!this._widget) return;
    const icon = this._widget.querySelector('.bgm-icon');
    const btn  = this._widget.querySelector('.bgm-btn');
    if (icon) icon.className = playing ? 'fas fa-pause bgm-icon' : 'fas fa-music bgm-icon';
    if (btn)  btn.classList.toggle('paused', !playing);
    this._widget.classList.toggle('bgm-idle', !playing);
  }

  /** Affiche le widget en mode "cliquez pour jouer" quand l'autoplay est bloqué */
  _widgetPromptClick() {
    if (!this._widget) {
      // Fallback : ancienne petite notification
      this.showAudioPrompt();
      return;
    }
    this._widgetSetPlaying(false);
    const nameEl = this._widget.querySelector('.bgm-zone-name');
    if (nameEl) nameEl.textContent = '▶ Cliquez pour la musique';
    this._widget.style.opacity   = '1';
    this._widget.style.animation = 'bgm-pulse 1s ease-in-out infinite alternate';
    // Un seul clic suffit pour démarrer
    const btn = this._widget.querySelector('.bgm-btn');
    if (btn) {
      const onFirstClick = () => {
        this.bgm.play()
          .then(() => { this.markUnlocked(); this._widgetSetPlaying(true); })
          .catch(() => {});
        this._widget.style.animation = '';
        const label = AudioManager._TRACK_LABELS[this._currentTrack] ?? this._currentTrack;
        const nameEl2 = this._widget.querySelector('.bgm-zone-name');
        if (nameEl2) nameEl2.textContent = label;
        btn.removeEventListener('click', onFirstClick);
      };
      btn.addEventListener('click', onFirstClick);
    }
  }

  showAudioPrompt() {
    const prompt = document.createElement('div');
    prompt.style.cssText = `
      position:fixed;bottom:80px;right:20px;
      background:rgba(15,20,40,0.92);color:white;
      padding:12px 18px;border-radius:8px;z-index:10000;
      font-family:Arial,sans-serif;font-size:13px;
      cursor:pointer;border:1px solid rgba(100,160,255,0.35);
    `;
    prompt.innerHTML = `<i class="fas fa-volume-mute mr-2"></i>Cliquez pour activer le son`;
    prompt.onclick = () => {
      this.bgm && this.bgm.play()
        .then(() => { this.markUnlocked(); this._widgetSetPlaying(true); })
        .catch(() => {});
      prompt.remove();
    };
    document.body.appendChild(prompt);
    setTimeout(() => prompt.parentNode && prompt.remove(), 6000);
  }

  preloadSounds(soundList) {
    soundList.forEach(sound => {
      const audio = new Audio(sound);
      audio.preload = 'auto';
      this.cache[sound] = audio;
    });
    
    console.log(`📦 Preloaded ${soundList.length} sounds`);
  }

  // ============================================================================
  // AUDIO VISUALIZATION (Optional)
  // ============================================================================

  createVisualizer(canvasElement) {
    if (!this.bgm || !this.audioSupported) return;
    
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaElementSource(this.bgm);
      
      source.connect(analyser);
      analyser.connect(audioContext.destination);
      
      analyser.fftSize = 256;
      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      const ctx = canvasElement.getContext('2d');
      const width = canvasElement.width;
      const height = canvasElement.height;
      
      const draw = () => {
        requestAnimationFrame(draw);
        
        analyser.getByteFrequencyData(dataArray);
        
        ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        ctx.fillRect(0, 0, width, height);
        
        const barWidth = (width / bufferLength) * 2.5;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
          const barHeight = (dataArray[i] / 255) * height;
          
          const r = barHeight + 25 * (i / bufferLength);
          const g = 250 * (i / bufferLength);
          const b = 50;
          
          ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
          ctx.fillRect(x, height - barHeight, barWidth, barHeight);
          
          x += barWidth + 1;
        }
      };
      
      draw();
      console.log('🎵 Audio visualizer created');
    } catch (error) {
      console.warn('Visualizer creation failed:', error);
    }
  }
}

// ============================================================================
// GLOBAL AUDIO CONTROLS (UI Integration)
// ============================================================================

// Create audio control panel
function createAudioControls() {
  const controls = document.createElement('div');
  controls.id = 'audio-controls';
  controls.style.cssText = `
    position: fixed;
    bottom: 20px;
    left: 20px;
    background: rgba(0,0,0,0.8);
    padding: 10px;
    border-radius: 8px;
    z-index: 9999;
    display: none;
  `;
  
  controls.innerHTML = `
    <div style="color: white; font-size: 12px; margin-bottom: 8px;">
      <strong>Audio Controls</strong>
    </div>
    <div style="display: flex; flex-direction: column; gap: 8px;">
      <label style="color: white; font-size: 11px;">
        BGM: <input type="range" id="bgm-volume" min="0" max="100" value="30" style="width: 100px;">
      </label>
      <label style="color: white; font-size: 11px;">
        SFX: <input type="range" id="sfx-volume" min="0" max="100" value="50" style="width: 100px;">
      </label>
      <button id="toggle-audio" style="padding: 5px; cursor: pointer;">
        Mute
      </button>
    </div>
  `;
  
  document.body.appendChild(controls);
  
  // Toggle visibility with keyboard shortcut
  document.addEventListener('keydown', (e) => {
    if (e.key === 'm' && e.ctrlKey) {
      controls.style.display = controls.style.display === 'none' ? 'block' : 'none';
    }
  });
}

// Noms lisibles pour les pistes de combat (défini hors classe pour compatibilité ES5)
AudioManager._TRACK_LABELS = {
  battle_wild:    'Combat Sauvage',
  battle_trainer: 'Combat Dresseur',
  battle_gym:     'Combat Arène',
  battle_rival:   'Combat Rival',
};

// Auto-create controls if in development
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
  document.addEventListener('DOMContentLoaded', createAudioControls);
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AudioManager;
}