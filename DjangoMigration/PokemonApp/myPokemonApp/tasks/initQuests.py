"""
Script d'initialisation du système de quêtes — Région de Kanto complète.

Usage :
    python manage.py shell
    >>> from myPokemonApp.initQuests import init_all
    >>> init_all()

Progression narrative complète Gen 1 / FRLG :
  Chapitre 1  : Bourg Palette → Jadielle (prologue)
  Chapitre 2  : Forêt de Jade → Argenta (Badge 1 Pierre)
  Chapitre 3  : Mont Sélénite → Azuria (Badge 2 Cascade)
  Chapitre 4  : Route 5/6 → Carmin sur Mer → SS Anne (Badge 3 Tonnerre)
  Chapitre 5  : Tunnel Roche → Lavanville → Céladopole (Badge 4 Arc-en-Ciel)
  Chapitre 6  : Tour Pokémon libérée → Routes 12/16 → Parmanie (Badge 5 Âme)
  Chapitre 7  : Surf → Safrania → Sylphe SARL (Badge 6 Marécage)
  Chapitre 8  : Cramois'Île → Manoir → Arène (Badge 7 Volcan)
  Chapitre 9  : Retour Jadielle → Giovanni (Badge 8 Terre)
  Chapitre 10 : Route 22 → Chemin de la Victoire → Ligue
  Quêtes annexes : Bicyclette, CS Vol, CS Force, Îles Écume, Grottes Inconnues
"""

import logging
logger = logging.getLogger(__name__)


# =============================================================================
# OBJETS CLÉS
# =============================================================================

KEY_ITEMS = [
    ("Colis de Chen",    "Un colis à remettre au Professeur Chen de Bourg Palette."),
    ("Pokedex",          "Encyclopédie recensant toutes les espèces Pokémon connues."),
    ("Carte de Kanto",   "Une carte détaillée de la région de Kanto."),
    ("CS01 Coupe",       "CS. Permet de couper les arbres bloquant le passage. Nécessite le Badge Pierre."),
    ("CS02 Vol",         "CS. Permet de voler jusqu'aux villes déjà visitées. Nécessite le Badge Arc-en-Ciel."),
    ("CS03 Surf",        "CS. Permet de surfer sur l'eau. Nécessite le Badge Âme."),
    ("CS04 Force",       "CS. Permet de pousser les rochers. Nécessite le Badge Arc-en-Ciel."),
    ("CS05 Flash",       "CS. Permet d'éclairer les grottes sombres. Nécessite le Badge Pierre."),
    ("Ticket SS",        "Billet pour monter à bord du navire SS Anne ancré à Carmin sur Mer."),
    ("Lunette Silph",    "Lunette permettant de voir à travers le brouillard de spectres de la Tour Pokémon."),
    ("Poké Flûte",       "Flûte qui réveille les Pokémon endormis. Indispensable sur les Routes 12 et 16."),
    ("Laissez-Passer",   "Laissez-passer pour les étages supérieurs de Sylphe SARL."),
    ("Clé Secrète",      "Clé de l'Arène de Cramois'Île, cachée dans le Manoir Pokémon."),
    ("Bicyclette",       "Vélo rapide offert par la boutique d'Azuria contre un Bon de Réduction."),
    ("Bon de Réduction", "Coupon offert par le Fan-Club Pokémon de Carmin. Échangeable contre une Bicyclette."),
    ("Dent en Or",       "Dent trouvée dans la Zone Safari. Le Gardien donne CS04 Force en échange."),
]


def init_key_items():
    from myPokemonApp.models import Item
    created = 0
    for name, desc in KEY_ITEMS:
        _, is_new = Item.objects.get_or_create(
            name=name,
            defaults={'description': desc, 'item_type': 'key', 'price': 0, 'is_consumable': False},
        )
        if is_new:
            created += 1
    print(f"  Objets clés : {created} créés, {len(KEY_ITEMS) - created} déjà présents")


# =============================================================================
# RIVAL (Blue)
# =============================================================================

def init_rival():
    from myPokemonApp.models import Trainer
    # update_or_create garantit que trainer_type='rival' est posé même si Blue
    # existait déjà avec un autre type (ex: 'player' ou 'npc').
    rival, created = Trainer.objects.update_or_create(
        username='Blue',
        defaults={
            'trainer_type': 'rival',
            'is_npc':       True,
            'npc_class':    'Rival',
            'sprite_name':  'blue-gen3.png',
            'can_rebattle': False,
            'intro_text':   "Trop lent ! Tu es complètement pathétique !",
            'defeat_text':  "Hein ?! Incroyable... Je dois m'entraîner plus dur.",
            'victory_text': "Je le savais ! Tu n'es pas à ma hauteur !",
        }
    )
    print(f"  Rival 'Blue' : {'créé' if created else 'mis à jour'}")
    return rival


# =============================================================================
# ZONES SUPPLÉMENTAIRES (bâtiments non créés par initKantoMaps)
# =============================================================================

EXTRA_ZONES = [
    # (name, zone_type, description, order, lv_min, lv_max, is_safe, has_center, has_shop)
    ('SS Anne',                 'building', "Grand paquebot ancré à Carmin. Le capitaine souffre du mal de mer.",           16, 18, 24, True,  False, False),
    ('Quartier Général Rocket', 'building', "Planque secrète de la Team Rocket sous le Casino de Céladopole.",              22, 25, 35, False, False, False),
    ('Sylphe SARL',             'building', "Siège de la société Sylphe, occupée par la Team Rocket.",                      24, 35, 45, False, False, False),
    ('Manoir Pokémon',          'building', "Manoir abandonné de Cramois'Île. La Clé Secrète s'y trouve au sous-sol.",      34, 42, 50, False, False, False),
]


def init_extra_zones():
    from myPokemonApp.models import Zone
    created = 0
    for name, ztype, desc, order, lv_min, lv_max, is_safe, has_center, has_shop in EXTRA_ZONES:
        _, is_new = Zone.objects.get_or_create(
            name=name,
            defaults={
                'zone_type':             ztype,
                'description':           desc,
                'order':                 order,
                'recommended_level_min': lv_min,
                'recommended_level_max': lv_max,
                'is_safe_zone':          is_safe,
                'has_pokemon_center':    has_center,
                'has_shop':              has_shop,
            }
        )
        if is_new:
            created += 1
    print(f"  Zones supplémentaires : {created} créées, {len(EXTRA_ZONES) - created} déjà présentes")


# =============================================================================
# TOUTES LES QUÊTES
# =============================================================================
#
# Champs disponibles :
#   quest_id, title, description, quest_type (main/side/rival/hm), order, icon
#   trigger_type  : visit_zone | defeat_trainer | defeat_gym | have_item | give_item | story_flag | auto
#   trigger_zone_name, trigger_item_name, trigger_gym_city, trigger_trainer_username, trigger_flag
#   objective_text
#   reward_item_name, reward_money, reward_flag

