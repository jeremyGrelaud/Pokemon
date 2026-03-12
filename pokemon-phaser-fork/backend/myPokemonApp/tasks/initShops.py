"""
Initialise tous les PokéMarts de Kanto Gen 1.

Assortiments fidèles au jeu original (R/B/J + FRLG) tout en intégrant
les items Gen 3+ présents en base (Net Ball, Timer Ball…).

Nomenclature des items : exactement ceux créés par initialize_items()
(initializeItemsAndNpcs.py) — tout écart génère un warning au runtime.

Progression par ville :
  Jadielle        → Pokédex requis pour les Poké Balls
  Argenta         → 0 badge (1ère ville avec arène)
  Azuria          → après 1er badge (Azuria ouvre ses portes)
  Carmin sur Mer  → après 2e badge
  Lavanville      → après 2e badge
  Céladopole (GM) → après 3e badge pour les meilleurs items
  Safrania        → après 5e badge
  Parmanie        → après 5e badge
  Cramois'Île     → après 7e badge
  Jadielle revisit→ après 7e badge (même PokéMart mais réassort complet)
  Plateau Indigo  → 8 badges
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
    Ajoute des items à l'inventaire d'une boutique (idempotent).

    items_config = liste de tuples :
        (nom_item, badge_requis, stock, featured, is_new, discount, unlock_condition)

    Valeurs par défaut : badge=0, stock=-1, featured=False, is_new=False,
                         discount=0, unlock_condition='none'
    unlock_condition : 'none' | 'has_pokedex'
    """
    for cfg in items_config:
        item_name        = cfg[0]
        badge_req        = cfg[1] if len(cfg) > 1 else 0
        stock            = cfg[2] if len(cfg) > 2 else -1
        featured         = cfg[3] if len(cfg) > 3 else False
        is_new           = cfg[4] if len(cfg) > 4 else False
        discount         = cfg[5] if len(cfg) > 5 else 0
        unlock_condition = cfg[6] if len(cfg) > 6 else 'none'

        item = _get_item(item_name)
        if not item:
            continue

        ShopInventory.objects.get_or_create(
            shop=shop,
            item=item,
            defaults={
                'stock':                 stock,
                'unlock_badge_required': badge_req,
                'unlock_condition':      unlock_condition,
                'is_featured':           featured,
                'is_new':                is_new,
                'discount_percentage':   discount,
            }
        )


