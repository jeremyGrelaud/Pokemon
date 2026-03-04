/**
 * tm-teach.js
 * Gestion de l'apprentissage des CT/CS (TM/HM) depuis :
 *   1. Le modal "Capacités" (onglet CT/CS dans le panneau droit)
 *   2. La section Inventaire CT/CS de la page Mon Équipe
 *
 * Dépendances attendues dans la page (définies dans my-team.js ou my_team.html) :
 *   - CSRF           : token CSRF Django (const string)
 *   - post(url, body): wrapper fetch POST JSON → Promise<json>
 *   - showToast(msg, type)          : toast global (toast-notifications.js)
 *   - showModalStatus(msg, type)   : statut dans le modal capacités
 *   - currentPokemonId             : ID du Pokémon sélectionné dans le modal
 *   - currentMovesData             : array des moves actifs du Pokémon en cours
 *   - renderActiveMoves(moves)     : redessine le deck gauche du modal
 *   - loadMovesModal(pokemonId)    : recharge entièrement le modal capacités
 *   - updateCardMoves(id, moves)   : met à jour les chips sur la card équipe
 *   - pendingAddMoveId, pendingAddMoveName : état du swap par niveau (réinitialisé ici)
 *
 * Routes API utilisées :
 *   GET  /api/items/tm/compatible/<pokemon_id>/
 *   POST /api/items/tm/<item_id>/use/
 */

/* ═══════════════════════════════════════════════════════════════════════════
   ÉTAT GLOBAL
   ═══════════════════════════════════════════════════════════════════════════ */

let currentLearnTab   = 'level'; // 'level' | 'tm'
let tmCompatData      = null;    // cache GET compatible
let pendingTMItemId   = null;
let pendingTMMoveName = '';

// Inventaire CT/CS
let selectedInvTMItemId   = null;
let selectedInvTMItemName = '';


/* ═══════════════════════════════════════════════════════════════════════════
   ONGLETS MODAL CAPACITÉS : Niveau / CT-CS
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Bascule entre l'onglet "Niveau" et "CT/CS" dans le panneau droit du modal.
 * @param {'level'|'tm'} tab
 */
function switchLearnTab(tab) {
  currentLearnTab = tab;

  const btnLevel = document.getElementById('tab-btn-level');
  const btnTM    = document.getElementById('tab-btn-tm');
  const panelLvl = document.getElementById('learnable-moves-list');
  const panelTM  = document.getElementById('tm-moves-list');
  const hint     = document.getElementById('learn-tab-hint');

  const activeStyle   = 'background:rgba(255,255,255,.25);border:1px solid rgba(255,255,255,.4);color:#fff;font-size:.72rem;padding:2px 8px;';
  const inactiveStyle = 'background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.25);color:rgba(255,255,255,.65);font-size:.72rem;padding:2px 8px;';

  if (tab === 'level') {
    btnLevel.style.cssText = activeStyle;
    btnTM.style.cssText    = inactiveStyle;
    panelLvl.classList.remove('d-none');
    panelTM.classList.add('d-none');
    if (hint) hint.textContent = 'Cliquez pour sélectionner';
    _cancelSwapTM();
  } else {
    btnTM.style.cssText    = activeStyle;
    btnLevel.style.cssText = inactiveStyle;
    panelTM.classList.remove('d-none');
    panelLvl.classList.add('d-none');
    if (hint) hint.textContent = "Cliquez sur «\u00a0Enseigner\u00a0» pour apprendre la CT/CS au Pokémon";
    _cancelSwapTM();
    loadTMCompat(currentPokemonId);
  }
}

/**
 * Charge les CT/CS compatibles pour ce Pokémon depuis l'API et les affiche.
 * @param {number} pokemonId
 */
