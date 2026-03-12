/**
 * battle-responsive.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Gère le passage entre le canvas 1280×540 (full) et 960×540 (compact)
 * selon la largeur disponible, en conservant sprites & UI parfaitement centrés.
 * ─────────────────────────────────────────────────────────────────────────────
 */

(function () {
  'use strict';

  /* ── Paramètres ─────────────────────────────────────────────────────────── */
  const SCENE_FULL_W    = 1280;   // Largeur canvas mode plein
  const SCENE_COMPACT_W =  960;   // Largeur canvas mode compact
  const SCENE_H         =  540;   // Hauteur fixe (inchangée dans les deux modes)

  /**
   * Seuil en pixels en dessous duquel on bascule en mode compact.
   * 1100px = on active le compact dès que l'écran n'a pas la place
   * d'afficher 1280px à scale ≥ 0.86 environ.
   */
  const COMPACT_THRESHOLD = 1100;

  /* ── Références DOM ─────────────────────────────────────────────────────── */
  const wrapper = document.getElementById('battle-wrapper');
  const scene   = document.querySelector('.battle-scene');

  if (!wrapper || !scene) {
    console.warn('[battle-responsive] Éléments DOM introuvables, scaling désactivé.');
    return;
  }

  /* ── Fonction principale ────────────────────────────────────────────────── */
  function scaleBattleScene() {
    const availableW = wrapper.clientWidth;

    /* ── 1. Choix du mode (compact vs full) ─────────────────────────────── */
    const isCompact = availableW < COMPACT_THRESHOLD;

    if (isCompact) {
      scene.classList.add('scene-compact');
    } else {
      scene.classList.remove('scene-compact');
    }

    /* ── 2. Largeur de référence du canvas ──────────────────────────────── */
    const referenceW = isCompact ? SCENE_COMPACT_W : SCENE_FULL_W;

    /* ── 3. Calcul du scale (jamais > 1 pour éviter le flou) ────────────── */
    const scale = Math.min(availableW / referenceW, 1);

    /* ── 4. Application du transform sur la scène ───────────────────────── */
    scene.style.transform       = `scale(${scale})`;
    scene.style.transformOrigin = 'top center';
    scene.style.marginLeft      = '';   // reset tout marginLeft manuel

    /* ── 5. Mise à jour de la hauteur du wrapper (letterbox) ─────────────── */
    //  La hauteur visuelle = SCENE_H * scale.
    //  Sans ça le wrapper garderait 540px et créerait un espace vide sous la scène.
    const renderedH = SCENE_H * scale;
    wrapper.style.height = renderedH + 'px';

    /* ── 6. Classes body pour le panel d'action (existantes) ────────────── */
    document.body.classList.remove('battle-lg', 'battle-md', 'battle-sm');
    if (availableW >= 1280) {
      document.body.classList.add('battle-lg');
    } else if (availableW >= 768) {
      document.body.classList.add('battle-md');
    } else {
      document.body.classList.add('battle-sm');
    }

    /* ── 7. Émission d'un event custom (optionnel) ───────────────────────── */
    //  Permet à battle-game.js d'écouter et d'ajuster d'autres éléments JS.
    window.dispatchEvent(new CustomEvent('battleSceneResized', {
      detail: { scale, isCompact, referenceW, availableW }
    }));
  }

  /* ── Lancement & écoute des events ─────────────────────────────────────── */
  // Init au chargement
  document.addEventListener('DOMContentLoaded', scaleBattleScene);

  // Suivi en temps réel du resize
  let resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(scaleBattleScene, 80); // debounce 80ms
  });

  // Exposition globale pour usage depuis battle-game.js
  window.scaleBattleScene = scaleBattleScene;

  // Re-scale si l'overlay trainer disparaît (peut décaler le layout)
  document.addEventListener('trainerIntroHidden', scaleBattleScene);

})();