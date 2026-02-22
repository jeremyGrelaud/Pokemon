/**
 * Capture System
 * Gère les animations et la logique de capture
 */

function lowerPokemonFileNames(str) {
    // Convertir en minuscules
    let result = str.toLowerCase();
    // Supprimer tout ce qui n'est pas alphanumérique
    // Vérifie la présence des symboles et les remplacer par "-m" ou "-f"
    if (str.includes('♂')) {
        result = result.replace(/♂/g, '').replace(/[^a-z0-9]/g, '') + 'm';
    } else if (str.includes('♀')) {
        result = result.replace(/♀/g, '').replace(/[^a-z0-9]/g, '') + 'f';
    } else {
        result = result.replace(/[^a-z0-9]/g, '');
    }
    return result;
}

class CaptureSystem {
  constructor() {
    this.overlay = null;
    this.onComplete = null;
  }

  /**
   * Lance une tentative de capture avec animation
   */
  async attemptCapture(pokemonData, ballType, captureRate) {
    return new Promise((resolve) => {
      this.onComplete = resolve;
      
      // Créer l'overlay
      this.createCaptureOverlay(pokemonData, ballType, captureRate);
      
      // Démarrer l'animation
      setTimeout(() => this.startCaptureAnimation(captureRate), 100);
    });
  }

  createCaptureOverlay(pokemonData, ballType, captureRate) {
    // Créer l'overlay
    this.overlay = document.createElement('div');
    this.overlay.className = 'capture-overlay';
    
    const probability = Math.min(100, captureRate * 100);

    const folder = pokemonData.is_shiny ? 'shiny' : 'normal';
    
    this.overlay.innerHTML = `
    <div class="capture-container">
        <!-- Barre de probabilité -->
        <div class="capture-probability">${probability} %</div>
        
        <!-- Pokémon -->
        <img class="capture-pokemon" src='/static/img/sprites_gen5/${folder}/${lowerPokemonFileNames(pokemonData.species_name)}.png'  onerror="this.src='/static/img/pokeball.png'">
        
        <!-- Poké Ball -->
        <div class="pokeball-capture ${ballType}"></div>
        
        <!-- Étoiles -->
        <div class="capture-stars"></div>
    </div>
    `;
    
    document.body.appendChild(this.overlay);
  }

  async startCaptureAnimation(captureRate) {
    const pokemon = this.overlay.querySelector('.capture-pokemon');
    const pokeball = this.overlay.querySelector('.pokeball-capture');
    
    // Phase 1: Lancer la ball
    pokeball.classList.add('throwing');
    await this.wait(800);
    
    // Phase 2: Pokémon aspiré dans la ball
    pokemon.classList.add('captured');
    await this.wait(800);
    
    // Phase 3: Ball tombe au sol
    pokeball.classList.remove('throwing');
    await this.wait(300);
    
    // Phase 4: Shakes (3 fois)
    const shakes = 3;
    let escaped = false;
    
    for (let i = 0; i < shakes; i++) {
      // Calculer la probabilité de casser à ce shake
      const shakeChance = Math.random();
      
      if (shakeChance > captureRate) {
        // Le Pokémon s'échappe !
        escaped = true;
        break;
      }
      
      // Shake
      pokeball.classList.add('shaking');
      await this.wait(500);
      pokeball.classList.remove('shaking');
      await this.wait(300);
    }
    
    // Phase 5: Succès ou échec
    if (escaped) {
      await this.showEscape(pokemon, pokeball);
      this.onComplete({ success: false });
    } else {
      await this.showSuccess(pokeball);
      this.onComplete({ success: true });
    }
  }

  async showEscape(pokemon, pokeball) {
    // Ball se brise
    pokeball.classList.add('failed');
    await this.wait(500);
    
    // Pokémon réapparaît
    pokemon.style.opacity = '0';
    pokemon.classList.remove('captured');
    pokemon.classList.add('escaping');
    await this.wait(500);
    
    // Message
    this.showMessage('Le Pokémon s\'est échappé !', 'failed');
    await this.wait(2000);
    
    // Fermer
    this.close();
  }

  async showSuccess(pokeball) {
    // Animation de succès
    pokeball.classList.add('success');
    await this.wait(600);
    
    // Étoiles
    this.createStars();
    
    // Message
    this.showMessage('Pokémon capturé !', 'success');
    await this.wait(3000);
    
    // Fermer
    this.close();
  }

  createStars() {
    const starsContainer = this.overlay.querySelector('.capture-stars');
    starsContainer.style.display = 'block';
    
    // Créer 20 étoiles
    for (let i = 0; i < 20; i++) {
      const star = document.createElement('div');
      star.className = 'star';
      
      const angle = (i / 20) * Math.PI * 2;
      const distance = 100 + Math.random() * 100;
      const tx = Math.cos(angle) * distance;
      const ty = Math.sin(angle) * distance;
      
      star.style.setProperty('--tx', `${tx}px`);
      star.style.setProperty('--ty', `${ty}px`);
      star.style.left = '50%';
      star.style.top = '50%';
      star.style.animationDelay = `${i * 0.05}s`;
      
      starsContainer.appendChild(star);
    }
  }

  showMessage(text, type) {
    const message = document.createElement('div');
    message.className = `capture-message ${type}`;
    message.textContent = text;
    
    this.overlay.querySelector('.capture-container').appendChild(message);
  }

  close() {
    if (this.overlay) {
      this.overlay.style.animation = 'fadeOut 0.3s ease';
      setTimeout(() => {
        this.overlay.remove();
        this.overlay = null;
      }, 300);
    }
  }

  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Ajouter animation fadeOut
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeOut {
    from { opacity: 1; }
    to { opacity: 0; }
  }
`;
document.head.appendChild(style);

// Export
window.CaptureSystem = CaptureSystem;