ALL_QUESTS = [

    # =========================================================================
    # CHAPITRE 1 — PROLOGUE : BOURG PALETTE
    # =========================================================================

    {
        'quest_id':       'start_journey',
        'title':          'Le Voyage Commence',
        'description':    "Le Professeur Chen vous remet votre premier Pokémon. L'aventure débute !",
        'quest_type':     'main',
        'order':          10,
        'trigger_type':   'auto',
        'objective_text': 'Choisir votre Pokémon de départ auprès du Professeur Chen',
        'reward_flag':    'has_starter',
        'icon':           'fa-star',
    },
    {
        'quest_id':       'get_oaks_parcel',
        'title':          'Le Colis du Professeur',
        'description':    "La boutique de Jadielle garde un colis destiné au Professeur Chen. Rendez-vous là-bas pour le récupérer.",
        'quest_type':     'main',
        'order':          20,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Jadielle',
        'objective_text': 'Aller à Jadielle et récupérer le colis',
        'reward_item_name': 'Colis de Chen',
        'icon':           'fa-box',
    },
    {
        'quest_id':       'give_parcel_to_oak',
        'title':          'Retour chez le Professeur',
        'description':    "Remettez le colis au Professeur Chen. En échange il vous confiera le Pokédex.",
        'quest_type':     'main',
        'order':          30,
        'trigger_type':   'give_item',
        'trigger_item_name': 'Colis de Chen',
        'objective_text': 'Remettre le colis au laboratoire de Bourg Palette',
        'reward_item_name': 'Pokedex',
        'reward_flag':    'has_pokedex',
        'icon':           'fa-book',
    },

    # =========================================================================
    # CHAPITRE 2 — FORÊT DE JADE → BADGE 1 PIERRE (ARGENTA)
    # =========================================================================

    {
        'quest_id':       'rival_route_22',
        'title':          'Premier Duel avec Blue',
        'description':    "Blue vous attend sur la Route 22. C'est son premier vrai combat — il veut prouver qu'il est meilleur que vous.",
        'quest_type':     'rival',
        'order':          35,
        'trigger_type':   'defeat_trainer',
        'trigger_trainer_username': 'Blue',
        'objective_text': 'Battre Blue sur la Route 22',
        'reward_flag':    'rival_route22_beaten',
        'icon':           'fa-user-ninja',
    },
    {
        'quest_id':       'cross_viridian_forest',
        'title':          'La Forêt de Jade',
        'description':    "La Forêt de Jade est infestée d'insectes et de jeunes dresseurs. Traversez-la pour atteindre Argenta.",
        'quest_type':     'main',
        'order':          40,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Argenta',
        'objective_text': 'Traverser la Forêt de Jade et atteindre Argenta',
        'reward_flag':    'reached_pewter',
        'icon':           'fa-tree',
    },
    {
        'quest_id':       'rival_viridian_forest',
        'title':          'Blue dans la Forêt !',
        'description':    "Blue surgit en pleine Forêt de Jade pour vous barrer la route. Battez-le pour continuer.",
        'quest_type':     'rival',
        'order':          45,
        'trigger_type':   'defeat_trainer',
        'trigger_trainer_username': 'Blue',
        'objective_text': 'Battre Blue dans la Forêt de Jade',
        'reward_flag':    'rival_forest_beaten',
        'icon':           'fa-user-ninja',
    },
    {
        'quest_id':       'defeat_brock',
        'title':          "Badge Pierre — Arène d'Argenta",
        'description':    "Brock, Champion d'Arène d'Argenta, utilise des Pokémon Roche et Sol. Montrez-lui ce que vous valez !",
        'quest_type':     'main',
        'order':          50,
        'trigger_type':   'defeat_gym',
        'trigger_gym_city': 'Pewter City',
        'objective_text': "Battre Brock et obtenir le Badge Pierre",
        'reward_item_name': 'CS05 Flash',
        'reward_flag':    'badge_boulder',
        'icon':           'fa-trophy',
    },

    # =========================================================================
    # CHAPITRE 3 — MONT SÉLÉNITE → BADGE 2 CASCADE (AZURIA)
    # =========================================================================

    {
        'quest_id':       'explore_mt_moon',
        'title':          'Les Mystères du Mont Sélénite',
        'description':    "Le Mont Sélénite cache de précieuses Pierres Lune et de nombreux Rockets. Traversez-le pour rejoindre Azuria.",
        'quest_type':     'main',
        'order':          60,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Azuria',
        'objective_text': 'Traverser le Mont Sélénite et atteindre Azuria',
        'reward_flag':    'reached_cerulean',
        'icon':           'fa-mountain',
    },
    {
        'quest_id':       'rival_cerulean',
        'title':          'Blue sur le Pont Cerclef',
        'description':    "Blue vous défie sur la Route 24, juste au nord d'Azuria. Il s'est entraîné depuis votre dernier duel.",
        'quest_type':     'rival',
        'order':          65,
        'trigger_type':   'defeat_trainer',
        'trigger_trainer_username': 'Blue',
        'objective_text': 'Battre Blue sur le Pont Cerclef (Route 24)',
        'reward_flag':    'rival_cerulean_beaten',
        'icon':           'fa-user-ninja',
    },
    {
        'quest_id':       'defeat_misty',
        'title':          "Badge Cascade — Arène d'Azuria",
        'description':    "Misty, la Championne d'Azuria, maîtrise les Pokémon Eau. Oserez-vous la défier ?",
        'quest_type':     'main',
        'order':          70,
        'trigger_type':   'defeat_gym',
        'trigger_gym_city': 'Cerulean City',
        'objective_text': "Battre Misty et obtenir le Badge Cascade",
        'reward_item_name': 'CS03 Surf',
        'reward_flag':    'badge_cascade',
        'icon':           'fa-trophy',
    },

    # =========================================================================
    # CHAPITRE 4 — SS ANNE → BADGE 3 TONNERRE (CARMIN)
    # =========================================================================

    {
        'quest_id':       'get_bike_voucher',
        'title':          'Le Fan-Club Pokémon',
        'description':    "Le Président du Fan-Club de Carmin veut que vous écoutiez ses histoires de Ronflex. En échange il vous remet un Bon de Réduction pour la boutique de vélos.",
        'quest_type':     'side',
        'order':          75,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Carmin sur Mer',
        'objective_text': 'Visiter le Fan-Club Pokémon de Carmin sur Mer',
        'reward_item_name': 'Bon de Réduction',
        'icon':           'fa-heart',
    },
    {
        'quest_id':       'get_bicycle',
        'title':          'La Bicyclette',
        'description':    "Échangez votre Bon de Réduction contre une Bicyclette à la boutique de vélos d'Azuria. Elle vous permettra de parcourir la Route du Vélo.",
        'quest_type':     'side',
        'order':          76,
        'trigger_type':   'have_item',
        'trigger_item_name': 'Bon de Réduction',
        'objective_text': 'Échanger le Bon de Réduction contre une Bicyclette à Azuria',
        'reward_item_name': 'Bicyclette',
        'reward_flag':    'has_bicycle',
        'icon':           'fa-bicycle',
    },
    {
        'quest_id':       'get_ss_ticket',
        'title':          'Le Ticket pour le SS Anne',
        'description':    "Un ami du Professeur Chen vous remet un Ticket SS pour embarquer sur le luxueux paquebot ancré à Carmin sur Mer.",
        'quest_type':     'main',
        'order':          80,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Route 24',
        'objective_text': 'Obtenir un Ticket SS auprès du Dr Boulmich (Route 25)',
        'reward_item_name': 'Ticket SS',
        'icon':           'fa-ticket-alt',
    },
    {
        'quest_id':       'reach_vermilion',
        'title':          'Direction Carmin sur Mer',
        'description':    "Empruntez la route souterraine depuis Safrania ou passez par les Routes 5 et 6 pour atteindre Carmin sur Mer, grande ville portuaire.",
        'quest_type':     'main',
        'order':          85,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Carmin sur Mer',
        'objective_text': 'Atteindre Carmin sur Mer',
        'reward_flag':    'reached_vermilion',
        'icon':           'fa-anchor',
    },
    {
        'quest_id':       'board_ss_anne',
        'title':          'À Bord du SS Anne',
        'description':    "Montez à bord du SS Anne avec votre Ticket SS. Le capitaine souffre du mal de mer — aidez-le pour obtenir CS01 Coupe.",
        'quest_type':     'main',
        'order':          90,
        'trigger_type':   'have_item',
        'trigger_item_name': 'Ticket SS',
        'objective_text': 'Monter à bord du SS Anne et aider le capitaine',
        'reward_item_name': 'CS01 Coupe',
        'reward_flag':    'visited_ss_anne',
        'icon':           'fa-ship',
    },
    {
        'quest_id':       'defeat_lt_surge',
        'title':          'Badge Tonnerre — Arène de Carmin',
        'description':    "Lt. Surge, le \"Guerrier Électrique\", protège son arène derrière des boîtes verrouillées. Démêlez le piège pour l'affronter.",
        'quest_type':     'main',
        'order':          100,
        'trigger_type':   'defeat_gym',
        'trigger_gym_city': 'Vermilion City',
        'objective_text': "Battre Lt. Surge et obtenir le Badge Tonnerre",
        'reward_item_name': 'CS02 Vol',
        'reward_flag':    'badge_thunder',
        'icon':           'fa-trophy',
    },

    # =========================================================================
    # CHAPITRE 5 — TUNNEL ROCHE → LAVANVILLE → BADGE 4 ARC-EN-CIEL (CÉLADOPOLE)
    # =========================================================================

    {
        'quest_id':       'explore_rock_tunnel',
        'title':          'Le Tunnel Roche',
        'description':    "Le Tunnel Roche est plongé dans l'obscurité totale. CS05 Flash réduit la précision des ennemis — utile pour traverser plus sereinement.",
        'quest_type':     'main',
        'order':          110,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Lavanville',
        'objective_text': 'Traverser le Tunnel Roche et atteindre Lavanville',
        'reward_flag':    'reached_lavender',
        'icon':           'fa-moon',
    },
    {
        'quest_id':       'reach_celadon',
        'title':          'Direction Céladopole',
        'description':    "Céladopole, grande métropole commerçante, abrite l'Arène d'Olga et un casino aux activités douteuses.",
        'quest_type':     'main',
        'order':          120,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Céladopole',
        'objective_text': 'Atteindre Céladopole (via Route 7 ou Route 8)',
        'reward_flag':    'reached_celadon',
        'icon':           'fa-city',
    },
    {
        'quest_id':       'get_hm_fly',
        'title':          'CS02 Vol — La Dresseuse Inconnue',
        'description':    "Une dresseuse gardée prisonnière à l'ouest de Céladopole vous offre CS02 Vol en remerciement de votre aide.",
        'quest_type':     'hm',
        'order':          125,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Route 16',
        'objective_text': "Trouver la dresseuse prisonnière à l'ouest de Céladopole (Route 16)",
        'reward_item_name': 'CS02 Vol',
        'reward_flag':    'has_hm_fly',
        'icon':           'fa-dove',
    },
    {
        'quest_id':       'clear_rocket_hideout',
        'title':          'La Planque de la Team Rocket',
        'description':    "La Team Rocket se cache sous le Casino de Céladopole. Giovanni y garde la Lunette Silph. Infiltrez les quatre sous-sols et battez-le.",
        'quest_type':     'main',
        'order':          130,
        'trigger_type':   'story_flag',
        'trigger_flag':   'rocket_hideout_cleared',
        'objective_text': 'Infiltrer le QG Rocket (Casino de Céladopole, B1F à B4F)',
        'reward_item_name': 'Lunette Silph',
        'reward_flag':    'rocket_hideout_cleared',
        'icon':           'fa-skull-crossbones',
    },
    {
        'quest_id':       'defeat_erika',
        'title':          'Badge Arc-en-Ciel — Arène de Céladopole',
        'description':    "Olga, la Championne de Céladopole, cultive ses Pokémon Plante avec délicatesse. Leurs pollens soporifiques et toxiques sont redoutables.",
        'quest_type':     'main',
        'order':          140,
        'trigger_type':   'defeat_gym',
        'trigger_gym_city': 'Celadon City',
        'objective_text': "Battre Olga et obtenir le Badge Arc-en-Ciel",
        'reward_item_name': 'CS04 Force',
        'reward_flag':    'badge_rainbow',
        'icon':           'fa-trophy',
    },

    # =========================================================================
    # CHAPITRE 6 — TOUR POKÉMON → ROUTES 12/16 → BADGE 5 ÂME (PARMANIE)
    # =========================================================================

    {
        'quest_id':       'rival_pokemon_tower',
        'title':          'Blue au Sommet de la Tour',
        'description':    "Blue vous attend au sommet de la Tour Pokémon — il cherche la même chose que vous.",
        'quest_type':     'rival',
        'order':          145,
        'trigger_type':   'defeat_trainer',
        'trigger_trainer_username': 'Blue',
        'objective_text': 'Battre Blue au sommet de la Tour Pokémon',
        'reward_flag':    'rival_tower_beaten',
        'icon':           'fa-user-ninja',
    },
    {
        'quest_id':       'clear_pokemon_tower',
        'title':          'Libérer la Tour Pokémon',
        'description':    "Muni de la Lunette Silph, gravissez les 7 étages, affrontez le Marowak spectral et chassez les Rockets. M. Fuji, libéré, vous offrira la Poké Flûte.",
        'quest_type':     'main',
        'order':          150,
        'trigger_type':   'story_flag',
        'trigger_flag':   'pokemon_tower_cleared',
        'objective_text': 'Gravir la Tour Pokémon (Lunette Silph requise) et libérer M. Fuji au 7F',
        'reward_item_name': 'Poké Flûte',
        'reward_flag':    'pokemon_tower_cleared',
        'icon':           'fa-ghost',
    },
    {
        'quest_id':       'wake_snorlax_r12',
        'title':          'Réveillez le Ronflex de la Route 12',
        'description':    "Un gigantesque Ronflex bloque la Route 12 au sud de Lavanville. Jouez de la Poké Flûte pour le réveiller — et l'affronter si vous le souhaitez.",
        'quest_type':     'main',
        'order':          155,
        'trigger_type':   'have_item',
        'trigger_item_name': 'Poké Flûte',
        'objective_text': 'Utiliser la Poké Flûte sur le Ronflex de la Route 12',
        'reward_flag':    'snorlax_r12_awoken',
        'icon':           'fa-music',
    },
    {
        'quest_id':       'wake_snorlax_r16',
        'title':          'Réveillez le Ronflex de la Route 16',
        'description':    "Un deuxième Ronflex bloque la Route 16 à l'ouest de Céladopole, sur la Route du Vélo. La Poké Flûte le réveillera.",
        'quest_type':     'main',
        'order':          156,
        'trigger_type':   'have_item',
        'trigger_item_name': 'Poké Flûte',
        'objective_text': 'Utiliser la Poké Flûte sur le Ronflex de la Route 16',
        'reward_flag':    'snorlax_r16_awoken',
        'icon':           'fa-music',
    },
    {
        'quest_id':       'reach_fuchsia',
        'title':          'Direction Parmanie',
        'description':    "Les Routes 12 et 16 sont maintenant accessibles. Rejoignez Parmanie, ville de la Zone Safari et de l'Arène de Stella.",
        'quest_type':     'main',
        'order':          160,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Parmanie',
        'objective_text': 'Atteindre Parmanie (via Route 12 ou Route du Vélo)',
        'reward_flag':    'reached_fuchsia',
        'icon':           'fa-map-pin',
    },
    {
        'quest_id':       'explore_safari_zone',
        'title':          'La Zone Safari',
        'description':    "La Zone Safari abrite des Pokémon rares : Kangaskhan, Scyther, Pinsir, Tauros et même Leveinard. La Dent en Or s'y trouve aussi.",
        'quest_type':     'side',
        'order':          165,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Zone Safari',
        'objective_text': 'Explorer la Zone Safari et capturer des Pokémon rares',
        'reward_flag':    'visited_safari',
        'icon':           'fa-paw',
    },
    {
        'quest_id':       'get_hm_strength',
        'title':          "CS04 Force — La Dent du Gardien",
        'description':    "Le Gardien de la Zone Safari a perdu sa Dent en Or dans la réserve. Retrouvez-la et il vous offrira CS04 Force.",
        'quest_type':     'hm',
        'order':          166,
        'trigger_type':   'have_item',
        'trigger_item_name': 'Dent en Or',
        'objective_text': 'Remettre la Dent en Or au Gardien de la Zone Safari',
        'reward_item_name': 'CS04 Force',
        'reward_flag':    'has_hm_strength',
        'icon':           'fa-tooth',
    },
    {
        'quest_id':       'defeat_koga',
        'title':          "Badge Âme — Arène de Parmanie",
        'description':    "Stella, expert en Pokémon Poison, use de statuts vicieux : poison, sommeil, paralysie. Soyez préparé.",
        'quest_type':     'main',
        'order':          170,
        'trigger_type':   'defeat_gym',
        'trigger_gym_city': 'Fuchsia City',
        'objective_text': "Battre Stella et obtenir le Badge Âme",
        'reward_flag':    'badge_soul',
        'icon':           'fa-trophy',
    },

    # =========================================================================
    # CHAPITRE 7 — SYLPHE SARL → BADGE 6 MARÉCAGE (SAFRANIA)
    # =========================================================================

    {
        'quest_id':       'reach_saffron',
        'title':          'Direction Safrania',
        'description':    "Safrania est assiégée par la Team Rocket. Les gardes aux quatre entrées réclament à boire — apportez-leur une bouteille de thé acheté à Céladopole.",
        'quest_type':     'main',
        'order':          180,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Safrania',
        'objective_text': 'Débloquer l\'accès à Safrania (bouteille de thé requise) et y entrer',
        'reward_flag':    'reached_saffron',
        'icon':           'fa-city',
    },
    {
        'quest_id':       'rival_silph_co',
        'title':          'Blue au 7F de Sylphe',
        'description':    "Blue vous bloque l'accès au Bureau du Président. Battez-le pour monter.",
        'quest_type':     'rival',
        'order':          185,
        'trigger_type':   'defeat_trainer',
        'trigger_trainer_username': 'Blue',
        'objective_text': 'Battre Blue au 7F de Sylphe SARL',
        'reward_flag':    'rival_silph_beaten',
        'icon':           'fa-user-ninja',
    },
    {
        'quest_id':       'liberate_silph_co',
        'title':          'Libérer Sylphe SARL',
        'description':    "La Team Rocket a investi Sylphe SARL pour mettre la main sur le Master Ball. Giovanni attend au 11e étage. Battez-le et libérez les employés.",
        'quest_type':     'main',
        'order':          190,
        'trigger_type':   'story_flag',
        'trigger_flag':   'silph_co_liberated',
        'objective_text': 'Affronter Giovanni au 11F de Sylphe SARL et libérer l\'entreprise',
        'reward_flag':    'silph_co_liberated',
        'icon':           'fa-building',
    },
    {
        'quest_id':       'defeat_sabrina',
        'title':          "Badge Marécage — Arène de Safrania",
        'description':    "Morgane, la \"Télépathe Mystérieuse\", aligne des Pokémon Psy redoutables. Leurs attaques mentales mettront vos Pokémon à genoux.",
        'quest_type':     'main',
        'order':          200,
        'trigger_type':   'defeat_gym',
        'trigger_gym_city': 'Saffron City',
        'objective_text': "Battre Morgane et obtenir le Badge Marécage",
        'reward_flag':    'badge_marsh',
        'icon':           'fa-trophy',
    },

    # =========================================================================
    # CHAPITRE 8 — CRAMOIS'ÎLE → BADGE 7 VOLCAN
    # =========================================================================

    {
        'quest_id':       'reach_cinnabar',
        'title':          "Direction Cramois'Île",
        'description':    "Surfez depuis Parmanie vers le sud pour atteindre l'île volcanique de Cramois'Île.",
        'quest_type':     'main',
        'order':          210,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': "Cramois'Île",
        'objective_text': "Surfer jusqu'à Cramois'Île (CS03 Surf requise)",
        'reward_flag':    'reached_cinnabar',
        'icon':           'fa-fire',
    },
    {
        'quest_id':       'find_secret_key',
        'title':          'La Clé Secrète du Manoir',
        'description':    "L'Arène de Cramois'Île est verrouillée. La Clé Secrète se cache dans le sous-sol du Manoir Pokémon, bâtiment hanté au nord de l'île.",
        'quest_type':     'main',
        'order':          220,
        'trigger_type':   'story_flag',
        'trigger_flag':   'found_secret_key',
        'objective_text': "Explorer le Manoir Pokémon et trouver la Clé Secrète (B1F)",
        'reward_item_name': 'Clé Secrète',
        'reward_flag':    'found_secret_key',
        'icon':           'fa-key',
    },
    {
        'quest_id':       'defeat_blaine',
        'title':          "Badge Volcan — Arène de Cramois'Île",
        'description':    "Pyro, le \"Vieux Sage Brûlant\", maîtrise des Pokémon Feu. Son Arcanin et son Ponyta seront impitoyables si vous n'êtes pas préparé.",
        'quest_type':     'main',
        'order':          230,
        'trigger_type':   'defeat_gym',
        'trigger_gym_city': 'Cinnabar Island',
        'objective_text': "Battre Pyro et obtenir le Badge Volcan",
        'reward_flag':    'badge_volcano',
        'icon':           'fa-trophy',
    },

    # =========================================================================
    # CHAPITRE 9 — RETOUR JADIELLE → BADGE 8 TERRE (GIOVANNI)
    # =========================================================================

    {
        'quest_id':       'final_viridian_gym',
        'title':          "L'Arène Mystère de Jadielle",
        'description':    "L'Arène de Jadielle était fermée depuis le début de votre aventure. Elle est maintenant ouverte. Qui se cache derrière cette porte ?",
        'quest_type':     'main',
        'order':          240,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Jadielle',
        'objective_text': "Retourner à Jadielle et entrer dans l'Arène",
        'reward_flag':    'reached_viridian_gym',
        'icon':           'fa-door-open',
    },
    {
        'quest_id':       'defeat_giovanni',
        'title':          'Badge Terre — Giovanni, le Boss Rocket',
        'description':    "Giovanni, chef de la Team Rocket, se révèle être le Champion d'Arène de Jadielle. Battez-le pour obtenir le 8e et dernier badge.",
        'quest_type':     'main',
        'order':          250,
        'trigger_type':   'defeat_gym',
        'trigger_gym_city': 'Viridian City',
        'objective_text': "Battre Giovanni et obtenir le Badge Terre",
        'reward_flag':    'badge_earth',
        'icon':           'fa-trophy',
    },

    # =========================================================================
    # CHAPITRE 10 — CHEMIN DE LA VICTOIRE → LIGUE POKÉMON
    # =========================================================================

    {
        'quest_id':       'rival_route_22_final',
        'title':          'Blue avant la Ligue',
        'description':    "Blue vous attend une dernière fois sur la Route 22, avant les gardes de la Ligue. C'est le combat le plus sérieux depuis le début.",
        'quest_type':     'rival',
        'order':          255,
        'trigger_type':   'defeat_trainer',
        'trigger_trainer_username': 'Blue',
        'objective_text': 'Battre Blue sur la Route 22 (avant les gardes de la Ligue)',
        'reward_flag':    'rival_route22_final_beaten',
        'icon':           'fa-user-ninja',
    },
    {
        'quest_id':       'reach_victory_road',
        'title':          'Le Chemin de la Victoire',
        'description':    "Le Chemin de la Victoire est une grotte truffée de dresseurs d'élite et de Pokémon niveau 40-50. CS04 Force est indispensable pour déplacer les rochers.",
        'quest_type':     'main',
        'order':          260,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Chemin de la Victoire',
        'objective_text': 'Traverser le Chemin de la Victoire (CS04 Force requise)',
        'reward_flag':    'entered_victory_road',
        'icon':           'fa-road',
    },
    {
        'quest_id':       'reach_indigo_plateau',
        'title':          'Le Plateau Indigo',
        'description':    "Vous avez traversé le Chemin de la Victoire. Le Plateau Indigo, siège de la Ligue Pokémon, vous attend. Les 4 As sont les meilleurs dresseurs de Kanto.",
        'quest_type':     'main',
        'order':          270,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Plateau Indigo',
        'objective_text': 'Atteindre le Plateau Indigo',
        'reward_flag':    'reached_indigo_plateau',
        'icon':           'fa-flag-checkered',
    },

    # -- Conseil des 4 --------------------------------------------------------

    {
        'quest_id':       'defeat_lorelei',
        'title':          'Conseil des 4 — Olga (Glace)',
        'description':    "Olga, experte en Pokémon Glace, ouvre le bal du Conseil des 4. Ses Pokémon infligent Congélation sans pitié.",
        'quest_type':     'main',
        'order':          280,
        'trigger_type':   'defeat_trainer',
        'trigger_trainer_username': 'Olga',
        'objective_text': 'Battre Olga, première membre du Conseil des 4',
        'reward_flag':    'elite4_lorelei_beaten',
        'icon':           'fa-snowflake',
    },
    {
        'quest_id':       'defeat_bruno',
        'title':          'Conseil des 4 — Raphaël (Combat)',
        'description':    "Raphaël, maître des arts martiaux, n'utilise que des Pokémon Combat. Force brute et vitesse absolue.",
        'quest_type':     'main',
        'order':          290,
        'trigger_type':   'defeat_trainer',
        'trigger_trainer_username': 'Raphaël',
        'objective_text': 'Battre Raphaël, deuxième membre du Conseil des 4',
        'reward_flag':    'elite4_bruno_beaten',
        'icon':           'fa-fist-raised',
    },
    {
        'quest_id':       'defeat_agatha',
        'title':          'Conseil des 4 — Agatha (Spectre)',
        'description':    "Agatha, vieille rivale du Professeur Chen, aligne des Pokémon Spectre aux effets vicieux : sommeil, confusion, malédiction.",
        'quest_type':     'main',
        'order':          300,
        'trigger_type':   'defeat_trainer',
        'trigger_trainer_username': 'Agatha',
        'objective_text': 'Battre Agatha, troisième membre du Conseil des 4',
        'reward_flag':    'elite4_agatha_beaten',
        'icon':           'fa-ghost',
    },
    {
        'quest_id':       'defeat_lance',
        'title':          'Conseil des 4 — Peter (Dragon)',
        'description':    "Peter, le Dompteur de Dragons, commande des Pokémon Dragon quasi invincibles. Seuls les types Glace et Dragon peuvent les contrer efficacement.",
        'quest_type':     'main',
        'order':          310,
        'trigger_type':   'defeat_trainer',
        'trigger_trainer_username': 'Peter',
        'objective_text': 'Battre Peter, quatrième membre du Conseil des 4',
        'reward_flag':    'elite4_lance_beaten',
        'icon':           'fa-dragon',
    },
    {
        'quest_id':       'rival_champion',
        'title':          'Blue — Le Champion !',
        'description':    "Blue vous a devancé et est devenu Champion. Battez votre rival une dernière fois pour revendiquer le titre suprême de la région.",
        'quest_type':     'rival',
        'order':          320,
        'trigger_type':   'defeat_trainer',
        'trigger_trainer_username': 'Blue',
        'objective_text': 'Battre Blue, Champion de la Ligue Pokémon',
        'reward_flag':    'rival_champion_beaten',
        'reward_money':   10000,
        'icon':           'fa-crown',
    },
    {
        'quest_id':       'become_champion',
        'title':          'Champion de Kanto !',
        'description':    "Vous avez vaincu les 4 As et le Champion ! Le Professeur Chen en personne salue votre victoire. Votre équipe entre au Hall de la Renommée.",
        'quest_type':     'main',
        'order':          330,
        'trigger_type':   'story_flag',
        'trigger_flag':   'is_champion',
        'objective_text': 'Être intronisé au Hall de la Renommée',
        'reward_flag':    'is_champion',
        'reward_money':   20000,
        'icon':           'fa-medal',
    },

    # =========================================================================
    # QUÊTES SECONDAIRES
    # =========================================================================

    {
        'quest_id':       'explore_seafoam',
        'title':          'Les Îles Écume',
        'description':    "Les Îles Écume, réseau de grottes glacées au large de Parmanie, abritent Artikodin — l'oiseau légendaire de la glace.",
        'quest_type':     'side',
        'order':          400,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Îles Écume',
        'objective_text': 'Explorer les Îles Écume (CS03 Surf requise)',
        'reward_flag':    'visited_seafoam',
        'icon':           'fa-icicles',
    },
    {
        'quest_id':       'explore_power_plant',
        'title':          'La Centrale Électrique',
        'description':    "La Centrale abandonnée entre les Routes 9 et 10 abrite des Pokémon Électrik… et peut-être Électhor, le légendaire.",
        'quest_type':     'side',
        'order':          410,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Centrale',
        'objective_text': 'Explorer la Centrale Électrique (CS01 Coupe requise)',
        'reward_flag':    'visited_power_plant',
        'icon':           'fa-bolt',
    },
    {
        'quest_id':       'visit_dr_boulmich',
        'title':          'Le Laboratoire du Dr Boulmich',
        'description':    "Le Dr Boulmich, ami du Professeur Chen, vit au bout de la Route 25. Il vous confiera un Ticket SS pour le SS Anne.",
        'quest_type':     'side',
        'order':          420,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Route 25',
        'objective_text': 'Atteindre la Route 25 et rencontrer le Dr Boulmich',
        'reward_flag':    'visited_boulmich',
        'icon':           'fa-flask',
    },
    {
        'quest_id':       'visit_cerulean_cave',
        'title':          'Grottes Inconnues — Mewtwo',
        'description':    "Les Grottes Inconnues au nord d'Azuria sont accessibles uniquement aux Champions de la Ligue. Mewtwo, le Pokémon le plus puissant au monde, s'y terrerait.",
        'quest_type':     'side',
        'order':          430,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Grottes Inconnues',
        'objective_text': 'Pénétrer dans les Grottes Inconnues (titre de Champion requis)',
        'reward_flag':    'visited_cerulean_cave',
        'icon':           'fa-dna',
    },
    {
        'quest_id':       'visit_route_21',
        'title':          'Route Maritime 21',
        'description':    "La Route 21 relie Cramois'Île à Bourg Palette par la mer. Des Tentacruel et des dresseurs sur leurs bateaux vous attendent.",
        'quest_type':     'side',
        'order':          440,
        'trigger_type':   'visit_zone',
        'trigger_zone_name': 'Route 21',
        'objective_text': "Parcourir la Route 21 de Cramois'Île à Bourg Palette",
        'reward_flag':    'visited_route21',
        'icon':           'fa-water',
    },
]


