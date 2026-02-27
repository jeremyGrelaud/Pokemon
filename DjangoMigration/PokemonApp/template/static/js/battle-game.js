/* battle-game.js — extrait de battle_game_v2.html */

// ============================================================================
// GLOBAL VARIABLES
// ============================================================================

let battleEffects;
let audioManager;
const battleId   = BATTLE_CONFIG.battleId;
const csrfToken  = BATTLE_CONFIG.csrfToken;

// ID du Pokémon actuellement en combat — mis à jour à chaque switch
let currentPlayerPokemonId = BATTLE_CONFIG.playerPokemonId;
let currentOpponentPokemonId = BATTLE_CONFIG.opponentPokemonId;

// ============================================================================
// INITIALIZATION
// ============================================================================

// Initialiser le système
let captureSystem = null;

// ============================================================================
// TRAINER INTRO ANIMATION
// ============================================================================

// Ces fonctions ne sont appelées que pour les combats trainer/gym
/**
 * Typewriter effect for dialogue text
 */
function typewriterEffect(element, text, speed, onDone) {
  element.textContent = '';
  let i = 0;
  const interval = setInterval(() => {
    element.textContent += text[i];
    i++;
    if (i >= text.length) {
      clearInterval(interval);
      if (onDone) onDone();
    }
  }, speed);
  return interval;
}

/**
 * Play the trainer intro sequence, then call onComplete when done.
 */
function playTrainerIntro(onComplete) {
  const overlay    = document.getElementById('trainer-intro-overlay');
  const spriteWrap = document.getElementById('trainer-intro-sprite-wrap');
  const nameplate  = document.getElementById('trainer-intro-nameplate');
  const dialogue   = document.getElementById('trainer-intro-dialogue');
  const vsFlash    = document.getElementById('trainer-vs-flash');
  const textEl     = document.getElementById('trainer-intro-text');
  const continueHint = overlay.querySelector('.trainer-dialogue-continue');

  const fullText = textEl.textContent.trim();
  textEl.textContent = '';

  let dismissed = false;
  let typeInterval = null;
  let dialogueShown = false;

  function dismissIntro() {
    if (dismissed) return;
    dismissed = true;

    // Clear typewriter if still running
    if (typeInterval) clearInterval(typeInterval);

    // Slide trainer out
    spriteWrap.classList.remove('slide-in');
    spriteWrap.classList.add('slide-out');

    // Fade overlay
    setTimeout(() => {
      overlay.classList.add('hiding');
      setTimeout(() => {
        overlay.style.display = 'none';
        if (onComplete) onComplete();
      }, 500);
    }, 300);
  }

  // Click/tap to dismiss or skip typewriter
  overlay.addEventListener('click', function handler() {
    if (!dialogueShown) return; // Wait until dialogue appears
    if (typeInterval) {
      // Skip typewriter — show full text immediately
      clearInterval(typeInterval);
      typeInterval = null;
      textEl.textContent = fullText;
      continueHint.classList.add('show-continue');
      // Second click dismisses
      overlay.removeEventListener('click', handler);
      overlay.addEventListener('click', dismissIntro, { once: true });
    } else {
      dismissIntro();
      overlay.removeEventListener('click', handler);
    }
  });

  // ── Sequence timing ──────────────────────────────────────────────────────

  // Step 1: VS flash (400ms)
  setTimeout(() => {
    vsFlash.classList.add('flash-in');
    // Play whoosh SFX
    try { audioManager.playSFX('ui/SFX_INTRO_WHOOSH'); } catch(e) {}
  }, 200);

  // Step 2: Trainer sprite slides in (800ms)
  setTimeout(() => {
    spriteWrap.classList.add('slide-in');
    try { audioManager.playSFX('ui/SFX_INTRO_CRASH'); } catch(e) {}
  }, 800);

  // Step 3: Nameplate fades in (1100ms)
  setTimeout(() => {
    nameplate.classList.add('fade-in');
  }, 1100);

  // Step 4: Dialogue slides up + typewriter (1600ms)
  setTimeout(() => {
    dialogue.classList.add('slide-up');
    dialogueShown = true;
    // Small delay then start typewriter
    setTimeout(() => {
      typeInterval = typewriterEffect(textEl, fullText, 30, () => {
        typeInterval = null;
        // Show continue hint and set up auto-dismiss
        continueHint.classList.add('show-continue');
        // Auto dismiss after 3s if user doesn't click
        setTimeout(() => {
          dismissIntro();
        }, 3000);
      });
    }, 200);
  }, 1600);
}

$(document).ready(function() {
  console.log('🎮 Battle Scene V2 Loaded');
  
  // Initialize systems
  battleEffects = new BattleEffects(document.getElementById('attack-canvas'));
  audioManager = new AudioManager();
  captureSystem = new CaptureSystem();

  /**
   * Start the actual battle after intro (or immediately for wild battles)
   */
  function startBattle() {
    // Start BGM
    if (BATTLE_CONFIG.battleType === 'gym') {
      audioManager.playBGM('battle_gym');
    } else if (BATTLE_CONFIG.battleType === 'trainer') {
      audioManager.playBGM('battle_trainer');
    } else {
      audioManager.playBGM('battle_wild');
    }
    
    // Entry animations
    setTimeout(() => {
      $('#opponent-container').addClass('slide-in-opponent');
      $('#player-container').addClass('slide-in-player');
    }, 100);
    
    // Initial log
    addBattleLog('Le combat commence !');
    
    // Play Pokemon cries
    setTimeout(() => {
      audioManager.playCry(BATTLE_CONFIG.opponentSpeciesId);
    }, 500);
    
    setTimeout(() => {
      audioManager.playCry(BATTLE_CONFIG.playerSpeciesId);
    }, 1500);
  }

  if (BATTLE_CONFIG.battleType === 'trainer' || BATTLE_CONFIG.battleType === 'gym') {
    // Trainer/gym intro, then start battle
    playTrainerIntro(startBattle);
  } else {
    // Wild battle — start immediately
    startBattle();
  }
});

// ============================================================================
// MENU NAVIGATION
// ============================================================================

function showMainMenu() {
  $('.menu-container').hide();
  $('#main-menu').fadeIn(200);
  audioManager.playSFX('ui/select');
}

function showMoves() {
  $('.menu-container').hide();
  $('#moves-menu').fadeIn(200);
  audioManager.playSFX('ui/select');
}

