#!/usr/bin/python3
"""
Point d'entrée unique pour initialiser une base de données Pokémon vierge.

Usage recommandé (management command) :
    python manage.py init_db
    python manage.py init_db --step 12
    python manage.py init_db --from-step 10
    python manage.py init_db --list

Ordre d'exécution (respecte les dépendances) :
    1.  Types, Moves, Pokémon Gen 1                 (base de tout — SANS learnsets)
    2.  Moves Gen 9 manquants                       (Aerial Ace, Blaze Kick, etc.)
    3.  Learnsets Gen 9 (FireRed/LeafGreen)         (remplace les niveaux Gen 1)
    4.  Items                                       (dépend de rien)
    5.  PokeballItems (modificateurs de capture)    (dépend de Items)
    6.  Champions d'Arène                           (dépend de Pokémon + Moves)
    8.  Dresseurs NPC complets Kanto                (initNPCTrainersComplete)
    9.  Combats Rival                               (dépend de Pokémon + Moves)
    10. Conseil des 4                               (dépend de Pokémon + Moves)
    11. Champion de la Ligue                        (dépend de Pokémon + Moves)
    12. Zones Kanto + Spawn rates                   (dépend de Pokémon)
    13. Centres Pokémon                             (dépend de Zones)
    14. Boutiques (Pokémarts)                       (dépend de Items)
    15. Succès / Achievements                       (indépendant)
    16. Quêtes                                      (dépend de Zones)
    17. Held Items                                  (dépend de Items)
    18. Zone Musics                                 (dépend de Zones)
    19. CS & CT (TM & HM)                           (dépend de Moves)
"""

import logging
import traceback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

# ---------------------------------------------------------------------------
# Imports des fonctions d'initialisation
# ---------------------------------------------------------------------------

from myPokemonApp.tasks.initializeDatabase import scriptToInitializeDatabase
from myPokemonApp.tasks.initializeItemsAndNpcs import (
    initialize_items,
    initialize_gym_leaders,
    initialize_rival_battles,
    initialize_elite_four,
    create_champion,
)
from myPokemonApp.tasks.initPokeballItem import scriptToInitNewPokeBalls
from myPokemonApp.tasks.initKantoMaps import init_kanto_map
from myPokemonApp.tasks.initPokeCenters import scriptToInitializePokeCenters
from myPokemonApp.tasks.initShops import initShops
from myPokemonApp.tasks.initAchievments import init_achievements
from myPokemonApp.tasks.initHeldItems import initHeldItems
from myPokemonApp.tasks.initZoneMusic import init_zone_music
from myPokemonApp.tasks.initQuests import init_all_quests
from myPokemonApp.tasks.InitTMsandCS import runCSAndTM
from myPokemonApp.tasks.initMovesGen9 import add_missing_gen9_moves
from myPokemonApp.tasks.initLearnableMovesGen9 import update_learnable_moves_gen9
from myPokemonApp.tasks.initNPCTrainersComplete import run_complete_npc_initialization
from myPokemonApp.tasks.initGymZones import run_gym_initialization


# ---------------------------------------------------------------------------
# Liste des étapes (exportée pour que la management command puisse l'afficher)
# ---------------------------------------------------------------------------

STEPS = [
    (1,  "Types, Capacités, Pokémon Gen 1",                   scriptToInitializeDatabase),
    (2,  "Moves Gen 9 manquants (Aerial Ace, Blaze Kick…)",   add_missing_gen9_moves),
    (3,  "Learnsets Gen 9",                                   update_learnable_moves_gen9, True),
    (4,  "Objets (Potions, Balls, Pierres, etc.)",            initialize_items),
    (5,  "PokeballItems (modificateurs de capture)",          scriptToInitNewPokeBalls),
    (6,  "Champions d'Arène",                                 initialize_gym_leaders),
    (8,  "Dresseurs NPC complets — Toutes zones Kanto",       run_complete_npc_initialization),
    (9,  "Combats Rival",                                     initialize_rival_battles),
    (10, "Conseil des 4",                                     initialize_elite_four),
    (11, "Champion de la Ligue",                              create_champion),
    (12, "Zones Kanto + Spawn rates",                         init_kanto_map),
    (13, "Centres Pokémon",                                   scriptToInitializePokeCenters),
    (14, "Boutiques (Pokémarts)",                             initShops),
    (15, "Succès / Achievements",                             init_achievements),
    (16, "Quêtes",                                            init_all_quests),
    (17, "Held Items",                                        initHeldItems),
    (18, "Zone Musics",                                       init_zone_music),
    (19, "CS & CT",                                           runCSAndTM),
    (20, "Gym Zones",                                         run_gym_initialization),
]


