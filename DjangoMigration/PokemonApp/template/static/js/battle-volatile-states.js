/**
 * battle-volatile-states.js
 * Gère l'affichage des états volatils ET des boost/malus de stats en combat.
 *
 * Fonctionnalités :
 *   - Météo (bannière + effet sur fond)
 *   - Badges volatils (Confusion, Vampigraine, Piège, Toxic, Charge, etc.)
 *   - Indicateurs de stat stages (−6 à +6) : ATK, DEF, SpA, SpD, VIT, PRÉC, ESQ
 *   - Tooltip au survol (nom complet + multiplicateur)
 *   - Animation flash vert/rouge à chaque changement de stage
 */

'use strict';

/* ── CONFIG ────────────────────────────────────────────────────────────────── */

const WEATHER_LABELS = {
    sunny:     { label: '☀️ Soleil intense',      cls: 'weather-sunny'     },
    rain:      { label: '🌧️ Pluie torrentielle',  cls: 'weather-rain'      },
    sandstorm: { label: '🌪️ Tempête de sable',    cls: 'weather-sandstorm' },
    hail:      { label: '🌨️ Grêle',               cls: 'weather-hail'      },
};

const VOLATILE_ICONS = {
    confused:       { icon: '😵', label: 'Confus',       cls: 'status-confuse'  },
    leech_seed:     { icon: '🌱', label: 'Vampigraine',  cls: 'status-seed'     },
    trapped:        { icon: '🔗', label: 'Piégé',        cls: 'status-trap'     },
    badly_poisoned: { icon: '☠️', label: 'Toxic',        cls: 'status-toxic'    },
    charging:       { icon: '⚡', label: 'Chargement…',  cls: 'status-charge'   },
    recharge:       { icon: '💤', label: 'Recharge',     cls: 'status-recharge' },
    protected:      { icon: '🛡️', label: 'Protégé',     cls: 'status-protect'  },
    focus_energy:   { icon: '🎯', label: 'Concentré',    cls: 'status-focus'    },
    ingrain:        { icon: '🌿', label: 'Enraciné',     cls: 'status-ingrain'  },
    rampaging:      { icon: '🔥', label: 'Emballement',  cls: 'status-rampage'  },
};

/**
 * STAT_DEFS : stats affichées dans l'indicateur.
 * key      → suffixe dans battle_state (ex: "player_atk_stage")
 * label    → abréviation dans la barre
 * fullName → nom affiché dans le tooltip
 */
const STAT_DEFS = [
    { key: 'atk_stage',   label: 'ATK',  fullName: 'Attaque'      },
    { key: 'def_stage',   label: 'DEF',  fullName: 'Défense'      },
    { key: 'spatk_stage', label: 'SpA',  fullName: 'Attaque Spé.' },
    { key: 'spdef_stage', label: 'SpD',  fullName: 'Défense Spé.' },
    { key: 'speed_stage', label: 'VIT',  fullName: 'Vitesse'      },
    { key: 'acc_stage',   label: 'PRÉC', fullName: 'Précision'    },
    { key: 'eva_stage',   label: 'ESQ',  fullName: 'Esquive'      },
];

/* Multiplicateurs affichés dans le tooltip */
const STAGE_MULT = {
    6:'×4',  5:'×3,5', 4:'×3',  3:'×2,5', 2:'×2',  1:'×1,5',
    0: 'Normal',
    '-1':'×0,67', '-2':'×0,5', '-3':'×0,4', '-4':'×0,33', '-5':'×0,29', '-6':'×0,25'
};

/* Mémorisation pour détecter les changements */
const _prevStages = { player: {}, opponent: {} };

/* ── POINT D'ENTRÉE ─────────────────────────────────────────────────────────── */

/**
 * Appeler cette fonction après chaque réponse JSON de l'API de combat.
 * @param {Object} data  Réponse complète de battle_action_view
 */
function updateVolatileStates(data) {
    if (!data || !data.battle_state) return;
    const bs = data.battle_state;

    updateWeather(bs.weather, bs.weather_turns);
    updatePokemonVolatile('player',   bs);
    updatePokemonVolatile('opponent', bs);
    updateScreens(bs);
    updateStatStages('player',   bs);
    updateStatStages('opponent', bs);
}

/* ── MÉTÉO ──────────────────────────────────────────────────────────────────── */