function showItems() {
  $('.menu-container').hide();
  $('#items-menu').fadeIn(200);
  loadItems();
  audioManager.playSFX('ui/select');
}

function showTeam() {
  $('.menu-container').hide();
  $('#team-menu').fadeIn(200);
  loadTeam();
  audioManager.playSFX('ui/select');
}

// ============================================================================
// BATTLE ACTIONS
// ============================================================================

function useMove(moveId) {
  $('button').prop('disabled', true);
  audioManager.playSFX('ui/confirm');

  // Send to server immediately — no pre-emptive animations
  $.post(BATTLE_CONFIG.urls.action, {
    action: 'attack',
    move_id: moveId,
    csrfmiddlewaretoken: csrfToken
  })
  .done(function(data) {
    // Play the correct attack sequence based on turn_info from server
    playTurnAnimations(data, () => {
      updateBattleState(data);
      updateVolatileStates(data);
    });
  })
  .fail(function(xhr) {
    console.error('Attack failed:', xhr);
    addBattleLog('Erreur lors de l\'attaque');
    $('button').prop('disabled', false);
  });
}

/**
 * Joue la séquence d'animations d'attaque dans l'ordre exact du tour,
 * puis appelle onDone() pour mettre à jour l'état du combat.
 *
 * Séquences possibles (basées sur turn_info) :
 *   player_first=true,  second_skipped=false → player attaque, puis ennemi attaque
 *   player_first=true,  second_skipped=true  → player attaque seulement (ennemi KO)
 *   player_first=false, second_skipped=false → ennemi attaque, puis player attaque
 *   player_first=false, second_skipped=true  → ennemi attaque seulement (player KO avant)
 */
function playTurnAnimations(data, onDone) {
  const ti = data.turn_info || { player_first: true, second_skipped: false, player_move: {}, opponent_move: {} };

  const playerMove   = ti.player_move   || {};
  const opponentMove = ti.opponent_move || {};

  const playerAttacked   = !(ti.player_first  === false && ti.second_skipped);
  const opponentAttacked = !(ti.player_first  === true  && ti.second_skipped);

  const ATTACK_DELAY  = 300;   // ms avant d'afficher l'effet
  const ATTACK_DUR    = 700;   // durée approximative de l'effet
  const BETWEEN_GAP   = 400;   // pause entre les deux attaques

  let seq = [];  // [{attacker: 'player'|'opponent', move: {...}}, ...]

  if (ti.player_first) {
    if (playerAttacked)   seq.push({ attacker: 'player',   move: playerMove });
    if (opponentAttacked) seq.push({ attacker: 'opponent', move: opponentMove });
  } else {
    if (opponentAttacked) seq.push({ attacker: 'opponent', move: opponentMove });
    if (playerAttacked)   seq.push({ attacker: 'player',   move: playerMove });
  }

  // Aucune attaque (ex: item/switch tour) → on va directement au onDone
  if (seq.length === 0) {
    onDone();
    return;
  }

  function playStep(index) {
    if (index >= seq.length) {
      onDone();
      return;
    }

    const { attacker, move } = seq[index];
    const isPlayer   = attacker === 'player';
    const spriteId   = isPlayer ? '#player-sprite'   : '#opponent-sprite';
    const fromSprite = isPlayer ? '#player-sprite'   : '#opponent-sprite';
    const toSprite   = isPlayer ? '#opponent-sprite' : '#player-sprite';

    const playerPos   = getElementCenter($('#player-sprite'));
    const opponentPos = getElementCenter($('#opponent-sprite'));
    const fromPos     = isPlayer ? playerPos   : opponentPos;
    const toPos       = isPlayer ? opponentPos : playerPos;

    const moveName    = move.name    || '';
    const moveType    = move.type    || 'normal';
    const moveCategory= move.category|| 'special';
    const cleanName   = moveName.replace(/\s+/g, '').toLowerCase();

    // Log
    const attackerName = isPlayer ? $('#player-name').text() : $('#opponent-name').text();
    if (moveName) addBattleLog(`${attackerName} utilise ${moveName} !`);

    // Sprite bounce
    $(spriteId).addClass('attacking');
    setTimeout(() => $(spriteId).removeClass('attacking'), 600);

    // Effect + sound
    setTimeout(() => {
      if (moveCategory === 'physical') {
        battleEffects.physicalAttack(fromPos, toPos, 'slash');
      } else {
        battleEffects.specialAttack(fromPos, toPos, moveType);
      }
      try { audioManager.playSFX(`attacks/${cleanName}`); } catch(e) {}
    }, ATTACK_DELAY);

    // Next step
    setTimeout(() => playStep(index + 1), ATTACK_DELAY + ATTACK_DUR + BETWEEN_GAP);
  }

  playStep(0);
}


function switchPokemon(pokemonId) {
  $('button').prop('disabled', true);
  
  $.post(BATTLE_CONFIG.urls.action, {
    action: 'switch',
    pokemon_id: pokemonId,
    csrfmiddlewaretoken: csrfToken
  })
  .done(function(data) {
    // Animate switch
    $('#player-sprite').addClass('fade-out');
    setTimeout(() => {
      updateBattleState(data);
      updateVolatileStates(data);
      $('#player-sprite').removeClass('fade-out');
    }, 500);
  })
  .fail(function(xhr) {
    console.error('Switch failed:', xhr);
    addBattleLog('Erreur lors du changement');
    $('button').prop('disabled', false);
  });
}

function useItem(itemId) {
  $('button').prop('disabled', true);
  
  $.post(BATTLE_CONFIG.urls.action, {
    action: 'item',
    item_id: itemId,
    csrfmiddlewaretoken: csrfToken
  })
  .done(function(data) {
    if (data.capture_attempt && data.capture_attempt.start_animation) {
      // POKEBALL — lancer l'animation de capture
      // Les boutons restent désactivés jusqu'à la fin de la séquence
      initiateCaptureSequence(itemId);
      return; // confirm_capture gérera la suite
    }

    // Objet normal (potion, antidote, réveil, etc.)
    if (data.log && data.log.length) {
      data.log.forEach(msg => addBattleLog(msg));
    }
    updateBattleState(data);
    updateVolatileStates(data);
    if (!data.battle_ended) {
      loadItems();
      $('button').prop('disabled', false);
    }
  })
  .fail(function(xhr) {
    console.error('Item use failed:', xhr);
    addBattleLog("Erreur lors de l'utilisation de l'objet");
    $('button').prop('disabled', false);
  });
}