# ---------------------------------------------------------------------------
# Étapes individuelles avec gestion d'erreur uniforme
# ---------------------------------------------------------------------------

def _run_step(step_num, label, fn, *args, stdout=None, **kwargs):
    """
    Exécute une étape d'initialisation avec logging et gestion d'erreur.
    Retourne True si succès, False si échec.

    stdout : objet BaseCommand (management command) ou None (logging standard).
    """
    sep = '─' * 60
    _log(stdout, sep)
    _log(stdout, f"  ÉTAPE {step_num} — {label}")
    _log(stdout, sep)
    try:
        fn(*args, **kwargs)
        _log(stdout, f"  ✅ {label} — OK\n", success=True)
        return True
    except Exception as e:
        _log(stdout, f"  ❌ {label} — ERREUR : {e}", error=True)
        logging.debug(traceback.format_exc())
        return False


def _log(stdout, msg, success=False, error=False):
    """Log vers management command stdout ou logging standard."""
    if stdout is not None:
        if error:
            stdout.stderr.write(stdout.style.ERROR(msg))
        elif success:
            stdout.stdout.write(stdout.style.SUCCESS(msg))
        else:
            stdout.stdout.write(msg)
    else:
        if error:
            logging.error(msg)
        else:
            logging.info(msg)


# ---------------------------------------------------------------------------
# Fonction principale
# ---------------------------------------------------------------------------

def initAllDatabase(stop_on_error=True, step_filter=None, stdout=None):
    """
    Initialise une base de données Pokémon vierge dans le bon ordre.

    Args:
        stop_on_error (bool):  Si True (défaut), lève une exception à la
                               première étape qui échoue.
        step_filter (callable|None): Fonction (step_num) -> bool.
                               Si None, toutes les étapes sont exécutées.
        stdout:                Objet BaseCommand pour output coloré depuis
                               la management command. None = logging standard.
    """
    _log(stdout, "=" * 60)
    _log(stdout, "  INITIALISATION COMPLÈTE DE LA BASE POKÉMON")
    _log(stdout, "=" * 60 + "\n")

    failed_steps = []

    for entry in STEPS:
        step_num, label, fn = entry[0], entry[1], entry[2]
        extra_args = entry[3:]

        # Filtrage optionnel des étapes
        if step_filter is not None and not step_filter(step_num):
            continue

        success = _run_step(step_num, label, fn, *extra_args, stdout=stdout)

        if not success:
            if stop_on_error:
                raise RuntimeError(
                    f"initAllDatabase() échouée à l'étape {step_num} : {label}\n"
                    f"Corrigez l'erreur et relancez avec --from-step {step_num}"
                )
            else:
                failed_steps.append((step_num, label))

    # Rapport final
    _log(stdout, "=" * 60)
    if failed_steps:
        _log(stdout, f"  ⚠️  TERMINÉ AVEC {len(failed_steps)} ERREUR(S) :", error=True)
        for n, lbl in failed_steps:
            _log(stdout, f"      - Étape {n} : {lbl}", error=True)
    else:
        _log(stdout, "  ✅  INITIALISATION TERMINÉE AVEC SUCCÈS", success=True)
    _log(stdout, "=" * 60)


# ---------------------------------------------------------------------------
# Point d'entrée direct (legacy)
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    initAllDatabase()