function updateWeather(weather, turns) {
    const el = document.getElementById('weather-banner');
    if (!el) return;

    if (!weather) {
        el.className = ''; el.textContent = ''; el.style.display = 'none';
        const bg = document.getElementById('weather-container');
        if (bg) bg.className = 'weather-effect';
        return;
    }

    const w = WEATHER_LABELS[weather] || { label: weather, cls: '' };
    el.className   = `weather-banner ${w.cls}`;
    el.textContent = `${w.label}${turns ? ` (${turns} tours)` : ''}`;
    el.style.display = 'block';

    const bg = document.getElementById('weather-container');
    if (bg) bg.className = `weather-effect weather-effect--${weather}`;
}

/* ── BADGES VOLATILS ────────────────────────────────────────────────────────── */

function updatePokemonVolatile(side, bs) {
    const container = document.getElementById(`${side}-volatile-badges`);
    if (!container) return;
    container.innerHTML = '';

    const active = [];
    if (bs[`${side}_confused`])        active.push('confused');
    if (bs[`${side}_leech_seed`])      active.push('leech_seed');
    if (bs[`${side}_trapped`])         active.push('trapped');
    if (bs[`${side}_badly_poisoned`])  active.push('badly_poisoned');
    if (bs[`${side}_charging`])        active.push('charging');
    if (bs[`${side}_recharge`])        active.push('recharge');
    if (bs[`${side}_protected`])       active.push('protected');
    if (bs[`${side}_focus_energy`])    active.push('focus_energy');
    if (bs[`${side}_ingrain`])         active.push('ingrain');
    if (bs[`${side}_rampaging`])       active.push('rampaging');

    active.forEach(k => {
        const info = VOLATILE_ICONS[k];
        if (!info) return;
        const badge = document.createElement('span');
        badge.className   = `volatile-badge ${info.cls}`;
        badge.title       = info.label;
        badge.textContent = (k === 'charging' && bs[`${side}_charging`])
            ? `⚡ ${bs[`${side}_charging`]}…`
            : `${info.icon} ${info.label}`;
        container.appendChild(badge);
    });
}

/* ── ÉCRANS ─────────────────────────────────────────────────────────────────── */

function updateScreens(bs) {
    ['player', 'opponent'].forEach(side => {
        const screens = bs[`${side}_screens`] || {};
        ['light_screen', 'reflect'].forEach(t => {
            const el = document.getElementById(`${side}-${t.replace('_', '-')}`);
            if (!el) return;
            const turns = screens[t] || 0;
            if (turns > 0) {
                el.style.display = 'inline-block';
                el.textContent = t === 'light_screen'
                    ? `💠 Écran Lumière (${turns})` : `🔴 Mur (${turns})`;
            } else {
                el.style.display = 'none';
            }
        });
    });
}

/* ── INDICATEURS DE STAT STAGES ─────────────────────────────────────────────── */

function updateStatStages(side, bs) {
    const container = document.getElementById(`${side}-stat-stages`);
    if (!container) return;

    /* Construction initiale (une seule fois) */
    if (!container.dataset.built) {
        _buildStatStagesUI(container);
        container.dataset.built = '1';
    }

    let anyNonZero = false;

    STAT_DEFS.forEach(def => {
        const stage     = bs[`${side}_${def.key}`] ?? 0;
        const prevStage = _prevStages[side][def.key] ?? 0;
        _prevStages[side][def.key] = stage;

        const row       = container.querySelector(`.stat-stage-row[data-stat="${def.key}"]`);
        if (!row) return;

        const valueEl   = row.querySelector('.ssi-value');
        const arrowEl   = row.querySelector('.ssi-arrow');
        const tooltipEl = row.querySelector('.ssi-tooltip');
        const trackEl   = row.querySelector('.ssi-track');

        /* Couleurs bien visibles sur fond blanc */
        const color     = stage > 0 ? '#16a34a' : stage < 0 ? '#dc2626' : '#6b7280';
        const bgColor   = stage > 0 ? '#dcfce7' : stage < 0 ? '#fee2e2' : 'transparent';

        /* Valeur numérique : badge coloré */
        valueEl.textContent      = stage === 0 ? '' : (stage > 0 ? `+${stage}` : `${stage}`);
        valueEl.style.color      = color;
        valueEl.style.background = bgColor;

        /* Flèche */
        arrowEl.textContent = stage > 0 ? '▲' : stage < 0 ? '▼' : '';
        arrowEl.style.color = color;

        /* Tooltip */
        if (tooltipEl) {
            tooltipEl.textContent = `${def.fullName} : ${STAGE_MULT[stage] ?? ''}`;
        }

        /* Barres de segments */
        _updateTrack(trackEl, stage);

        /* Visibilité : n'afficher QUE les lignes avec stage ≠ 0 */
        row.style.display = stage !== 0 ? 'flex' : 'none';

        /* Animation flash si changement (même si la ligne vient d'apparaître/disparaître) */
        if (stage !== prevStage) {
            if (stage !== 0) row.style.display = 'flex'; // forcer visible pour l'anim
            _flashRow(row, stage > prevStage ? 'boost' : 'drop');
        }

        if (stage !== 0) anyNonZero = true;
    });

    /* Masquer le bloc entier seulement si TOUS les stages sont à 0 */
    container.style.display = anyNonZero ? 'block' : 'none';
}

