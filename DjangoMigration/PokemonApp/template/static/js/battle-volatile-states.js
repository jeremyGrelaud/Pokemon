/**
 * battle-volatile-states.js
 * À inclure dans battle_game_v2.html (ou dans le bloc {% block extra_scripts %})
 * 
 * Gère l'affichage des états volatils renvoyés par l'API :
 *   - Météo (icône + bannière)
 *   - Confusion, Vampigraine, Piège
 *   - Toxic (poison sévère)
 *   - Charge en cours (SolarBeam, Fly, Dig…)
 *   - Rechargement (Hyper Beam…)
 *   - Protect / Focus Energy / Ingrain
 *   - Light Screen / Reflect
 */

/* ─────────────────────────────────────────────────────────────────────────────
   LABELS & STYLES
   ───────────────────────────────────────────────────────────────────────────── */
const WEATHER_LABELS = {
    sunny:     { label: '☀️ Soleil intense',  class: 'weather-sunny'     },
    rain:      { label: '🌧️ Pluie torrentielle', class: 'weather-rain'   },
    sandstorm: { label: '🌪️ Tempête de sable', class: 'weather-sandstorm' },
    hail:      { label: '🌨️ Grêle',            class: 'weather-hail'     },
};

const VOLATILE_ICONS = {
    confused:       { icon: '😵', label: 'Confus',       class: 'status-confuse'  },
    leech_seed:     { icon: '🌱', label: 'Vampigraine',  class: 'status-seed'     },
    trapped:        { icon: '🔗', label: 'Piégé',        class: 'status-trap'     },
    badly_poisoned: { icon: '☠️', label: 'Toxic',        class: 'status-toxic'    },
    charging:       { icon: '⚡', label: 'Chargement…',  class: 'status-charge'   },
    recharge:       { icon: '💤', label: 'Recharge',     class: 'status-recharge' },
    protected:      { icon: '🛡️', label: 'Protégé',     class: 'status-protect'  },
    focus_energy:   { icon: '🎯', label: 'Concentré',   class: 'status-focus'    },
    ingrain:        { icon: '🌿', label: 'Enraciné',    class: 'status-ingrain'  },
    rampaging:      { icon: '🔥', label: 'Emballement', class: 'status-rampage'  },
};

/* ─────────────────────────────────────────────────────────────────────────────
   MISE À JOUR PRINCIPALE
   Appelée après chaque réponse API de combat.
   data = la réponse JSON complète de battle_action_view
   ───────────────────────────────────────────────────────────────────────────── */
function updateVolatileStates(data) {
    if (!data || !data.battle_state) return;
    const bs = data.battle_state;

    updateWeather(bs.weather, bs.weather_turns);
    updatePokemonVolatile('player',   bs);
    updatePokemonVolatile('opponent', bs);
    updateScreens(bs);
}

/* ─── Météo ──────────────────────────────────────────────────────────────── */
function updateWeather(weather, turns) {
    const el = document.getElementById('weather-banner');
    if (!el) return;

    if (!weather) {
        el.className = '';
        el.textContent = '';
        el.style.display = 'none';
        return;
    }

    const w = WEATHER_LABELS[weather] || { label: weather, class: 'weather-unknown' };
    el.className     = `weather-banner ${w.class}`;
    el.textContent   = `${w.label}${turns ? ` (${turns} tours)` : ''}`;
    el.style.display = 'block';

    // Effets visuels sur le conteneur de fond
    const bg = document.getElementById('weather-container');
    if (bg) {
        bg.className = `weather-effect weather-effect--${weather}`;
    }
}

