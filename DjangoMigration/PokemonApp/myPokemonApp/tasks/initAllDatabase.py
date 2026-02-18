#!/usr/bin/python3
"""
Point d'entrée unique pour initialiser une base de données Pokémon vierge.

Usage :
    python manage.py shell -c "from myPokemonApp.tasks.initAllDatabase import initAllDatabase; initAllDatabase()"

Ordre d'exécution (respecte les dépendances) :
    1. Types, Moves, Pokémon, LearnableMoves  (base de tout)
    2. Items                                   (dépend de rien)
    3. PokeballItems                           (dépend de Items)
    4. Gym Leaders, NPCs, Elite 4, Champion   (dépend de Pokémon + Moves)
    5. Zones Kanto + Spawn rates              (dépend de Pokémon)
    6. Pokémon Centers                         (dépend de Zones)
    7. Shops                                   (dépend de Items)
    8. Achievements                            (indépendant)
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
    initialize_npc_trainers,
    initialize_rival_battles,
    initialize_elite_four,
    create_champion,
)
from myPokemonApp.tasks.initPokeballItem import scriptToInitNewPokeBalls
from myPokemonApp.tasks.initKantoMaps import init_kanto_map
from myPokemonApp.tasks.initPokeCenters import scriptToInitializePokeCenters
from myPokemonApp.tasks.initShops import initShops
from myPokemonApp.tasks.initAchievments import init_achievements


# ---------------------------------------------------------------------------
# Étapes individuelles avec gestion d'erreur uniforme
# ---------------------------------------------------------------------------

def _run_step(step_num, label, fn, *args, **kwargs):
    """
    Exécute une étape d'initialisation avec logging et gestion d'erreur.
    Retourne True si succès, False si échec (sans stopper les étapes suivantes
    si stop_on_error=False).
    """
    logging.info(f"{'─'*60}")
    logging.info(f"  ÉTAPE {step_num} — {label}")
    logging.info(f"{'─'*60}")
    try:
        fn(*args, **kwargs)
        logging.info(f"  ✅ {label} — OK\n")
        return True
    except Exception as e:
        logging.error(f"  ❌ {label} — ERREUR : {e}")
        logging.debug(traceback.format_exc())
        return False


# ---------------------------------------------------------------------------
# Fonction principale
# ---------------------------------------------------------------------------

def initAllDatabase(stop_on_error=True):
    """
    Initialise une base de données Pokémon vierge dans le bon ordre.

    Args:
        stop_on_error (bool): Si True (défaut), lève une exception à la
                              première étape qui échoue. Si False, continue
                              et affiche un rapport final.

    Usage :
        from myPokemonApp.tasks.initAllDatabase import initAllDatabase
        initAllDatabase()
    """

    logging.info("=" * 60)
    logging.info("  INITIALISATION COMPLÈTE DE LA BASE POKÉMON")
    logging.info("=" * 60 + "\n")

    steps = [
        # (numéro, label, fonction, *args)
        (1,  "Types, Capacités, Pokémon Gen 1, Learnable Moves",  scriptToInitializeDatabase),
        (2,  "Objets (Potions, Balls, Pierres, etc.)",            initialize_items),
        (3,  "PokeballItems (modificateurs de capture)",          scriptToInitNewPokeBalls),
        (4,  "Champions d'Arène",                                 initialize_gym_leaders),
        (5,  "Dresseurs NPC",                                     initialize_npc_trainers),
        (6,  "Combats Rival",                                     initialize_rival_battles),
        (7,  "Conseil des 4",                                     initialize_elite_four),
        (8,  "Champion de la Ligue",                              create_champion),
        (9,  "Zones Kanto + Spawn rates",                         init_kanto_map),
        (10, "Centres Pokémon",                                   scriptToInitializePokeCenters),
        (11, "Boutiques (Pokémarts)",                             initShops),
        (12, "Succès / Achievements",                             init_achievements),
    ]

    failed_steps = []

    for step_num, label, fn, *args in steps:
        success = _run_step(step_num, label, fn, *args)

        if not success:
            if stop_on_error:
                logging.error(
                    f"\n❌ Arrêt à l'étape {step_num} — '{label}'.\n"
                    f"   Corrigez l'erreur et relancez initAllDatabase().\n"
                    f"   (Astuce : les étapes utilisent get_or_create,\n"
                    f"    vous pouvez relancer sans risquer les doublons.)"
                )
                raise RuntimeError(f"initAllDatabase() échouée à l'étape {step_num} : {label}")
            else:
                failed_steps.append((step_num, label))

    # Rapport final
    logging.info("=" * 60)
    if failed_steps:
        logging.warning(f"  ⚠️  INITIALISATION TERMINÉE AVEC {len(failed_steps)} ERREUR(S)")
        for n, lbl in failed_steps:
            logging.warning(f"      - Étape {n} : {lbl}")
    else:
        logging.info("  ✅  INITIALISATION TERMINÉE AVEC SUCCÈS")
    logging.info("=" * 60)


# ---------------------------------------------------------------------------
# Point d'entrée direct (python manage.py shell -c "...")
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    initAllDatabase()