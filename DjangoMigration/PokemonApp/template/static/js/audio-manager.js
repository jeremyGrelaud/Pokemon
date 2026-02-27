/**
 * Audio Manager
 * Centralized audio system for Pokemon battle
 */

class AudioManager {
  constructor() {
    this.bgm = null;
    this.sfx = {};
    this.enabled = true;
    
    // Volume levels (0.0 to 1.0)
    this.volume = {
      bgm: 0.3,
      sfx: 0.5,
      cries: 0.7
    };
    
    // Preloaded audio cache
    this.cache = {};
    
    // Check if audio is supported
    this.audioSupported = typeof Audio !== 'undefined';
    
    console.log('🔊 AudioManager initialized', {
      supported: this.audioSupported,
      volumes: this.volume
    });
  }

  // ============================================================================
  // BGM (Background Music)
  // ============================================================================

  playBGM(track) {
    if (!this.audioSupported || !this.enabled) return;
    
    try {
      // Stop current BGM
      if (this.bgm) {
        this.bgm.pause();
        this.bgm.currentTime = 0;
      }
      
      // Create new BGM
      this.bgm = new Audio(`/static/sounds/bgm/${track}.mp3`);
      this.bgm.loop = true;
      this.bgm.volume = this.volume.bgm;
      
      // Play with error handling
      const playPromise = this.bgm.play();
      
      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            console.log(`🎵 Playing BGM: ${track}`);
          })
          .catch(error => {
            console.warn(`❌ BGM playback failed for "${track}": ${error.message}`);
            // Fallback : si battle_rival manque, utiliser battle_trainer
            if (track === 'battle_rival') {
              console.info('🎵 Fallback: battle_rival → battle_trainer');
              this.playBGM('battle_trainer');
            } else {
              this.showAudioPrompt();
            }
          });
      }

      // Fallback réseau (fichier 404)
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
    if (this.bgm) {
      this.bgm.volume = this.volume.bgm;
    }
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

  showAudioPrompt() {
    // Show a small UI prompt to enable audio (for browsers that block autoplay)
    const prompt = document.createElement('div');
    prompt.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: rgba(0,0,0,0.9);
      color: white;
      padding: 15px 20px;
      border-radius: 8px;
      z-index: 10000;
      font-family: Arial, sans-serif;
      font-size: 14px;
      cursor: pointer;
      animation: slideInRight 0.3s ease;
    `;
    
    prompt.innerHTML = `
      <div style="display: flex; align-items: center; gap: 10px;">
        <i class="fas fa-volume-mute"></i>
        <span>Cliquez pour activer le son</span>
      </div>
    `;
    
    prompt.onclick = () => {
      this.resumeBGM();
      prompt.remove();
    };
    
    document.body.appendChild(prompt);
    
    setTimeout(() => {
      if (prompt.parentNode) {
        prompt.remove();
      }
    }, 5000);
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

// Auto-create controls if in development
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
  document.addEventListener('DOMContentLoaded', createAudioControls);
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AudioManager;
}