function tryRun() {
  if (!confirm('Voulez-vous vraiment fuir le combat ?')) {
    return;
  }
  
  $.post(BATTLE_CONFIG.urls.action, {
    action: 'flee',
    csrfmiddlewaretoken: csrfToken
  })
  .done(function(data) {
    if (data.fled) {
      addBattleLog('Vous avez fui le combat !');
      setTimeout(() => {
        window.location.href = BATTLE_CONFIG.urls.returnZone;
      }, 2000);
    } else {
      addBattleLog('Impossible de fuir !');
      updateBattleState(data);
    }
  })
  .fail(function(xhr) {
    console.error('Flee failed:', xhr);
    addBattleLog('Erreur');
  });
}

// ============================================================================
// DATA LOADING
// ============================================================================

function loadItems() {
  $('#items-list').html('<p class="text-center"><i class="fas fa-spinner fa-spin"></i> Chargement...</p>');

  $.get(BATTLE_CONFIG.urls.getItems, {
    trainer_id: BATTLE_CONFIG.playerTrainerId
  })
  .done(function(data) {
    if (!data.items || data.items.length === 0) {
      $('#items-list').html('<p class="text-center text-muted">Aucun objet disponible</p>');
      return;
    }

    // Mapping item_type → dossier sprite
    const itemTypeFolderMap = {
      'potion': 'medicine',
      'status': 'medicine',
      'pokeball': 'ball',
      'battle': 'battle-item',
      'evolution': 'evo-item',
      'held': 'hold-item',
      'key': 'key-item',
    };

    // Fonction pour stripper le nom des Poké Balls
    function stripPokeballName(name) {
      return name.toLowerCase()
        .replace(/ ball/g, '')  // Enlève " Ball"
        .replace(/[^a-z0-9]/g, '');  // Enlève les caractères spéciaux
    }

    // Convertir le nom de l'objet en slug pour le fichier sprite
    function itemNameToSlug(name, itemType) {
      if (itemType === 'pokeball') {
        return stripPokeballName(name);
      }
      return name.toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[éè]/g, 'e')
        .replace(/[à]/g, 'a')
        .replace(/[ù]/g, 'u')
        .replace(/[^a-z0-9\-]/g, '');
    }

    const baseStaticUrl = BATTLE_CONFIG.static.itemsSprites;

    let html = '<div class="items-grid">';
    data.items.forEach(item => {
      const folder = itemTypeFolderMap[item.item_type] || 'medicine';
      const slug = itemNameToSlug(item.name, item.item_type);
      const spriteUrl = baseStaticUrl + folder + '/' + slug + '.png';
      const fallbackUrl = baseStaticUrl + 'medicine/potion.png';

      html += `
        <button class="item-btn" onclick="useItem(${item.id})" title="${item.description || item.name}">
          <div class="item-icon">
            <img src="${spriteUrl}" alt="${item.name}"
                 class="item-sprite"
                 onerror="this.onerror=null; this.src='${fallbackUrl}'">
          </div>
          <div class="item-info">
            <span class="item-name">${item.name}</span>
            <span class="item-qty">x${item.quantity}</span>
          </div>
        </button>
      `;
    });
    html += '</div>';

    $('#items-list').html(html);
  })
  .fail(function() {
    $('#items-list').html('<p class="text-center text-danger">Erreur de chargement</p>');
  });
}

function loadTeam() {
  $('#team-list').html('<p class="text-center"><i class="fas fa-spinner fa-spin"></i> Chargement...</p>');
  
  $.get(BATTLE_CONFIG.urls.getTeam, {
    trainer_id: BATTLE_CONFIG.playerTrainerId,
    exclude_pokemon_id: currentPlayerPokemonId
  })
  .done(function(data) {
    if (!data.team || data.team.length === 0) {
      $('#team-list').html('<p class="text-center text-muted">Aucun autre Pokémon disponible</p>');
      return;
    }
    
    let html = '<div class="team-switch-grid">';
    data.team.forEach(pokemon => {
      const hpPercent = (pokemon.current_hp / pokemon.max_hp) * 100;
      const hpClass = hpPercent > 50 ? 'hp-high' : (hpPercent > 20 ? 'hp-medium' : 'hp-low');
      const isKO = pokemon.current_hp === 0;
      const spriteName = lowerPokemonFileNames(pokemon.species.name);
      const folder = pokemon.is_shiny ? 'shiny' : 'normal';
      const spriteUrl = BATTLE_CONFIG.static.spritesGen5 + folder + "/" + spriteName + ".png";

      html += `
        <button class="list-group-item list-group-item-action team-switch-item ${isKO ? 'team-switch-ko' : ''}"
                onclick="switchPokemon(${pokemon.id})"
                ${isKO ? 'disabled' : ''}>
          <div class="d-flex justify-content-between align-items-center" style="width:100%;">
            <div class="d-flex align-items-center">
              <div class="team-switch-sprite-wrap ${isKO ? 'ko-sprite' : ''}">
                <img src="${spriteUrl}"
                     alt="${pokemon.nickname || pokemon.species.name}"
                     style="width:56px;height:56px;object-fit:contain;"
                     onerror="this.style.display='none'">
                ${isKO ? '<div class="ko-badge">K.O.</div>' : ''}
              </div>
              <div class="ml-3">
                <h6 class="mb-0" style="color:#2c3e50;"><strong>${pokemon.nickname || pokemon.species.name}</strong></h6>
                <small style="color:#7f8c8d;">Niv. ${pokemon.level}</small>
                ${pokemon.status_condition ? `<span class="badge badge-secondary ml-1" style="font-size:0.65em;">${pokemon.status_condition.toUpperCase()}</span>` : ''}
              </div>
            </div>
            <div class="text-right" style="min-width:110px;">
              <div class="team-hp-bar-track">
                <div class="team-hp-bar-fill ${hpClass}" style="width:${isKO ? 0 : hpPercent}%;"></div>
              </div>
              <small style="color:${isKO ? '#e74c3c' : '#7f8c8d'}; font-weight:${isKO ? '700' : '400'};">
                ${isKO ? 'K.O.' : `${pokemon.current_hp}/${pokemon.max_hp} HP`}
              </small>
            </div>
          </div>
        </button>
      `;
    });
    html += '</div>';
    
    $('#team-list').html(html);
  })
  .fail(function() {
    $('#team-list').html('<p class="text-center text-danger">Erreur de chargement</p>');
  });
}

// ============================================================================
// BATTLE STATE UPDATE
// ============================================================================