def init_quests():
    from myPokemonApp.models import Quest, Zone, Item, Trainer, GymLeader

    created = 0
    for qdata in ALL_QUESTS:
        defaults = {
            'title':          qdata['title'],
            'description':    qdata['description'],
            'quest_type':     qdata.get('quest_type', 'main'),
            'order':          qdata.get('order', 0),
            'trigger_type':   qdata.get('trigger_type', 'auto'),
            'trigger_flag':   qdata.get('trigger_flag', ''),
            'objective_text': qdata.get('objective_text', ''),
            'reward_money':   qdata.get('reward_money', 0),
            'reward_flag':    qdata.get('reward_flag', ''),
            'icon':           qdata.get('icon', 'fa-scroll'),
        }

        if qdata.get('trigger_zone_name'):
            zone = Zone.objects.filter(name__icontains=qdata['trigger_zone_name']).first()
            if zone:
                defaults['trigger_zone'] = zone
            else:
                logger.warning("Zone introuvable : %s", qdata['trigger_zone_name'])

        if qdata.get('trigger_item_name'):
            item = Item.objects.filter(name=qdata['trigger_item_name']).first()
            if item:
                defaults['trigger_item'] = item
            else:
                logger.warning("Item trigger introuvable : %s", qdata['trigger_item_name'])

        if qdata.get('trigger_trainer_username'):
            t = Trainer.objects.filter(username=qdata['trigger_trainer_username']).first()
            if t:
                defaults['trigger_trainer'] = t
            else:
                logger.warning("Trainer introuvable : %s", qdata['trigger_trainer_username'])

        if qdata.get('trigger_gym_city'):
            gl = GymLeader.objects.filter(
                gym_city__icontains=qdata['trigger_gym_city']
            ).first()
            if gl:
                defaults['trigger_trainer'] = gl.trainer
            else:
                logger.warning("GymLeader introuvable : %s", qdata['trigger_gym_city'])

        if qdata.get('reward_item_name'):
            item = Item.objects.filter(name=qdata['reward_item_name']).first()
            if item:
                defaults['reward_item'] = item
            else:
                logger.warning("Item récompense introuvable : %s", qdata['reward_item_name'])

        _, is_new = Quest.objects.update_or_create(
            quest_id=qdata['quest_id'],
            defaults=defaults,
        )
        if is_new:
            created += 1

    # ── Prérequis ──────────────────────────────────────────────────────────────
    PREREQS = {
        # Ch1 prologue
        'get_oaks_parcel':        ['start_journey'],
        'give_parcel_to_oak':     ['get_oaks_parcel'],
        # Ch2
        'rival_route_22':         ['give_parcel_to_oak'],
        'cross_viridian_forest':  ['give_parcel_to_oak'],
        'rival_viridian_forest':  ['cross_viridian_forest'],
        'defeat_brock':           ['cross_viridian_forest'],
        # Ch3
        'explore_mt_moon':        ['defeat_brock'],
        'rival_cerulean':         ['explore_mt_moon'],
        'defeat_misty':           ['explore_mt_moon'],
        # Ch4
        'get_bike_voucher':       ['reach_vermilion'],
        'get_bicycle':            ['get_bike_voucher'],
        'get_ss_ticket':          ['defeat_misty'],
        'reach_vermilion':        ['defeat_misty'],
        'board_ss_anne':          ['reach_vermilion', 'get_ss_ticket'],
        'defeat_lt_surge':        ['board_ss_anne'],
        # Ch5
        'explore_rock_tunnel':    ['defeat_lt_surge'],
        'reach_celadon':          ['explore_rock_tunnel'],
        'get_hm_fly':             ['reach_celadon'],
        'clear_rocket_hideout':   ['reach_celadon'],
        'defeat_erika':           ['reach_celadon'],
        # Ch6
        'rival_pokemon_tower':    ['clear_rocket_hideout'],
        'clear_pokemon_tower':    ['clear_rocket_hideout', 'rival_pokemon_tower'],
        'wake_snorlax_r12':       ['clear_pokemon_tower'],
        'wake_snorlax_r16':       ['clear_pokemon_tower'],
        'reach_fuchsia':          ['wake_snorlax_r12', 'wake_snorlax_r16'],
        'explore_safari_zone':    ['reach_fuchsia'],
        'get_hm_strength':        ['explore_safari_zone'],
        'defeat_koga':            ['reach_fuchsia'],
        # Ch7
        'reach_saffron':          ['defeat_koga'],
        'rival_silph_co':         ['reach_saffron'],
        'liberate_silph_co':      ['rival_silph_co'],
        'defeat_sabrina':         ['liberate_silph_co'],
        # Ch8
        'reach_cinnabar':         ['defeat_sabrina'],
        'find_secret_key':        ['reach_cinnabar'],
        'defeat_blaine':          ['find_secret_key'],
        # Ch9
        'final_viridian_gym':     ['defeat_blaine'],
        'defeat_giovanni':        ['final_viridian_gym'],
        # Ch10
        'rival_route_22_final':   ['defeat_giovanni'],
        'reach_victory_road':     ['defeat_giovanni'],
        'reach_indigo_plateau':   ['reach_victory_road'],
        'defeat_lorelei':         ['reach_indigo_plateau'],
        'defeat_bruno':           ['defeat_lorelei'],
        'defeat_agatha':          ['defeat_bruno'],
        'defeat_lance':           ['defeat_agatha'],
        'rival_champion':         ['defeat_lance'],
        'become_champion':        ['rival_champion'],
        # Side quests
        'explore_seafoam':        ['defeat_koga'],
        'explore_power_plant':    ['explore_rock_tunnel'],
        'visit_dr_boulmich':      ['defeat_misty'],
        'visit_cerulean_cave':    ['become_champion'],
        'visit_route_21':         ['reach_cinnabar'],
    }

    for quest_id, prereq_ids in PREREQS.items():
        try:
            quest = Quest.objects.get(quest_id=quest_id)
            prereqs = Quest.objects.filter(quest_id__in=prereq_ids)
            quest.prerequisite_quests.set(prereqs)
        except Quest.DoesNotExist:
            logger.warning("Quête introuvable (prérequis) : %s", quest_id)

    print(f"  Quêtes : {created} nouvelles, {len(ALL_QUESTS) - created} mises à jour ({len(ALL_QUESTS)} total)")


