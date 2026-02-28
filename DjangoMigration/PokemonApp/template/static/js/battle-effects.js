/**
 * BattleEffects — Moteur d'animations basé sur PokémonShowdown
 *
 * Architecture :
 *   - showEffect(sprite, start, end, transition, after)  → anime un PNG de PS depuis le CDN
 *   - backgroundEffect(color, duration, opacity, delay)  → flash de fond coloré
 *   - Sprite animations (attacker bounce / defender shake) via CSS class
 *   - playMoveAnimation(moveName, from, to, isPlayer)    → animation nommée
 *   - specialAttack / physicalAttack                     → compatibilité legacy
 *
 * Sprites PNG chargés depuis : https://play.pokemonshowdown.com/fx/
 */

const PS_FX_BASE = 'https://play.pokemonshowdown.com/fx/';

// ─── Catalogue des sprites disponibles (w/h en px natifs) ────────────────────
const PS_SPRITES = {
  // Énergie / générique
  wisp:         { url: 'wisp.png',         w: 100, h: 100 },
  electroball:  { url: 'electroball.png',  w: 100, h: 100 },
  energyball:   { url: 'energyball.png',   w: 100, h: 100 },
  shadowball:   { url: 'shadowball.png',   w: 100, h: 100 },
  mistball:     { url: 'mistball.png',     w: 100, h: 100 },
  iceball:      { url: 'iceball.png',      w: 100, h: 100 },
  flareball:    { url: 'flareball.png',    w: 100, h: 100 },
  // Feu
  fireball:     { url: 'fireball.png',     w: 64,  h: 64  },
  bluefireball: { url: 'bluefireball.png', w: 64,  h: 64  },
  // Eau
  waterwisp:    { url: 'waterwisp.png',    w: 100, h: 100 },
  mudwisp:      { url: 'mudwisp.png',      w: 100, h: 100 },
  // Glace
  icicle:       { url: 'icicle.png',       w: 80,  h: 60  },
  // Électricité
  lightning:    { url: 'lightning.png',    w: 41,  h: 229 },
  // Poison
  poisonwisp:   { url: 'poisonwisp.png',   w: 100, h: 100 },
  // Plante
  leaf1:        { url: 'leaf1.png',        w: 32,  h: 26  },
  leaf2:        { url: 'leaf2.png',        w: 40,  h: 26  },
  // Roche / sol
  rocks:        { url: 'rocks.png',        w: 100, h: 100 },
  rock1:        { url: 'rock1.png',        w: 64,  h: 80  },
  rock2:        { url: 'rock2.png',        w: 66,  h: 72  },
  rock3:        { url: 'rock3.png',        w: 66,  h: 72  },
  // Coups physiques
  rightslash:   { url: 'rightslash.png',   w: 100, h: 100 },
  leftslash:    { url: 'leftslash.png',    w: 100, h: 100 },
  rightchop:    { url: 'rightchop.png',    w: 100, h: 100 },
  leftchop:     { url: 'leftchop.png',     w: 100, h: 100 },
  fist:         { url: 'fist.png',         w: 69,  h: 69  },
  fist1:        { url: 'fist1.png',        w: 69,  h: 69  },
  foot:         { url: 'foot.png',         w: 49,  h: 52  },
  impact:       { url: 'impact.png',       w: 100, h: 100 },
  hitmark:      { url: 'hitmarker.png',    w: 100, h: 100 },
  // Divers
  blackwisp:    { url: 'blackwisp.png',    w: 100, h: 100 },
  rainbow:      { url: 'rainbow.png',      w: 100, h: 100 },
  heart:        { url: 'heart.png',        w: 32,  h: 28  },
  stare:        { url: 'stare.png',        w: 100, h: 100 },
  angry:        { url: 'angry.png',        w: 100, h: 100 },
  shine:        { url: 'shine.png',        w: 70,  h: 70  },
  pokeball:     { url: 'pokeball.png',     w: 24,  h: 24  },
  bone:         { url: 'bone.png',         w: 29,  h: 29  },
  petal:        { url: 'petal.png',        w: 28,  h: 24  },
};

// Easing functions (jQuery-style custom)
const EASINGS = {
  linear:      t => t,
  quadUp:      t => t * t,
  quadDown:    t => t * (2 - t),
  ballisticUp: t => {
    if (t < 0.5) return t * t * 2;
    const u = 2 * t - 1; return 1 - u * u * 0.5;
  },
  ballisticDown: t => {
    if (t < 0.5) { const u = 2 * t; return 1 - u * u * 0.5; }
    return (2 * t - 1) * (2 * t - 1) * 0.5;
  },
  swing: t => 0.5 - Math.cos(t * Math.PI) / 2,
  decel: t => t * (2 - t),
  accel: t => t * t,
};

// ─────────────────────────────────────────────────────────────────────────────

class BattleEffects {
  /**
   * @param {HTMLCanvasElement|null} canvas  — canvas pour les particules legacy
   */
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas ? canvas.getContext('2d') : null;
    this.particles = [];

    // Conteneur $fx : div absolu par-dessus la scène pour les sprites PS
    this.$scene = document.querySelector('.battle-scene');
    this.$fx    = this._createFxLayer();
    this.$bgFx  = this._createBgFxLayer();