/* ─── Étiquettes volatiles par Pokémon ─────────────────────────────────── */
function updatePokemonVolatile(side, bs) {
    const container = document.getElementById(`${side}-volatile-badges`);
    if (!container) return;

    container.innerHTML = '';
    const states = [];

    if (bs[`${side}_confused`])        states.push('confused');
    if (bs[`${side}_leech_seed`])      states.push('leech_seed');
    if (bs[`${side}_trapped`])         states.push('trapped');
    if (bs[`${side}_badly_poisoned`])  states.push('badly_poisoned');
    if (bs[`${side}_charging`])        states.push('charging');
    if (bs[`${side}_recharge`])        states.push('recharge');
    if (bs[`${side}_protected`])       states.push('protected');
    if (bs[`${side}_focus_energy`])    states.push('focus_energy');
    if (bs[`${side}_ingrain`])         states.push('ingrain');
    if (bs[`${side}_rampaging`])       states.push('rampaging');

    states.forEach(stateKey => {
        const info = VOLATILE_ICONS[stateKey];
        if (!info) return;

        const badge = document.createElement('span');
        badge.className   = `volatile-badge ${info.class}`;
        badge.title       = info.label;
        badge.textContent = `${info.icon} ${info.label}`;
        container.appendChild(badge);
    });

    // Afficher "chargement" avec le nom du move si disponible
    if (bs[`${side}_charging`]) {
        const chargeEl = container.querySelector('.status-charge');
        if (chargeEl) {
            chargeEl.textContent = `⚡ ${bs[`${side}_charging`]}…`;
        }
    }
}

/* ─── Écrans (Light Screen / Reflect) ───────────────────────────────────── */
function updateScreens(bs) {
    ['player', 'opponent'].forEach(side => {
        const screens = bs[`${side}_screens`] || {};

        ['light_screen', 'reflect'].forEach(screenType => {
            const id  = `${side}-${screenType.replace('_', '-')}`;
            const el  = document.getElementById(id);
            if (!el) return;

            const turns = screens[screenType] || 0;
            if (turns > 0) {
                el.style.display = 'inline-block';
                el.textContent   = `${screenType === 'light_screen' ? '💠 Écran Lumière' : '🔴 Mur'} (${turns})`;
            } else {
                el.style.display = 'none';
            }
        });
    });
}

/* ─────────────────────────────────────────────────────────────────────────────
   CSS INLINE (à déplacer dans un fichier .css séparé)
   ───────────────────────────────────────────────────────────────────────────── */
(function injectStyles() {
    if (document.getElementById('volatile-states-css')) return;
    const style = document.createElement('style');
    style.id = 'volatile-states-css';
    style.textContent = `
        /* Bannière météo */
        .weather-banner {
            display: none;
            text-align: center;
            font-weight: bold;
            padding: 4px 12px;
            border-radius: 8px;
            margin: 4px auto;
            font-size: 0.85rem;
            max-width: 300px;
            transition: background 0.5s;
        }
        .weather-sunny     { background: #ffe066; color: #7a5800; }
        .weather-rain      { background: #6699cc; color: #fff;    }
        .weather-sandstorm { background: #d4a847; color: #4a2e00; }
        .weather-hail      { background: #aed6f1; color: #1b4f72; }

        /* Badges volatiles */
        .volatile-badge {
            display: inline-block;
            font-size: 0.7rem;
            padding: 2px 6px;
            border-radius: 4px;
            margin: 1px;
            font-weight: 600;
            white-space: nowrap;
        }
        .status-confuse  { background: #d7bde2; color: #6c3483; }
        .status-seed     { background: #a9dfbf; color: #1e8449; }
        .status-trap     { background: #f0b27a; color: #784212; }
        .status-toxic    { background: #9b59b6; color: #fff;    }
        .status-charge   { background: #f9e79f; color: #7d6608; }
        .status-recharge { background: #aeb6bf; color: #212121; }
        .status-protect  { background: #85c1e9; color: #154360; }
        .status-focus    { background: #f8c471; color: #7e5109; }
        .status-ingrain  { background: #82e0aa; color: #1d8348; }
        .status-rampage  { background: #e74c3c; color: #fff;    }

        /* Écrans */
        #player-light-screen, #opponent-light-screen,
        #player-reflect, #opponent-reflect {
            display: none;
            font-size: 0.7rem;
            padding: 2px 6px;
            border-radius: 4px;
            margin: 1px;
            font-weight: 600;
        }
        #player-light-screen, #opponent-light-screen {
            background: #d6eaf8; color: #154360;
        }
        #player-reflect, #opponent-reflect {
            background: #fadbd8; color: #641e16;
        }

        /* Effet météo léger sur le fond */
        .weather-effect--sunny     { filter: brightness(1.1) saturate(1.2); }
        .weather-effect--rain      { filter: brightness(0.85) hue-rotate(180deg); }
        .weather-effect--sandstorm { filter: sepia(0.4) brightness(0.95); }
        .weather-effect--hail      { filter: brightness(0.9) hue-rotate(200deg); }
    `;
    document.head.appendChild(style);
})();