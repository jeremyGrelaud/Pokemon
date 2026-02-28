"""
initZoneMusic.py
================
Peuple le champ `Zone.music` avec les noms de fichiers normalisés
de la Kanto Soundtrack 2004.

Les fichiers audio doivent être placés dans :
    static/sounds/bgm/kanto/<nom_normalise>.mp3

Après avoir renommé les fichiers avec rename_kanto_soundtrack.py,
exécutez ce script depuis le shell Django :
    python manage.py shell < initZoneMusic.py

Ou importez la fonction dans initAllDatabase.py :
    from myPokemonApp.tasks.initZoneMusic import init_zone_music
    init_zone_music()
"""

import logging
from myPokemonApp.models import Zone

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapping  zone.name  →  nom du fichier (sans extension) dans bgm/kanto/
#
# Convention : les fichiers sont dans  static/sounds/bgm/kanto/
# Le champ Zone.music stocke uniquement le nom relatif à ce dossier,
# ex : "route_1" → le lecteur chargera /static/sounds/bgm/kanto/route_1.mp3
# ---------------------------------------------------------------------------

ZONE_MUSIC = {
    # ── Villes ───────────────────────────────────────────────────────────────
    'Bourg Palette':   'pallet_town',           # 06
    'Jadielle':        'pewter_city',            # 15  (town 1 = Viridian → Pewter style)
    'Argenta':         'pewter_city',            # 15
    'Azuria':          'cerulean_city',          # 33
    'Carmin sur Mer':  'vermillion_city',        # 35
    'Lavanville':      'lavender_town',          # 37
    'Safrania':        'celadon_city',           # 38  (Saffron partage la musique de Celadon dans FRLG)
    'Céladopole':      'celadon_city',           # 38
    'Parmanie':        'vermillion_city',        # 35  (Fuchsia n'a pas de thème distinct dans FRLG)
    "Cramois'Île":     'cinnabar_island',        # 55
    'Plateau Indigo':  'indigo_plateau',         # 62

    # ── Routes ───────────────────────────────────────────────────────────────
    'Route 1':   'route_1',     # 13
    'Route 2':   'route_1',     # 13  (Route 2 partage le thème de Route 1)
    'Route 3':   'route_1',
    'Route 4':   'route_1',
    'Route 5':   'route_11',    # 48  (Routes Ouest partage Route 11)
    'Route 6':   'route_11',
    'Route 7':   'route_11',
    'Route 8':   'route_11',
    'Route 9':   'route_11',
    'Route 10':  'route_11',
    'Route 11':  'route_11',    # 48
    'Route 12':  'route_11',
    'Route 13':  'route_11',
    'Route 14':  'route_11',
    'Route 15':  'route_11',
    'Route 16':  'cycling',     # 34  (Route du Vélo)
    'Route 17':  'cycling',     # 34
    'Route 18':  'route_11',
    'Route 21':  'route_11',
    'Route 22':  'route_1',
    'Route 23':  'route_11',
    'Route 24':  'route_1',
    'Route 25':  'route_1',

    # ── Zones spéciales ──────────────────────────────────────────────────────
    'Forêt de Jade':       'viridian_forest',           # 17
    'Mont Sélénite':       'the_caves_of_mt_moon',      # 32
    'Tunnel Roche':        'the_caves_of_mt_moon',      # 32
    'Tour Pokémon':        'pokemon_tower',              # 47
    'Zone Safari':         'route_11',
    'Îles Écume':          'the_caves_of_mt_moon',      # 32
    'Centrale':            'team_rocket_hideout',       # 43  (ambiance industrielle similaire)
    'Grottes Inconnues':   'the_caves_of_mt_moon',      # 32
    'Chemin de la Victoire': 'the_caves_of_mt_moon',    # 32
    'Cave Taupiqueur':       'the_caves_of_mt_moon',    # 32 (grotte, même ambiance)
    'Île Nuptiale':          'route_1',                 # ambiance douce Route 1

    # ── Surf ─────────────────────────────────────────────────────────────────
    # Pas de zone "Surf" distincte dans le modèle, mais on peut ajouter ici
    # si une zone "Mer" est créée plus tard :
    # 'Mer':  'surfing',    # 52
}


def init_zone_music():
    """Met à jour le champ music de chaque Zone selon ZONE_MUSIC."""
    updated = 0
    missing = []

    for zone_name, track in ZONE_MUSIC.items():
        count = Zone.objects.filter(name=zone_name).update(music=track)
        if count:
            updated += count
            logger.info(f"  ✅  {zone_name}  →  {track}")
        else:
            missing.append(zone_name)

    logger.info(f"\n🎵  {updated} zones mises à jour.")
    if missing:
        logger.warning(f"⚠️   Zones introuvables (ignorées) :")
        for z in missing:
            logger.warning(f"     • {z}")


# ---------------------------------------------------------------------------
# Exécution directe via  python manage.py shell < initZoneMusic.py
# ---------------------------------------------------------------------------
if __name__ == '__main__' or True:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    init_zone_music()