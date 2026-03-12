"""
initHeldItems.py
================
Initialisation des Objets Tenus (Held Items) pour Kanto.

Usage :
    from myPokemonApp.tasks.initHeldItems import initHeldItems
    initHeldItems()

Créé et injecté dans les boutiques existantes (définies dans initShops.py).
Les noms d'items sont calibrés sur _ITEM_SPRITE_MAP de custom_filters.py.
Les noms de boutiques correspondent exactement à ceux de initShops.py.
"""

from myPokemonApp.models import Item, Shop, ShopInventory
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# CATALOGUE DES HELD ITEMS
# ─────────────────────────────────────────────────────────────────────────────
#
# held_effect → identifiant logique utilisé dans Battle.py
# Noms choisis pour correspondre aux entrées existantes de _ITEM_SPRITE_MAP.
#
HELD_ITEMS_DATA = [

    # ── Régénération / Sustain ─────────────────────────────────────────────
    {
        "name":        "Restes",
        "description": "Restaure 1/16 des PV max du porteur à chaque fin de tour.",
        "held_effect": "leftovers",
        "price":       0,          # introuvable en boutique, ramassé sur la map
        "is_consumable": False,
    },
    {
        "name":        "Baie Sitrus",
        "description": "Restaure 1/8 des PV max quand les PV passent sous 50 %.",
        "held_effect": "sitrus_berry",
        "price":       200,
        "is_consumable": True,
    },
    {
        "name":        "Baie Oran",
        "description": "Restaure 10 PV quand les PV passent sous 50 %.",
        "held_effect": "oran_berry",
        "price":       100,
        "is_consumable": True,
    },
    {
        "name":        "Baie Lum",
        "description": "Guérit n'importe quelle altération de statut une seule fois.",
        "held_effect": "lum_berry",
        "price":       300,
        "is_consumable": True,
    },

    # ── Boost offensif ─────────────────────────────────────────────────────
    {
        "name":        "Bandeau Choix",
        "description": "Augmente l'Attaque de 50 %, mais le porteur ne peut utiliser qu'une seule capacité.",
        "held_effect": "choice_band",
        "price":       0,
        "is_consumable": False,
    },
    {
        "name":        "Lunettes Choix",
        "description": "Augmente l'Attaque Spéciale de 50 %, mais le porteur ne peut utiliser qu'une seule capacité.",
        "held_effect": "choice_specs",
        "price":       0,
        "is_consumable": False,
    },
    {
        "name":        "Foulard Choix",
        "description": "Augmente la Vitesse de 50 %, mais le porteur ne peut utiliser qu'une seule capacité.",
        "held_effect": "choice_scarf",
        "price":       0,
        "is_consumable": False,
    },
    {
        "name":        "Orbe Vie",
        "description": "Augmente la puissance des attaques de 30 %, mais inflige 10 % des PV max à chaque attaque.",
        "held_effect": "life_orb",
        "price":       0,
        "is_consumable": False,
    },

    # ── Boost de type (+20%) ───────────────────────────────────────────────
    {
        "name":        "Charbon",
        "description": "Augmente de 20 % la puissance des attaques de type Feu.",
        "held_effect": "type_boost_fire",
        "price":       2100,
        "is_consumable": False,
    },
    {
        "name":        "Aimant",
        "description": "Augmente de 20 % la puissance des attaques de type Électrik.",
        "held_effect": "type_boost_electric",
        "price":       2100,
        "is_consumable": False,
    },
    {
        "name":        "Eau Mystique",
        "description": "Augmente de 20 % la puissance des attaques de type Eau.",
        "held_effect": "type_boost_water",
        "price":       2100,
        "is_consumable": False,
    },
    {
        "name":        "Filtre Miroir",
        "description": "Augmente de 20 % la puissance des attaques de type Psy.",
        "held_effect": "type_boost_psychic",
        "price":       2100,
        "is_consumable": False,
    },
    {
        "name":        "Herbe Miracle",
        "description": "Augmente de 20 % la puissance des attaques de type Plante.",
        "held_effect": "type_boost_grass",
        "price":       2100,
        "is_consumable": False,
    },
    {
        "name":        "Écharpe Soie",
        "description": "Augmente de 20 % la puissance des attaques de type Normal.",
        "held_effect": "type_boost_normal",
        "price":       2100,
        "is_consumable": False,
    },

    # ── Défense / Survie ───────────────────────────────────────────────────
    {
        "name":        "Veste Assaut",
        "description": "Réduit de 50 % les dégâts des attaques super efficaces reçues.",
        "held_effect": "assault_vest",
        "price":       0,
        "is_consumable": False,
    },
    {
        "name":        "Ceinture Concentration",
        "description": "Survie avec 1 PV si le porteur est à PV max et encaisse un coup fatal. Consommé à l'usage.",
        "held_effect": "focus_sash",
        "price":       0,
        "is_consumable": True,
    },
    {
        "name":        "Casque Rocheux",
        "description": "Inflige 1/6 des PV max à l'adversaire à chaque fois que le porteur subit une attaque de contact.",
        "held_effect": "rocky_helmet",
        "price":       0,
        "is_consumable": False,
    },

    # ── Baies de résistance (consommables) ────────────────────────────────
    {
        "name":        "Baie Yache",
        "description": "Réduit de 50 % les dégâts d'une attaque super efficace de type Glace. Consommé à l'usage.",
        "held_effect": "resist_berry_ice",
        "price":       500,
        "is_consumable": True,
    },
    {
        "name":        "Baie Chople",
        "description": "Réduit de 50 % les dégâts d'une attaque super efficace de type Combat. Consommé à l'usage.",
        "held_effect": "resist_berry_fight",
        "price":       500,
        "is_consumable": True,
    },

    # ── Baies de guérison de statut (consommables) ────────────────────────
    {
        "name":        "Baie Pêche",
        "description": "Guérit la paralysie quand le porteur en est affecté. Consommé à l'usage.",
        "held_effect": "cure_paralysis_berry",
        "price":       100,
        "is_consumable": True,
    },
    {
        "name":        "Baie Mepo",
        "description": "Guérit le sommeil quand le porteur en est affecté. Consommé à l'usage.",
        "held_effect": "cure_sleep_berry",
        "price":       100,
        "is_consumable": True,
    },
    {
        "name":        "Baie Gribi",
        "description": "Guérit le poison quand le porteur en est affecté. Consommé à l'usage.",
        "held_effect": "cure_poison_berry",
        "price":       100,
        "is_consumable": True,
    },
    {
        "name":        "Baie Rago",
        "description": "Guérit la brûlure quand le porteur en est affecté. Consommé à l'usage.",
        "held_effect": "cure_burn_berry",
        "price":       100,
        "is_consumable": True,
    },
    {
        "name":        "Baie Glace",
        "description": "Guérit le gel quand le porteur en est affecté. Consommé à l'usage.",
        "held_effect": "cure_freeze_berry",
        "price":       100,
        "is_consumable": True,
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# PLACEMENT EN BOUTIQUE
#
# Clé = nom exact de la boutique (cf. initShops.py)
# Valeur = liste de tuples :
#   (nom_item, badge_requis, stock, featured, is_new)
# ─────────────────────────────────────────────────────────────────────────────
SHOP_PLACEMENTS = {

    # ── Jadielle : baies de statut basiques dès le début ──────────────────
    "PokéMart de Jadielle": [
        ("Baie Oran",      0, -1, False, True),
        ("Baie Pêche",     0, -1, False, False),
        ("Baie Mepo",      0, -1, False, False),
        ("Baie Gribi",     0, -1, False, False),
        ("Baie Rago",      0, -1, False, False),
        ("Baie Glace",     0, -1, False, False),
    ],

    # ── Argenta : idem, + Charbon (fire boost pour early Charmander) ──────
    "PokéMart d'Argenta": [
        ("Baie Oran",      0, -1, False, False),
        ("Baie Pêche",     0, -1, False, False),
        ("Baie Gribi",     0, -1, False, False),
        ("Charbon",        1, -1, True,  True),   # 1 badge requis
    ],

    # ── Azuria : Herbe Miracle (Plante) + Oran/statut ─────────────────────
    "PokéMart d'Azuria": [
        ("Baie Oran",      0, -1, False, False),
        ("Baie Pêche",     0, -1, False, False),
        ("Baie Mepo",      0, -1, False, False),
        ("Herbe Miracle",  1, -1, True,  True),
    ],

    # ── Carmin sur Mer : Eau Mystique (Water boost, SS Anne) ──────────────
    "PokéMart de Carmin sur Mer": [
        ("Baie Sitrus",    2, -1, True,  True),
        ("Eau Mystique",   2, -1, True,  True),
        ("Baie Pêche",     0, -1, False, False),
    ],

    # ── Lavanville : Baie Lum (statut mixte, utile Tour Pokémon) ─────────
    "PokéMart de Lavanville": [
        ("Baie Lum",       3, -1, True,  True),
        ("Baie Sitrus",    3, -1, False, False),
    ],

    # ── Céladopole 2F Soins : Baies sustain haut de gamme ─────────────────
    "Grand Magasin de Céladopole — 2F Soins": [
        ("Baie Sitrus",    3, -1, True,  False),
        ("Baie Lum",       3, -1, True,  False),
        ("Baie Pêche",     0, -1, False, False),
        ("Baie Mepo",      0, -1, False, False),
        ("Baie Gribi",     0, -1, False, False),
        ("Baie Rago",      0, -1, False, False),
        ("Baie Glace",     0, -1, False, False),
    ],

    # ── Céladopole 4F Combat : boosts de type offensifs ───────────────────
    "Grand Magasin de Céladopole — 4F Combat": [
        ("Charbon",        3, -1, False, True),
        ("Aimant",         3, -1, False, True),
        ("Eau Mystique",   3, -1, False, False),
        ("Filtre Miroir",  4, -1, False, True),
        ("Herbe Miracle",  3, -1, False, False),
        ("Écharpe Soie",   3, -1, False, False),
        ("Baie Yache",     4, -1, False, False),
        ("Baie Chople",    4, -1, False, False),
    ],

    # ── Safrania : Filtre Miroir (Psy, ville psy), sustain ────────────────
    "PokéMart de Safrania": [
        ("Filtre Miroir",  5, -1, True,  True),
        ("Baie Lum",       5, -1, False, False),
        ("Baie Sitrus",    5, -1, False, False),
    ],

    # ── Parmanie : Aimant (Zone Safari, eau/insecte), boosts ──────────────
    "PokéMart de Parmanie": [
        ("Aimant",         5, -1, True,  True),
        ("Eau Mystique",   5, -1, False, False),
        ("Baie Lum",       5, -1, False, False),
        ("Baie Yache",     5, -1, False, True),
        ("Baie Chople",    5, -1, False, True),
    ],

    # ── Cramois'Île : Écharpe Soie (Normal boost), items haut niveau ──────
    "PokéMart de Cramois'Île": [
        ("Écharpe Soie",   7, -1, True,  True),
        ("Baie Lum",       7, -1, False, False),
        ("Baie Sitrus",    7, -1, False, False),
    ],

    # ── Plateau Indigo : tout le haut de gamme ────────────────────────────
    "PokéMart du Plateau Indigo": [
        ("Bandeau Choix",  8, -1, True,  True),
        ("Lunettes Choix", 8, -1, True,  True),
        ("Foulard Choix",  8, -1, True,  True),
        ("Orbe Vie",       8, -1, True,  True),
        ("Veste Assaut",   8, -1, False, True),
        ("Baie Lum",       8, -1, False, False),
        ("Baie Sitrus",    8, -1, False, False),
        ("Baie Yache",     8, -1, False, False),
        ("Baie Chople",    8, -1, False, False),
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# FONCTION PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────

def initHeldItems():
    print("\n🎒 Initialisation des Objets Tenus (Held Items)...")

    item_map: dict[str, Item] = {}

    # ── 1. Créer / mettre à jour les Items ───────────────────────────────
    for data in HELD_ITEMS_DATA:
        item, created = Item.objects.update_or_create(
            name=data["name"],
            defaults={
                "description":   data["description"],
                "item_type":     "held",
                "price":         data["price"],
                "held_effect":   data["held_effect"],
                "is_consumable": data["is_consumable"],
            },
        )
        marker = "✅ créé" if created else "🔄 mis à jour"
        print(f"  {marker} : {item.name} [{item.held_effect}]")
        item_map[item.name] = item

    # ── 2. Placement en boutique ──────────────────────────────────────────
    print("\n🏪 Placement dans les boutiques...")
    placed = 0

    for shop_name, entries in SHOP_PLACEMENTS.items():
        shop = Shop.objects.filter(name=shop_name).first()
        if not shop:
            print(f"  ⚠️  Boutique introuvable : '{shop_name}' — ignorée")
            continue

        for cfg in entries:
            item_name    = cfg[0]
            badge_req    = cfg[1] if len(cfg) > 1 else 0
            stock        = cfg[2] if len(cfg) > 2 else -1
            featured     = cfg[3] if len(cfg) > 3 else False
            is_new       = cfg[4] if len(cfg) > 4 else False

            item = item_map.get(item_name)
            if not item:
                item = Item.objects.filter(name=item_name).first()
            if not item:
                print(f"    ❌ Item introuvable : '{item_name}'")
                continue

            _, inv_created = ShopInventory.objects.update_or_create(
                shop=shop,
                item=item,
                defaults={
                    "stock":                   stock,
                    "unlock_badge_required":   badge_req,
                    "is_featured":             featured,
                    "is_new":                  is_new,
                    "unlock_condition":        "none",
                },
            )
            if inv_created:
                print(f"    ➕ {item.name} → {shop.name} (badge {badge_req})")
            placed += 1

    print(f"\n✅ {len(HELD_ITEMS_DATA)} held items initialisés, {placed} entrées boutique.")