"""
Initialise tous les PokéMarts de Kanto Gen 1.
Chaque ville a sa boutique avec un assortiment progressif selon les badges.
Le Grand Magasin de Céladopole a plusieurs rayons.
"""

from myPokemonApp.models import Shop, ShopInventory, Item
import logging

logging.basicConfig(level=logging.INFO)


def _get_item(name):
    """Helper : retourne l'Item par nom exact, ou None avec warning."""
    item = Item.objects.filter(name=name).first()
    if not item:
        logging.warning(f"[!] Item introuvable : '{name}'")
    return item


def _create_shop(name, location, shop_type='pokemart',
                 description=None, greeting=None):
    """Helper : crée ou récupère une boutique."""
    shop, created = Shop.objects.get_or_create(
        name=name,
        defaults={
            'shop_type': shop_type,
            'location': location,
            'description': description or f"Le PokéMart de {location}.",
            'shopkeeper_greeting': greeting or "Bienvenue ! Comment puis-je vous aider ?",
        }
    )
    logging.info(f"  {'✅' if created else '⭕'} {name}")
    return shop


def _add_items(shop, items_config):
    """
    Helper : ajoute des items à l'inventaire d'une boutique.
    items_config = [
        (nom_item, badge_requis, stock, featured, is_new, discount),
        ...
    ]
    """
    for cfg in items_config:
        item_name = cfg[0]
        badge_req = cfg[1] if len(cfg) > 1 else 0
        stock     = cfg[2] if len(cfg) > 2 else -1   # -1 = illimité
        featured  = cfg[3] if len(cfg) > 3 else False
        is_new    = cfg[4] if len(cfg) > 4 else False
        discount  = cfg[5] if len(cfg) > 5 else 0

        item = _get_item(item_name)
        if not item:
            continue

        ShopInventory.objects.get_or_create(
            shop=shop,
            item=item,
            defaults={
                'stock': stock,
                'unlock_badge_required': badge_req,
                'is_featured': featured,
                'is_new': is_new,
                'discount_percentage': discount,
            }
        )