# =============================================================================
# RENCONTRES RIVAL
# =============================================================================

RIVAL_ENCOUNTERS_DATA = [
    {
        'quest_id':    'rival_route_22',
        'zone_name':   'Route 22',
        'pre_battle':  "Hé ! Attends un peu ! Je savais que tu viendrais ici. Allez !",
        'post_battle': "Quoi ?! Tu as gagné ?! Peu importe. La prochaine fois ce sera différent.",
    },
    {
        'quest_id':    'rival_viridian_forest',
        'zone_name':   'Forêt de Jade',
        'pre_battle':  "Hé toi ! Tu pensais m'éviter ? Allez, on se bat !",
        'post_battle': "Hein ?! Incroyable... Je dois m'entraîner plus dur.",
    },
    {
        'quest_id':    'rival_cerulean',
        'zone_name':   'Route 24',
        'pre_battle':  "Encore toi ! Mes Pokémon ont grandi depuis la dernière fois. Prépare-toi !",
        'post_battle': "Encore ?! Bah... La prochaine fois je te battrai facilement.",
    },
    {
        'quest_id':    'rival_pokemon_tower',
        'zone_name':   'Tour Pokémon',
        'floor_number': 7,
        'pre_battle':  "Tu es venu chercher la même chose que moi ? Montre-moi si tu le mérites !",
        'post_battle': "J'aurais dû mieux m'entraîner avant de venir ici.",
    },
    {
        'quest_id':    'rival_silph_co',
        'zone_name':   'Sylphe SARL',
        'floor_number': 7,
        'pre_battle':  "Tu as du culot de venir jusqu'ici. Mais tu ne passeras pas !",
        'post_battle': "Tch... tu as encore gagné. Va, monte voir le Président.",
    },
    {
        'quest_id':    'rival_route_22_final',
        'zone_name':   'Route 22',
        'pre_battle':  "Tu veux affronter la Ligue ? Tu devras d'abord passer par moi.",
        'post_battle': "Pfff... Vas-y alors. Mais ne crois pas que tu vas gagner facilement là-haut.",
    },
    {
        'quest_id':    'rival_champion',
        'zone_name':   'Plateau Indigo',
        'pre_battle':  "J'ai battu les 4 As en premier. Je suis le Champion ! Tu n'as aucune chance.",
        'post_battle': "Perdu... contre toi... Je dois revoir toute ma façon de dresser. Tu mérites vraiment ce titre.",
    },
]