function updateBattleState(data) {
  console.log('Updating battle state:', data);

  // --- Turn info: was each side actually hit this turn? ---
  // player_first=true + second_skipped=true → opponent KO'd first → player NOT hit
  // player_first=false + second_skipped=true → player KO'd first → opponent NOT hit
  const ti = data.turn_info || { player_first: true, second_skipped: false };
  const playerWasHit   = !(ti.player_first  && ti.second_skipped);
  const opponentWasHit = !(!ti.player_first && ti.second_skipped);

  // Update Pokemon data
  if (data.player_pokemon) {
    updatePokemonDisplay('player', data.player_pokemon);
  }

  // Update HP with correct damage-animation flag
  if (data.player_hp !== undefined) {
    updateHP('player', data.player_hp, data.player_max_hp, false, playerWasHit);
  }

  if (data.opponent_hp !== undefined) {
    updateHP('opponent', data.opponent_hp, data.opponent_max_hp, false, opponentWasHit);
  }

  // Opponent pokemon display:
  // If the incoming pokemon has a different ID than the current one, the previous
  // pokemon just fainted — trigger death animation on old sprite first, then swap.
  if (data.opponent_pokemon) {
    const isNewOpponent = data.opponent_pokemon.id !== currentOpponentPokemonId;
    if (isNewOpponent) {
      const oldSprite = $('#opponent-sprite');
      oldSprite.addClass('fainted');
      try { audioManager.playSFX('battle/faint'); } catch(e) {}

      setTimeout(() => {
        oldSprite.removeClass('fainted');
        updatePokemonDisplay('opponent', data.opponent_pokemon);
        // Slide-in entrance for the new pokemon
        oldSprite.addClass('slide-in-opponent');
        setTimeout(() => oldSprite.removeClass('slide-in-opponent'), 600);
      }, 1400);
    } else {
      updatePokemonDisplay('opponent', data.opponent_pokemon);
    }
  }

  
  // Add logs
  if (data.log && data.log.length > 0) {
    data.log.forEach(msg => addBattleLog(msg));
  }
  
  // Check battle end — l'évolution est PRIORITAIRE sur la victoire :
  // si le pokemon évolue sur le dernier coup, on montre l'évolution d'abord,
  // puis le modal de victoire s'affiche quand le joueur clique "Super !".
  if (data.pending_evolution) {
    triggerEvolution(data.pending_evolution, data.battle_ended ? data : null);
  } else if (data.battle_ended) {
    handleBattleEnd(data);
  } else if (data.pending_moves && data.pending_moves.length > 0) {
    // Moves en attente d'apprentissage → afficher la modal de sélection
    // On bloque les boutons jusqu'à résolution de tous les moves
    $('button').prop('disabled', true);
    const pokemonId = data.player_pokemon ? data.player_pokemon.id : null;
    handlePendingMoves(data.pending_moves, pokemonId);
  } else {
    $('button').prop('disabled', false);
    showMainMenu();
  }
}

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

// Modifier updatePokemonDisplay
function updatePokemonDisplay(side, pokemonData) {
  const sprite = $(`#${side}-sprite`);
  const name = $(`#${side}-name`);
  const level = $(`#${side}-level`);
  
  // Mettre à jour l'ID du Pokémon actif si c'est le joueur
  if (side === 'player' && pokemonData.id) {
    currentPlayerPokemonId = pokemonData.id;
  }
  if (side === 'opponent' && pokemonData.id) {
    currentOpponentPokemonId = pokemonData.id;
  }
  
  // IMPORTANT: Retirer la classe fainted si présente (fix du bug de sprite invisible)
  sprite.removeClass('fainted fade-out taking-damage');
  
  // Update sprite
  let newSrc;
  if (side === 'player') {
    const folder = pokemonData.is_shiny ? 'back-shiny' : 'back';
    newSrc = BATTLE_CONFIG.static.spritesGen5 + folder + "/" + lowerPokemonFileNames(pokemonData.species_name) + ".png";
  }
  else {
    const folder = pokemonData.is_shiny ? 'shiny' : 'normal';
    newSrc = BATTLE_CONFIG.static.spritesGen5 + folder + "/" + lowerPokemonFileNames(pokemonData.species_name) + ".png";
  }

  sprite.attr('src', newSrc)
    .on('error', function() {
      $(this).attr('src', BATTLE_CONFIG.static.pokeball);
    });
  
  // Update name and level
  name.text(pokemonData.name);
  level.text('Niv.' + pokemonData.level);
  
  // Update HP
  updateHP(side, pokemonData.current_hp, pokemonData.max_hp, true);
  
  // Update moves on swicth
  if (side === 'player' && pokemonData.moves) {
    updateMovesMenu(pokemonData.moves);
  }
  
  // Update exp bar
  if (side === 'player' && pokemonData.exp_percent !== undefined) {
    updateExpBar(pokemonData.exp_percent);
  }
}


function updateHP(side, current, max, skipDamageAnimation = false, wasHitThisTurn = true) {
  const percent = Math.floor((current / max) * 100);
  const bar = $(`#${side}-hp-bar`);
  
  // Animate width
  bar.css('width', percent + '%');
  
  // Update color class
  bar.removeClass('hp-high hp-medium hp-low');
  if (percent > 50) {
    bar.addClass('hp-high');
  } else if (percent > 20) {
    bar.addClass('hp-medium');
  } else {
    bar.addClass('hp-low');
  }
  
  // Update text (player only)
  if (side === 'player') {
    $('#player-hp-current').text(current);
    $('#player-hp-max').text(max);
  }
  
  // Damage animation: only if not skipped AND the side was actually hit this turn
  const sprite = $(`#${side}-sprite`);
  if (!skipDamageAnimation && wasHitThisTurn && current < max) {
    sprite.addClass('taking-damage');
    setTimeout(() => sprite.removeClass('taking-damage'), 600);
  }
  
  // Check if fainted
  if (current === 0 && side === 'player') {
    sprite.addClass('fainted');
    audioManager.playSFX('battle/faint');
    
    // Afficher le modal de switch forcé après l'animation
    setTimeout(() => {
      showForcedSwitchModal();
    }, 1500); // Attendre la fin de l'animation faint
  } else if (current === 0) {
    sprite.addClass('fainted');
    audioManager.playSFX('battle/faint');
  }
}