def initShops():
    """Crée tous les PokéMarts de Kanto avec leur assortiment."""

    logging.info("🏪 Initialisation des boutiques de Kanto...")

    # =========================================================================
    # JADIELLE — Boutique basique (disponible après la livraison du Parcel)
    # =========================================================================
    shop = _create_shop(
        "PokéMart de Jadielle", "Jadielle",
        greeting="Je ne vends des Poké Balls qu'aux Dresseurs qui ont un Pokédex !"
    )
    _add_items(shop, [
        # (item, badge_requis, stock, featured)
        ('Poké Ball',    0, -1, True),
        ('Potion',       0, -1, True),
        ('Antidote',     0, -1, False),
        ('Repel',        0, -1, False),
        ('Escape Rope',  0, -1, False),
    ])

    # =========================================================================
    # ARGENTA — Après 1er badge
    # =========================================================================
    shop = _create_shop(
        "PokéMart d'Argenta", "Argenta",
        greeting="Bienvenue ! Les Dresseurs sérieux font leurs emplettes ici !"
    )
    _add_items(shop, [
        ('Potion',       0, -1, True),
        ('Super Potion', 1, -1, False),
        ('Antidote',     0, -1, False),
        ('Paralyze Heal', 0, -1, False),
        ('Repel',        0, -1, False),
        ('Escape Rope',  0, -1, False),
        ('Poké Ball',    0, -1, True),
    ])

    # =========================================================================
    # AZURIA — Après 2e badge
    # =========================================================================
    shop = _create_shop(
        "PokéMart d'Azuria", "Azuria",
        greeting="Azuria est une ville de chercheurs — et de bons achats !"
    )
    _add_items(shop, [
        ('Potion',        0, -1, True),
        ('Super Potion',  0, -1, False, False, True),
        ('Antidote',      0, -1, False),
        ('Paralyze Heal', 0, -1, False),
        ('Repel',         0, -1, False),
        ('Super Repel',   2, -1, False),
        ('Escape Rope',   0, -1, False),
        ('Poké Ball',     0, -1, True),
        ('Great Ball',    2, -1, False, True),
    ])

    # =========================================================================
    # CARMIN SUR MER — Après 3e badge
    # =========================================================================
    shop = _create_shop(
        "PokéMart de Carmin sur Mer", "Carmin sur Mer",
        greeting="Port de Carmin ! Les marins savent quoi acheter. Vous aussi ?"
    )
    _add_items(shop, [
        ('Super Potion',  0,  -1, True),
        ('Antidote',      0,  -1, False),
        ('Paralyze Heal', 0,  -1, False),
        ('Burn Heal',     0,  -1, False),
        ('Ice Heal',      0,  -1, False),
        ('Awakening',     0,  -1, False),
        ('Super Repel',   0,  -1, False),
        ('Escape Rope',   0,  -1, False),
        ('Poké Ball',     0,  -1, True),
        ('Great Ball',    0,  -1, False, True),
        ('Ether',         3,  -1, False),
    ])

    # =========================================================================
    # LAVANVILLE — Après 3e badge
    # =========================================================================
    shop = _create_shop(
        "PokéMart de Lavanville", "Lavanville",
        greeting="Cette ville est triste, mais notre boutique, elle, est bien achalandée !"
    )
    _add_items(shop, [
        ('Super Potion',  0,  -1, True),
        ('Revive',        0,  -1, False, True),
        ('Antidote',      0,  -1, False),
        ('Paralyze Heal', 0,  -1, False),
        ('Full Heal',     3,  -1, False),
        ('Super Repel',   0,  -1, False),
        ('Escape Rope',   0,  -1, False),
        ('Poké Ball',     0,  -1, True),
        ('Great Ball',    0,  -1, False),
    ])

    # =========================================================================
    # CÉLADOPOLE — Grand Magasin (6 rayons)
    # =========================================================================

    # Rayon 2F — Articles courants
    shop = _create_shop(
        "Grand Magasin de Céladopole — 2F Articles", "Céladopole",
        shop_type='department_store',
        description="Le Grand Magasin de Céladopole, 2F — Articles courants.",
        greeting="Bonjour et bienvenue au Grand Magasin ! Comment puis-je vous aider ?"
    )
    _add_items(shop, [
        ('Potion',        0, -1, True),
        ('Super Potion',  0, -1, False),
        ('Hyper Potion',  4, -1, False, True),
        ('Full Restore',  6, -1, False),
        ('Revive',        0, -1, False),
        ('Antidote',      0, -1, False),
        ('Paralyze Heal', 0, -1, False),
        ('Burn Heal',     0, -1, False),
        ('Ice Heal',      0, -1, False),
        ('Awakening',     0, -1, False),
        ('Full Heal',     0, -1, False),
    ])

    # Rayon 3F — Poké Balls
    shop = _create_shop(
        "Grand Magasin de Céladopole — 3F Balls", "Céladopole",
        shop_type='department_store',
        description="Grand Magasin Céladopole, 3F — Poké Balls.",
        greeting="Vous cherchez la meilleure Ball ? Vous êtes au bon endroit !"
    )
    _add_items(shop, [
        ('Poké Ball',  0, -1, True),
        ('Great Ball', 0, -1, False, True),
        ('Ultra Ball', 4, -1, False, False, 5),
    ])

    # Rayon 4F — Objets de combat
    shop = _create_shop(
        "Grand Magasin de Céladopole — 4F Combat", "Céladopole",
        shop_type='department_store',
        description="Grand Magasin Céladopole, 4F — Objets de combat.",
        greeting="Pour booster vos Pokémon en combat, c'est ici !"
    )
    _add_items(shop, [
        ('X Attack',   0, -1, False),
        ('X Defense',  0, -1, False),
        ('X Speed',    0, -1, False),
        ('X Special',  0, -1, False),
        ('Guard Spec.', 0, -1, False),
        ('Dire Hit',   0, -1, False),
    ])

    # Rayon 5F — Répulsifs & Divers
    shop = _create_shop(
        "Grand Magasin de Céladopole — 5F Divers", "Céladopole",
        shop_type='department_store',
        description="Grand Magasin Céladopole, 5F — Répulsifs et divers.",
        greeting="Nous avons tout ce dont vous avez besoin pour votre aventure !"
    )
    _add_items(shop, [
        ('Repel',     0, -1, False),
        ('Super Repel', 0, -1, False),
        ('Max Repel', 4, -1, False, True),
        ('Escape Rope', 0, -1, False),
        ('Ether',     0, -1, False),
        ('Max Ether', 4, -1, False, True),
        ('Elixir',    4, -1, False),
        ('Max Elixir', 6, -1, False, True),
        ('PP Up',     4, -1, False),
    ])

    # Rayon 6F — Pierres d'évolution
    shop = _create_shop(
        "Grand Magasin de Céladopole — 6F Pierres", "Céladopole",
        shop_type='department_store',
        description="Grand Magasin Céladopole, 6F — Pierres d'évolution.",
        greeting="Nos pierres d'évolution sont les meilleures de Kanto !"
    )
    _add_items(shop, [
        ('Fire Stone',    0, 5, True),
        ('Water Stone',   0, 5, True),
        ('Thunder Stone', 0, 5, True),
        ('Leaf Stone',    0, 5, True),
        ('Moon Stone',    0, 3, False),
    ])

    # =========================================================================
    # SAFRANIA — Après 5e badge
    # =========================================================================
    shop = _create_shop(
        "PokéMart de Safrania", "Safrania",
        greeting="Safrania n'a jamais pris de pause, et nous non plus !"
    )
    _add_items(shop, [
        ('Super Potion',  0,  -1, True),
        ('Hyper Potion',  5,  -1, False, True),
        ('Revive',        0,  -1, False),
        ('Full Heal',     0,  -1, False),
        ('Super Repel',   0,  -1, False),
        ('Max Repel',     5,  -1, False),
        ('Escape Rope',   0,  -1, False),
        ('Great Ball',    0,  -1, True),
        ('Ultra Ball',    5,  -1, False, True),
        ('Ether',         0,  -1, False),
        ('Elixir',        5,  -1, False, True),
    ])

    # =========================================================================
    # Parmanie — Après 5e badge
    # =========================================================================
    shop = _create_shop(
        "PokéMart de Parmanie", "Parmanie",
        greeting="La Zone Safari est épuisante. Réapprovisionnez-vous ici !"
    )
    _add_items(shop, [
        ('Hyper Potion',  0,  -1, True),
        ('Max Potion',    6,  -1, False, True),
        ('Revive',        0,  -1, False),
        ('Full Heal',     0,  -1, False),
        ('Max Repel',     0,  -1, False),
        ('Escape Rope',   0,  -1, False),
        ('Great Ball',    0,  -1, True),
        ('Ultra Ball',    0,  -1, False, True),
        ('Elixir',        0,  -1, False),
    ])

    # =========================================================================
    # CRAMOIS'ÎLE — Après 7e badge
    # =========================================================================
    shop = _create_shop(
        "PokéMart de Cramois'Île", "Cramois'Île",
        greeting="Bienvenue sur l'île ! Le stock est limité mais de qualité !"
    )
    _add_items(shop, [
        ('Hyper Potion',  0,  -1, True),
        ('Max Potion',    7,  -1, False, True),
        ('Revive',        0,  -1, False),
        ('Max Revive',    7,  -1, False, True),
        ('Full Heal',     0,  -1, False),
        ('Max Repel',     0,  -1, False),
        ('Ultra Ball',    0,  -1, True),
        ('Elixir',        0,  -1, False),
        ('Max Elixir',    7,  -1, False, True),
    ])

    # =========================================================================
    # PLATEAU INDIGO — La boutique des Champions
    # =========================================================================
    shop = _create_shop(
        "PokéMart du Plateau Indigo", "Plateau Indigo",
        greeting="Seuls les meilleurs Dresseurs arrivent ici. Voici ce qu'il vous faut !"
    )
    _add_items(shop, [
        ('Full Restore',  8,  -1, True),
        ('Max Revive',    8,  -1, True),
        ('Max Potion',    8,  -1, False),
        ('Full Heal',     8,  -1, False),
        ('Max Repel',     8,  -1, False),
        ('Ultra Ball',    8,  -1, True),
        ('Max Elixir',    8,  -1, False),
        ('PP Up',         8,  -1, False),
        ('X Attack',      8,  -1, False),
        ('X Defense',     8,  -1, False),
        ('X Speed',       8,  -1, False),
    ])

    logging.info("\n✅ Boutiques de Kanto initialisées !")