def init_rival_encounters():
    from myPokemonApp.models import Quest, Trainer, Zone, ZoneFloor, RivalEncounter

    # On cherche uniquement par username pour éviter un échec si trainer_type
    # n'a pas encore été mis à jour par init_rival().
    rival = Trainer.objects.filter(username='Blue').first()
    if not rival:
        print("  ⚠ Rival 'Blue' introuvable — lancez init_rival() d'abord.")
        return

    created = updated = 0
    for enc in RIVAL_ENCOUNTERS_DATA:
        quest = Quest.objects.filter(quest_id=enc['quest_id']).first()
        zone  = Zone.objects.filter(name__icontains=enc['zone_name']).first()
        if not quest or not zone:
            print(f"  ⚠ Rencontre ignorée (quête/zone manquante) : {enc['quest_id']}")
            continue

        floor = None
        if enc.get('floor_number') is not None:
            floor = ZoneFloor.objects.filter(
                zone=zone, floor_number=enc['floor_number']
            ).first()

        _, is_new = RivalEncounter.objects.update_or_create(
            quest=quest,
            defaults={
                'rival':           rival,
                'zone':            zone,
                'floor':           floor,
                'pre_battle_text': enc['pre_battle'],
                'post_battle_text':enc['post_battle'],
            }
        )
        if is_new:
            created += 1
        else:
            updated += 1

    print(f"  Rencontres rival : {created} créées, {updated} mises à jour")