// Mettre à jour moves
function updateMovesMenu(moves) {
  const movesGrid = $('.moves-grid');
  movesGrid.empty();
  
  if (!moves || moves.length === 0) {
    movesGrid.html('<p>Aucune attaque</p>');
    return;
  }
  
  moves.forEach(move => {
    const disabled = move.current_pp === 0 ? 'disabled' : '';
    const catMap = { physical: 'move-physical', special: 'move-special', status: 'move-status' };
    const catFile = catMap[move.category] || 'move-status';
    const catImg = `<img src="/static/img/movesTypesSprites/${catFile}.png" alt="${move.category}" title="${move.category}" style="width:18px;height:18px;object-fit:contain;vertical-align:middle;">`;
    const html = `
      <button class="move-btn move-type-${move.type}" 
              onclick="useMove(${move.id})" ${disabled}>
        <div class="move-header">
          <span class="move-name">${move.name}</span>
          <span class="move-pp">PP: ${move.current_pp}/${move.max_pp}</span>
        </div>
        <div class="move-footer">
          <span class="move-type-badge type-${move.type}">${move.type}</span>
          ${catImg}
          <span class="move-power">${move.power ? 'PWR: ' + move.power : '—'}</span>
          <span class="move-accuracy" style="font-size:0.75em;color:#aaa;">${move.accuracy ? 'PREC: ' + move.accuracy + '%' : '∞'}</span>
        </div>
      </button>
    `;
    movesGrid.append(html);
  });
}


// Mettre à jour EXP bar
function updateExpBar(expPercent) {
  const bar = $('.exp-bar-fill');
  const currentWidth = parseFloat(bar.css('width')) || 0;
  const parentWidth = bar.parent().width() || 1;
  const currentPercent = (currentWidth / parentWidth) * 100;

  // Only animate and play sound if XP actually increased
  if (expPercent > currentPercent + 0.5) {
    // Play EXP gain sound
    try { audioManager.playSFX('ui/exp_gain'); } catch(e) {}

    // Restart shimmer + tip glow animations cleanly
    bar.removeClass('exp-animating exp-pulse');
    bar[0].offsetWidth; // force reflow
    bar.addClass('exp-animating');

    // Animate bar width
    bar.css('transition', 'width 1s ease-out');
    bar.css('width', expPercent + '%');

    // After fill completes: swap shimmer for end pulse
    setTimeout(() => {
      bar.removeClass('exp-animating');
      bar.addClass('exp-pulse');
      setTimeout(() => bar.removeClass('exp-pulse'), 500);
    }, 1050);

    // Clean up transition override
    setTimeout(() => bar.css('transition', ''), 1200);
  } else {
    bar.css('width', expPercent + '%');
  }
}



function handleBattleEnd(data) {
  console.log('🏁 Battle ended:', data);
  
  // Arrêter la musique
  if (audioManager) {
    audioManager.stopBGM();
  }
  
  // Désactiver tous les boutons
  $('button').prop('disabled', true);

  // Fonction pour réactiver les boutons
  const enableButtons = () => {
    $('button').prop('disabled', false);
  };
  
  if (data.result === 'victory') {
    // VICTOIRE
    addBattleLog('🎉 Vous avez gagné le combat !');
    
    if (battleEffects) {
      battleEffects.createVictoryEffect();
    }
    
    if (audioManager) {
      audioManager.playVictory();
    }
    
    // Afficher modal victoire
    if (data.exp_gained) {
      $('#victory-exp-message').text(`Votre Pokémon a gagné ${data.exp_gained} EXP !`);
    }
    
    setTimeout(() => {
      $('#victory-modal').modal('show');
      $('#victory-modal').find('button').prop('disabled', false);
      $('#victory-modal').on('hidden.bs.modal', enableButtons);
    }, 1500);
    
  } else if (data.result === 'defeat') {
    // DEFAITE
    addBattleLog('💀 Vous avez perdu le combat...');
    
    if (audioManager) {
      audioManager.playDefeat();
    }
    
    setTimeout(() => {
      $('#defeat-modal').modal('show');
      $('#defeat-modal').find('button').prop('disabled', false);
      $('#defeat-modal').on('hidden.bs.modal', enableButtons);
    }, 1500);
    
  } else if (data.result === 'fled') {
    // FUITE
    addBattleLog('🏃 Vous avez fui le combat !');
    
    setTimeout(() => {
      $('#fled-modal').modal('show');
      $('#fled-modal').find('button').prop('disabled', false);
      $('#fled-modal').on('hidden.bs.modal', enableButtons);
    }, 1000);
    
  } else if (data.winner_id == BATTLE_CONFIG.playerTrainerId) {
    // Fallback victoire (ancien format)
    addBattleLog('🎉 Vous avez gagné le combat !');
    if (battleEffects) battleEffects.createVictoryEffect();
    if (audioManager) audioManager.playVictory();
    
    setTimeout(() => {
      $('#victory-modal').modal('show');
      $('#victory-modal').find('button').prop('disabled', false);
      $('#victory-modal').on('hidden.bs.modal', enableButtons);
    }, 1500);
    
  } else {
    // Fallback défaite ou reload
    setTimeout(() => {
      location.reload();
    }, 3000);
  }
}

// ============================================================================
// UI HELPERS
// ============================================================================

function addBattleLog(message) {
  const log = $('#log-messages');
  const entry = $(`<div class="log-entry">${message}</div>`);
  log.prepend(entry);
  
  // Limit to 10 messages
  if (log.children().length > 10) {
    log.children().last().remove();
  }
  
  // Auto-scroll
  log.parent().scrollTop(0);
}

function getElementCenter(element) {
  const offset = element.offset();
  const width = element.width();
  const height = element.height();
  
  return {
    x: offset.left + width / 2,
    y: offset.top + height / 2
  };
}

// ============================================================================
// FORCED SWITCH MODAL (quand Pokemon KO)
// ============================================================================