def initShops():
    """Crée tous les PokéMarts de Kanto avec leur assortiment."""

    logging.info("🏪 Initialisation des boutiques de Kanto...")

    # =========================================================================
    # JADIELLE — PokéMart basique
    # Ouvre après la livraison du Parcel du Prof. Chen.
    # Les Poké Balls nécessitent le Pokédex (story_flag 'has_pokedex').
    # =========================================================================
    shop = _create_shop(
        "PokéMart de Jadielle", "Jadielle",
        greeting="Je ne vends des Poke Balls qu'aux Dresseurs qui ont un Pokédex !"
    )
    _add_items(shop, [
        # (item, badge_requis, stock, featured, is_new, discount, unlock_condition)
        ('Poke Ball',   0, -1, True,  False, 0, 'has_pokedex'),
        ('Potion',      0, -1, True,  False, 0, 'none'),
        ('Antidote',    0, -1, False, False, 0, 'none'),
        ('Burn Heal',   0, -1, False, False, 0, 'none'),
        ('Escape Rope', 0, -1, False, False, 0, 'none'),
        ('Repel',       0, -1, False, False, 0, 'none'),
    ])

    # =========================================================================
    # ARGENTA (Pewter City) — Après 1er badge
    # =========================================================================
    shop = _create_shop(
        "PokéMart d'Argenta", "Argenta",
        greeting="Bienvenue ! Les Dresseurs sérieux font leurs emplettes ici !"
    )
    _add_items(shop, [
        ('Poke Ball',     0, -1, True),
        ('Potion',        0, -1, True),
        ('Antidote',      0, -1, False),
        ('Burn Heal',     0, -1, False),
        ('Paralyze Heal', 0, -1, False),
        ('Escape Rope',   0, -1, False),
        ('Repel',         0, -1, False),
    ])

    # =========================================================================
    # AZURIA (Cerulean City) — Après 1er badge
    # =========================================================================
    shop = _create_shop(
        "PokéMart d'Azuria", "Azuria",
        greeting="Azuria est une ville de chercheurs — et de bons achats !"
    )
    _add_items(shop, [
        ('Poke Ball',     0, -1, True),
        ('Potion',        0, -1, True),
        ('Super Potion',  1, -1, False, True),
        ('Antidote',      0, -1, False),
        ('Burn Heal',     0, -1, False),
        ('Ice Heal',      0, -1, False),
        ('Paralyze Heal', 0, -1, False),
        ('Escape Rope',   0, -1, False),
        ('Repel',         0, -1, False),
    ])

    # =========================================================================
    # CARMIN SUR MER (Vermilion City) — Après 2e badge
    # =========================================================================
    shop = _create_shop(
        "PokéMart de Carmin sur Mer", "Carmin sur Mer",
        greeting="Port de Carmin ! Les marins savent quoi acheter. Vous aussi ?"
    )
    _add_items(shop, [
        ('Poke Ball',     0, -1, True),
        ('Super Potion',  0, -1, True),
        ('Antidote',      0, -1, False),
        ('Burn Heal',     0, -1, False),
        ('Ice Heal',      0, -1, False),
        ('Awakening',     0, -1, False),
        ('Paralyze Heal', 0, -1, False),
        ('Super Repel',   2, -1, False, True),
        ('Escape Rope',   0, -1, False),
        ('Great Ball',    2, -1, False, True),
    ])

    # =========================================================================
    # LAVANVILLE (Lavender Town) — Après 3e badge
    # Ville triste proche de la Tour Pokémon — stock utile pour l'exploration.
    # =========================================================================
    shop = _create_shop(
        "PokéMart de Lavanville", "Lavanville",
        greeting="Cette ville est triste, mais notre boutique, elle, est bien achalandée !"
    )
    _add_items(shop, [
        ('Poke Ball',     0, -1, True),
        ('Super Potion',  0, -1, True),
        ('Revive',        0, -1, False, True),
        ('Antidote',      0, -1, False),
        ('Burn Heal',     0, -1, False),
        ('Ice Heal',      0, -1, False),
        ('Awakening',     0, -1, False),
        ('Paralyze Heal', 0, -1, False),
        ('Full Heal',     3, -1, False),
        ('Escape Rope',   0, -1, False),
        ('Super Repel',   0, -1, False),
        ('Great Ball',    3, -1, False),
        # Balls utiles pour la Tour Pokémon (nuit/grotte)
        ('Dusk Ball',     3, -1, False, True),
    ])

    # =========================================================================
    # CÉLADOPOLE (Celadon City) — Grand Magasin (plusieurs rayons)
    # =========================================================================

    # 2F — Soins & Statuts
    shop = _create_shop(
        "Grand Magasin de Céladopole — 2F Soins", "Céladopole",
        shop_type='department_store',
        description="Grand Magasin de Céladopole, 2F — Potions et soins de statut.",
        greeting="Bonjour et bienvenue au Grand Magasin de Céladopole !"
    )
    _add_items(shop, [
        ('Potion',        0, -1, False),
        ('Super Potion',  0, -1, True),
        ('Hyper Potion',  4, -1, False, True),
        ('Full Restore',  6, -1, False),
        ('Revive',        0, -1, False),
        ('Max Revive',    6, -1, False, True),
        ('Antidote',      0, -1, False),
        ('Paralyze Heal', 0, -1, False),
        ('Burn Heal',     0, -1, False),
        ('Ice Heal',      0, -1, False),
        ('Awakening',     0, -1, False),
        ('Full Heal',     0, -1, False),
    ])

    # 3F — Poké Balls
    shop = _create_shop(
        "Grand Magasin de Céladopole — 3F Balls", "Céladopole",
        shop_type='department_store',
        description="Grand Magasin Céladopole, 3F — Poké Balls.",
        greeting="Vous cherchez la meilleure Ball ? Vous êtes au bon endroit !"
    )
    _add_items(shop, [
        ('Poke Ball',   0, -1, False),
        ('Great Ball',  0, -1, True),
        ('Ultra Ball',  4, -1, False, True),
        ('Net Ball',    3, -1, False, True),
        ('Repeat Ball', 3, -1, False, True),
        ('Timer Ball',  4, -1, False),
        ('Dusk Ball',   3, -1, False),
        ('Quick Ball',  4, -1, False),
        ('Luxury Ball', 4, -1, False),
    ])

    # 4F — Objets de Combat
    shop = _create_shop(
        "Grand Magasin de Céladopole — 4F Combat", "Céladopole",
        shop_type='department_store',
        description="Grand Magasin Céladopole, 4F — Objets de combat.",
        greeting="Pour booster vos Pokémon en combat, c'est ici !"
    )
    _add_items(shop, [
        ('X Attack',    0, -1, False),
        ('X Defense',   0, -1, False),
        ('X Speed',     0, -1, False),
        ('X Special',   0, -1, False),
        ('Guard Spec.', 0, -1, False),
        ('Dire Hit',    0, -1, False),
    ])

    # 5F — Répulsifs & PP
    shop = _create_shop(
        "Grand Magasin de Céladopole — 5F Divers", "Céladopole",
        shop_type='department_store',
        description="Grand Magasin Céladopole, 5F — Répulsifs, PP et divers.",
        greeting="Nous avons tout ce dont vous avez besoin pour votre aventure !"
    )
    _add_items(shop, [
        ('Repel',       0, -1, False),
        ('Super Repel', 0, -1, False),
        ('Max Repel',   4, -1, False, True),
        ('Escape Rope', 0, -1, False),
        ('Ether',       0, -1, False),
        ('Max Ether',   4, -1, False, True),
        ('Elixir',      4, -1, False),
        ('Max Elixir',  6, -1, False, True),
        ('PP Up',       4, -1, False),
    ])

    # 6F — Pierres d'Évolution
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
    # SAFRANIA (Saffron City) — Après 5e badge
    # Dans le jeu original, Safrania n'a pas de PokéMart propre (Sylphe Co.)
    # On propose une boutique de qualité accessible après libération de la ville.
    # =========================================================================
    shop = _create_shop(
        "PokéMart de Safrania", "Safrania",
        greeting="Safrania n'a jamais pris de pause, et nous non plus !"
    )
    _add_items(shop, [
        ('Great Ball',    0, -1, True),
        ('Ultra Ball',    5, -1, False, True),
        ('Super Potion',  0, -1, False),
        ('Hyper Potion',  5, -1, False, True),
        ('Revive',        0, -1, False),
        ('Full Heal',     0, -1, False),
        ('Paralyze Heal', 0, -1, False),
        ('Super Repel',   0, -1, False),
        ('Max Repel',     5, -1, False),
        ('Escape Rope',   0, -1, False),
        ('Ether',         0, -1, False),
        ('Elixir',        5, -1, False, True),
        ('Timer Ball',    5, -1, False),
        ('Repeat Ball',   5, -1, False),
    ])

    # =========================================================================
    # PARMANIE (Fuchsia City) — Après 5e badge
    # Proche de la Zone Safari — bon stock de balls et de soins.
    # =========================================================================
    shop = _create_shop(
        "PokéMart de Parmanie", "Parmanie",
        greeting="La Zone Safari est épuisante. Réapprovisionnez-vous ici !"
    )
    _add_items(shop, [
        ('Great Ball',   0, -1, True),
        ('Ultra Ball',   5, -1, False, True),
        ('Net Ball',     0, -1, False, True),  # utile pour la Zone Safari (type Eau/Insecte)
        ('Hyper Potion', 0, -1, True),
        ('Max Potion',   6, -1, False, True),
        ('Revive',       0, -1, False),
        ('Full Heal',    0, -1, False),
        ('Max Repel',    0, -1, False),
        ('Escape Rope',  0, -1, False),
        ('Elixir',       0, -1, False),
    ])

    # =========================================================================
    # CRAMOIS'ÎLE (Cinnabar Island) — Après 7e badge
    # Stock limité mais haut de gamme, proche du dernier badge.
    # =========================================================================
    shop = _create_shop(
        "PokéMart de Cramois'Île", "Cramois'Île",
        greeting="Bienvenue sur l'île ! Le stock est limité mais de qualité !"
    )
    _add_items(shop, [
        ('Ultra Ball',   0, -1, True),
        ('Hyper Potion', 0, -1, True),
        ('Max Potion',   7, -1, False, True),
        ('Full Restore', 7, -1, False),
        ('Revive',       0, -1, False),
        ('Max Revive',   7, -1, False, True),
        ('Full Heal',    0, -1, False),
        ('Max Repel',    0, -1, False),
        ('Escape Rope',  0, -1, False),
        ('Elixir',       0, -1, False),
        ('Max Elixir',   7, -1, False, True),
        # Balls spéciales utiles avant le dernier badge
        ('Dusk Ball',    7, -1, False),
        ('Quick Ball',   7, -1, False),
    ])

    # =========================================================================
    # JADIELLE — Réassortiment après 7e badge
    # Le même PokéMart, mais réouverte avec un stock de Champions.
    # =========================================================================
    shop = _create_shop(
        "PokéMart de Jadielle — Champions", "Jadielle",
        greeting="Vous avez 7 badges ! Vous méritez notre meilleur stock !"
    )
    _add_items(shop, [
        ('Ultra Ball',   7, -1, True),
        ('Full Restore', 7, -1, True),
        ('Max Revive',   7, -1, True),
        ('Max Potion',   7, -1, False),
        ('Full Heal',    7, -1, False),
        ('Max Repel',    7, -1, False),
        ('Max Elixir',   7, -1, False, True),
        ('Escape Rope',  7, -1, False),
        ('PP Up',        7, -1, False),
        ('X Attack',     7, -1, False),
        ('X Defense',    7, -1, False),
        ('X Speed',      7, -1, False),
        ('Guard Spec.',  7, -1, False),
    ])

    # =========================================================================
    # PLATEAU INDIGO — La boutique des Champions
    # =========================================================================
    shop = _create_shop(
        "PokéMart du Plateau Indigo", "Plateau Indigo",
        greeting="Seuls les meilleurs Dresseurs arrivent ici. Voici ce qu'il vous faut !"
    )
    _add_items(shop, [
        ('Ultra Ball',   8, -1, True),
        ('Full Restore', 8, -1, True),
        ('Max Revive',   8, -1, True),
        ('Max Potion',   8, -1, False),
        ('Full Heal',    8, -1, False),
        ('Max Repel',    8, -1, False),
        ('Escape Rope',  8, -1, False),
        ('Max Elixir',   8, -1, False),
        ('PP Up',        8, -1, False),
        ('PP Max',       8, -1, False, True),
        ('X Attack',     8, -1, False),
        ('X Defense',    8, -1, False),
        ('X Speed',      8, -1, False),
        ('X Special',    8, -1, False),
        ('Guard Spec.',  8, -1, False),
        ('Dire Hit',     8, -1, False),
    ])

    logging.info("\n✅ Boutiques de Kanto initialisées !")