# =============================================================================
# ÉTAGES DES BÂTIMENTS
# =============================================================================
#
# Convention pour les NPC : Trainer.location = "<Nom de zone>-<floor_number>"
# Ex: "Tour Pokémon-4" pour un Rocket au 4F.

FLOORS_DATA = {

    'Tour Pokémon': [
        {'n': 1, 'name': '1F',
         'desc': "Hall d'entrée. Les tombes de Pokémon bien-aimés jalonnent les murs. Zone calme.",
         'safe': True,  'flag': '',                'label': ''},
        {'n': 2, 'name': '2F',
         'desc': "Des dresseurs endeuillés veillent sur les tombes de leurs Pokémon.",
         'safe': False, 'flag': '',                'label': ''},
        {'n': 3, 'name': '3F',
         'desc': "L'atmosphère se fait plus lourde. Des esprits commencent à rôder.",
         'safe': False, 'flag': '',                'label': ''},
        {'n': 4, 'name': '4F',
         'desc': "Des membres de la Team Rocket bloquent l'accès aux étages supérieurs.",
         'safe': False, 'flag': '',                'label': ''},
        {'n': 5, 'name': '5F',
         'desc': "Le brouillard de spectres s'épaissit. La Lunette Silph devient indispensable.",
         'safe': False, 'flag': 'has_silph_scope', 'label': "La Lunette Silph est nécessaire pour percer le brouillard."},
        {'n': 6, 'name': '6F',
         'desc': "Un Rocket d'élite monte la garde devant le dernier escalier.",
         'safe': False, 'flag': 'has_silph_scope', 'label': "La Lunette Silph est nécessaire."},
        {'n': 7, 'name': '7F — Sommet',
         'desc': "Le spectre de Marowak et le boss Rocket vous attendent. M. Fuji est prisonnier ici.",
         'safe': False, 'flag': 'has_silph_scope', 'label': "La Lunette Silph est indispensable pour atteindre le sommet."},
    ],

    'Sylphe SARL': [
        {'n':  1, 'name': '1F',
         'desc': "Hall d'accueil. La réception est sous contrôle de la Team Rocket.",
         'safe': False, 'flag': '',               'label': ''},
        {'n':  2, 'name': '2F',
         'desc': "Couloirs de bureaux. Les Rockets patrouillent entre les cloisons.",
         'safe': False, 'flag': '',               'label': ''},
        {'n':  3, 'name': '3F',
         'desc': "Laboratoires de recherche verrouillés.",
         'safe': False, 'flag': 'has_silph_pass', 'label': "Le Laissez-Passer est requis pour accéder aux étages supérieurs."},
        {'n':  4, 'name': '4F',
         'desc': "Salle de réunion transformée en poste de commandement Rocket.",
         'safe': False, 'flag': 'has_silph_pass', 'label': "Laissez-Passer requis."},
        {'n':  5, 'name': '5F',
         'desc': "Un scientifique prisonnier vous remet le Laissez-Passer en secret.",
         'safe': False, 'flag': '',               'label': ''},
        {'n':  6, 'name': '6F',
         'desc': "Couloir de connexion entre les deux ailes du bâtiment.",
         'safe': False, 'flag': 'has_silph_pass', 'label': "Laissez-Passer requis."},
        {'n':  7, 'name': '7F',
         'desc': "Blue vous bloque l'accès au Bureau du Président. Battez-le pour monter.",
         'safe': False, 'flag': 'has_silph_pass', 'label': "Laissez-Passer requis."},
        {'n':  9, 'name': '9F',
         'desc': "Salle de conférence. Quelques Rockets en retrait surveillent les issues.",
         'safe': False, 'flag': 'has_silph_pass', 'label': "Laissez-Passer requis."},
        {'n': 11, 'name': '11F — Bureau du Président',
         'desc': "Giovanni attend ici, entouré de ses gardes d'élite. C'est le combat décisif.",
         'safe': False, 'flag': 'has_silph_pass', 'label': "Laissez-Passer requis."},
    ],

    'Manoir Pokémon': [
        {'n':  1, 'name': '1F',
         'desc': "Hall d'entrée en ruines. Des Ponyta et Krabby errent dans les couloirs effondrés.",
         'safe': False, 'flag': '', 'label': ''},
        {'n':  2, 'name': '2F',
         'desc': "Bibliothèque aux livres épars. Des journaux de recherche sur Mew y traînent.",
         'safe': False, 'flag': '', 'label': ''},
        {'n':  3, 'name': '3F',
         'desc': "Couloir obscur. Des Grimer et Koffing patrouillent entre les débris.",
         'safe': False, 'flag': '', 'label': ''},
        {'n': -1, 'name': 'B1F',
         'desc': "Sous-sol humide. La Clé Secrète est dissimulée ici. Des Ditto et Muk rôdent.",
         'safe': False, 'flag': '', 'label': ''},
    ],

    'Chemin de la Victoire': [
        {'n': 1, 'name': '1F',
         'desc': "Entrée du Chemin de la Victoire. Des rochers obstruent le passage — CS04 Force requise.",
         'safe': False, 'flag': '', 'label': ''},
        {'n': 2, 'name': '2F',
         'desc': "Deuxième niveau. Des dresseurs d'élite vous attendent entre les rochers et les failles.",
         'safe': False, 'flag': '', 'label': ''},
        {'n': 3, 'name': '3F',
         'desc': "Sortie vers le Plateau Indigo. Le niveau des Pokémon dépasse les 45.",
         'safe': False, 'flag': '', 'label': ''},
    ],

    'Îles Écume': [
        {'n': 1, 'name': 'B1F',
         'desc': "Premier niveau souterrain. De l'eau glacée s'écoule dans les galeries sombres.",
         'safe': False, 'flag': '', 'label': ''},
        {'n': 2, 'name': 'B2F',
         'desc': "Galeries inondées. CS03 Surf indispensable. Des Seel et Dewgong nagent dans les eaux.",
         'safe': False, 'flag': '', 'label': ''},
        {'n': 3, 'name': 'B3F',
         'desc': "Caverne profonde. Artikodin, le légendaire oiseau de glace, se terrerait quelque part ici.",
         'safe': False, 'flag': '', 'label': ''},
        {'n': 4, 'name': 'B4F',
         'desc': "Niveau le plus profond. Des courants sous-marins redirigent vers la chambre d'Artikodin.",
         'safe': False, 'flag': '', 'label': ''},
    ],

    'SS Anne': [
        {'n': 1, 'name': 'Pont extérieur',
         'desc': "Le pont supérieur du paquebot. L'air marin est vivifiant. Des dresseurs en tenue de soirée se promènent.",
         'safe': True,  'flag': '', 'label': ''},
        {'n': 2, 'name': '1F',
         'desc': "Salon principal. Tables de repas et dresseurs avides de combats.",
         'safe': False, 'flag': '', 'label': ''},
        {'n': 3, 'name': '2F',
         'desc': "Cabines de luxe. Des dresseurs y reposent leurs Pokémon entre deux combats.",
         'safe': False, 'flag': '', 'label': ''},
        {'n': 4, 'name': 'Cabine du Capitaine',
         'desc': "Le capitaine est allongé sur sa couchette, terrassé par le mal de mer. Aidez-le pour obtenir CS01 Coupe.",
         'safe': True,  'flag': '', 'label': ''},
    ],

    'Quartier Général Rocket': [
        {'n': -1, 'name': 'B1F',
         'desc': "Premier sous-sol. Des Rockets montent la garde devant les ascenseurs et les interrupteurs.",
         'safe': False, 'flag': '', 'label': ''},
        {'n': -2, 'name': 'B2F',
         'desc': "Couloirs labyrinthiques truffés de pièges, de tourniquets et de Rockets en patrouille.",
         'safe': False, 'flag': '', 'label': ''},
        {'n': -3, 'name': 'B3F',
         'desc': "Bureau de commandement. Giovanni vous y attend, entouré de ses meilleurs agents.",
         'safe': False, 'flag': '', 'label': ''},
        {'n': -4, 'name': 'B4F',
         'desc': "Salle au trésor. La Lunette Silph est conservée ici sous haute surveillance.",
         'safe': False, 'flag': '', 'label': ''},
    ],
}