function showForcedSwitchModal() {
  console.log('🚨 Forced switch modal triggered');
  
  // Afficher le nom du Pokemon KO
  $('#fainted-pokemon-name').text($('#player-name').text());
  
  // Charger la liste de l'équipe
  $('#forced-switch-list').html('<p class="text-center"><i class="fas fa-spinner fa-spin"></i> Chargement...</p>');
  
  $.get(BATTLE_CONFIG.urls.getTeam, {
    trainer_id: BATTLE_CONFIG.playerTrainerId,
    exclude_pokemon_id: currentPlayerPokemonId
  })
  .done(function(data) {
    if (!data.team || data.team.length === 0) {
      $('#forced-switch-list').html('<p class="text-center text-danger">Aucun Pokémon disponible - Vous allez perdre!</p>');
      
      // Auto-perdre après 3 secondes si pas de Pokemon
      setTimeout(() => {
        location.reload();
      }, 3000);
      return;
    }
    
    // Filtrer seulement les Pokemon vivants
    const alivePokemon = data.team.filter(p => p.current_hp > 0);
    
    if (alivePokemon.length === 0) {
      $('#forced-switch-list').html('<p class="text-center text-danger">Tous vos Pokémon sont K.O. - Défaite!</p>');
      setTimeout(() => {
        location.reload();
      }, 3000);
      return;
    }
    
    let html = '<div class="list-group">';
    alivePokemon.forEach(pokemon => {
      const hpPercent = (pokemon.current_hp / pokemon.max_hp) * 100;
      const hpClass = hpPercent > 50 ? 'success' : (hpPercent > 20 ? 'warning' : 'danger');
      const spriteName = lowerPokemonFileNames(pokemon.species.name);
      const folder = pokemon.is_shiny ? 'shiny' : 'normal';
      const spriteUrl = BATTLE_CONFIG.static.spritesGen5 + folder + "/" + spriteName + ".png";
      
      html += `
        <button class="list-group-item list-group-item-action" 
                onclick="forcedSwitch(${pokemon.id})">
          <div class="d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
              <img src="${spriteUrl}" 
                   alt="${pokemon.nickname || pokemon.species.name}"
                   style="width:56px;height:56px;object-fit:contain;margin-right:12px;flex-shrink:0;"
                   onerror="this.style.display='none'">
              <div>
                <h6 class="mb-0"><strong>${pokemon.nickname || pokemon.species.name}</strong></h6>
                <small class="text-muted">Niv. ${pokemon.level}</small>
              </div>
            </div>
            <div class="text-right">
              <div class="progress" style="width: 100px; height: 10px;">
                <div class="progress-bar bg-${hpClass}" style="width: ${hpPercent}%"></div>
              </div>
              <small>${pokemon.current_hp}/${pokemon.max_hp} HP</small>
            </div>
          </div>
        </button>
      `;
    });
    html += '</div>';
    
    $('#forced-switch-list').html(html);
  })
  .fail(function() {
    $('#forced-switch-list').html('<p class="text-center text-danger">Erreur de chargement</p>');
  });
  
  // Afficher le modal (Bootstrap)
  $('#forced-switch-modal').modal('show');
}

function forcedSwitch(pokemonId) {
  console.log('⚡ Forced switch to Pokemon ID:', pokemonId);
  
  // Désactiver tous les boutons du modal
  $('#forced-switch-list button').prop('disabled', true);
  
  // Faire le switch
  $.post(BATTLE_CONFIG.urls.action, {
    action: 'switch',
    type: 'forcedSwitch',
    pokemon_id: pokemonId,
    csrfmiddlewaretoken: csrfToken
  })
  .done(function(data) {
    // Fermer le modal
    $('#forced-switch-modal').modal('hide');
    
    // Animer le nouveau Pokemon qui entre
    $('#player-sprite').removeClass('fainted').addClass('fade-out');
    
    setTimeout(() => {
      // Mettre à jour l'affichage
      updateBattleState(data);
      
      // Retirer fade-out et réafficher
      $('#player-sprite').removeClass('fade-out');
      
      addBattleLog(`${data.player_pokemon.name} entre au combat !`);
    }, 500);
  })
  .fail(function(xhr) {
    console.error('Forced switch failed:', xhr);
    addBattleLog('Erreur lors du changement');
    $('#forced-switch-list button').prop('disabled', false);
  });
}

// ============================================================================
// APPRENTISSAGE DE MOVE (modal de sélection)
// ============================================================================

// File d'attente si plusieurs moves sont appris en meme temps
let pendingMovesQueue = [];
let currentPendingMove = null;
let learnMovePokemonId = null;

function handlePendingMoves(pendingMoves, pokemonId) {
  if (!pendingMoves || pendingMoves.length === 0) return;
  learnMovePokemonId = pokemonId;
  pendingMovesQueue = [...pendingMoves];
  showNextPendingMove();
}

function showNextPendingMove() {
  if (pendingMovesQueue.length === 0) {
    currentPendingMove = null;
    // Re-activer les boutons une fois tous les moves traités
    $('button').prop('disabled', false);
    showMainMenu();
    return;
  }

  currentPendingMove = pendingMovesQueue.shift();

  const pokemonName = $('#player-name').text();
  $('#learn-move-pokemon-name').text(pokemonName);
  $('#learn-move-new-name').text(currentPendingMove.move_name);
  $('#new-move-display-name').text(currentPendingMove.move_name);
  $('#new-move-type-badge')
    .text((currentPendingMove.move_type || '').toUpperCase())
    .attr('class', `badge type-${currentPendingMove.move_type}`);
  $('#new-move-power-display').text(
    currentPendingMove.move_power ? `Puissance : ${currentPendingMove.move_power}` : 'Puissance : —'
  );
  $('#new-move-pp-display').text(`PP : ${currentPendingMove.move_pp}`);

  // Afficher les moves actuels
  let html = '';
  (currentPendingMove.current_moves || []).forEach(move => {
    html += `
      <div class="col-6 mb-2">
        <button class="btn btn-outline-danger btn-block move-replace-btn"
                onclick="confirmReplaceMove(${move.id})"
                style="text-align:left; padding: 8px 12px;">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong>${move.name}</strong>
              <br>
              <small class="badge type-${move.type}">${(move.type || '').toUpperCase()}</small>
              <small class="text-muted ml-1">${move.power ? 'PWR ' + move.power : '—'}</small>
            </div>
            <div class="text-right">
              <small class="text-muted">PP: ${move.pp}</small>
            </div>
          </div>
        </button>
      </div>
    `;
  });
  $('#current-moves-list').html(html);

  $('#learn-move-modal').modal('show');
}

function confirmReplaceMove(replacedMoveId) {
  if (!currentPendingMove || !learnMovePokemonId) return;

  // Désactiver les boutons pour éviter double-clic
  $('.move-replace-btn').prop('disabled', true);

  $.post(BATTLE_CONFIG.urls.learnMove, {
    new_move_id:      currentPendingMove.move_id,
    replaced_move_id: replacedMoveId,
    pokemon_id:       learnMovePokemonId,
    csrfmiddlewaretoken: csrfToken
  })
  .done(function(data) {
    $('#learn-move-modal').modal('hide');
    addBattleLog(data.message || 'Capacité apprise !');
    if (data.moves) {
      updateMovesMenu(data.moves);
    }
    // Passer au move suivant si file d'attente
    setTimeout(showNextPendingMove, 400);
  })
  .fail(function() {
    addBattleLog('Erreur lors de l\'apprentissage du move.');
    $('.move-replace-btn').prop('disabled', false);
  });
}

