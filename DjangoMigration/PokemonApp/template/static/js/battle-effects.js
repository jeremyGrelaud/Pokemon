/**
 * Battle Effects System
 * Advanced visual effects for Pokemon battles
 */

class BattleEffects {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas ? canvas.getContext('2d') : null;
    this.particles = [];
    this.activeEffects = [];
    
    if (this.ctx) {
      this.startAnimationLoop();
    }
  }

  startAnimationLoop() {
    const animate = () => {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      
      // Update and draw particles
      this.particles = this.particles.filter(p => {
        p.update();
        p.draw(this.ctx);
        return p.life > 0;
      });
      
      requestAnimationFrame(animate);
    };
    
    animate();
  }

  // ============================================================================
  // PHYSICAL ATTACKS
  // ============================================================================

  physicalAttack(from, to, type = 'slash') {
    switch(type) {
      case 'slash':
        this.createSlashEffect(from, to);
        break;
      case 'punch':
        this.createPunchEffect(from, to);
        break;
      case 'tackle':
        this.createTackleEffect(from, to);
        break;
      default:
        this.createGenericPhysical(from, to);
    }
  }

  createSlashEffect(from, to) {
    // Create multiple slash lines
    for (let i = 0; i < 3; i++) {
      setTimeout(() => {
        const slash = document.createElement('div');
        slash.className = 'effect-slash';
        slash.style.cssText = `
          position: absolute;
          width: 120px;
          height: 4px;
          background: linear-gradient(90deg, transparent, #fff, transparent);
          top: ${to.y - 20 + i * 20}px;
          left: ${to.x - 60}px;
          transform: rotate(${-45 + i * 15}deg);
          transform-origin: center;
          pointer-events: none;
          z-index: 100;
          animation: slash-swipe 0.3s ease-out;
        `;
        
        document.body.appendChild(slash);
        setTimeout(() => slash.remove(), 300);
      }, i * 100);
    }
    
    // Impact particles
    setTimeout(() => {
      this.createImpactParticles(to, '#fff', 15);
    }, 250);
  }

  createPunchEffect(from, to) {
    // Create impact circle
    const impact = document.createElement('div');
    impact.className = 'effect-impact';
    impact.style.cssText = `
      position: absolute;
      width: 80px;
      height: 80px;
      border: 4px solid #fff;
      border-radius: 50%;
      top: ${to.y - 40}px;
      left: ${to.x - 40}px;
      pointer-events: none;
      z-index: 100;
      animation: impact-ring 0.4s ease-out;
    `;
    
    document.body.appendChild(impact);
    setTimeout(() => impact.remove(), 400);
    
    // Impact particles
    this.createImpactParticles(to, '#fff', 20);
  }

  createTackleEffect(from, to) {
    // Speed lines effect
    for (let i = 0; i < 5; i++) {
      const line = document.createElement('div');
      line.style.cssText = `
        position: absolute;
        width: 100px;
        height: 2px;
        background: linear-gradient(90deg, #fff, transparent);
        top: ${from.y + (Math.random() - 0.5) * 60}px;
        left: ${from.x}px;
        pointer-events: none;
        z-index: 100;
        animation: speed-line 0.3s ease-out;
      `;
      
      document.body.appendChild(line);
      setTimeout(() => line.remove(), 300);
    }
    
    setTimeout(() => {
      this.createImpactParticles(to, '#fff', 12);
    }, 200);
  }

  createGenericPhysical(from, to) {
    this.createImpactParticles(to, '#fff', 10);
  }

  // ============================================================================
  // SPECIAL ATTACKS
  // ============================================================================

  specialAttack(from, to, moveType) {
    const color = this.getTypeColor(moveType);
    
    switch(moveType) {
      case 'fire':
        this.createFireball(from, to);
        break;
      case 'water':
        this.createWaterGun(from, to);
        break;
      case 'electric':
        this.createThunderbolt(from, to);
        break;
      case 'grass':
        this.createVineWhip(from, to);
        break;
      case 'ice':
        this.createIceBeam(from, to);
        break;
      case 'psychic':
        this.createPsychic(from, to);
        break;
      default:
        this.createGenericProjectile(from, to, moveType, color);
    }
  }

  createFireball(from, to) {
    const projectile = document.createElement('div');
    projectile.style.cssText = `
      position: absolute;
      width: 50px;
      height: 50px;
      border-radius: 50%;
      background: radial-gradient(circle, #ff6b35, #f7931e, transparent);
      box-shadow: 0 0 30px #ff6b35, 0 0 60px #f7931e;
      top: ${from.y - 25}px;
      left: ${from.x - 25}px;
      pointer-events: none;
      z-index: 100;
    `;
    
    document.body.appendChild(projectile);
    
    // Animate to target
    setTimeout(() => {
      projectile.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
      projectile.style.top = `${to.y - 25}px`;
      projectile.style.left = `${to.x - 25}px`;
      projectile.style.transform = 'scale(2)';
    }, 50);
    
    // Create fire trail
    const trailInterval = setInterval(() => {
      this.createParticle(
        {x: parseInt(projectile.style.left) + 25, y: parseInt(projectile.style.top) + 25},
        '#ff6b35',
        20
      );
    }, 50);
    
    // Impact
    setTimeout(() => {
      clearInterval(trailInterval);
      this.createFireExplosion(to);
      projectile.remove();
    }, 650);
  }

  createFireExplosion(position) {
    // Create explosion particles
    for (let i = 0; i < 30; i++) {
      const angle = (i / 30) * Math.PI * 2;
      const velocity = 80 + Math.random() * 40;
      const size = 8 + Math.random() * 12;
      const colors = ['#ff6b35', '#f7931e', '#ffaa00'];
      const color = colors[Math.floor(Math.random() * colors.length)];
      
      this.createParticle(position, color, velocity, angle, size);
    }
  }

  createWaterGun(from, to) {
    // Create multiple water droplets
    const projectileCount = 15;
    
    for (let i = 0; i < projectileCount; i++) {
      setTimeout(() => {
        const droplet = document.createElement('div');
        const offsetY = (Math.random() - 0.5) * 30;
        
        droplet.style.cssText = `
          position: absolute;
          width: 12px;
          height: 16px;
          border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
          background: radial-gradient(ellipse at 30% 30%, #6eb5ff, #4a90e2);
          top: ${from.y + offsetY}px;
          left: ${from.x}px;
          pointer-events: none;
          z-index: 100;
          opacity: 0.8;
        `;
        
        document.body.appendChild(droplet);
        
        setTimeout(() => {
          droplet.style.transition = 'all 0.5s linear';
          droplet.style.top = `${to.y + offsetY}px`;
          droplet.style.left = `${to.x}px`;
          droplet.style.opacity = '0';
        }, 50);
        
        setTimeout(() => droplet.remove(), 550);
      }, i * 40);
    }
    
    // Water splash on impact
    setTimeout(() => {
      this.createWaterSplash(to);
    }, 600);
  }

  createWaterSplash(position) {
    for (let i = 0; i < 20; i++) {
      this.createParticle(position, '#4a90e2', 60, (Math.random() * Math.PI) - Math.PI/2, 8);
    }
  }

  createThunderbolt(from, to) {
    // Create lightning bolt path
    const bolt = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    bolt.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 100;
    `;
    
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    
    // Generate zigzag path
    let pathData = `M ${from.x} ${from.y}`;
    const segments = 8;
    const dx = (to.x - from.x) / segments;
    const dy = (to.y - from.y) / segments;
    
    for (let i = 1; i <= segments; i++) {
      const x = from.x + dx * i + (Math.random() - 0.5) * 40;
      const y = from.y + dy * i + (Math.random() - 0.5) * 40;
      pathData += ` L ${x} ${y}`;
    }
    pathData += ` L ${to.x} ${to.y}`;
    
    path.setAttribute('d', pathData);
    path.setAttribute('stroke', '#ffff00');
    path.setAttribute('stroke-width', '4');
    path.setAttribute('fill', 'none');
    path.setAttribute('filter', 'drop-shadow(0 0 10px #ffff00)');
    
    bolt.appendChild(path);
    document.body.appendChild(bolt);
    
    // Flash effect
    document.body.style.animation = 'flash-white 0.1s';
    setTimeout(() => {
      document.body.style.animation = '';
    }, 100);
    
    // Remove bolt
    setTimeout(() => {
      bolt.remove();
      this.createElectricSparks(to);
    }, 200);
  }

  createElectricSparks(position) {
    for (let i = 0; i < 25; i++) {
      this.createParticle(position, '#ffff00', 70, Math.random() * Math.PI * 2, 4);
    }
  }

  createVineWhip(from, to) {
    // Create vine path
    const vine = document.createElement('div');
    vine.style.cssText = `
      position: absolute;
      width: 8px;
      height: ${Math.sqrt((to.x-from.x)**2 + (to.y-from.y)**2)}px;
      background: linear-gradient(to bottom, #78c850, #48a020);
      top: ${from.y}px;
      left: ${from.x}px;
      transform-origin: top center;
      transform: rotate(${Math.atan2(to.y - from.y, to.x - from.x) * 180 / Math.PI + 90}deg);
      pointer-events: none;
      z-index: 100;
      animation: vine-grow 0.4s ease-out;
    `;
    
    document.body.appendChild(vine);
    
    setTimeout(() => {
      vine.style.animation = 'vine-shrink 0.2s ease-in';
      this.createImpactParticles(to, '#78c850', 15);
    }, 400);
    
    setTimeout(() => vine.remove(), 600);
  }

  createIceBeam(from, to) {
    const beam = document.createElement('div');
    const angle = Math.atan2(to.y - from.y, to.x - from.x);
    const distance = Math.sqrt((to.x-from.x)**2 + (to.y-from.y)**2);
    
    beam.style.cssText = `
      position: absolute;
      width: ${distance}px;
      height: 20px;
      background: linear-gradient(90deg, 
        transparent,
        rgba(173, 216, 230, 0.8) 20%,
        rgba(135, 206, 250, 0.9) 50%,
        rgba(173, 216, 230, 0.8) 80%,
        transparent
      );
      box-shadow: 0 0 20px rgba(135, 206, 250, 0.8);
      top: ${from.y - 10}px;
      left: ${from.x}px;
      transform-origin: left center;
      transform: rotate(${angle}rad);
      pointer-events: none;
      z-index: 100;
      animation: beam-fade 0.6s ease-out;
    `;
    
    document.body.appendChild(beam);
    
    setTimeout(() => {
      this.createFreezeEffect(to);
      beam.remove();
    }, 600);
  }

  createFreezeEffect(position) {
    // Create ice crystals
    for (let i = 0; i < 20; i++) {
      const crystal = document.createElement('div');
      const size = 6 + Math.random() * 10;
      const angle = Math.random() * Math.PI * 2;
      const distance = 30 + Math.random() * 40;
      
      crystal.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        background: linear-gradient(135deg, #add8e6, #87ceeb);
        top: ${position.y + Math.sin(angle) * distance}px;
        left: ${position.x + Math.cos(angle) * distance}px;
        transform: rotate(${Math.random() * 360}deg);
        pointer-events: none;
        z-index: 100;
        opacity: 0.8;
        animation: crystal-fade 0.8s ease-out;
      `;
      
      document.body.appendChild(crystal);
      setTimeout(() => crystal.remove(), 800);
    }
  }

  createPsychic(from, to) {
    // Create psychic waves
    for (let i = 0; i < 5; i++) {
      setTimeout(() => {
        const wave = document.createElement('div');
        wave.style.cssText = `
          position: absolute;
          width: 100px;
          height: 100px;
          border: 3px solid #f85888;
          border-radius: 50%;
          top: ${to.y - 50}px;
          left: ${to.x - 50}px;
          pointer-events: none;
          z-index: 100;
          opacity: 0.8;
          animation: psychic-wave 0.8s ease-out;
        `;
        
        document.body.appendChild(wave);
        setTimeout(() => wave.remove(), 800);
      }, i * 150);
    }
  }

  createGenericProjectile(from, to, moveType, color) {
    const projectile = document.createElement('div');
    projectile.style.cssText = `
      position: absolute;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: radial-gradient(circle, ${color}, transparent);
      box-shadow: 0 0 20px ${color};
      top: ${from.y - 20}px;
      left: ${from.x - 20}px;
      pointer-events: none;
      z-index: 100;
    `;
    
    document.body.appendChild(projectile);
    
    setTimeout(() => {
      projectile.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
      projectile.style.top = `${to.y - 20}px`;
      projectile.style.left = `${to.x - 20}px`;
      projectile.style.transform = 'scale(1.5)';
      projectile.style.opacity = '0';
    }, 50);
    
    setTimeout(() => {
      this.createImpactParticles(to, color, 15);
      projectile.remove();
    }, 650);
  }

  // ============================================================================
  // PARTICLE SYSTEM
  // ============================================================================

  createParticle(position, color, velocity = 50, angle = null, size = 8) {
    if (!this.ctx) {
      // Fallback DOM particle
      const particle = document.createElement('div');
      const finalAngle = angle !== null ? angle : Math.random() * Math.PI * 2;
      const dx = Math.cos(finalAngle) * velocity;
      const dy = Math.sin(finalAngle) * velocity;
      
      particle.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        background: ${color};
        top: ${position.y}px;
        left: ${position.x}px;
        pointer-events: none;
        z-index: 100;
      `;
      
      document.body.appendChild(particle);
      
      setTimeout(() => {
        particle.style.transition = 'all 0.8s ease-out';
        particle.style.top = `${position.y + dy}px`;
        particle.style.left = `${position.x + dx}px`;
        particle.style.opacity = '0';
        particle.style.transform = 'scale(0)';
      }, 50);
      
      setTimeout(() => particle.remove(), 850);
      return;
    }
    
    // Canvas particle (better performance)
    const finalAngle = angle !== null ? angle : Math.random() * Math.PI * 2;
    const particle = new Particle(
      position.x,
      position.y,
      Math.cos(finalAngle) * velocity,
      Math.sin(finalAngle) * velocity,
      color,
      size
    );
    
    this.particles.push(particle);
  }

  createImpactParticles(position, color, count = 15) {
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2;
      const velocity = 40 + Math.random() * 60;
      const size = 4 + Math.random() * 8;
      
      this.createParticle(position, color, velocity, angle, size);
    }
  }

  // ============================================================================
  // SPECIAL EFFECTS
  // ============================================================================

  createVictoryEffect() {
    // Confetti burst
    const colors = ['#FFD700', '#FFA500', '#FF69B4', '#00CED1', '#7FFF00'];
    
    for (let i = 0; i < 50; i++) {
      setTimeout(() => {
        const color = colors[Math.floor(Math.random() * colors.length)];
        const x = window.innerWidth / 2;
        const y = window.innerHeight / 2;
        
        this.createParticle({x, y}, color, 100 + Math.random() * 100, null, 10);
      }, i * 30);
    }
  }

  // ============================================================================
  // TYPE COLORS
  // ============================================================================

  getTypeColor(type) {
    const colors = {
      fire: '#F08030',
      water: '#6890F0',
      grass: '#78C850',
      electric: '#F8D030',
      ice: '#98D8D8',
      fighting: '#C03028',
      poison: '#A040A0',
      ground: '#E0C068',
      flying: '#A890F0',
      psychic: '#F85888',
      bug: '#A8B820',
      rock: '#B8A038',
      ghost: '#705898',
      dragon: '#7038F8',
      dark: '#705848',
      steel: '#B8B8D0',
      fairy: '#EE99AC',
      normal: '#A8A878'
    };
    
    return colors[type] || '#A8A878';
  }
}

// ============================================================================
// PARTICLE CLASS
// ============================================================================

class Particle {
  constructor(x, y, vx, vy, color, size) {
    this.x = x;
    this.y = y;
    this.vx = vx;
    this.vy = vy;
    this.color = color;
    this.size = size;
    this.life = 1.0;
    this.decay = 0.02;
    this.gravity = 0.5;
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.vy += this.gravity;
    this.vx *= 0.98;
    this.vy *= 0.98;
    this.life -= this.decay;
  }

  draw(ctx) {
    ctx.save();
    ctx.globalAlpha = this.life;
    ctx.fillStyle = this.color;
    ctx.beginPath();
    // Fix: Prevent negative radius
    const radius = Math.max(0.1, this.size * this.life);
    ctx.arc(this.x, this.y, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

// ============================================================================
// CSS ANIMATIONS (injected dynamically)
// ============================================================================

const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes slash-swipe {
    from { opacity: 0; transform: scale(0.5) rotate(-45deg); }
    50% { opacity: 1; }
    to { opacity: 0; transform: scale(1.5) rotate(-45deg); }
  }

  @keyframes impact-ring {
    from { transform: scale(0); opacity: 1; }
    to { transform: scale(2); opacity: 0; }
  }

  @keyframes speed-line {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(150px); opacity: 0; }
  }

  @keyframes vine-grow {
    from { height: 0; }
    to { height: 100%; }
  }

  @keyframes vine-shrink {
    from { height: 100%; }
    to { height: 0; }
  }

  @keyframes beam-fade {
    0% { opacity: 0; }
    20% { opacity: 1; }
    100% { opacity: 0; }
  }

  @keyframes crystal-fade {
    0% { opacity: 0; transform: scale(0) rotate(0deg); }
    50% { opacity: 0.8; }
    100% { opacity: 0; transform: scale(1) rotate(180deg); }
  }

  @keyframes psychic-wave {
    from { transform: scale(0.5); opacity: 0.8; }
    to { transform: scale(2.5); opacity: 0; }
  }

  @keyframes flash-white {
    0%, 100% { filter: brightness(1); }
    50% { filter: brightness(2); }
  }
`;

document.head.appendChild(styleSheet);