def init_zone_floors():
    from myPokemonApp.models import Zone, ZoneFloor

    created = updated = skipped = 0
    for zone_name, floors in FLOORS_DATA.items():
        zone = Zone.objects.filter(name__icontains=zone_name).first()
        if not zone:
            print(f"  ⚠ Zone introuvable : {zone_name}")
            skipped += 1
            continue

        zone.has_floors = True
        zone.save(update_fields=['has_floors'])

        for i, f in enumerate(floors):
            _, is_new = ZoneFloor.objects.update_or_create(
                zone=zone,
                floor_number=f['n'],
                defaults={
                    'floor_name':          f['name'],
                    'description':         f['desc'],
                    'required_flag':       f['flag'],
                    'required_flag_label': f['label'],
                    'is_safe':             f['safe'],
                    'order':               i,
                }
            )
            if is_new:
                created += 1
            else:
                updated += 1

    total = sum(len(v) for v in FLOORS_DATA.values())
    print(f"  Étages : {created} créés, {updated} mis à jour ({total} total, {skipped} zones ignorées)")



# =============================================================================
# ÉLITE 4 & CHAMPION (NPC Trainers)
# =============================================================================
# Ces dresseurs ne sont pas créés par initNPCTrainersComplete.py.
# On les crée ici pour que les quêtes defeat_trainer puissent les référencer.