function skipLearnMove() {
  if (!currentPendingMove || !learnMovePokemonId) return;

  $.post(BATTLE_CONFIG.urls.learnMove, {
    new_move_id:      currentPendingMove.move_id,
    replaced_move_id: 'skip',
    pokemon_id:       learnMovePokemonId,
    csrfmiddlewaretoken: csrfToken
  })
  .done(function(data) {
    $('#learn-move-modal').modal('hide');
    addBattleLog(data.message || 'Capacité ignorée.');
    setTimeout(showNextPendingMove, 400);
  })
  .fail(function() {
    addBattleLog('Erreur.');
  });
}

// ============================================================================
// SYSTÈME D'ÉVOLUTION
// ============================================================================

let pendingEvolutionData        = null;
let pendingEvolutionStatsBefore = null;
let pendingBattleEndData        = null;  // fin de combat à déclencher après l'évolution

const SPRITE_BASE_NORMAL = BATTLE_CONFIG.static.spritesNormal;
const SPRITE_BASE_BACK   = BATTLE_CONFIG.static.spritesBack;
const SPRITE_BASE_SHINY  = BATTLE_CONFIG.static.spritesShiny;
const SPRITE_BASE_BACK_SHINY = BATTLE_CONFIG.static.spritesBackShiny;

function lowerForSprite(name) {
  return name.toLowerCase().replace(/[^a-z0-9]/g, '');
}

/** Appelé par updateBattleState quand pending_evolution est présent */
// Référence globale à l'audio d'évolution
let evoAudio = null;

function triggerEvolution(evoData, battleEndData = null) {
  pendingEvolutionData        = evoData;
  pendingEvolutionStatsBefore = evoData.stats_before;
  pendingBattleEndData        = battleEndData;

  const fromName = evoData.from_name;
  const toName   = evoData.to_name;

  if (evoData.is_shiny){
    const spriteBefore = SPRITE_BASE_BACK_SHINY   + lowerForSprite(fromName) + '.png';
    const spriteAfter  = SPRITE_BASE_SHINY + lowerForSprite(toName)   + '.png';
  } else {
    const spriteBefore = SPRITE_BASE_BACK   + lowerForSprite(fromName) + '.png';
    const spriteAfter  = SPRITE_BASE_NORMAL + lowerForSprite(toName)   + '.png';
  }

  document.getElementById('evo-sprite-before').src = spriteBefore;
  document.getElementById('evo-sprite-after').src  = spriteAfter;
  document.getElementById('evo-result-before-sprite').src = spriteBefore;
  document.getElementById('evo-result-after-sprite').src  = spriteAfter;

  document.getElementById('evo-from-name').textContent   = fromName;
  document.getElementById('evo-from-name-2').textContent = fromName;
  document.getElementById('evo-to-name').textContent     = toName;

  document.getElementById('evo-phase-announce').classList.remove('d-none');
  document.getElementById('evo-phase-anim').classList.add('d-none');
  document.getElementById('evo-phase-result').classList.add('d-none');

  $('button').prop('disabled', true);

  // Couper la BGM et lancer le son d'évolution
  if (typeof audioManager !== 'undefined') audioManager.stopBGM();
  evoAudio = new Audio(BATTLE_CONFIG.static.evoSound);
  evoAudio.volume = 0.85;
  evoAudio.play().catch(() => {});

  $('#evolution-modal').modal('show');
  runEvolutionSequence(fromName, toName);
}

async function runEvolutionSequence(fromName, toName) {
  // Durée de la fin d'animation (glow + flash + swap + reveal)
  const seqStart = performance.now();

  await sleep(1800);   // lire l'annonce

  document.getElementById('evo-phase-announce').classList.add('d-none');
  document.getElementById('evo-phase-anim').classList.remove('d-none');

  const beforeWrap = document.getElementById('evo-before-wrap');
  const afterWrap  = document.getElementById('evo-after-wrap');
  const glow       = document.getElementById('evo-glow');
  const flash      = document.getElementById('evo-flash');

  // 1. Scintillement (4×)
  for (let i = 0; i < 4; i++) {
    beforeWrap.classList.add('evo-blink');
    await sleep(220);
    beforeWrap.classList.remove('evo-blink');
    await sleep(180);
  }

  // 2. Silhouette + accélération progressive
  beforeWrap.classList.add('evo-silhouette');
  const spinDurations = [1040, 980, 920, 860, 800, 740, 680, 620, 560, 500, 440, 380, 320, 260, 200, 160, 130, 100, 80];
  for (const dur of spinDurations) {
    beforeWrap.classList.add('evo-spin-frame');
    await sleep(dur / 2);
    beforeWrap.classList.remove('evo-spin-frame');
    await sleep(dur / 2);
  }

  // 3. Spin soutenu à pleine vitesse — s'arrête à 14s dans l'audio
  const getAudioTimeMs = () => {
    if (evoAudio && evoAudio.currentTime) {
      return evoAudio.currentTime * 1000;
    }
    return performance.now() - seqStart;
  };

  while (getAudioTimeMs() < 14000) { // après 14 secondes d'audio commence la séquence de transformation
    beforeWrap.classList.add('evo-spin-frame');
    await sleep(30);
    beforeWrap.classList.remove('evo-spin-frame');
    await sleep(30);
  }

  // 4. Glow + flash en fin d'audio
  glow.classList.add('evo-glow-active');
  await sleep(300);
  flash.classList.add('evo-flash-active');
  await sleep(350);

  // 5. Swap sprites sous le flash
  beforeWrap.classList.add('d-none');
  afterWrap.classList.remove('d-none');
  afterWrap.classList.add('evo-silhouette');
  await sleep(200);

  flash.classList.remove('evo-flash-active');
  await sleep(400);

  // 6. Révélation couleurs
  afterWrap.classList.remove('evo-silhouette');
  afterWrap.querySelector('img').classList.add('evo-sprite-reveal-anim');
  await sleep(800);

  applyEvolutionOnServer();
}