function loadTMCompat(pokemonId, onReady) {
  const panel = document.getElementById('tm-moves-list');
  if (!panel) return;
  panel.innerHTML = '<div class="text-center text-muted py-4"><i class="fas fa-spinner fa-spin"></i> Chargement des CT/CS…</div>';
  tmCompatData = null;

  fetch(`/api/items/tm/compatible/${pokemonId}/`)
    .then(r => r.json())
    .then(data => {
      tmCompatData = data.compatible_tms || [];
      renderTMMoves(tmCompatData);
      if (typeof onReady === 'function') onReady();
    })
    .catch(() => {
      panel.innerHTML = '<p class="text-danger text-center small py-3"><i class="fas fa-exclamation-triangle"></i> Erreur réseau.</p>';
    });
}

/**
 * Affiche la liste des CT/CS dans le panneau droit du modal.
 * Séparation : apprenables (avec bouton Enseigner) | déjà connues (grisées).
 * @param {Array} tms
 */
function renderTMMoves(tms) {
  const panel = document.getElementById('tm-moves-list');
  if (!panel) return;

  if (!tms || !tms.length) {
    panel.innerHTML = `
      <div class="text-center py-4 text-muted">
        <i class="fas fa-compact-disc fa-2x mb-2 d-block" style="opacity:.3;"></i>
        <p class="mb-0 small">Aucune CT/CS disponible pour ce Pokémon<br>dans votre inventaire.</p>
      </div>`;
    return;
  }

  const learnable = tms.filter(t => !t.already_known);
  const known     = tms.filter(t =>  t.already_known);
  let html = '';

  if (learnable.length) {
    html += learnable.map(t => `
      <div class="move-card-full move-learnable badge-type-${(t.move_type || 'normal').toLowerCase()} mb-2 tm-modal-card"
           data-item-id="${t.item_id}" data-move-id="${t.move_id}"
           data-move-name="${_esc(t.move_name)}">
        <div class="d-flex justify-content-between align-items-center mb-1">
          <div class="d-flex align-items-center gap-2">
            <span class="tm-badge-pill">${t.item_type === 'cs' ? 'CS' : 'CT'}</span>
            <span class="move-card-name">${t.move_name}</span>
          </div>
          <span class="move-type-pill">${(t.move_type || '—').toUpperCase()}</span>
        </div>
        <div class="d-flex justify-content-end">
          <button class="btn btn-warning btn-sm mt-1 use-tm-btn"
                  data-item-id="${t.item_id}"
                  data-move-name="${_esc(t.move_name)}">
            <i class="fas fa-graduation-cap"></i> Enseigner
          </button>
        </div>
      </div>`).join('');
  }

  if (known.length) {
    html += `<div class="mt-2 mb-1">
      <small class="text-muted fw-bold text-uppercase" style="font-size:.68rem;letter-spacing:.05em;">
        Déjà connues
      </small>
    </div>`;
    html += known.map(t => `
      <div class="move-card-full badge-type-${(t.move_type || 'normal').toLowerCase()} mb-2 opacity-50" style="cursor:default;">
        <div class="d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center gap-2">
            <span class="tm-badge-pill">${t.item_type === 'cs' ? 'CS' : 'CT'}</span>
            <span class="move-card-name">${t.move_name}</span>
          </div>
          <span class="badge bg-light text-dark" style="font-size:.65rem;">
            <i class="fas fa-check"></i> Connu
          </span>
        </div>
      </div>`).join('');
  }

  panel.innerHTML = html;

  // Binding boutons "Enseigner"
  panel.querySelectorAll('.use-tm-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      initiateTMTeachFromModal(parseInt(this.dataset.itemId), this.dataset.moveName);
    });
  });
}

/**
 * Déclenche le flux d'enseignement d'une CT depuis le modal :
 *   - deck non plein → panneau confirmation directe
 *   - deck plein     → affiche boutons "Remplacer" sur les moves actifs
 * @param {number} itemId
 * @param {string} moveName
 */