    if (this.ctx) this._startParticleLoop();
    this._preloadSprites();
  }

  // ── DOM layers ────────────────────────────────────────────────────────────

  _createFxLayer() {
    let el = document.getElementById('ps-fx-layer');
    if (!el) {
      el = document.createElement('div');
      el.id = 'ps-fx-layer';
      el.style.cssText = [
        'position:absolute', 'top:0', 'left:0',
        'width:100%', 'height:100%',
        'pointer-events:none', 'z-index:50', 'overflow:hidden',
      ].join(';');
      (this.$scene || document.body).appendChild(el);
    }
    return el;
  }

  _createBgFxLayer() {
    let el = document.getElementById('ps-bg-fx-layer');
    if (!el) {
      el = document.createElement('div');
      el.id = 'ps-bg-fx-layer';
      el.style.cssText = [
        'position:absolute', 'top:0', 'left:0',
        'width:100%', 'height:100%',
        'pointer-events:none', 'z-index:2', 'overflow:hidden',
      ].join(';');
      (this.$scene || document.body).insertBefore(el, (this.$scene || document.body).firstChild);
    }
    return el;
  }

  _preloadSprites() {
    Object.values(PS_SPRITES).forEach(sp => {
      const img = new Image();
      img.src = PS_FX_BASE + sp.url;
    });
  }

  // ── Coordinate helpers ────────────────────────────────────────────────────

  /**
   * Retourne {x, y} du centre d'un élément en coordonnées locales de .battle-scene
   * (espace non-scalé 1280×540), en tenant compte du transform: scale() appliqué.
   */
  _getCenter(el) {
    if (!el) return { x: 0, y: 0 };
    const scene = this.$scene;
    if (!scene) return { x: 0, y: 0 };
    const sceneRect = scene.getBoundingClientRect();
    const r = el.getBoundingClientRect();
    const scale = sceneRect.width / 1280;
    return {
      x: (r.left + r.width  / 2 - sceneRect.left) / scale,
      y: (r.top  + r.height / 2 - sceneRect.top)  / scale,
    };
  }

  /**
   * Convertit une position {x, y} en coordonnées CSS pour un sprite
   * (positionne le centre de l'image au point x, y)
   */
  _spriteCSS(sp, loc, scaleOverride) {
    const sc = (scaleOverride !== undefined ? scaleOverride : (loc.scale !== undefined ? loc.scale : 1));
    const xs = loc.xscale !== undefined ? loc.xscale : sc;
    const ys = loc.yscale !== undefined ? loc.yscale : sc;
    const w  = sp.w * xs;
    const h  = sp.h * ys;
    return {
      position:   'absolute',
      width:      w + 'px',
      height:     h + 'px',
      left:       (loc.x - w / 2) + 'px',
      top:        (loc.y - h / 2) + 'px',
      opacity:    loc.opacity !== undefined ? loc.opacity : 1,
      'pointer-events': 'none',
    };
  }

  // ── Core animation engine ─────────────────────────────────────────────────

  /**
   * showEffect(spriteName, startPos, endPos, transition, after)
   *
   * Crée un <img> du sprite PS et l'anime de startPos → endPos.
   * Compatible avec l'API PS (même noms de paramètres).
   *
   * @param {string}  spriteName  — clé dans PS_SPRITES
   * @param {object}  start       — { x, y, scale?, xscale?, yscale?, opacity?, time? }
   * @param {object}  end         — { x, y, scale?, opacity?, time? }
   * @param {string}  transition  — 'linear'|'decel'|'accel'|'ballistic'|'swing'
   * @param {string}  after       — 'fade'|'explode'|undefined
   * @returns HTMLImageElement
   */
  showEffect(spriteName, start, end, transition = 'linear', after = undefined) {
    const sp = typeof spriteName === 'object' ? spriteName : PS_SPRITES[spriteName];
    if (!sp) {
      console.warn('[BattleEffects] sprite inconnu :', spriteName);
      return null;
    }

    const img = document.createElement('img');
    img.src = PS_FX_BASE + sp.url;
    img.style.position = 'absolute';
    img.style.pointerEvents = 'none';
    this.$fx.appendChild(img);

    const startTime  = (start.time || 0);
    const endTime    = (end.time   || startTime + 500);
    const duration   = endTime - startTime;

    // --- Valeurs interpolées ---
    const s = {
      x:       start.x       || 0,
      y:       start.y       || 0,
      scale:   start.scale   !== undefined ? start.scale   : 1,
      xscale:  start.xscale  !== undefined ? start.xscale  : (start.scale !== undefined ? start.scale : 1),
      yscale:  start.yscale  !== undefined ? start.yscale  : (start.scale !== undefined ? start.scale : 1),
      opacity: start.opacity !== undefined ? start.opacity : 1,
    };
    const e = {
      x:       end.x       !== undefined ? end.x       : s.x,
      y:       end.y       !== undefined ? end.y       : s.y,
      scale:   end.scale   !== undefined ? end.scale   : s.scale,
      xscale:  end.xscale  !== undefined ? end.xscale  : (end.scale !== undefined ? end.scale : s.xscale),
      yscale:  end.yscale  !== undefined ? end.yscale  : (end.scale !== undefined ? end.scale : s.yscale),
      opacity: end.opacity !== undefined ? end.opacity : s.opacity,
    };

    const easeFn = EASINGS[transition] || EASINGS.linear;
    let rafId = null;
    let startTs = null;

    const applyState = (state) => {
      const w = sp.w * state.xscale;
      const h = sp.h * state.yscale;
      img.style.width   = w + 'px';
      img.style.height  = h + 'px';
      img.style.left    = (state.x - w / 2) + 'px';
      img.style.top     = (state.y - h / 2) + 'px';
      img.style.opacity = Math.max(0, Math.min(1, state.opacity));
    };

    const lerp = (a, b, t) => a + (b - a) * t;

    const animate = (ts) => {
      if (!startTs) startTs = ts;
      const elapsed = ts - startTs;
      const rawT = Math.min(1, elapsed / Math.max(1, duration));
      const t    = easeFn(rawT);

      applyState({
        x:       lerp(s.x, e.x, t),
        y:       lerp(s.y, e.y, t),
        xscale:  lerp(s.xscale, e.xscale, t),
        yscale:  lerp(s.yscale, e.yscale, t),
        opacity: lerp(s.opacity, e.opacity, t),
      });

      if (rawT < 1) {
        rafId = requestAnimationFrame(animate);
      } else {
        // after effects
        if (after === 'fade') {
          this._fadeOut(img, 100, () => img.remove());
        } else if (after === 'explode') {
          const ex = e.xscale * 2.5;
          const ey = e.yscale * 2.5;
          this._tweenImg(img, { xscale: e.xscale, yscale: e.yscale, x: e.x, y: e.y, opacity: e.opacity },
                              { xscale: ex, yscale: ey, x: e.x, y: e.y, opacity: 0 }, sp, 200,
                              EASINGS.decel, () => img.remove());
        } else {
          img.remove();
        }
      }
    };

    if (startTime > 0) {
      img.style.opacity = '0';
      setTimeout(() => requestAnimationFrame(animate), startTime);
    } else {
      applyState(s);
      requestAnimationFrame(animate);
    }

    return img;
  }

  /** Tween rapide d'un img déjà en place */
  _tweenImg(img, from, to, sp, duration, easeFn, onDone) {
    let startTs = null;
    const lerp = (a, b, t) => a + (b - a) * t;
    const applyState = (state) => {
      const w = sp.w * state.xscale;
      const h = sp.h * state.yscale;
      img.style.width   = w + 'px';
      img.style.height  = h + 'px';
      img.style.left    = (state.x - w / 2) + 'px';
      img.style.top     = (state.y - h / 2) + 'px';
      img.style.opacity = Math.max(0, Math.min(1, state.opacity));
    };
    const tick = (ts) => {
      if (!startTs) startTs = ts;
      const rawT = Math.min(1, (ts - startTs) / Math.max(1, duration));
      const t = easeFn(rawT);
      applyState({ x: lerp(from.x, to.x, t), y: lerp(from.y, to.y, t),
                   xscale: lerp(from.xscale, to.xscale, t),
                   yscale: lerp(from.yscale, to.yscale, t),
                   opacity: lerp(from.opacity, to.opacity, t) });
      if (rawT < 1) requestAnimationFrame(tick);
      else if (onDone) onDone();
    };
    requestAnimationFrame(tick);
  }

  _fadeOut(el, duration, onDone) {
    let startTs = null;
    const tick = (ts) => {
      if (!startTs) startTs = ts;
      const t = Math.min(1, (ts - startTs) / duration);
      el.style.opacity = (1 - t);
      if (t < 1) requestAnimationFrame(tick);
      else if (onDone) onDone();
    };
    requestAnimationFrame(tick);
  }

  // ── Background effect ─────────────────────────────────────────────────────

  /**
   * Flash de fond coloré (identique à PS backgroundEffect)
   */
  backgroundEffect(bg, duration, opacity = 1, delay = 0) {
    const el = document.createElement('div');
    el.style.cssText = [
      'position:absolute', 'inset:0',
      `background:${bg}`, 'opacity:0',
      'pointer-events:none', 'z-index:3',
    ].join(';');
    this.$bgFx.appendChild(el);

    const fadeDur = Math.min(250, duration / 3);

    setTimeout(() => {
      this._tweenOpacity(el, 0, opacity, fadeDur, () => {
        setTimeout(() => {
          this._tweenOpacity(el, opacity, 0, fadeDur, () => el.remove());
        }, duration - fadeDur * 2);
      });
    }, delay);
  }

  _tweenOpacity(el, from, to, duration, onDone) {
    let startTs = null;
    const tick = (ts) => {
      if (!startTs) startTs = ts;
      const t = Math.min(1, (ts - startTs) / Math.max(1, duration));
      el.style.opacity = from + (to - from) * t;
      if (t < 1) requestAnimationFrame(tick);
      else if (onDone) onDone();
    };
    requestAnimationFrame(tick);
  }

  // ── Sprite animations (CSS class) ────────────────────────────────────────

  attackSprite(isPlayer) {
    const id = isPlayer ? '#player-sprite' : '#opponent-sprite';
    const el = document.querySelector(id);
    if (!el) return;
    el.classList.add('attacking');
    setTimeout(() => el.classList.remove('attacking'), 600);
  }

  damageSprite(isPlayer, delayMs = 0) {
    const id = isPlayer ? '#player-sprite' : '#opponent-sprite';
    const el = document.querySelector(id);
    if (!el) return;
    setTimeout(() => {
      el.classList.add('taking-damage');
      setTimeout(() => el.classList.remove('taking-damage'), 600);
    }, delayMs);
  }

  // ── Clear ─────────────────────────────────────────────────────────────────

  clearEffects() {
    this.$fx.innerHTML    = '';
    this.$bgFx.innerHTML  = '';
  }

  // =========================================================================
  // MOVE ANIMATIONS — portage direct depuis PS graphics.js
  // =========================================================================

  /**
   * Point d'entrée principal.
   *
   * @param {string}  moveName  — nom normalisé (ex: 'thunderbolt', 'flamethrower')
   * @param {{x,y}}   from      — position de l'attaquant (centre, px dans .battle-scene)
   * @param {{x,y}}   to        — position du défenseur
   * @param {boolean} isPlayer  — true si c'est le joueur qui attaque
   * @param {string}  moveType  — type Pokémon (fallback si moveName inconnu)
   * @param {string}  moveCategory — 'physical'|'special'|'status'
   */
  playMoveAnimation(moveName, from, to, isPlayer = true, moveType = 'normal', moveCategory = 'special') {
    // Nettoyage doux des effets précédents
    this.clearEffects();

    // Sprite bounce attaquant
    this.attackSprite(isPlayer);

    // Damage sprite au moment de l'impact (~400ms)
    this.damageSprite(!isPlayer, 450);

    const scene = this;  // alias pour lisibilité dans les anims

    // Lookup par nom exact puis fallback par type
    const fn = MOVE_ANIMS[moveName] || MOVE_ANIMS['__type__' + moveType];
    if (fn) {
      fn(scene, from, to, isPlayer);
    } else if (moveCategory === 'physical') {
      MOVE_ANIMS.__physical(scene, from, to, isPlayer);
    } else {
      MOVE_ANIMS.__generic_special(scene, from, to, isPlayer, moveType);
    }
  }

  // ── Legacy API (compatibilité battle-game.js existant) ───────────────────

  physicalAttack(from, to, type = 'slash') {
    this.clearEffects();
    if (type === 'slash') {
      MOVE_ANIMS.slash(this, from, to, true);
    } else if (type === 'punch') {
      MOVE_ANIMS.megapunch(this, from, to, true);
    } else {
      MOVE_ANIMS.__physical(this, from, to, true);
    }
    this.damageSprite(false, 400);
  }

  specialAttack(from, to, moveType = 'normal') {
    this.clearEffects();
    const fn = MOVE_ANIMS['__type__' + moveType];
    if (fn) fn(this, from, to, true);
    else    MOVE_ANIMS.__generic_special(this, from, to, true, moveType);
    this.damageSprite(false, 400);
  }

  // ── Victory ───────────────────────────────────────────────────────────────

  createVictoryEffect() {
    const colors = ['#FFD700', '#FFA500', '#FF69B4', '#00CED1', '#7FFF00'];
    const scene = this.$scene || document.body;
    const sr = scene.getBoundingClientRect();

    for (let i = 0; i < 40; i++) {
      setTimeout(() => {
        const color = colors[Math.floor(Math.random() * colors.length)];
        const x = sr.width  * (0.3 + Math.random() * 0.4);
        const y = sr.height * (0.3 + Math.random() * 0.4);
        this._domParticle({ x, y }, color, 100 + Math.random() * 80, null, 10, true);
      }, i * 40);
    }
  }

  // ── Canvas particle system (legacy) ──────────────────────────────────────

  _startParticleLoop() {
    const loop = () => {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.particles = this.particles.filter(p => { p.update(); p.draw(this.ctx); return p.life > 0; });
      requestAnimationFrame(loop);
    };
    loop();
  }

  createImpactParticles(pos, color, count = 12) {
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2;
      this._domParticle(pos, color, 50 + Math.random() * 40, angle, 5 + Math.random() * 6, false);
    }
  }

  _domParticle(pos, color, velocity = 50, angle = null, size = 8, gravity = false) {
    const a = angle !== null ? angle : Math.random() * Math.PI * 2;
    const dx = Math.cos(a) * velocity;
    const dy = Math.sin(a) * velocity;

    const el = document.createElement('div');
    el.style.cssText = [
      'position:absolute',
      `width:${size}px`, `height:${size}px`,
      'border-radius:50%',
      `background:${color}`,
      `top:${pos.y}px`, `left:${pos.x}px`,
      'pointer-events:none', 'z-index:200',
    ].join(';');
    (this.$fx || document.body).appendChild(el);

    const start  = performance.now();
    const dur    = 700;
    let prevT    = 0;
    let vy       = dy;
    let cx = pos.x, cy = pos.y;

    const tick = (now) => {
      const dt = (now - start - prevT * dur) / 1000;
      const t  = Math.min(1, (now - start) / dur);
      cx += dx * (1/60);
      vy += gravity ? 0.5 : 0;
      cy += vy * (1/60);
      el.style.left    = cx + 'px';
      el.style.top     = cy + 'px';
      el.style.opacity = 1 - t;
      if (t < 1) requestAnimationFrame(tick);
      else el.remove();
    };
    requestAnimationFrame(tick);
  }

  getTypeColor(type) {
    const c = {
      fire:'#F08030',water:'#6890F0',grass:'#78C850',electric:'#F8D030',
      ice:'#98D8D8',fighting:'#C03028',poison:'#A040A0',ground:'#E0C068',
      flying:'#A890F0',psychic:'#F85888',bug:'#A8B820',rock:'#B8A038',
      ghost:'#705898',dragon:'#7038F8',dark:'#705848',steel:'#B8B8D0',
      fairy:'#EE99AC',normal:'#A8A878',
    };
    return c[type] || '#A8A878';
  }
}

