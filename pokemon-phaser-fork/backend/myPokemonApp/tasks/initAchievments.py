"""
Initialise tous les achievements du jeu
"""

from myPokemonApp.models import Achievement

import logging

logging.basicConfig(level=logging.INFO)

def init_achievements():
    """Crée tous les succès"""
    
    logging.info("🏆 Initialisation des achievements...")
    
    achievements = [
        # ===== COMBAT =====
        {
            'name': 'Premier Combat',
            'description': 'Gagner votre premier combat',
            'category': 'combat',
            'required_value': 1,
            'reward_money': 500,
            'icon': 'fist-raised',
            'order': 1,
        },
        {
            'name': 'Combattant Aguerri',
            'description': 'Gagner 50 combats',
            'category': 'combat',
            'required_value': 50,
            'reward_money': 5000,
            'icon': 'trophy',
            'order': 2,
        },
        {
            'name': 'Vétéran',
            'description': 'Gagner 100 combats',
            'category': 'combat',
            'required_value': 100,
            'reward_money': 10000,
            'icon': 'medal',
            'order': 3,
        },
        
        # ===== CAPTURE =====
        {
            'name': 'Premier Compagnon',
            'description': 'Capturer votre premier Pokémon',
            'category': 'capture',
            'required_value': 1,
            'reward_money': 300,
            'icon': 'network-wired',
            'order': 10,
        },
        {
            'name': 'Collectionneur Débutant',
            'description': 'Capturer 10 Pokémon',
            'category': 'capture',
            'required_value': 10,
            'reward_money': 1000,
            'icon': 'box',
            'order': 11,
        },
        {
            'name': 'Collectionneur Expert',
            'description': 'Capturer 50 Pokémon',
            'category': 'capture',
            'required_value': 50,
            'reward_money': 5000,
            'icon': 'boxes',
            'order': 12,
        },
        
        # ===== COLLECTION =====
        {
            'name': 'Dresseur Complet',
            'description': 'Avoir une équipe de 6 Pokémon',
            'category': 'collection',
            'required_value': 6,
            'reward_money': 1000,
            'icon': 'users',
            'order': 20,
        },
        {
            'name': 'Connaisseur',
            'description': 'Posséder 50 espèces différentes',
            'category': 'collection',
            'required_value': 50,
            'reward_money': 8000,
            'icon': 'book',
            'order': 21,
        },
        {
            'name': 'Maître Pokémon',
            'description': 'Compléter le Pokédex (151)',
            'category': 'collection',
            'required_value': 151,
            'reward_money': 50000,
            'icon': 'crown',
            'order': 22,
            'is_hidden': True,
        },
        
        # ===== EXPLORATION =====
        {
            'name': 'Explorateur',
            'description': 'Visiter 10 zones différentes',
            'category': 'exploration',
            'required_value': 10,
            'reward_money': 2000,
            'icon': 'map',
            'order': 30,
        },
        {
            'name': 'Globe-Trotter',
            'description': 'Visiter toutes les zones de Kanto',
            'category': 'exploration',
            'required_value': 30,
            'reward_money': 10000,
            'icon': 'globe',
            'order': 31,
        },
        
        # ===== PROGRESSION =====
        {
            'name': 'Champion de Arène',
            'description': 'Obtenir votre premier badge',
            'category': 'progression',
            'required_value': 1,
            'reward_money': 3000,
            'icon': 'award',
            'order': 40,
        },
        {
            'name': 'Maître de la Ligue',
            'description': 'Obtenir les 8 badges',
            'category': 'progression',
            'required_value': 8,
            'reward_money': 20000,
            'icon': 'trophy',
            'order': 41,
        },
        {
            'name': 'Niveau 50',
            'description': 'Avoir un Pokémon niveau 50',
            'category': 'progression',
            'required_value': 50,
            'reward_money': 5000,
            'icon': 'star',
            'order': 42,
        },
        {
            'name': 'Niveau 100',
            'description': 'Avoir un Pokémon niveau 100',
            'category': 'progression',
            'required_value': 100,
            'reward_money': 25000,
            'icon': 'fire',
            'order': 43,
            'is_hidden': True,
        },
    ]
    
    created = 0
    for data in achievements:
        obj, was_created = Achievement.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if was_created:
            created += 1
            logging.info(f"  ✅ {data['name']}")
        else:
            logging.info(f"  ⏭️  {data['name']}")
    
    logging.info(f"\n✅ {created} achievements créés sur {len(achievements)}")