function initiateTMTeachFromModal(itemId, moveName) {
  // Surbrillance de la carte sélectionnée
  document.querySelectorAll('.tm-modal-card').forEach(el => el.classList.remove('move-learnable-selected'));
  const card = document.querySelector(`.tm-modal-card[data-item-id="${itemId}"]`);
  if (card) card.classList.add('move-learnable-selected');

  pendingTMItemId   = itemId;
  pendingTMMoveName = moveName;

  // Compter les moves actifs depuis le DOM (plus fiable que currentMovesData
  // qui peut être vide si loadMovesModal n'a pas encore terminé son fetch)
  const activeMoveCount = document.querySelectorAll('#active-moves-list .move-active-item').length;
  const deckFull = activeMoveCount >= 4;

  const panel = document.getElementById('swap-confirm-panel');

  if (!deckFull) {
    panel.querySelector('p').innerHTML = `
      <i class="fas fa-compact-disc text-primary"></i>
      Enseigner <strong class="text-success">${moveName}</strong> via CT/CS ?`;
    panel.classList.remove('d-none');
    document.getElementById('swap-confirm-btn').onclick = () => confirmTMTeach(null);
  } else {
    // Deck plein : ouvrir le modal dédié au remplacement
    openTMReplaceModal({
      itemId:    itemId,
      moveName:  moveName,
      itemType:  'tm',
      pokemonId: currentPokemonId,
      pokemonName: document.getElementById('modal-pokemon-name')?.textContent || '',
      currentMoves: currentMovesData,
    });
  }
}

/**
 * Confirme l'enseignement de la CT/CS en appelant l'API.
 * @param {number|null} replaceMoveId  — ID du move à remplacer (null = ajout direct)
 */
function confirmTMTeach(replaceMoveId) {
  if (!pendingTMItemId || !currentPokemonId) return;
  document.getElementById('swap-confirm-btn').disabled = true;

  const body = { pokemon_id: currentPokemonId };
  if (replaceMoveId) body.replace_move_id = replaceMoveId;

  post(`/api/items/tm/${pendingTMItemId}/use/`, body)
    .then(data => {
      document.getElementById('swap-confirm-btn').disabled = false;

      if (data.success) {
        _showTMFeedback(data.message, 'success');
        pendingTMItemId = null;
        pendingTMMoveName = '';
        _cancelSwapTM();
        loadMovesModal(currentPokemonId);
        if (currentLearnTab === 'tm') {
          tmCompatData = null;
          loadTMCompat(currentPokemonId);
        }
      } else if (data.needs_replace) {
        _showTMFeedback('Deck plein : choisissez un move à remplacer.', 'warning');
      } else {
        _showTMFeedback(data.message, 'danger');
      }
    })
    .catch(() => {
      document.getElementById('swap-confirm-btn').disabled = false;
      _showTMFeedback('Erreur réseau.', 'danger');
    });
}

/**
 * Annule la sélection CT/CS en cours dans le modal (sans toucher à pendingAddMove*).
 */
function _cancelSwapTM() {
  pendingTMItemId   = null;
  pendingTMMoveName = '';
  document.querySelectorAll('.tm-modal-card').forEach(el => el.classList.remove('move-learnable-selected'));
}

/**
 * Hook : réinitialise l'onglet et le cache quand on change de Pokémon dans le modal.
 * Appelé par le listener .manage-moves-btn défini dans my-team.js ou my_team.html.
 */
function onModalOpenTMReset() {
  if (currentLearnTab === 'tm') switchLearnTab('level');
  tmCompatData = null;
}


/* ═══════════════════════════════════════════════════════════════════════════
   EXTENSION DE cancelSwap (définie dans my_team.html / my-team.js)
   On wrappe la fonction existante pour inclure la réinitialisation TM.
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * À appeler APRÈS que cancelSwap() d'origine soit défini.
 * Surcharge cancelSwap pour ajouter la réinitialisation TM.
 */
(function patchCancelSwap() {
  const _orig = window.cancelSwap;
  window.cancelSwap = function () {
    _cancelSwapTM();
    if (typeof _orig === 'function') _orig();
  };
})();