ELITE4_TRAINERS = [
    {
        'username':    'Olga',
        'npc_class':   'Membre du Conseil',
        'sprite_name': 'lorelei.png',
        'intro_text':  "Le froid ne montre aucune pitié. Mes Pokémon Glace non plus.",
        'defeat_text': "Je ne m'attendais pas à perdre... Vous méritez de continuer.",
        'victory_text':"Vous êtes encore loin du niveau requis pour la Ligue.",
        'location':    'Plateau Indigo',
        'money':       8000,
    },
    {
        'username':    'Raphaël',
        'npc_class':   'Membre du Conseil',
        'sprite_name': 'bruno.png',
        'intro_text':  "Force et détermination ! Mes Pokémon Combat vous écraseront !",
        'defeat_text': "Incroyable... Votre force dépasse la mienne.",
        'victory_text':"Vous manquez de puissance brute.",
        'location':    'Plateau Indigo',
        'money':       8000,
    },
    {
        'username':    'Agatha',
        'npc_class':   'Membre du Conseil',
        'sprite_name': 'agatha.png',
        'intro_text':  "Vous êtes venu jusqu'ici ? Mes fantômes vont s'amuser avec vous.",
        'defeat_text': "Bien joué, gamin. Vous avez du caractère.",
        'victory_text':"Mes fantômes vous ont bien perturbé, n'est-ce pas ?",
        'location':    'Plateau Indigo',
        'money':       8000,
    },
    {
        'username':    'Peter',
        'npc_class':   'Membre du Conseil',
        'sprite_name': 'lance.png',
        'intro_text':  "Je suis le Dompteur de Dragons. Mes Pokémon sont les plus puissants !",
        'defeat_text': "Vous avez réussi à vaincre mes Dragons... Respect.",
        'victory_text':"Vos Pokémon n'étaient pas à la hauteur de mes Dragons.",
        'location':    'Plateau Indigo',
        'money':       10000,
    },
]


def init_elite4():
    """Crée les 4 As comme trainers NPC s'ils n'existent pas encore."""
    from myPokemonApp.models import Trainer
    created = 0
    for data in ELITE4_TRAINERS:
        _, is_new = Trainer.objects.update_or_create(
            username=data['username'],
            defaults={
                'trainer_type': 'elite4',
                'is_npc':       True,
                'npc_class':    data['npc_class'],
                'sprite_name':  data['sprite_name'],
                'intro_text':   data['intro_text'],
                'defeat_text':  data['defeat_text'],
                'victory_text': data['victory_text'],
                'location':     data['location'],
                'money':        data['money'],
                'can_rebattle': True,
            }
        )
        if is_new:
            created += 1
    print(f"  Élite 4 : {created} créés, {len(ELITE4_TRAINERS) - created} mis à jour")

# =============================================================================
# ENTRY POINT
# =============================================================================

def init_all():
    print("── Initialisation du système de quêtes de Kanto ─────────────────────")
    print("[1/8] Objets clés…")
    init_key_items()
    print("[2/8] Rival Blue…")
    init_rival()
    print("[3/8] Zones supplémentaires…")
    init_extra_zones()
    print("[4/8] Élite 4…")
    init_elite4()
    print("[5/8] Quêtes…")
    init_quests()
    print("[6/8] Rencontres rival…")
    init_rival_encounters()
    print("[7/8] Étages des bâtiments…")
    init_zone_floors()
    print("[8/8] Vérification…")
    _verify()
    print("✅ Système de quêtes Kanto initialisé.")


def _verify():
    try:
        from myPokemonApp.models import Quest, ZoneFloor, RivalEncounter
        q  = Quest.objects.count()
        f  = ZoneFloor.objects.count()
        r  = RivalEncounter.objects.count()
        print(f"  Bilan BDD : {q} quêtes | {f} étages | {r} rencontres rival")
    except Exception as e:
        print(f"  ⚠ Erreur vérification : {e}")


if __name__ == '__main__':
    init_all()