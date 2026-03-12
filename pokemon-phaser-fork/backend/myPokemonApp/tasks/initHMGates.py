"""
initHMGates.py
==============
Configure les portes CS (Hidden Machines) sur les zones et connexions de Kanto.

Canonique Gen 1 :
  CS01 Coupe    — Arbres bloquant certains passages (Forêt de Jade, Route 2 sud,
                  Cave Taupiqueur, Île Nuptiale)
  CS02 Vol      — Aucun blocage de connexion (Vol = déplacement libre entre villes)
  CS03 Surf     — Toutes les routes/zones aquatiques (Route 19, 20, 21,
                  Île Nuptiale, Îles Écume, Zone Safari eau, Grottes Inconnues accès eau)
  CS04 Force    — Rochers dans Mont Sélénite, Chemin de la Victoire, Îles Écume
  CS05 Flash    — Tunnel Roche (optionnel, facilite la navigation)

Stratégie :
  1. Zone.required_hm   → la zone ENTIÈRE nécessite la CS pour être accessible
  2. ZoneConnection.required_hm → le PASSAGE entre deux zones nécessite la CS

Exécution :
    python manage.py shell -c "from myPokemonApp.tasks.initHMGates import init_hm_gates; init_hm_gates()"
"""

import logging
from myPokemonApp.models import Zone, ZoneConnection

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(message)s')


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _zone(name: str):
    """Retourne la Zone par nom exact, ou None avec warning."""
    z = Zone.objects.filter(name=name).first()
    if not z:
        logger.warning(f"  ⚠️  Zone introuvable : « {name} »")
    return z


def _set_zone_hm(zone_name: str, hm: str):
    """
    Définit Zone.required_hm pour accéder à cette zone entière.
    Met toujours à jour même si déjà configuré.
    """
    z = _zone(zone_name)
    if not z:
        return
    old = z.required_hm
    z.required_hm = hm
    z.save(update_fields=['required_hm'])
    mark = '✅' if not old else ('⭕' if old == hm else '🔄')
    logger.info(f"  {mark} Zone [{hm.upper():8}] {zone_name}")


def _set_conn_hm(from_name: str, to_name: str, hm: str, message: str = '',
                 bidirectional: bool = True):
    """
    Définit ZoneConnection.required_hm sur la connexion from→to.
    Crée la connexion si elle n'existe pas encore.
    Met toujours à jour les champs même si la connexion existe déjà.
    """
    from_z = _zone(from_name)
    to_z   = _zone(to_name)
    if not from_z or not to_z:
        return

    # Chercher dans les deux sens si bidirectionnel
    conn = ZoneConnection.objects.filter(from_zone=from_z, to_zone=to_z).first()
    if not conn and bidirectional:
        conn = ZoneConnection.objects.filter(from_zone=to_z, to_zone=from_z).first()

    if conn:
        created = False
    else:
        conn, created = ZoneConnection.objects.get_or_create(
            from_zone=from_z, to_zone=to_z,
            defaults={
                'is_bidirectional': bidirectional,
                'required_hm': hm,
                'passage_message': message,
            }
        )

    if not created:
        conn.required_hm      = hm
        conn.is_bidirectional = bidirectional
        if message:
            conn.passage_message = message
        conn.save(update_fields=['required_hm', 'is_bidirectional', 'passage_message'])

    mark = '✅' if created else '⭕'
    arrow = '↔' if bidirectional else '→'
    logger.info(f"  {mark} Connexion [{hm.upper():8}] {from_name} {arrow} {to_name}")


def _clear_zone_hm(zone_name: str):
    """Retire le required_hm d'une zone (remet à '')."""
    z = _zone(zone_name)
    if not z:
        return
    if z.required_hm:
        z.required_hm = ''
        z.save(update_fields=['required_hm'])
        logger.info(f"  🔓 Zone [LIBRE   ] {zone_name}")


