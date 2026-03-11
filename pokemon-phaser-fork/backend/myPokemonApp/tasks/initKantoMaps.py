"""
Initialise la carte complète de Kanto Gen 1
Toutes les villes, routes, grottes et zones spéciales avec leurs spawns canoniques.
"""

from myPokemonApp.models import Zone, ZoneConnection, WildPokemonSpawn, Pokemon
import logging

logging.basicConfig(level=logging.INFO)

def _get_pokemon(name):
    """Helper : retourne le Pokémon par nom (insensible à la casse), ou None."""
    return Pokemon.objects.filter(name__iexact=name).first()


def _add_spawns(zone, spawns, encounter_type='grass'):
    """
    Helper : crée les WildPokemonSpawn pour une zone.
    spawns = [(nom_pokemon, spawn_rate%, level_min, level_max), ...]
    """
    for poke_name, rate, lv_min, lv_max in spawns:
        pokemon = _get_pokemon(poke_name)
        if pokemon:
            WildPokemonSpawn.objects.get_or_create(
                zone=zone,
                pokemon=pokemon,
                encounter_type=encounter_type,
                defaults={
                    'spawn_rate': rate,
                    'level_min': lv_min,
                    'level_max': lv_max,
                }
            )
        else:
            logging.warning(f"[!] Pokémon introuvable : {poke_name}")