/* Construit le DOM de l'indicateur (appelé une seule fois) */
function _buildStatStagesUI(container) {
    container.innerHTML = '';

    STAT_DEFS.forEach(def => {
        /* Segments : 13 cases, positions −6 à +6 */
        let segs = '';
        for (let i = 0; i < 13; i++) {
            const pos = i - 6;
            const cls = pos === 0 ? ' ssi-seg-center' : '';
            segs += `<span class="ssi-seg${cls}" data-pos="${pos}"></span>`;
        }

        const row = document.createElement('div');
        row.className   = 'stat-stage-row';
        row.dataset.stat = def.key;
        row.innerHTML = `
            <span class="ssi-label" title="${def.fullName}">${def.label}</span>
            <div class="ssi-track">${segs}</div>
            <span class="ssi-arrow"></span>
            <span class="ssi-value">—</span>
            <span class="ssi-tooltip">${def.fullName} : Normal</span>
        `;
        container.appendChild(row);
    });
}

/* Colorie les segments selon le stage */
function _updateTrack(trackEl, stage) {
    trackEl.querySelectorAll('.ssi-seg').forEach(seg => {
        const pos = parseInt(seg.dataset.pos, 10);
        /* Réinitialiser */
        seg.className = 'ssi-seg' + (pos === 0 ? ' ssi-seg-center' : '');

        if (stage === 0) {
            /* Rien d'actif */
        } else if (stage > 0) {
            if (pos > 0 && pos <= stage)  seg.classList.add('ssi-boost');
            else if (pos < 0)             seg.classList.add('ssi-dim');
        } else {
            if (pos < 0 && pos >= stage)  seg.classList.add('ssi-drop');
            else if (pos > 0)             seg.classList.add('ssi-dim');
        }
    });
}

/* Flash d'animation sur une ligne */
function _flashRow(row, type) {
    row.classList.remove('ssi-flash-boost', 'ssi-flash-drop');
    void row.offsetWidth; /* forcer reflow */
    row.classList.add(type === 'boost' ? 'ssi-flash-boost' : 'ssi-flash-drop');
    setTimeout(() => row.classList.remove('ssi-flash-boost', 'ssi-flash-drop'), 700);
}

/* ── CSS INJECTÉ ────────────────────────────────────────────────────────────── */