// =============================================================================
// BIBLIOTHÈQUE D'ANIMATIONS — portage fidèle de PS graphics.js
//
// Chaque fonction reçoit : (scene, attacker, defender, isPlayer)
// où attacker/defender sont des { x, y } en px dans .battle-scene
// =============================================================================

const MOVE_ANIMS = {

  // ── Coups physiques génériques ──────────────────────────────────────────

  __physical(scene, atk, def, isPlayer) {
    // Attacker se précipite vers le défenseur
    const el = document.querySelector(isPlayer ? '#player-sprite' : '#opponent-sprite');
    const defEl = document.querySelector(isPlayer ? '#opponent-sprite' : '#player-sprite');
    if (el) {
      el.style.transition = 'transform 0.15s ease-out';
      const dir = isPlayer ? 1 : -1;
      el.style.transform = `translateX(${dir * 60}px)`;
      setTimeout(() => { el.style.transform = ''; el.style.transition = ''; }, 300);
    }
    setTimeout(() => {
      scene.showEffect('impact', { x: def.x, y: def.y, scale: 0.5, opacity: 1 },
                                 { scale: 1.5, opacity: 0, time: 300 }, 'decel', 'fade');
    }, 150);
  },

  // ── Coups physiques nommés ─────────────────────────────────────────────

  tackle(scene, atk, def) {
    const el = document.querySelector('#player-sprite');
    const oel = document.querySelector('#opponent-sprite');
    if (el) {
      el.style.transition = 'transform 0.18s ease-out';
      el.style.transform = 'translateX(70px)';
      setTimeout(() => { el.style.transform = ''; el.style.transition = ''; }, 350);
    }
    scene.showEffect('impact', { x: def.x, y: def.y, scale: 0.3, opacity: 0 },
                               { scale: 1.2, opacity: 1, time: 200 }, 'decel', 'explode');
  },

  slash(scene, atk, def) {
    scene.showEffect('rightslash', { x: def.x, y: def.y, scale: 0.5, opacity: 0 },
                                   { scale: 1.2, opacity: 1, time: 200 }, 'decel', 'fade');
    setTimeout(() => {
      scene.showEffect('leftslash',  { x: def.x, y: def.y - 10, scale: 0.5, opacity: 0 },
                                     { scale: 1.3, opacity: 0.9, time: 200 }, 'decel', 'fade');
    }, 150);
    setTimeout(() => {
      scene.showEffect('rightslash', { x: def.x + 5, y: def.y + 10, scale: 0.4, opacity: 0 },
                                     { scale: 1.1, opacity: 0.8, time: 200 }, 'decel', 'fade');
    }, 300);
  },

  scratch(scene, atk, def) {
    scene.showEffect('rightslash', { x: def.x, y: def.y, scale: 0.5, opacity: 1 },
                                   { scale: 1.0, opacity: 0, time: 300 }, 'decel', 'fade');
    setTimeout(() => {
      scene.showEffect('rightslash', { x: def.x - 10, y: def.y + 15, scale: 0.4, opacity: 0.8 },
                                     { scale: 0.9, opacity: 0, time: 300 }, 'decel', 'fade');
    }, 150);
  },

  megapunch(scene, atk, def) {
    scene.showEffect('fist', { x: atk.x, y: atk.y, scale: 0.5, opacity: 1 },
                             { x: def.x, y: def.y, scale: 1, time: 350 }, 'decel', 'explode');
  },

  doubleedge(scene, atk, def) {
    const el = document.querySelector('#player-sprite, #opponent-sprite');
    MOVE_ANIMS.__physical(scene, atk, def, true);
    scene.showEffect('impact', { x: def.x, y: def.y, scale: 0.6, opacity: 1 },
                               { scale: 2, opacity: 0, time: 400 }, 'decel', 'fade');
  },

  bodyslam(scene, atk, def) {
    scene.showEffect('impact', { x: def.x, y: def.y + 20, scale: 0.3, opacity: 0 },
                               { scale: 1.8, opacity: 1, time: 300 }, 'accel', 'explode');
    setTimeout(() => {
      scene.showEffect('impact', { x: def.x, y: def.y, scale: 0.2, opacity: 0.5 },
                                 { scale: 1.5, opacity: 0, time: 300 }, 'decel', 'fade');
    }, 200);
  },

  // ── Plante ─────────────────────────────────────────────────────────────

  vinewhip(scene, atk, def) {
    for (let i = 0; i < 4; i++) {
      scene.showEffect('leaf1', {
        x: atk.x + (Math.random() - 0.5) * 30,
        y: atk.y,
        scale: 0.8, opacity: 0.8, time: i * 80,
      }, {
        x: def.x + (Math.random() - 0.5) * 20,
        y: def.y - 10,
        scale: 1.2, opacity: 0.6, time: i * 80 + 350,
      }, 'decel', 'explode');
    }
    setTimeout(() => {
      scene.showEffect('leaf2', { x: def.x, y: def.y, scale: 0.5, opacity: 0 },
                                { scale: 1.5, opacity: 0, time: 200 }, 'decel', 'fade');
    }, 300);
  },

  razorleaf(scene, atk, def) {
    for (let i = 0; i < 6; i++) {
      const offset = (i - 2.5) * 18;
      scene.showEffect('leaf1', {
        x: atk.x, y: atk.y, scale: 0.7, opacity: 0.8, time: i * 60,
      }, {
        x: def.x + offset, y: def.y + offset * 0.3, scale: 1.1, opacity: 0.9, time: i * 60 + 400,
      }, 'linear', 'explode');
    }
  },

  solarbeam(scene, atk, def) {
    scene.backgroundEffect('#ffff88', 600, 0.4);
    // Charge (énergie montant au-dessus de l'attaquant)
    scene.showEffect('energyball', { x: atk.x, y: atk.y, scale: 0.4, opacity: 0.6 },
                                   { x: atk.x, y: atk.y - 120, scale: 1.2, opacity: 0, time: 400 }, 'decel');
    // Faisceau
    for (let i = 0; i < 5; i++) {
      scene.showEffect('flareball', {
        x: atk.x, y: atk.y - 100, scale: 0.4, opacity: 0.6, time: 300 + i * 75,
      }, {
        x: def.x + (i - 2) * 15, y: def.y, scale: 0.6, opacity: 0.3, time: 500 + i * 75,
      }, 'linear', 'explode');
    }
  },

  seedbomb(scene, atk, def) {
    scene.showEffect('energyball', { x: atk.x, y: atk.y, scale: 0.5, opacity: 0.8 },
                                   { x: def.x, y: def.y, scale: 1, opacity: 1, time: 350 }, 'decel', 'explode');
  },

  // ── Feu ────────────────────────────────────────────────────────────────

  flamethrower(scene, atk, def) {
    for (let i = 0; i < 4; i++) {
      const ox = (i - 1.5) * 12;
      const oy = (i % 2) * 8 - 4;
      scene.showEffect('fireball', {
        x: atk.x, y: atk.y, scale: 0.8, opacity: 0.7, time: i * 100,
      }, {
        x: def.x + ox, y: def.y + oy, opacity: 0.5, time: i * 100 + 400,
      }, 'decel', 'explode');
    }
  },

  ember(scene, atk, def) {
    MOVE_ANIMS.flamethrower(scene, atk, def);
  },

  fireblast(scene, atk, def) {
    scene.backgroundEffect('#ff4400', 500, 0.2);
    for (let i = 0; i < 6; i++) {
      const angle = (i / 6) * Math.PI * 2;
      const r = 40;
      scene.showEffect('fireball', {
        x: atk.x, y: atk.y, scale: 0.6, opacity: 0.8, time: i * 50,
      }, {
        x: def.x + Math.cos(angle) * r, y: def.y + Math.sin(angle) * r * 0.5,
        scale: 1.2, opacity: 0.4, time: i * 50 + 500,
      }, 'decel', 'explode');
    }
  },

  firespin(scene, atk, def) {
    for (let i = 0; i < 5; i++) {
      const a = (i / 5) * Math.PI * 2;
      scene.showEffect('flareball', {
        x: def.x + Math.cos(a) * 60, y: def.y + Math.sin(a) * 30,
        scale: 0.5, opacity: 0.7, time: i * 120,
      }, {
        x: def.x + Math.cos(a + 2) * 40, y: def.y + Math.sin(a + 2) * 20,
        scale: 0.8, opacity: 0, time: i * 120 + 400,
      }, 'linear', 'fade');
    }
  },

  // ── Eau ────────────────────────────────────────────────────────────────

  watergun(scene, atk, def) {
    for (let i = 0; i < 3; i++) {
      const oy = (i - 1) * 12;
      scene.showEffect('waterwisp', {
        x: atk.x, y: atk.y, scale: 0.3, opacity: 0.7, time: i * 100,
      }, {
        x: def.x, y: def.y + oy, scale: 0.7, opacity: 0.6, time: i * 100 + 400,
      }, 'decel', 'explode');
    }
  },

  surf(scene, atk, def) {
    scene.backgroundEffect('#0044cc', 700, 0.18);
    for (const ox of [0, -50, 50]) {
      scene.showEffect('waterwisp', {
        x: atk.x, y: atk.y - 20, scale: 0.35, opacity: 0.3,
      }, {
        x: def.x + ox, y: def.y, scale: 1, opacity: 0.6, time: 450,
      }, 'decel', 'explode');
    }
  },

  hydropump(scene, atk, def) {
    scene.backgroundEffect('#0044cc', 700, 0.2);
    for (let i = 0; i < 3; i++) {
      const oy = (i - 1) * 15;
      scene.showEffect('waterwisp', {
        x: atk.x, y: atk.y, scale: 0.4, opacity: 0.8, time: i * 80,
      }, {
        x: def.x, y: def.y + oy, scale: 1.1, opacity: 0.5, time: i * 80 + 480,
      }, 'decel', 'explode');
    }
  },

  blizzard(scene, atk, def) {
    scene.backgroundEffect('#aaddff', 600, 0.25);
    for (let i = 0; i < 6; i++) {
      const oy = (i - 2.5) * 15;
      scene.showEffect('icicle', {
        x: atk.x, y: atk.y, scale: 0.8, opacity: 0.7, time: i * 60,
      }, {
        x: def.x + (i % 2 === 0 ? 20 : -20), y: def.y + oy,
        scale: 1.1, opacity: 0.4, time: i * 60 + 450,
      }, 'linear', 'fade');
    }
  },

  // ── Glace ──────────────────────────────────────────────────────────────

  icebeam(scene, atk, def) {
    const steps = 5;
    const dx = (def.x - atk.x) / steps;
    const dy = (def.y - atk.y) / steps;
    for (let i = 0; i < 4; i++) {
      scene.showEffect('icicle', {
        x: atk.x + dx * (i + 1), y: atk.y + dy * (i + 1),
        scale: 1.2, opacity: 0.6, time: 40 * i,
      }, { opacity: 0, time: 40 * i + 500 }, 'linear');
    }
    scene.showEffect('iceball', { x: def.x, y: def.y, scale: 0, opacity: 1, time: 100 },
                                { scale: 2, opacity: 0, time: 450 }, 'linear');
    scene.showEffect('iceball', { x: def.x, y: def.y, scale: 0, opacity: 1, time: 300 },
                                { scale: 2, opacity: 0, time: 650 }, 'linear');
    // wisp
    for (const [ox, oy, t] of [[-30,0,200],[0,-30,300],[15,0,400]]) {
      scene.showEffect('wisp', { x: def.x + ox, y: def.y + oy, scale: 1.5, opacity: 0.5, time: t },
                               { scale: 3.5, opacity: 0, time: t + 400 }, 'linear', 'fade');
    }
  },

  // ── Électricité ────────────────────────────────────────────────────────

  thunderbolt(scene, atk, def) {
    scene.backgroundEffect('#000000', 600, 0.2);
    const offsets = [0, -15, 15];
    offsets.forEach((ox, i) => {
      scene.showEffect('lightning', {
        x: def.x + ox, y: def.y + 150,
        yscale: 0, xscale: 2, time: i * 200,
      }, {
        y: def.y + 50, yscale: 1, xscale: 1.5, opacity: 0.8, time: i * 200 + 200,
      }, 'linear', 'fade');
    });
  },

  thunder(scene, atk, def) {
    scene.backgroundEffect('#ffffff', 200, 0.6);
    scene.backgroundEffect('#000000', 800, 0.2, 200);
    for (let i = 0; i < 4; i++) {
      const ox = (Math.random() - 0.5) * 40;
      scene.showEffect('lightning', {
        x: def.x + ox, y: def.y + 200,
        yscale: 0, xscale: 2.5, time: i * 150,
      }, {
        y: def.y + 30, yscale: 1.2, xscale: 2, opacity: 0.9, time: i * 150 + 250,
      }, 'linear', 'fade');
    }
  },

  thunderwave(scene, atk, def) {
    for (let i = 0; i < 2; i++) {
      scene.showEffect('electroball', {
        x: atk.x, y: atk.y, scale: 1, opacity: 0.2, time: i * 200,
      }, { scale: 8, opacity: 0.1, time: i * 200 + 600 }, 'linear', 'fade');
    }
    scene.showEffect('electroball', {
      x: def.x, y: def.y, scale: 1, opacity: 0.2, time: 500,
    }, { scale: 4, opacity: 0.1, time: 800 }, 'linear', 'fade');
    scene.backgroundEffect('#ffff44', 400, 0.1, 400);
  },

  // ── Psychique ──────────────────────────────────────────────────────────

  psychic(scene, atk, def) {
    scene.backgroundEffect('#AA44BB', 250, 0.5);
    scene.backgroundEffect('#AA44FF', 250, 0.5, 400);
    // Pulse du défenseur — on gère via CSS scale
    const defEl = document.querySelector('#opponent-sprite, #player-sprite');
    if (defEl) {
      const pulses = [[1.2, 100], [1.0, 100], [1.35, 150], [1.0, 150]];
      let delay = 0;
      pulses.forEach(([sc, dur]) => {
        setTimeout(() => {
          defEl.style.transition = `transform ${dur}ms ease-in-out`;
          defEl.style.transform  = `scale(${sc})`;
        }, delay);
        delay += dur;
      });
      setTimeout(() => { defEl.style.transition = ''; defEl.style.transform = ''; }, delay + 50);
    }
  },

  confusion(scene, atk, def) {
    MOVE_ANIMS.psychic(scene, atk, def);
  },

  // ── Spectre ────────────────────────────────────────────────────────────

  shadowball(scene, atk, def) {
    scene.backgroundEffect('#330033', 500, 0.3);
    scene.showEffect('shadowball', { x: atk.x, y: atk.y, scale: 0.5, opacity: 0.8 },
                                   { x: def.x, y: def.y, scale: 1.2, opacity: 1, time: 400 }, 'decel', 'explode');
    scene.showEffect('blackwisp', { x: atk.x, y: atk.y, scale: 0.3, opacity: 0.5, time: 80 },
                                  { x: def.x, y: def.y - 10, scale: 0.8, opacity: 0, time: 420 }, 'decel', 'fade');
  },

  nightshade(scene, atk, def) {
    scene.backgroundEffect('#330000', 500, 0.3);
    scene.showEffect('blackwisp', { x: atk.x, y: atk.y + 30, scale: 2.5, opacity: 0.3, time: 50 },
                                  { x: def.x, y: def.y + 35, scale: 3, opacity: 0.1, time: 600 }, 'accel', 'fade');
  },

  lick(scene, atk, def) {
    scene.backgroundEffect('#550055', 300, 0.2);
    MOVE_ANIMS.__physical(scene, atk, def, true);
  },

  // ── Sol ────────────────────────────────────────────────────────────────

  earthquake(scene, atk, def) {
    const scene_el = scene.$scene;
    if (scene_el) {
      // Tremblement du fond
      let t = 0;
      const shakes = [
        [0,-10],[10,10],[-7,0],[7,-5],[-7,0],[7,-5],[0,0]
      ];
      shakes.forEach(([dx, dy], i) => {
        setTimeout(() => {
          scene_el.style.transform = `translateX(${dx}px) translateY(${dy}px)`;
        }, i * 100);
      });
      setTimeout(() => { scene_el.style.transform = ''; }, 700);
    }
    for (let i = 0; i < 5; i++) {
      scene.showEffect('rocks', {
        x: def.x + (Math.random() - 0.5) * 80, y: def.y + 60,
        scale: 0.4, opacity: 0.8, time: i * 100,
      }, {
        y: def.y - 30, scale: 0.8, opacity: 0.3, time: i * 100 + 350,
      }, 'accel', 'fade');
    }
  },

  digdown: null,
  magnitude(scene, atk, def) { MOVE_ANIMS.earthquake(scene, atk, def); },
  fissure(scene, atk, def)   { MOVE_ANIMS.earthquake(scene, atk, def); },

  // ── Roche ──────────────────────────────────────────────────────────────

  rockslide(scene, atk, def) {
    for (let i = 0; i < 5; i++) {
      const sp = ['rock1', 'rock2', 'rock3'][i % 3];
      scene.showEffect(sp, {
        x: def.x + (Math.random() - 0.5) * 80,
        y: def.y - 100 - Math.random() * 60,
        scale: 0.5, opacity: 0.8, time: i * 80,
      }, {
        y: def.y + 20, scale: 0.8, opacity: 0.6, time: i * 80 + 450,
      }, 'accel', 'explode');
    }
  },

  rockthrow(scene, atk, def) {
    scene.showEffect('rock3', { x: atk.x, y: atk.y, scale: 0.6, opacity: 0.8 },
                              { x: def.x, y: def.y, scale: 0.8, opacity: 1, time: 400 }, 'ballistic', 'explode');
  },

  // ── Normal/Hyper ───────────────────────────────────────────────────────

  hyperbeam(scene, atk, def) {
    scene.backgroundEffect('#000000', 700, 0.25);
    const offsets = [[30,30,0],[20,-30,75],[-30,0,150],[-10,10,225],[10,-10,300],[-20,0,375]];
    offsets.forEach(([ox, oy, t]) => {
      scene.showEffect('electroball', {
        x: atk.x, y: atk.y, scale: 0.4, opacity: 0.6, time: t,
      }, {
        x: def.x + ox, y: def.y + oy, scale: 0.6, opacity: 0.3, time: t + 200,
      }, 'linear', 'explode');
    });
    // Explosion finale
    setTimeout(() => {
      scene.showEffect('shadowball', { x: def.x, y: def.y, scale: 0, opacity: 0.5, time: 0 },
                                     { scale: 4, opacity: 0, time: 300 }, 'decel');
    }, 600);
  },

  Swift(scene, atk, def) {
    for (let i = 0; i < 5; i++) {
      const oy = (i - 2) * 20;
      scene.showEffect('shine', { x: atk.x, y: atk.y + oy, scale: 0.5, opacity: 0.8, time: i * 50 },
                                { x: def.x, y: def.y + oy, scale: 1, opacity: 0.4, time: i * 50 + 350 },
                                'linear', 'fade');
    }
  },

  swift(scene, atk, def) { MOVE_ANIMS.Swift(scene, atk, def); },

  // ── Poison ─────────────────────────────────────────────────────────────

  toxic(scene, atk, def) {
    scene.showEffect('poisonwisp', {
      x: atk.x, y: atk.y, scale: 0.1, opacity: 0,
    }, {
      x: def.x, y: def.y, scale: 0.6, opacity: 1, time: 450,
    }, 'ballistic', 'explode');
  },

  poisonsting(scene, atk, def) {
    scene.showEffect('poisonwisp', {
      x: atk.x, y: atk.y, scale: 0.2, opacity: 0.8,
    }, {
      x: def.x, y: def.y, scale: 0.5, opacity: 1, time: 350,
    }, 'decel', 'explode');
  },

  // ── Statuts ────────────────────────────────────────────────────────────

  growl(scene, atk, def) {
    // Ondes sonores concentriques
    for (let i = 0; i < 3; i++) {
      scene.showEffect('electroball', {
        x: atk.x, y: atk.y, scale: 0, opacity: 0.3, time: i * 150,
      }, { scale: 4, opacity: 0, time: i * 150 + 500 }, 'decel', 'fade');
    }
  },

  roar: null,
  sing: null,
  supersonic(scene, atk, def) { MOVE_ANIMS.growl(scene, atk, def); },

  tailwhip(scene, atk, def) {
    MOVE_ANIMS.__physical(scene, atk, def, true);
  },

  string_shot(scene, atk, def) {
    scene.showEffect('wisp', { x: atk.x, y: atk.y, scale: 0.2, opacity: 0.7 },
                             { x: def.x, y: def.y, scale: 0.6, opacity: 0.3, time: 400 }, 'decel', 'fade');
  },

  // ── Soins / défensifs ──────────────────────────────────────────────────

  recover(scene, atk, def) {
    for (let i = 0; i < 5; i++) {
      scene.showEffect('wisp', {
        x: atk.x + (Math.random() - 0.5) * 60,
        y: atk.y + 60, scale: 0.3, opacity: 0, time: i * 80,
      }, {
        y: atk.y - 40, scale: 0.8, opacity: 0.6, time: i * 80 + 400,
      }, 'decel', 'fade');
    }
    scene.backgroundEffect('#44ff44', 400, 0.1);
  },

  softboiled(scene, atk, def) { MOVE_ANIMS.recover(scene, atk, def); },
  moonlight(scene, atk, def) { MOVE_ANIMS.recover(scene, atk, def); },

  // ── Dragon ─────────────────────────────────────────────────────────────

  dragonrage(scene, atk, def) {
    scene.backgroundEffect('#4400aa', 500, 0.25);
    for (let i = 0; i < 4; i++) {
      scene.showEffect('flareball', {
        x: atk.x, y: atk.y, scale: 0.3, opacity: 0.7, time: i * 80,
      }, {
        x: def.x + (i % 2 === 0 ? 20 : -20), y: def.y,
        scale: 0.8, opacity: 0.4, time: i * 80 + 400,
      }, 'decel', 'explode');
    }
  },

  // ── Type fallbacks ─────────────────────────────────────────────────────

  __type__fire    (scene, atk, def) { MOVE_ANIMS.flamethrower(scene, atk, def); },
  __type__water   (scene, atk, def) { MOVE_ANIMS.watergun(scene, atk, def); },
  __type__grass   (scene, atk, def) { MOVE_ANIMS.vinewhip(scene, atk, def); },
  __type__electric(scene, atk, def) { MOVE_ANIMS.thunderbolt(scene, atk, def); },
  __type__ice     (scene, atk, def) { MOVE_ANIMS.icebeam(scene, atk, def); },
  __type__psychic (scene, atk, def) { MOVE_ANIMS.psychic(scene, atk, def); },
  __type__ghost   (scene, atk, def) { MOVE_ANIMS.shadowball(scene, atk, def); },
  __type__rock    (scene, atk, def) { MOVE_ANIMS.rockthrow(scene, atk, def); },
  __type__ground  (scene, atk, def) { MOVE_ANIMS.earthquake(scene, atk, def); },
  __type__poison  (scene, atk, def) { MOVE_ANIMS.poisonsting(scene, atk, def); },
  __type__dragon  (scene, atk, def) { MOVE_ANIMS.dragonrage(scene, atk, def); },
  __type__normal  (scene, atk, def) { MOVE_ANIMS.__physical(scene, atk, def, true); },
  __type__fighting(scene, atk, def) { MOVE_ANIMS.megapunch(scene, atk, def); },
  __type__flying  (scene, atk, def) { MOVE_ANIMS.Swift(scene, atk, def); },
  __type__bug     (scene, atk, def) {
    scene.showEffect('leaf1', { x: atk.x, y: atk.y, scale: 0.7, opacity: 0.8 },
                              { x: def.x, y: def.y, scale: 1, opacity: 0.5, time: 350 }, 'decel', 'explode');
  },

  __generic_special(scene, atk, def, isPlayer, moveType) {
    const colors = {
      normal:'#ffffff', fire:'#ff6600', water:'#4488ff', electric:'#ffdd00',
      grass:'#44cc44', ice:'#88eeff', psychic:'#ff44aa', ghost:'#8844cc',
      dragon:'#7744ff', rock:'#ccaa44', ground:'#ccaa44', poison:'#aa44aa',
      bug:'#88aa44', fighting:'#cc4422', flying:'#8899ff', dark:'#664422',
      steel:'#aaaacc', fairy:'#ffaacc',
    };
    const color = colors[moveType] || '#ffffff';
    scene.showEffect('wisp', {
      x: atk.x, y: atk.y, scale: 0.3, opacity: 0.8,
    }, {
      x: def.x, y: def.y, scale: 1, opacity: 0, time: 400,
    }, 'decel', 'fade');
    setTimeout(() => scene.createImpactParticles(def, color, 12), 400);
  },
};