def init_kanto_map():
    """Crée toutes les zones de Kanto Gen 1 avec connexions et spawn rates."""

    logging.info("🗺️  Initialisation de la carte Kanto (Gen 1)...")

    # =========================================================================
    # 1. DÉFINITION DES ZONES
    #    (name, zone_type, description, order, level_min, level_max, flags)
    # =========================================================================

    zones_data = [

        # ── VILLES ────────────────────────────────────────────────────────────
        ('Bourg Palette',  'city',   'Ville natale du joueur. Petit village paisible.',              1,  1,  5,  True,  True,  False),
        ('Jadielle',       'city',   'Première ville. Une boutique s\'ouvre après la livraison.',    3,  3,  6,  True,  True,  True ),
        ('Argenta',        'city',   'Ville du premier Champion d\'Arène (Pierre, type Roche).',     7,  8, 12,  True,  True,  True ),
        ('Azuria',         'city',   'Grande ville au bord du lac (Ondine, type Eau).',             11, 18, 21,  True,  True,  True ),
        ('Carmin sur Mer', 'city',   'Port animé (Capitaine, type Électrique).',                   16, 20, 25,  True,  True,  True ),
        ('Lavanville',     'city',   'Ville hantée avec sa célèbre Tour Pokémon.',                 20, 25, 28,  True,  True,  True ),
        ('Safrania',       'city',   'Grande métropole (Morgane, type Psy).',                      24, 35, 42,  True,  True,  True ),
        ('Céladopole',     'city',   'Ville du Grand Magasin (Olga, type Plante).',                22, 30, 35,  True,  True,  True ),
        ('Parmanie',        'city',   'Ville du Zoo Safari (Stella, type Poison).',                 28, 40, 46,  True,  True,  True ),
        ("Cramois'Île",    'city',   'Île volcanique (Pyro, type Feu).',                           34, 45, 50,  True,  True,  True ),
        ('Plateau Indigo', 'city',   'Siège de la Ligue Pokémon. Terminus du voyage.',             38, 50, 55,  True,  True,  True ),

        # ── ROUTES ────────────────────────────────────────────────────────────
        ('Route 1',  'route', 'Entre Bourg Palette et Jadielle.',             2,  2,  4,  False, False, False),
        ('Route 2',  'route', 'Entre Jadielle et la Forêt de Jade.',          4,  3,  5,  False, False, False),
        ('Route 3',  'route', 'Entre Argenta et le Mont Sélénite.',           8,  6, 10,  False, False, False),
        ('Route 4',  'route', 'Entre Mont Sélénite et Azuria.',              10, 10, 14,  False, False, False),
        ('Route 5',  'route', 'Entre Azuria et le souterrain de Safrania.',  21, 13, 17,  False, False, False),
        ('Route 6',  'route', 'Entre Safrania et Carmin sur Mer.',           17, 13, 17,  False, False, False),
        ('Route 7',  'route', 'Entre Safrania et Céladopole.',               23, 18, 22,  False, False, False),
        ('Route 8',  'route', 'Entre Safrania et Lavanville.',               21, 18, 22,  False, False, False),
        ('Route 9',  'route', 'Entre Azuria et le Tunnel Roche.',            12, 16, 20,  False, False, False),
        ('Route 10', 'route', 'Descente vers Lavanville (Centrale au nord).', 13, 18, 22,  False, False, False),
        ('Route 11', 'route', 'À l\'est de Carmin sur Mer.',                 18, 13, 17,  False, False, False),
        ('Route 12', 'route', 'Longue route côtière au sud de Lavanville.',  26, 20, 25,  False, False, False),
        ('Route 13', 'route', 'Route venteuse au sud.',                      27, 20, 25,  False, False, False),
        ('Route 14', 'route', 'Route au sud menant vers Parmanie.',           28, 20, 25,  False, False, False),
        ('Route 15', 'route', 'Relie Route 14 à Parmanie.',                   29, 22, 26,  False, False, False),
        ('Route 16', 'route', 'À l\'ouest de Céladopole, Route du Vélo.',   30, 20, 24,  False, False, False),
        ('Route 17', 'route', 'Route du Vélo — longue descente vers Parmanie.', 31, 22, 26, False, False, False),
        ('Route 18', 'route', 'Prolongement est de la Route du Vélo.',       32, 22, 26,  False, False, False),
        ('Route 21', 'route', 'Route maritime entre Cramois\'Île et Bourg Palette.', 35, 25, 35, False, False, False),
        ('Route 22', 'route', 'Entre Jadielle et les Gardes de la Ligue.',    4,  3,  5,  False, False, False),
        ('Route 23', 'route', 'Chemin vers le Plateau Indigo (8 Gardes).',   36, 35, 45,  False, False, False),
        ('Route 24', 'route', 'Au nord d\'Azuria — Pont Cerclef.',           14, 13, 16,  False, False, False),
        ('Route 25', 'route', 'Bout du Monde — laboratoire du Dr Boulmich.',  15, 13, 16,  False, False, False),

        # ── ZONES SPÉCIALES ───────────────────────────────────────────────────
        ('Forêt de Jade',       'forest',   'Forêt dense infestée de Pokémon Insecte.',                  6,  3,  6,  False, False, False),
        ('Mont Sélénite',       'cave',     'Grotte rocheuse entre Argenta et Azuria. Plusieurs étages à explorer.', 9, 8, 12, False, False, False),
        ('Tunnel Roche',        'cave',     'Grotte sombre entre la Route 9 et Route 10.',               13, 15, 20,  False, False, False),
        ('Tour Pokémon',        'building', 'Tour hantée de Lavanville, repère de Spectreux.',           19, 15, 22,  False, False, False),
        ('Zone Safari',         'route',    'Parc Safari de Parmanie — Pokémon rares à attraper.',        28, 22, 30,  True,  False, False),
        ('Îles Écume',          'cave',     'Réseau de grottes et rivières glacées, repaire d\'Artikodin.', 33, 35, 44, False, False, False),
        ('Centrale',            'building', 'Centrale électrique abandonnée entre Route 10 et 9.',       15, 22, 35,  False, False, False),
        ('Grottes Inconnues',   'cave',     'Grotte secrète au nord d\'Azuria — Mewtwo s\'y cache.',    40, 60, 70,  False, False, False),
        ('Chemin de la Victoire','cave',    'Dernière épreuve avant la Ligue Pokémon.',                  37, 40, 50,  False, False, False),
        ("Route 19",            'water',    'Route maritime entre Parmanie et les Îles Écume.',           33, 25, 35,  False, False, False),
        ("Route 20",            'water',    'Route maritime entre les Îles Écume et Cramois\'Île.',      34, 25, 35,  False, False, False),

        # ── ZONES MANQUANTES ──────────────────────────────────────────────────
        ('Cave Taupiqueur',     'cave',     'Tunnel obscur reliant Carmin sur Mer à la Route 2 sud. Infesté de Taupiqueur et Triopikeur.', 16, 15, 22, False, False, False),
        ('Île Nuptiale',        'route',    'Petite île au nord d\'Azuria — lieu romantique où vivait le Dr Boulmich avant de partir vers la Route 25.', 15, 13, 16, True, False, False),
    ]

    created_zones = {}
    for (name, ztype, desc, order, lv_min, lv_max,
         is_safe, has_center, has_shop) in zones_data:
        zone, created = Zone.objects.get_or_create(
            name=name,
            defaults={
                'zone_type': ztype,
                'description': desc,
                'order': order,
                'recommended_level_min': lv_min,
                'recommended_level_max': lv_max,
                'is_safe_zone': is_safe,
                'has_pokemon_center': has_center,
                'has_shop': has_shop,
            }
        )
        created_zones[name] = zone
        logging.info(f"  {'✅' if created else '⭕'} {name}")

    # =========================================================================
    # 2. CONNEXIONS
    # =========================================================================

    logging.info("\n🔗 Connexions...")
    connections = [
        # Axe principal Nord-Sud
        ('Bourg Palette',  'Route 1'),
        ('Route 1',        'Jadielle'),
        ('Jadielle',       'Route 2'),
        ('Route 2',        'Forêt de Jade'),
        ('Forêt de Jade',  'Argenta'),
        ('Argenta',        'Route 3'),
        ('Route 3',        'Mont Sélénite'),
        ('Mont Sélénite',  'Route 4'),
        ('Route 4',        'Azuria'),
        # Routes autour d'Azuria
        ('Azuria',         'Route 24'),
        ('Route 24',       'Route 25'),
        ('Azuria',         'Route 9'),
        ('Route 9',        'Route 10'),
        ('Route 10',       'Lavanville'),
        ('Route 10',       'Centrale'),
        # Axes depuis Carmin
        ('Azuria',         'Route 5'),
        ('Route 5',        'Safrania'),
        ('Safrania',       'Route 6'),
        ('Route 6',        'Carmin sur Mer'),
        ('Carmin sur Mer', 'Route 11'),
        ('Route 11',       'Route 12'),
        ('Route 12',       'Lavanville'),
        # Axes depuis Safrania/Céladopole
        ('Safrania',       'Route 7'),
        ('Route 7',        'Céladopole'),
        ('Safrania',       'Route 8'),
        ('Route 8',        'Lavanville'),
        # Axe Céladopole → Parmanie
        ('Céladopole',     'Route 16'),
        ('Route 16',       'Route 17'),
        ('Route 17',       'Route 18'),
        ('Route 18',       'Parmanie'),
        # Routes 13-15 sud
        ('Route 12',       'Route 13'),
        ('Route 13',       'Route 14'),
        ('Route 14',       'Route 15'),
        ('Route 15',       'Parmanie'),
        # Lavanville → Tour Pokémon
        ('Lavanville',     'Tour Pokémon'),
        # Parmanie → Zone Safari
        ('Parmanie',        'Zone Safari'),
        # Routes maritimes vers Cramois'Île
        ('Parmanie',        'Route 19'),
        ('Route 19',       'Îles Écume'),
        ('Îles Écume',     'Route 20'),
        ("Route 20",       "Cramois'Île"),
        # Cramois'Île → Bourg Palette par mer
        ("Cramois'Île",    'Route 21'),
        ('Route 21',       'Bourg Palette'),
        # Ligue
        ('Jadielle',       'Route 22'),
        # Route 22 → Route 23 : connexion gérée séparément (condition 8 badges)
        ('Route 23',       'Chemin de la Victoire'),
        ('Chemin de la Victoire', 'Plateau Indigo'),
        # Grottes Inconnues (Azuria)
        ('Azuria',         'Grottes Inconnues'),
        # Tunnel Roche
        ('Route 9',        'Tunnel Roche'),
        ('Tunnel Roche',   'Route 10'),
        # Cave Taupiqueur : relie Carmin sur Mer (Route 11) à Route 2 sud
        ('Carmin sur Mer', 'Cave Taupiqueur'),
        ('Cave Taupiqueur', 'Route 2'),
        # Île Nuptiale : accessible depuis Route 24 (surf)
        ('Route 24',       'Île Nuptiale'),
        # Bâtiments principaux (créés par initQuests.init_extra_zones)
        ("Carmin sur Mer", 'SS Anne'),
        ("Céladopole",     'Quartier Général Rocket'),
        ("Safrania",       'Sylphe SARL'),
        ("Cramois'Île",    'Manoir Pokémon'),
    ]

    for from_name, to_name in connections:
        from_z = created_zones.get(from_name)
        to_z   = created_zones.get(to_name)
        if from_z and to_z:
            ZoneConnection.objects.get_or_create(
                from_zone=from_z, to_zone=to_z,
                defaults={'is_bidirectional': True}
            )
        else:
            logging.warning(f"[!] Connexion impossible : {from_name} ↔ {to_name}")

    # ── Connexion spéciale Route 22 → Route 23 : 8 badges requis ──────────────
    logging.info("  🔒 Connexion Route 22 → Route 23 (8 badges requis)...")
    r22 = created_zones.get('Route 22')
    r23 = created_zones.get('Route 23')
    if r22 and r23:
        conn, created = ZoneConnection.objects.get_or_create(
            from_zone=r22,
            to_zone=r23,
            defaults={
                'is_bidirectional': False,
                'required_flag': 'all_badges_obtained',
                'passage_message': "Les gardes de la Ligue Pokémon bloquent le passage. Il vous faut les 8 badges de Kanto pour continuer vers le Plateau Indigo.",
            }
        )
        if not created:
            # Mettre à jour si déjà existant sans condition
            conn.required_flag = 'all_badges_obtained'
            conn.is_bidirectional = False
            conn.passage_message = "Les gardes de la Ligue Pokémon bloquent le passage. Il vous faut les 8 badges de Kanto pour continuer vers le Plateau Indigo."
            conn.save()
        logging.info(f"  {'✅' if created else '⭕'} Route 22 → Route 23 (flag: all_badges_obtained)")

    # ── Connexion Cave Taupiqueur : CS01 Coupe requise ─────────────────────────
    # (géré de façon centralisée par initHMGates.init_hm_gates)
    cave_t = created_zones.get('Cave Taupiqueur')
    carmin = created_zones.get('Carmin sur Mer')
    if cave_t and carmin:
        ZoneConnection.objects.get_or_create(
            from_zone=carmin, to_zone=cave_t,
            defaults={'is_bidirectional': True}
        )

    # ── Connexions bâtiments (depuis initQuests.init_extra_zones) ──────────────
    # Ces zones n'existant pas lors de la 1ère passe, on les crée ici en get_or_create
    logging.info("  🏢 Connexions bâtiments ville...")
    building_links = [
        ("Carmin sur Mer",  'SS Anne',                  '',         'ss_ticket_obtained',
         "Vous avez besoin du Ticket SS pour monter à bord de la SS Anne."),
        ("Céladopole",      'Quartier Général Rocket',  '',         '',
         ''),
        ("Safrania",        'Sylphe SARL',              '',         'reached_saffron',
         "Vous devez d'abord atteindre Safrania."),
        ("Cramois'Île",     'Manoir Pokémon',           '',         '',
         ''),
    ]
    for city_name, bldg_name, req_hm, req_flag, msg in building_links:
        from myPokemonApp.models import Zone as ZoneModel
        city_z = ZoneModel.objects.filter(name=city_name).first()
        bldg_z = ZoneModel.objects.filter(name=bldg_name).first()
        if city_z and bldg_z:
            conn, created_c = ZoneConnection.objects.get_or_create(
                from_zone=city_z, to_zone=bldg_z,
                defaults={
                    'is_bidirectional': True,
                    'required_hm': req_hm,
                    'required_flag': req_flag,
                    'passage_message': msg,
                }
            )
            logging.info(f"  {'✅' if created_c else '⭕'} {city_name} ↔ {bldg_name}")

    # =========================================================================
    # 3. SPAWN RATES (données canoniques Gen 1)
    # =========================================================================

    logging.info("\n🎲 Spawn rates...")

    def add(zone_name, spawns, enc='grass'):
        z = created_zones.get(zone_name)
        if z:
            _add_spawns(z, spawns, enc)
        else:
            logging.warning(f"[!] Zone introuvable pour spawns : {zone_name}")

    # ── Route 1 ──────────────────────────────────────────────────────────────
    add('Route 1', [
        ('Rattata', 50.0, 2, 4),
        ('Pidgey',  50.0, 2, 4),
    ])

    # ── Route 2 ──────────────────────────────────────────────────────────────
    add('Route 2', [
        ('Rattata',    30.0, 3, 5),
        ('Pidgey',     30.0, 3, 5),
        ('Nidoran♂',  20.0, 3, 5),
        ('Nidoran♀',  20.0, 3, 5),
    ])

    # ── Forêt de Jade ────────────────────────────────────────────────────────
    add('Forêt de Jade', [
        ('Pidgey',   30.0, 4, 6),
        ('Caterpie', 25.0, 3, 5),
        ('Weedle',   25.0, 3, 5),
        ('Pikachu',  20.0, 3, 5),
    ])

    # ── Route 3 ──────────────────────────────────────────────────────────────
    add('Route 3', [
        ('Pidgey',    30.0, 6, 10),
        ('Nidoran♂', 20.0, 6, 10),
        ('Nidoran♀', 20.0, 6, 10),
        ('Jigglypuff', 15.0, 8, 10),
        ('Mankey',    15.0, 8, 10),
    ])

    # ── Mont Sélénite ─────────────────────────────────────────────────────────
    add('Mont Sélénite', [
        ('Zubat',    40.0,  8, 12),
        ('Geodude',  30.0,  8, 12),
        ('Clefairy', 15.0,  8, 12),
        ('Paras',    15.0,  8, 12),
    ], enc='cave')

    # ── Route 4 ──────────────────────────────────────────────────────────────
    add('Route 4', [
        ('Rattata',   30.0, 10, 14),
        ('Spearow',   30.0, 10, 14),
        ('Ekans',     20.0, 10, 14),
        ('Mankey',    20.0, 10, 14),
    ])

    # ── Route 24/25 (Pont Cerclef) ───────────────────────────────────────────
    add('Route 24', [
        ('Caterpie',  20.0, 13, 15),
        ('Weedle',    20.0, 13, 15),
        ('Bellsprout', 30.0, 13, 15),
        ('Oddish',    30.0, 13, 15),
    ])
    add('Route 25', [
        ('Caterpie',  15.0, 13, 15),
        ('Weedle',    15.0, 13, 15),
        ('Bellsprout', 35.0, 13, 15),
        ('Oddish',    35.0, 13, 15),
    ])

    # ── Route 9 ──────────────────────────────────────────────────────────────
    add('Route 9', [
        ('Rattata',    25.0, 16, 20),
        ('Nidoran♂',  25.0, 16, 20),
        ('Nidoran♀',  25.0, 16, 20),
        ('Ekans',      25.0, 16, 20),
    ])

    # ── Tunnel Roche ─────────────────────────────────────────────────────────
    add('Tunnel Roche', [
        ('Zubat',    40.0, 15, 20),
        ('Geodude',  30.0, 15, 20),
        ('Machop',   20.0, 15, 20),
        ('Onix',     10.0, 15, 20),
    ], enc='cave')

    # ── Route 10 ─────────────────────────────────────────────────────────────
    add('Route 10', [
        ('Voltorb',   30.0, 18, 22),
        ('Magnemite', 30.0, 18, 22),
        ('Rattata',   20.0, 16, 20),
        ('Spearow',   20.0, 16, 20),
    ])

    # ── Centrale ─────────────────────────────────────────────────────────────
    add('Centrale', [
        ('Pikachu',   30.0, 22, 26),
        ('Raichu',    10.0, 28, 34),
        ('Magnemite', 25.0, 22, 26),
        ('Magneton',  10.0, 28, 34),
        ('Voltorb',   15.0, 22, 26),
        ('Electabuzz', 10.0, 30, 35),
    ])

    # ── Route 5/6 ────────────────────────────────────────────────────────────
    add('Route 5', [
        ('Pidgey',   25.0, 13, 17),
        ('Meowth',   25.0, 13, 17),
        ('Mankey',   25.0, 13, 17),
        ('Abra',     25.0, 13, 17),
    ])
    add('Route 6', [
        ('Pidgey',   25.0, 13, 17),
        ('Meowth',   25.0, 13, 17),
        ('Mankey',   25.0, 13, 17),
        ('Doduo',    25.0, 13, 17),
    ])

    # ── Route 11 ─────────────────────────────────────────────────────────────
    add('Route 11', [
        ('Ekans',    30.0, 13, 17),
        ('Drowzee',  30.0, 13, 17),
        ('Spearow',  25.0, 13, 17),
        ('Rattata',  15.0, 13, 17),
    ])

    # ── Route 7/8 ────────────────────────────────────────────────────────────
    add('Route 7', [
        ('Pidgey',     20.0, 18, 22),
        ('Vulpix',     20.0, 18, 22),
        ('Growlithe',  20.0, 18, 22),
        ('Drowzee',    20.0, 18, 22),
        ('Pidgeotto',  20.0, 22, 26),
    ])
    add('Route 8', [
        ('Pidgey',     25.0, 18, 22),
        ('Drowzee',    25.0, 18, 22),
        ('Growlithe',  25.0, 18, 22),
        ('Ekans',      25.0, 18, 22),
    ])

    # ── Tour Pokémon ─────────────────────────────────────────────────────────
    add('Tour Pokémon', [
        ('Gastly',   50.0, 15, 20),
        ('Haunter',  30.0, 17, 22),
        ('Cubone',   20.0, 15, 20),
    ], enc='cave')

    # ── Route 12/13/14/15 ────────────────────────────────────────────────────
    add('Route 12', [
        ('Bellsprout', 25.0, 20, 24),
        ('Pidgeotto',  20.0, 22, 26),
        ('Venonat',    30.0, 20, 24),
        ('Weepinbell', 25.0, 22, 26),
    ])
    add('Route 13', [
        ('Bellsprout', 25.0, 20, 24),
        ('Pidgeotto',  20.0, 22, 26),
        ('Venonat',    30.0, 20, 24),
        ('Weepinbell', 25.0, 22, 26),
    ])
    add('Route 14', [
        ('Pidgeotto',  30.0, 22, 26),
        ('Venonat',    30.0, 22, 26),
        ('Weepinbell', 25.0, 22, 26),
        ('Gloom',      15.0, 22, 26),
    ])
    add('Route 15', [
        ('Pidgeotto',  30.0, 22, 26),
        ('Venonat',    30.0, 22, 26),
        ('Weepinbell', 20.0, 22, 26),
        ('Gloom',      20.0, 22, 26),
    ])

    # ── Routes 16/17/18 ──────────────────────────────────────────────────────
    add('Route 16', [
        ('Rattata',  25.0, 20, 24),
        ('Doduo',    25.0, 20, 24),
        ('Spearow',  25.0, 20, 24),
        ('Drowzee',  25.0, 20, 24),
    ])
    add('Route 17', [
        ('Rattata',  20.0, 20, 24),
        ('Doduo',    35.0, 20, 26),
        ('Fearow',   15.0, 25, 30),
        ('Ponyta',   30.0, 22, 26),
    ])
    add('Route 18', [
        ('Doduo',    40.0, 22, 26),
        ('Fearow',   20.0, 25, 30),
        ('Ponyta',   25.0, 22, 26),
        ('Rattata',  15.0, 20, 24),
    ])

    # ── Zone Safari ──────────────────────────────────────────────────────────
    add('Zone Safari', [
        ('Nidoran♂',  10.0, 22, 26),
        ('Nidoran♀',  10.0, 22, 26),
        ('Nidorino',    5.0, 28, 32),
        ('Nidorina',    5.0, 28, 32),
        ('Rhyhorn',    10.0, 25, 30),
        ('Kangaskhan',  5.0, 25, 30),
        ('Tauros',      5.0, 22, 26),
        ('Scyther',     5.0, 23, 27),
        ('Pinsir',      5.0, 23, 27),
        ('Exeggcute',  10.0, 20, 25),
        ('Parasect',    5.0, 25, 30),
        ('Paras',      10.0, 20, 25),
        ('Slowpoke',    8.0, 20, 25),
        ('Chansey',     2.0, 20, 25),
        ('Drowzee',     5.0, 22, 26),
    ])
    # Pokémon aquatiques dans le Safari
    add('Zone Safari', [
        ('Psyduck',   40.0, 22, 27),
        ('Slowpoke',  40.0, 22, 27),
        ('Golduck',   20.0, 28, 33),
    ], enc='water')

    # ── Îles Écume ───────────────────────────────────────────────────────────
    add('Îles Écume', [
        ('Zubat',    30.0, 35, 42),
        ('Golbat',   20.0, 38, 44),
        ('Geodude',  20.0, 35, 42),
        ('Graveler', 10.0, 38, 43),
        ('Slowpoke', 20.0, 33, 40),
    ], enc='cave')
    add('Îles Écume', [
        ('Seel',      30.0, 30, 35),
        ('Dewgong',   20.0, 35, 40),
        ('Psyduck',   25.0, 28, 33),
        ('Slowpoke',  25.0, 28, 33),
    ], enc='water')

    # ── Routes maritimes 19/20/21 ────────────────────────────────────────────
    add('Route 19', [
        ('Tentacool',   80.0, 20, 30),
        ('Tentacruel',  20.0, 25, 35),
    ], enc='water')
    add('Route 20', [
        ('Tentacool',   80.0, 20, 30),
        ('Tentacruel',  20.0, 25, 35),
    ], enc='water')
    add('Route 21', [
        ('Tentacool',   60.0, 20, 30),
        ('Tentacruel',  20.0, 25, 35),
        ('Pidgey',      10.0, 22, 26),
        ('Pidgeotto',   10.0, 24, 28),
    ])
    add('Route 21', [
        ('Tentacool',   70.0, 20, 30),
        ('Tentacruel',  30.0, 25, 35),
    ], enc='water')

    # ── Route 22 ─────────────────────────────────────────────────────────────
    add('Route 22', [
        ('Nidoran♂',  40.0, 3, 5),
        ('Nidoran♀',  40.0, 3, 5),
        ('Mankey',     20.0, 2, 4),
    ])

    # ── Route 23 ─────────────────────────────────────────────────────────────
    add('Route 23', [
        ('Ekans',   20.0, 30, 40),
        ('Spearow', 20.0, 30, 40),
        ('Arbok',   15.0, 35, 45),
        ('Fearow',  15.0, 35, 45),
        ('Ditto',   20.0, 30, 35),
        ('Weezing', 10.0, 35, 42),
    ])

    # ── Chemin de la Victoire ─────────────────────────────────────────────────
    add('Chemin de la Victoire', [
        ('Zubat',    25.0, 35, 40),
        ('Golbat',   25.0, 40, 45),
        ('Geodude',  20.0, 35, 40),
        ('Graveler', 10.0, 38, 43),
        ('Onix',     10.0, 35, 40),
        ('Machoke',  10.0, 35, 40),
    ], enc='cave')

    # ── Grottes Inconnues ─────────────────────────────────────────────────────
    add('Grottes Inconnues', [
        ('Machoke',  20.0, 45, 50),
        ('Golbat',   25.0, 45, 55),
        ('Ditto',    25.0, 45, 50),
        ('Kadabra',  15.0, 45, 55),
        ('Parasect', 10.0, 45, 50),
        ('Hypno',     5.0, 45, 50),
    ], enc='cave')
    # Mewtwo est un combat unique, pas un spawn aléatoire → pas de WildPokemonSpawn

    # ── Cave Taupiqueur ───────────────────────────────────────────────────────
    add('Cave Taupiqueur', [
        ('Diglett',   95.0, 15, 22),
        ('Dugtrio',    5.0, 29, 31),
    ], enc='cave')

    logging.info("\n✅ Carte Kanto initialisée !")

    # ── Appliquer toutes les portes CS (required_hm) ─────────────────────────
    logging.info("\n🔑 Application des portes CS (HM Gates)...")
    try:
        from myPokemonApp.tasks.initHMGates import init_hm_gates
        init_hm_gates()
    except Exception as e:
        logging.warning(f"initHMGates skipped: {e}")