function applyEvolutionOnServer() {
  $.post(BATTLE_CONFIG.urls.action, {
    action:       'confirm_evolution',
    evolution_id: pendingEvolutionData.evolution_id,
    csrfmiddlewaretoken: csrfToken
  })
  .done(function(data) {
    const statsAfter = data.stats_after || {};
    renderEvolutionStats(pendingEvolutionStatsBefore, statsAfter);

    // Phase résultat
    document.getElementById('evo-phase-anim').classList.add('d-none');
    document.getElementById('evo-phase-result').classList.remove('d-none');
    document.getElementById('evo-confirm-btn').disabled = false;

    // Mettre à jour le combat avec les nouvelles données
    if (data.player_pokemon) {
      updatePokemonDisplay('player', data.player_pokemon);
    }
    if (data.log) data.log.forEach(m => addBattleLog(m));
  })
  .fail(function() {
    addBattleLog('Erreur lors de l\'évolution.');
    document.getElementById('evo-confirm-btn').disabled = false;
    closeEvolutionModal();
  });
}

function renderEvolutionStats(before, after) {
  const stats = [
    { key: 'hp',              label: 'PV' },
    { key: 'attack',          label: 'Attaque' },
    { key: 'defense',         label: 'Défense' },
    { key: 'special_attack',  label: 'Att. Spé.' },
    { key: 'special_defense', label: 'Def. Spé.' },
    { key: 'speed',           label: 'Vitesse' },
  ];

  const rows = stats.map(s => {
    const bVal = before[s.key] || 0;
    const aVal = after[s.key]  || 0;
    const diff = aVal - bVal;
    const diffHtml = diff > 0
      ? `<span class="text-success">+${diff}</span>`
      : diff < 0
        ? `<span class="text-danger">${diff}</span>`
        : `<span class="text-muted">—</span>`;

    return `<div class="evo-stat-row">
      <span class="evo-stat-label">${s.label}</span>
      <span class="evo-stat-before">${bVal}</span>
      <span class="evo-stat-arrow">→</span>
      <span class="evo-stat-after font-weight-bold">${aVal}</span>
      <span class="evo-stat-diff">${diffHtml}</span>
    </div>`;
  }).join('');

  document.getElementById('evo-stats-table').innerHTML = rows;
}

function confirmEvolution() {
  // Refermer le modal et re-autoriser les actions
  closeEvolutionModal();
}

function closeEvolutionModal() {
  $('#evolution-modal').modal('hide');

  // Arrêter l'audio d'évolution s'il tourne encore
  if (evoAudio) {
    evoAudio.pause();
    evoAudio.currentTime = 0;
    evoAudio = null;
  }

  pendingEvolutionData = null;

  // Si un combat s'est terminé pendant l'évolution, l'afficher maintenant
  if (pendingBattleEndData) {
    const battleData     = pendingBattleEndData;
    pendingBattleEndData = null;
    setTimeout(() => handleBattleEnd(battleData), 400);
    return;
  }

  // Sinon réactiver les boutons normalement
  if (!pendingMovesQueue.length) {
    $('button').prop('disabled', false);
    showMainMenu();
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ============================================================================
// KEYBOARD SHORTCUTS
// ============================================================================

$(document).keydown(function(e) {
  if ($('#main-menu').is(':visible')) {
    switch(e.key) {
      case '1': showMoves(); break;
      case '2': showTeam(); break;
      case '3': showItems(); break;
      case '4': tryRun(); break;
    }
  } else if (e.key === 'Escape') {
    showMainMenu();
  }
});


// ============================================================================
// SYSTÈME DE CAPTURE
// ============================================================================


async function initiateCaptureSequence(itemId) {
  // Fermer le menu items
  showMainMenu();
  
  // Demander au serveur les infos pour la capture
  const response = await $.post(BATTLE_CONFIG.urls.action, {
    action: 'item',
    item_id: itemId,
    csrfmiddlewaretoken: csrfToken
  });
  
  if (response.capture_attempt) {
    // Lancer l'animation avec les shakes/résultat pré-calculés par le backend
    // (formule Gen 3 officielle — pas de random côté client)
    const result = await captureSystem.attemptCapture(
      response.capture_attempt.pokemon,
      response.capture_attempt.ball_type,
      response.capture_attempt.capture_rate,
      response.capture_attempt.shakes,
      response.capture_attempt.success
    );
    
    // Confirmer la capture au serveur
    const finalResult = await $.post(BATTLE_CONFIG.urls.action, {
      action: 'confirm_capture',
      item_id: itemId,
      csrfmiddlewaretoken: csrfToken
    });
    
    // Traiter le résultat
    if (finalResult.capture_result && finalResult.capture_result.success) {
      // SUCCÈS !
      addBattleLog(finalResult.capture_result.message);
      
      if (audioManager) {
        audioManager.playSFX('capture/success');
      }
      
      // Afficher modal de succès
      setTimeout(() => {
        showCaptureSuccessModal(finalResult.capture_result);
      }, 500);
    } else {
      // ÉCHEC
      addBattleLog(finalResult.capture_result.message);
      
      if (audioManager) {
        audioManager.playSFX('capture/failed');
      }
      
      // Continuer le combat
      updateBattleState(finalResult);
      $('button').prop('disabled', false);
    }
  }
}

function showCaptureSuccessModal(captureData) {
  const modal = `
    <div class="modal fade" id="capture-success-modal" tabindex="-1" data-backdrop="static">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-success">
          <div class="modal-header bg-success text-white">
            <h5 class="modal-title">
              <i class="fas fa-trophy"></i> Pokémon Capturé !
            </h5>
          </div>
          <div class="modal-body text-center">
            <i class="fas fa-check-circle fa-5x text-success mb-3"></i>
            <h4>${captureData.captured_pokemon.name} capturé !</h4>
            <p class="mb-2">Niveau ${captureData.captured_pokemon.level}</p>
            ${captureData.is_first_catch ? '<p class="text-warning"><i class="fas fa-star"></i> Premier capturé !</p>' : ''}
            <hr>
            <p class="text-muted small">Le Pokémon a été envoyé dans votre PC</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-success" onclick="window.location.href=BATTLE_CONFIG.urls.returnZone">
              <i class="fas fa-map-marker-alt"></i> Retour à la zone
            </button>
            <button type="button" class="btn btn-primary" onclick="window.location.href=BATTLE_CONFIG.urls.myTeam">
              <i class="fas fa-laptop"></i> Voir le PC
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  $('body').append(modal);
  $('#capture-success-modal').modal('show');
}