/* ═══════════════════════════════════════════════════════════════════════════
   INVENTAIRE CT/CS — Onglets + Enseigner depuis l'inventaire
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Bascule entre l'onglet "Objets" et "CT/CS" dans la section Inventaire.
 * @param {'items'|'tm'} tab
 */
function switchInvTab(tab) {
  const panelItems = document.getElementById('inv-panel-items');
  const panelTM    = document.getElementById('inv-panel-tm');
  const btnItems   = document.getElementById('inv-tab-btn-items');
  const btnTM      = document.getElementById('inv-tab-btn-tm');

  if (tab === 'items') {
    panelItems.classList.remove('d-none');
    panelTM.classList.add('d-none');
    btnItems.classList.add('active');
    btnTM.classList.remove('active');
  } else {
    panelTM.classList.remove('d-none');
    panelItems.classList.add('d-none');
    btnTM.classList.add('active');
    btnItems.classList.remove('active');
  }
  cancelTMTeach();
}

/**
 * Sélectionne (ou désélectionne) une CT/CS dans l'inventaire.
 * @param {HTMLElement} el — la .tm-inv-card cliquée
 */
function selectTMItem(el) {
  const itemId   = parseInt(el.dataset.itemId);
  const itemName = el.dataset.itemName;

  if (selectedInvTMItemId === itemId) {
    cancelTMTeach();
    return;
  }

  selectedInvTMItemId   = itemId;
  selectedInvTMItemName = itemName;

  document.querySelectorAll('.tm-inv-card').forEach(c => c.classList.remove('tm-inv-selected'));
  el.classList.add('tm-inv-selected');

  const nameEl = document.getElementById('tm-teach-name');
  if (nameEl) nameEl.textContent = itemName;

  const teachPanel = document.getElementById('tm-teach-panel');
  if (teachPanel) teachPanel.classList.remove('d-none');
}

/**
 * Annule la sélection CT/CS dans l'inventaire.
 */
function cancelTMTeach() {
  selectedInvTMItemId   = null;
  selectedInvTMItemName = '';
  document.querySelectorAll('.tm-inv-card').forEach(c => c.classList.remove('tm-inv-selected'));
  const p = document.getElementById('tm-teach-panel');
  if (p) p.classList.add('d-none');
}

/**
 * Enseigne la CT/CS sélectionnée à un Pokémon de l'équipe.
 * Appelle POST /api/items/tm/<item_id>/use/
 * @param {number} pokemonId
 * @param {string} pokemonName
 */
function teachTMToPokemon(pokemonId, pokemonName) {
  if (!selectedInvTMItemId) return;

  const picker = document.getElementById('tm-pokemon-picker');
  if (picker) { picker.style.pointerEvents = 'none'; picker.style.opacity = '.6'; }

  post(`/api/items/tm/${selectedInvTMItemId}/use/`, { pokemon_id: pokemonId })
    .then(data => {
      if (picker) { picker.style.pointerEvents = ''; picker.style.opacity = ''; }

      if (data.success) {
        showToast(data.message, 'success');
        cancelTMTeach();
        if (data.move) {
          fetch(`/api/pokemon/moves/?pokemon_id=${pokemonId}`)
            .then(r => r.json())
            .then(d => { if (d.success) updateCardMoves(pokemonId, d.moves); });
        }

      } else if (data.needs_replace) {
        const capturedItemId   = selectedInvTMItemId;
        const capturedMoveName = data.move ? data.move.name : pendingTMMoveName;
        const capturedItemType = document.querySelector(`.tm-inv-card[data-item-id="${capturedItemId}"]`)?.dataset.itemType || 'tm';
        cancelTMTeach();

        openTMReplaceModal({
          itemId:    capturedItemId,
          moveName:  capturedMoveName,
          itemType:  capturedItemType,
          pokemonId,
          pokemonName,
        });

      } else {
        _showTMFeedback(data.message, 'danger');
      }
    })
    .catch(() => {
      if (picker) { picker.style.pointerEvents = ''; picker.style.opacity = ''; }
      _showTMFeedback('Erreur réseau.', 'danger');
    });
}