(function injectStyles() {
    if (document.getElementById('volatile-states-css')) return;
    const s = document.createElement('style');
    s.id = 'volatile-states-css';
    s.textContent = `
/* ── Météo ─────────────────────────────────────────────────────────────────── */
.weather-banner{display:none;text-align:center;font-weight:700;padding:3px 10px;
  border-radius:6px;margin:3px 0;font-size:.76rem;transition:background .5s}
.weather-sunny{background:#ffe066;color:#7a5800}
.weather-rain{background:#6699cc;color:#fff}
.weather-sandstorm{background:#d4a847;color:#4a2e00}
.weather-hail{background:#aed6f1;color:#1b4f72}
.weather-effect--sunny    {filter:brightness(1.1) saturate(1.2)}
.weather-effect--rain     {filter:brightness(.85) hue-rotate(180deg)}
.weather-effect--sandstorm{filter:sepia(.4) brightness(.95)}
.weather-effect--hail     {filter:brightness(.9) hue-rotate(200deg)}

/* ── Badges volatils ─────────────────────────────────────────────────────── */
.volatile-badge{display:inline-block;font-size:.62rem;padding:1px 5px;border-radius:4px;
  margin:1px;font-weight:600;white-space:nowrap}
.status-confuse {background:#d7bde2;color:#6c3483}
.status-seed    {background:#a9dfbf;color:#1e8449}
.status-trap    {background:#f0b27a;color:#784212}
.status-toxic   {background:#9b59b6;color:#fff}
.status-charge  {background:#f9e79f;color:#7d6608}
.status-recharge{background:#aeb6bf;color:#212121}
.status-protect {background:#85c1e9;color:#154360}
.status-focus   {background:#f8c471;color:#7e5109}
.status-ingrain {background:#82e0aa;color:#1d8348}
.status-rampage {background:#e74c3c;color:#fff}

/* ── Écrans ──────────────────────────────────────────────────────────────── */
#player-light-screen,#opponent-light-screen,#player-reflect,#opponent-reflect{
  display:none;font-size:.62rem;padding:1px 5px;border-radius:4px;margin:1px;font-weight:600}
#player-light-screen,#opponent-light-screen{background:#d6eaf8;color:#154360}
#player-reflect,#opponent-reflect{background:#fadbd8;color:#641e16}

/* ── Bloc stat stages ────────────────────────────────────────────────────── */
/*
  Design : chips horizontales compactes, une ligne par stat modifiée.
  Fond blanc de l'info-bar → couleurs pleines nécessaires pour contraste.
*/
.stat-stages-container{
  display:none;
  margin-top:4px;
  /* Pas de padding ni fond propre : on laisse respirer l'info-bar */
}

/* ── Ligne = une chip ────────────────────────────────────────────────────── */
.stat-stage-row{
  display:none;           /* caché par défaut, JS l'active si stage ≠ 0 */
  align-items:center;
  gap:3px;
  margin-bottom:2px;
  border-radius:4px;
  padding:1px 3px;
  position:relative;
  width:100%;
  box-sizing:border-box;
}

/* Label */
.ssi-label{
  font-size:.58rem;
  font-weight:800;
  color:#444;
  text-transform:uppercase;
  letter-spacing:.03em;
  min-width:22px;
  flex-shrink:0;
}

/* ── Barres de segments ───────────────────────────────────────────────────── */
.ssi-track{
  display:flex;
  align-items:center;
  gap:1px;
  flex-shrink:0;
}
.ssi-seg{
  display:inline-block;
  width:4px;
  height:7px;
  border-radius:1px;
  background:#d0d0d0;         /* gris clair visible sur blanc */
  transition:background .2s, transform .15s;
}
.ssi-seg-center{
  width:2px !important;
  height:10px !important;
  background:#999 !important;
  border-radius:1px !important;
}
/* Segments actifs : couleurs plein opaque sur fond blanc */
.ssi-boost{ background:#16a34a !important; transform:scaleY(1.3); } /* vert foncé */
.ssi-drop { background:#dc2626 !important; transform:scaleY(1.3); } /* rouge foncé */
.ssi-dim  { background:#e5e7eb !important; }                         /* gris très clair */

/* Flèche */
.ssi-arrow{
  font-size:.6rem;
  font-weight:900;
  min-width:7px;
  text-align:center;
  flex-shrink:0;
}

/* Valeur numérique : badge coloré bien visible */
.ssi-value{
  font-size:.6rem;
  font-weight:800;
  min-width:18px;
  text-align:center;
  border-radius:3px;
  padding:0 3px;
  flex-shrink:0;
  /* couleur posée dynamiquement par JS */
}

/* ── Tooltip ─────────────────────────────────────────────────────────────── */
.ssi-tooltip{
  display:none;
  position:absolute;
  left:calc(100% + 4px);
  top:50%;
  transform:translateY(-50%);
  background:rgba(15,15,25,.9);
  color:#f0f0f0;
  font-size:.6rem;
  padding:2px 7px;
  border-radius:4px;
  white-space:nowrap;
  pointer-events:none;
  z-index:400;
  box-shadow:0 2px 8px rgba(0,0,0,.5);
}
.stat-stage-row:hover .ssi-tooltip{ display:block; }

/* ── Flash ───────────────────────────────────────────────────────────────── */
@keyframes ssiBoost{
  0%  {background:transparent}
  30% {background:rgba(22,163,74,.25)}
  100%{background:transparent}
}
@keyframes ssiDrop{
  0%  {background:transparent}
  30% {background:rgba(220,38,38,.25)}
  100%{background:transparent}
}
.ssi-flash-boost{ animation:ssiBoost .6s ease-out; }
.ssi-flash-drop { animation:ssiDrop  .6s ease-out; }
    `;
    document.head.appendChild(s);
})();