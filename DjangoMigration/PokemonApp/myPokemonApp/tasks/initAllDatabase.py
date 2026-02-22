#!/usr/bin/python3
"""
Point d'entrée unique pour initialiser une base de données Pokémon vierge.

Usage :
    python manage.py shell -c "from myPokemonApp.tasks.initAllDatabase import initAllDatabase; initAllDatabase()"

Ordre d'exécution (respecte les dépendances) :
    1.  Types, Moves, Pokémon Gen 1                 (base de tout — SANS learnsets)
    2.  Moves Gen 3 manquants                        (Aerial Ace, Blaze Kick, etc.)
    3.  Learnsets Gen 3 (FireRed/LeafGreen)          (remplace les niveaux Gen 1)
    4.  Items                                        (dépend de rien)
    5.  PokeballItems                                (dépend de Items)
    6.  Champions d'Arène                            (dépend de Pokémon + Moves)
    7.  Dresseurs NPC de base                        (initializeItemsAndNpcs)
    8.  Dresseurs NPC complets Kanto                 (initNPCTrainersComplete)
    9.  Combats Rival                                (dépend de Pokémon + Moves)
    10. Conseil des 4                                (dépend de Pokémon + Moves)
    11. Champion de la Ligue                         (dépend de Pokémon + Moves)
    12. Zones Kanto + Spawn rates                    (dépend de Pokémon)
    13. Centres Pokémon                              (dépend de Zones)
    14. Boutiques (Pokémarts)                        (dépend de Items)
    15. Succès / Achievements                        (indépendant)
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

# ── Anciens scripts (mis à jour) ───────────────────────────────────────────
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

# ── Nouveaux scripts Gen 3 ─────────────────────────────────────────────────
from myPokemonApp.tasks.initMovesGen9 import add_missing_gen9_moves
from myPokemonApp.tasks.initLearnableMovesGen9 import update_learnable_moves_gen9
from myPokemonApp.tasks.initNPCTrainersComplete import run_complete_npc_initialization


# ---------------------------------------------------------------------------
# Étapes individuelles avec gestion d'erreur uniforme
# ---------------------------------------------------------------------------

def _run_step(step_num, label, fn, *args, **kwargs):
    """
    Exécute une étape d'initialisation avec logging et gestion d'erreur.
    Retourne True si succès, False si échec.
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
        # ── SOCLE ─────────────────────────────────────────────────────────────
        # scriptToInitializeDatabase ne génère PLUS les learnsets (étape 3).
        (1,  "Types, Capacités, Pokémon Gen 1",
             scriptToInitializeDatabase),

        # ── MOVES GEN 3 ───────────────────────────────────────────────────────
        # Doit tourner AVANT les learnsets pour que les moves existent en base.
        (2,  "Moves Gen 9 manquants (Aerial Ace, Blaze Kick, Discharge…)",
             add_missing_gen9_moves),

        # ── LEARNSETS GEN 9 ────────────────────────────────────────────
        # True = clear_existing : vide les anciens learnsets avant recréation.
        (3,  "Learnsets Gen 9",
             update_learnable_moves_gen9, True),

        # ── ITEMS ─────────────────────────────────────────────────────────────
        (4,  "Objets (Potions, Balls, Pierres, etc.)",
             initialize_items),
        (5,  "PokeballItems (modificateurs de capture)",
             scriptToInitNewPokeBalls),

        # ── DRESSEURS & LEADERS ───────────────────────────────────────────────
        (6,  "Champions d'Arène",
             initialize_gym_leaders),

        # NPCs de base : Bourg-Palette, Mt. Moon, Grotte Azurée, quelques routes.
        (7,  "Dresseurs NPC de base",
             initialize_npc_trainers),

        # NPCs complets : toutes les routes de Kanto, Centrale électrique,
        # Tour Pokémon, S.S. Anne, Îles Écume, Silph Co., etc. (FRLG).
        (8,  "Dresseurs NPC complets — Toutes zones Kanto",
             run_complete_npc_initialization),

        (9,  "Combats Rival",
             initialize_rival_battles),
        (10, "Conseil des 4",
             initialize_elite_four),
        (11, "Champion de la Ligue",
             create_champion),

        # ── MONDE ─────────────────────────────────────────────────────────────
        (12, "Zones Kanto + Spawn rates",
             init_kanto_map),
        (13, "Centres Pokémon",
             scriptToInitializePokeCenters),
        (14, "Boutiques (Pokémarts)",
             initShops),

        # ── SUCCÈS ────────────────────────────────────────────────────────────
        (15, "Succès / Achievements",
             init_achievements),
    ]

    failed_steps = []

    for entry in steps:
        step_num, label, fn = entry[0], entry[1], entry[2]
        extra_args = entry[3:]
        success = _run_step(step_num, label, fn, *extra_args)

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