/** Cherche dans l'inventaire CT/CS l'item_id qui enseigne un move donné. */
function _findInvItemForMove(moveId) {
  const card = document.querySelector(`.tm-inv-card[data-move-id="${moveId}"]`);
  return card ? parseInt(card.dataset.itemId) : null;
}


/* ═══════════════════════════════════════════════════════════════════════════
   UTILITAIRE
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Affiche un message d'erreur : dans le modal si ouvert, sinon en alerte page.
 * @param {string} msg
 * @param {'danger'|'warning'|'success'} type
 */
function _showTMFeedback(msg, type = 'danger') {
  const modalEl = document.getElementById('moves-modal');
  const isOpen  = modalEl && modalEl.classList.contains('show');
  if (isOpen) {
    showModalStatus(msg, type);
  }
  // Toujours afficher le toast (visible même si le modal masque le statut)
  showToast(msg, type === 'danger' ? 'error' : type);
}

/* ═══════════════════════════════════════════════════════════════════════════
   MODAL DÉDIÉ AU REMPLACEMENT CT/CS  (#tm-replace-modal)
   ═══════════════════════════════════════════════════════════════════════════ */

let _tmrState = null;   // { itemId, moveName, itemType, pokemonId, pokemonName }
let _tmrBsModal = null;

/**
 * Ouvre le modal de remplacement CT/CS.
 * @param {{ itemId, moveName, itemType, pokemonId, pokemonName, currentMoves? }} opts
 */
function openTMReplaceModal(opts) {
  _tmrState = opts;

  // Disc label + style CS
  const disc = document.getElementById('tmr-disc-label');
  disc.textContent = opts.itemType === 'cs' ? 'CS' : 'CT';
  disc.parentElement.querySelector('.tm-replace-disc')?.classList.toggle('cs-disc', opts.itemType === 'cs');

  // Move name
  document.getElementById('tmr-move-name').textContent = opts.moveName;

  // Pokémon sprite & name (chercher le sprite depuis la page)
  document.getElementById('tmr-poke-name').textContent = opts.pokemonName;
  const spriteEl = document.querySelector(`.team-slot[data-id="${opts.pokemonId}"] img.pokemon-sprite-sm`);
  const sprite   = document.getElementById('tmr-sprite');
  sprite.src     = spriteEl ? spriteEl.src : '';
  sprite.onerror = () => { sprite.src = '/static/img/pokeball.png'; };

  // Bouton close
  document.getElementById('tmr-close-btn').onclick = () => tmrClose(false);

  // Remplir la grille des moves
  _tmrFillMoves(opts.currentMoves || currentMovesData);

  // Masquer la zone de confirmation
  document.getElementById('tmr-confirm-zone').classList.add('d-none');
  document.getElementById('tmr-moves-grid').classList.remove('d-none');

  // Ouvrir
  _tmrBsModal = new bootstrap.Modal(document.getElementById('tm-replace-modal'));
  _tmrBsModal.show();

  // Bootstrap insère le backdrop à la fin du <body> après l'animation.
  // On lui applique une classe pour forcer son z-index au-dessus du modal capacités.
  document.getElementById('tm-replace-modal').addEventListener('shown.bs.modal', () => {
    const backdrops = document.querySelectorAll('.modal-backdrop');
    // Le dernier backdrop est celui du modal qu'on vient d'ouvrir
    if (backdrops.length) backdrops[backdrops.length - 1].classList.add('tm-replace-backdrop');
  }, { once: true });
}