def _clear_conn_hm(from_name: str, to_name: str):
    """Retire le required_hm d'une connexion."""
    from_z = _zone(from_name)
    to_z   = _zone(to_name)
    if not from_z or not to_z:
        return
    conn = ZoneConnection.objects.filter(from_zone=from_z, to_zone=to_z).first()
    if not conn:
        conn = ZoneConnection.objects.filter(from_zone=to_z, to_zone=from_z).first()
    if conn and conn.required_hm:
        conn.required_hm = ''
        conn.passage_message = ''
        conn.save(update_fields=['required_hm', 'passage_message'])
        logger.info(f"  🔓 Connexion [LIBRE   ] {from_name} ↔ {to_name}")


# ─────────────────────────────────────────────────────────────────────────────
# SCRIPT PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def init_hm_gates():
    """
    Configure toutes les portes CS de Kanto Gen 1.
    Idempotent : peut être relancé sans risque.
    """

    logger.info("\n" + "═" * 60)
    logger.info("🔑  Initialisation des portes CS — Kanto Gen 1")
    logger.info("═" * 60)

    # =========================================================================
    # CS01 COUPE — Arbres bloquants
    # =========================================================================
    logger.info("\n🌳  CS01 COUPE — Arbres bloquants")
    logger.info("-" * 40)

    # ── Route 2 / Forêt de Jade ───────────────────────────────────────────────
    # Le chemin principal est : Bourg Palette → Route 1 → Jadielle → Route 2 → Forêt de Jade → Argenta.
    # L'arbre Coupe canonique sur Route 2 est le RACCOURCI entre la sortie
    # nord de Cave Taupiqueur et Jadielle (contournement de la Forêt).
    _clear_conn_hm('Route 2', 'Forêt de Jade')

    # Cave Taupiqueur : entrée bloquée par un arbre (déjà partiellement configuré)
    _set_conn_hm(
        'Carmin sur Mer', 'Cave Taupiqueur', 'cut',
        message="Un arbuste épais bloque l'entrée de la Cave Taupiqueur. CS01 Coupe est requise.",
    )
    # Sortie côté Route 2 également
    _set_conn_hm(
        'Cave Taupiqueur', 'Route 2', 'cut',
        message="Un arbuste épais bloque la sortie de la Cave Taupiqueur. CS01 Coupe est requise.",
        bidirectional=False,  # sens unique : on sort vers Route 2
    )

    # Île Nuptiale : petit arbre à l'intérieur de l'île
    _set_conn_hm(
        'Route 24', 'Île Nuptiale', 'cut',
        message="Un arbuste épais bloque le chemin vers l'Île Nuptiale. CS01 Coupe est requise.",
    )

    # =========================================================================
    # CS03 SURF — Zones et connexions aquatiques
    # =========================================================================
    logger.info("\n🌊  CS03 SURF — Zones et connexions aquatiques")
    logger.info("-" * 40)

    # ── Zones entières (type 'water') nécessitent Surf pour y accéder ─────────
    _set_zone_hm('Route 19', 'surf')   # Parmanie → Îles Écume
    _set_zone_hm('Route 20', 'surf')   # Îles Écume → Cramois'Île
    _set_zone_hm('Route 21', 'surf')   # Cramois'Île → Bourg Palette

    # ── Connexions aquatiques (passage en mer) ────────────────────────────────
    _set_conn_hm(
        'Parmanie', 'Route 19', 'surf',
        message="Il faut Surfer pour traverser la Route 19. CS03 Surf est requise.",
    )
    _set_conn_hm(
        'Route 19', 'Îles Écume', 'surf',
        message="Il faut Surfer pour atteindre les Îles Écume. CS03 Surf est requise.",
    )
    _set_conn_hm(
        'Îles Écume', 'Route 20', 'surf',
        message="Il faut Surfer pour traverser la Route 20. CS03 Surf est requise.",
    )
    _set_conn_hm(
        'Route 20', "Cramois'Île", 'surf',
        message="Il faut Surfer pour atteindre Cramois'Île. CS03 Surf est requise.",
    )
    _set_conn_hm(
        "Cramois'Île", 'Route 21', 'surf',
        message="Il faut Surfer pour rejoindre la Route 21. CS03 Surf est requise.",
    )
    _set_conn_hm(
        'Route 21', 'Bourg Palette', 'surf',
        message="Il faut Surfer pour rejoindre Bourg Palette par la mer. CS03 Surf est requise.",
    )

    # Accès à l'Île Nuptiale (surf depuis Route 24/25)
    # L'Île Nuptiale est entourée d'eau → Surf requis pour y accéder
    _set_zone_hm("Île Nuptiale", 'surf')

    # Accès Azuria → Grottes Inconnues : en Gen 1 on surf depuis Azuria
    _set_conn_hm(
        'Azuria', 'Grottes Inconnues', 'surf',
        message="Il faut Surfer depuis Azuria pour atteindre les Grottes Inconnues. CS03 Surf est requise.",
    )

    # =========================================================================
    # CS04 FORCE — Rochers poussables
    # =========================================================================
    logger.info("\n💪  CS04 FORCE — Rochers poussables")
    logger.info("-" * 40)

    # Mont Sélénite : les rochers intérieurs bloquent certains passages.
    # En Gen 1, Force est optionnel pour traverser (on peut contourner),
    # mais on bloque le passage DIRECT (étages profonds).
    # On applique Force sur la Zone entière pour simuler l'accès aux zones profondes.
    # (Si vous avez un système de floors, appliquez-le à l'étage B2F+)
    _set_zone_hm('Mont Sélénite', 'strength')

    # Îles Écume : Force nécessaire pour pousser les rochers et accéder au bas des grottes
    _set_zone_hm('Îles Écume', 'strength')

    # Chemin de la Victoire : Force requise pour traverser
    _set_zone_hm('Chemin de la Victoire', 'strength')

    # =========================================================================
    # CS05 FLASH — Tunnel sombre
    # =========================================================================
    logger.info("\n💡  CS05 FLASH — Zones sombres (optionnel)")
    logger.info("-" * 40)

    # Tunnel Roche : en Gen 1, Flash n'est pas obligatoire mais simplifie la navigation.
    # On laisse la zone accessible SANS Flash, mais on note la recommandation
    # en configurant les connexions uniquement si vous voulez le rendre obligatoire.
    # ⚠️ Décommentez les lignes ci-dessous pour rendre Flash OBLIGATOIRE :

    # _set_conn_hm(
    #     'Route 9', 'Tunnel Roche', 'flash',
    #     message="Le Tunnel Roche est plongé dans l'obscurité. CS05 Flash est vivement recommandé.",
    # )

    logger.info("  ℹ️  Flash : non obligatoire (décommentez dans le script pour l'activer)")

    # =========================================================================
    # NETTOYAGE — Retirer les required_hm incorrects ou obsolètes
    # =========================================================================
    logger.info("\n🧹  Nettoyage des gates obsolètes")
    logger.info("-" * 40)

    # Ces zones/connexions ne nécessitent PAS de CS en Gen 1
    zones_to_clear = [
        'Route 1', 'Route 2', 'Route 3', 'Route 4',
        'Route 5', 'Route 6', 'Route 7', 'Route 8',
        'Route 9', 'Route 10', 'Route 11', 'Route 12',
        'Route 13', 'Route 14', 'Route 15', 'Route 16', 'Route 17', 'Route 18',
        'Route 22', 'Route 23', 'Route 24', 'Route 25',
        'Forêt de Jade',          # zone accessible sans CS (connexion bloquée, pas la zone)
        'Bourg Palette', 'Jadielle', 'Argenta', 'Azuria',
        'Carmin sur Mer', 'Lavanville', 'Safrania', 'Céladopole',
        'Parmanie', "Cramois'Île", 'Plateau Indigo',
        'Tour Pokémon', 'Zone Safari',
        'Tunnel Roche',            # pas de Flash obligatoire
        'Centrale', 'Cave Taupiqueur',
        'Grottes Inconnues',       # accès par Surf (connexion), la zone en elle-même = libre
    ]
    for z_name in zones_to_clear:
        z = Zone.objects.filter(name=z_name).first()
        if z and z.required_hm:
            z.required_hm = ''
            z.save(update_fields=['required_hm'])
            logger.info(f"  🔓 Zone [LIBRE   ] {z_name}")

    # =========================================================================
    # RONFLEX — Blocages par Poké Flûte (required_flag sur ZoneConnection)
    # =========================================================================
    # Route 12 : Lavanville ↔ Route 12  (Ronflex bloque la descente vers Parmanie)
    # Route 16 : Céladopole ↔ Route 16  (Ronflex bloque l'accès à la Route du Vélo)
    # Strategy : on stocke le flag dans passage_message via un préfixe spécial
    # MAIS le ZoneConnection.required_flag est le champ canonique.
    logger.info("\n😴  RONFLEX — Portes Poké Flûte")
    logger.info("-" * 40)

    _SNORLAX_CONNS = [
        ('Lavanville',   'Route 12', 'snorlax_route12_awakened',
         "Un Ronflex endormi barre la Route 12. Jouez de la Poké Flûte pour le réveiller."),
        ('Céladopole',   'Route 16', 'snorlax_route16_awakened',
         "Un Ronflex endormi barre la Route du Vélo. Jouez de la Poké Flûte pour le réveiller."),
    ]

    for from_name, to_name, flag, msg in _SNORLAX_CONNS:
        from_z = _zone(from_name)
        to_z   = _zone(to_name)
        if not from_z or not to_z:
            continue
        conn = ZoneConnection.objects.filter(from_zone=from_z, to_zone=to_z).first()
        if not conn:
            conn = ZoneConnection.objects.filter(from_zone=to_z, to_zone=from_z).first()
        if not conn:
            conn, _ = ZoneConnection.objects.get_or_create(
                from_zone=from_z, to_zone=to_z,
                defaults={'is_bidirectional': True}
            )
        conn.required_flag   = flag
        conn.passage_message = msg
        conn.save(update_fields=['required_flag', 'passage_message'])
        logger.info(f"  😴 Ronflex [{flag}] {from_name} ↔ {to_name}")

    # =========================================================================
    # RAPPORT FINAL
    # =========================================================================
    logger.info("\n" + "═" * 60)
    logger.info("📊  BILAN DES GATES CONFIGURÉES")
    logger.info("═" * 60)

    # Zones avec required_hm
    zones_with_hm = Zone.objects.exclude(required_hm='').order_by('required_hm', 'name')
    if zones_with_hm.exists():
        logger.info("\n🗺️  Zones bloquées par CS :")
        for z in zones_with_hm:
            hm_label = {
                'cut': 'CS01 Coupe', 'fly': 'CS02 Vol', 'surf': 'CS03 Surf',
                'strength': 'CS04 Force', 'flash': 'CS05 Flash',
            }.get(z.required_hm, z.required_hm)
            logger.info(f"    [{hm_label}] {z.name}")

    # Connexions avec required_hm
    conns_with_hm = ZoneConnection.objects.exclude(required_hm='').select_related(
        'from_zone', 'to_zone'
    ).order_by('required_hm', 'from_zone__name')
    if conns_with_hm.exists():
        logger.info("\n🔗  Connexions bloquées par CS :")
        for c in conns_with_hm:
            hm_label = {
                'cut': 'CS01 Coupe', 'fly': 'CS02 Vol', 'surf': 'CS03 Surf',
                'strength': 'CS04 Force', 'flash': 'CS05 Flash',
            }.get(c.required_hm, c.required_hm)
            arrow = '↔' if c.is_bidirectional else '→'
            logger.info(f"    [{hm_label}] {c.from_zone.name} {arrow} {c.to_zone.name}")

    total_zones = zones_with_hm.count()
    total_conns = conns_with_hm.count()
    logger.info(f"\n✅  {total_zones} zone(s) + {total_conns} connexion(s) configurées avec CS")
    logger.info("═" * 60 + "\n")