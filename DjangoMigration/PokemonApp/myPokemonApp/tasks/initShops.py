from myPokemonApp.models import Shop, ShopInventory, Item, PokemonType

import logging

logging.basicConfig(level=logging.INFO)


def initShops():
    # Créer une boutique
    shop = Shop.objects.create(
        name="PokéMart de Bourg Palette",
        shop_type='pokemart',
        location='Bourg Palette',
        description='Votre boutique de confiance pour tous vos besoins de Dresseur !',
        shopkeeper_greeting='Bienvenue au PokéMart ! Comment puis-je vous aider aujourd\'hui ?'
    )

    # Créer des objets si pas déjà créés
    potion, _ = Item.objects.get_or_create(
        name='Potion',
        defaults={
            'description': 'Restaure 20 HP d\'un Pokémon',
            'item_type': 'potion',
            'price': 300,
            'heal_amount': 20,
            'is_consumable': True
        }
    )

    super_potion, _ = Item.objects.get_or_create(
        name='Super Potion',
        defaults={
            'description': 'Restaure 50 HP d\'un Pokémon',
            'item_type': 'potion',
            'price': 700,
            'heal_amount': 50,
            'is_consumable': True
        }
    )

    pokeball, _ = Item.objects.get_or_create(
        name='Poké Ball',
        defaults={
            'description': 'Une Ball pour capturer des Pokémon sauvages',
            'item_type': 'pokeball',
            'price': 200,
            'catch_rate_modifier': 1.0,
            'is_consumable': True
        }
    )

    great_ball, _ = Item.objects.get_or_create(
        name='Super Ball',
        defaults={
            'description': 'Une Ball avec un meilleur taux de capture',
            'item_type': 'pokeball',
            'price': 600,
            'catch_rate_modifier': 1.5,
            'is_consumable': True
        }
    )

    antidote, _ = Item.objects.get_or_create(
        name='Antidote',
        defaults={
            'description': 'Guérit l\'empoisonnement',
            'item_type': 'status',
            'price': 100,
            'cures_status': True,
            'specific_status': 'poison',
            'is_consumable': True
        }
    )

    # Ajouter les objets à l'inventaire de la boutique
    ShopInventory.objects.create(
        shop=shop,
        item=potion,
        stock=-1,  # Stock illimité
        unlock_badge_required=0,
        is_featured=True
    )

    ShopInventory.objects.create(
        shop=shop,
        item=super_potion,
        stock=-1,
        unlock_badge_required=1,
        is_new=True
    )

    ShopInventory.objects.create(
        shop=shop,
        item=pokeball,
        stock=-1,
        unlock_badge_required=0,
        is_featured=True
    )

    ShopInventory.objects.create(
        shop=shop,
        item=great_ball,
        stock=50,  # Stock limité
        unlock_badge_required=2,
        discount_percentage=10  # -10%
    )

    ShopInventory.objects.create(
        shop=shop,
        item=antidote,
        stock=-1,
        unlock_badge_required=0
    )

    logging.info("[+] Boutique et inventaire créés avec succès!")