function _tmrFillMoves(moves) {
  const grid = document.getElementById('tmr-moves-grid');

  // Si moves vides, charger depuis l'API
  if (!moves || !moves.length) {
    grid.innerHTML = '<div class="text-center text-muted py-3 col-span-2"><i class="fas fa-spinner fa-spin"></i></div>';
    fetch(`/api/pokemon/moves/?pokemon_id=${_tmrState.pokemonId}`)
      .then(r => r.json())
      .then(d => {
        if (d.success) {
          currentMovesData = d.moves;
          _tmrFillMoves(d.moves);
        }
      });
    return;
  }

  const CAT_ICON = { physical: '⚔️', special: '✨', status: '💫' };

  grid.innerHTML = moves.map(m => `
    <div class="tm-replace-move-card badge-type-${(m.type || 'normal').toLowerCase()}"
         data-move-id="${m.id}" data-move-name="${_esc(m.name)}"
         onclick="tmrSelectMove(${m.id}, '${_esc(m.name)}')">
      <div class="mc-forget-icon"><i class="fas fa-times"></i></div>
      <div class="mc-name">${m.name}</div>
      <div class="mc-meta">
        <span>${CAT_ICON[m.category] || ''} ${m.category}</span>
        ${m.power ? `<span>💥 ${m.power}</span>` : ''}
        <span style="margin-left:auto;opacity:.7;">${m.current_pp}/${m.pp} PP</span>
      </div>
    </div>`).join('');
}

function tmrSelectMove(moveId, moveName) {
  // Surbrillance
  document.querySelectorAll('.tm-replace-move-card').forEach(c => c.classList.remove('selected'));
  const card = document.querySelector(`.tm-replace-move-card[data-move-id="${moveId}"]`);
  if (card) card.classList.add('selected');

  // Zone de confirmation
  const zone = document.getElementById('tmr-confirm-zone');
  document.getElementById('tmr-confirm-text').innerHTML =
    `Oublier <strong class="forget">${moveName}</strong> et apprendre <strong class="learn">${_tmrState.moveName}</strong> ?`;
  zone.classList.remove('d-none');

  const btn = document.getElementById('tmr-confirm-btn');
  btn.disabled = false;
  btn.onclick  = () => tmrConfirm(moveId);
}

function tmrCancelConfirm() {
  document.querySelectorAll('.tm-replace-move-card').forEach(c => c.classList.remove('selected'));
  document.getElementById('tmr-confirm-zone').classList.add('d-none');
}

function tmrConfirm(replaceMoveId) {
  if (!_tmrState) return;
  const btn = document.getElementById('tmr-confirm-btn');
  btn.disabled = true;

  post(`/api/items/tm/${_tmrState.itemId}/use/`, {
    pokemon_id:      _tmrState.pokemonId,
    replace_move_id: replaceMoveId,
  })
    .then(data => {
      btn.disabled = false;
      if (data.success) {
        tmrClose(true);
        showToast(data.message, 'success');
        // Mettre à jour les chips sur la card équipe
        if (data.move) {
          fetch(`/api/pokemon/moves/?pokemon_id=${_tmrState.pokemonId}`)
            .then(r => r.json())
            .then(d => {
              if (d.success) {
                updateCardMoves(_tmrState.pokemonId, d.moves);
                // Si le modal capacités est ouvert sur ce même Pokémon, le recharger
                const movesModal = document.getElementById('moves-modal');
                if (movesModal?.classList.contains('show') && currentPokemonId === _tmrState.pokemonId) {
                  currentMovesData = d.moves;
                  renderActiveMoves(d.moves);
                  if (currentLearnTab === 'tm') { tmCompatData = null; loadTMCompat(_tmrState.pokemonId); }
                }
              }
            });
        }
      } else {
        _showTMFeedback(data.message, 'danger');
        btn.disabled = false;
      }
    })
    .catch(() => {
      btn.disabled = false;
      _showTMFeedback('Erreur réseau.', 'danger');
    });
}

function tmrClose(success) {
  if (_tmrBsModal) { _tmrBsModal.hide(); _tmrBsModal = null; }
  if (!success) _tmrState = null;
}


/** Échappe les apostrophes pour les attrs HTML inline. */
function _esc(str) {
  return (str || '').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
}