// Aliases Gen 1 courants
MOVE_ANIMS['double-edge']   = MOVE_ANIMS.doubleedge;
MOVE_ANIMS['vine-whip']     = MOVE_ANIMS.vinewhip;
MOVE_ANIMS['razor-leaf']    = MOVE_ANIMS.razorleaf;
MOVE_ANIMS['solar-beam']    = MOVE_ANIMS.solarbeam;
MOVE_ANIMS['fire-blast']    = MOVE_ANIMS.fireblast;
MOVE_ANIMS['fire-spin']     = MOVE_ANIMS.firespin;
MOVE_ANIMS['water-gun']     = MOVE_ANIMS.watergun;
MOVE_ANIMS['hydro-pump']    = MOVE_ANIMS.hydropump;
MOVE_ANIMS['ice-beam']      = MOVE_ANIMS.icebeam;
MOVE_ANIMS['thunder-bolt']  = MOVE_ANIMS.thunderbolt;
MOVE_ANIMS['thunder-wave']  = MOVE_ANIMS.thunderwave;
MOVE_ANIMS['shadow-ball']   = MOVE_ANIMS.shadowball;
MOVE_ANIMS['hyper-beam']    = MOVE_ANIMS.hyperbeam;
MOVE_ANIMS['rock-slide']    = MOVE_ANIMS.rockslide;
MOVE_ANIMS['rock-throw']    = MOVE_ANIMS.rockthrow;
MOVE_ANIMS['body-slam']     = MOVE_ANIMS.bodyslam;
MOVE_ANIMS['mega-punch']    = MOVE_ANIMS.megapunch;
MOVE_ANIMS['seed-bomb']     = MOVE_ANIMS.seedbomb;
MOVE_ANIMS['dragon-rage']   = MOVE_ANIMS.dragonrage;
MOVE_ANIMS['poison-sting']  = MOVE_ANIMS.poisonsting;
MOVE_ANIMS['night-shade']   = MOVE_ANIMS.nightshade;
MOVE_ANIMS['night shade']   = MOVE_ANIMS.nightshade;
MOVE_ANIMS['hyper beam']    = MOVE_ANIMS.hyperbeam;
MOVE_ANIMS['razor leaf']    = MOVE_ANIMS.razorleaf;
MOVE_ANIMS['solar beam']    = MOVE_ANIMS.solarbeam;
MOVE_ANIMS['vine whip']     = MOVE_ANIMS.vinewhip;
MOVE_ANIMS['water gun']     = MOVE_ANIMS.watergun;
MOVE_ANIMS['hydro pump']    = MOVE_ANIMS.hydropump;
MOVE_ANIMS['fire blast']    = MOVE_ANIMS.fireblast;
MOVE_ANIMS['fire spin']     = MOVE_ANIMS.firespin;
MOVE_ANIMS['ice beam']      = MOVE_ANIMS.icebeam;
MOVE_ANIMS['thunder bolt']  = MOVE_ANIMS.thunderbolt;
MOVE_ANIMS['thunder wave']  = MOVE_ANIMS.thunderwave;
MOVE_ANIMS['shadow ball']   = MOVE_ANIMS.shadowball;
MOVE_ANIMS['rock slide']    = MOVE_ANIMS.rockslide;
MOVE_ANIMS['rock throw']    = MOVE_ANIMS.rockthrow;
MOVE_ANIMS['body slam']     = MOVE_ANIMS.bodyslam;
MOVE_ANIMS['mega punch']    = MOVE_ANIMS.megapunch;
MOVE_ANIMS['seed bomb']     = MOVE_ANIMS.seedbomb;
MOVE_ANIMS['dragon rage']   = MOVE_ANIMS.dragonrage;
MOVE_ANIMS['poison sting']  = MOVE_ANIMS.poisonsting;
MOVE_ANIMS['double edge']   = MOVE_ANIMS.doubleedge;

// Injecter CSS nécessaire
(function injectCSS() {
  const style = document.createElement('style');
  style.textContent = `
    /* PS effect sprites uses requestAnimationFrame — no CSS transition needed */
    #ps-fx-layer img { image-rendering: pixelated; }

    /* Damage flash override — plus lisible avec les anims PS */
    .opponent-sprite.taking-damage,
    .player-sprite.taking-damage {
      animation: damage-shake 0.5s ease !important;
      filter: brightness(3) saturate(0) drop-shadow(0 0 8px #fff) !important;
    }
  `;
  document.head.appendChild(style);
})();