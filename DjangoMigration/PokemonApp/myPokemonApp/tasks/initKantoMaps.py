"""
Initialise la carte de Kanto avec zones et spawn rates
"""

from myPokemonApp.models import *

def init_kanto_map():
    """Crée toutes les zones de Kanto Gen 1"""
    
    print("🗺️ Initialisation de la carte Kanto...")
    
    # ===== VILLES ET ROUTES =====
    
    zones_data = [
        # Début
        {
            'name': 'Bourg Palette',
            'zone_type': 'city',
            'description': 'Ville natale du joueur. Petit village paisible.',
            'order': 1,
            'level_min': 1,
            'level_max': 5,
            'is_safe_zone': True,
            'has_pokemon_center': True,
        },
        {
            'name': 'Route 1',
            'zone_type': 'route',
            'description': 'Première route entre Bourg Palette et Jadielle.',
            'order': 2,
            'level_min': 2,
            'level_max': 4,
        },
        {
            'name': 'Jadielle',
            'zone_type': 'city',
            'description': 'Première ville avec une boutique.',
            'order': 3,
            'level_min': 3,
            'level_max': 6,
            'is_safe_zone': True,
            'has_pokemon_center': True,
            'has_shop': True,
        },
        {
            'name': 'Route 22',
            'zone_type': 'route',
            'description': 'Route vers la Ligue Pokémon (bloquée au début).',
            'order': 4,
            'level_min': 3,
            'level_max': 5,
        },
        {
            'name': 'Route 2',
            'zone_type': 'route',
            'description': 'Route au nord de Jadielle vers la Forêt de Jade.',
            'order': 5,
            'level_min': 3,
            'level_max': 5,
        },
        {
            'name': 'Forêt de Jade',
            'zone_type': 'forest',
            'description': 'Forêt dense remplie de Pokémon Insecte.',
            'order': 6,
            'level_min': 4,
            'level_max': 6,
        },
        {
            'name': 'Argenta',
            'zone_type': 'city',
            'description': 'Ville avec la première Arène (Pierre, type Roche).',
            'order': 7,
            'level_min': 8,
            'level_max': 12,
            'is_safe_zone': True,
            'has_pokemon_center': True,
            'has_shop': True,
        },
        {
            'name': 'Route 3',
            'zone_type': 'route',
            'description': 'Route vers le Mont Sélénite.',
            'order': 8,
            'level_min': 6,
            'level_max': 10,
        },
        {
            'name': 'Mont Sélénite',
            'zone_type': 'cave',
            'description': 'Grotte sombre pleine de Pokémon Roche et Sol.',
            'order': 9,
            'level_min': 8,
            'level_max': 12,
        },
        {
            'name': 'Route 4',
            'zone_type': 'route',
            'description': 'Sortie du Mont Sélénite vers Azuria.',
            'order': 10,
            'level_min': 10,
            'level_max': 14,
        },
        {
            'name': 'Azuria',
            'zone_type': 'city',
            'description': 'Grande ville avec l\'Arène Eau (Ondine).',
            'order': 11,
            'level_min': 18,
            'level_max': 21,
            'is_safe_zone': True,
            'has_pokemon_center': True,
            'has_shop': True,
        },
        # Ajoutez les autres zones...
    ]
    
    created_zones = {}
    for data in zones_data:
        zone, created = Zone.objects.get_or_create(
            name=data['name'],
            defaults={
                'zone_type': data['zone_type'],
                'description': data['description'],
                'recommended_level_min': data['level_min'],
                'recommended_level_max': data['level_max'],
                'order': data['order'],
                'is_safe_zone': data.get('is_safe_zone', False),
                'has_pokemon_center': data.get('has_pokemon_center', False),
                'has_shop': data.get('has_shop', False),
            }
        )
        created_zones[data['name']] = zone
        print(f"  {'✅' if created else '⏭️'} {data['name']}")
    
    # ===== CONNEXIONS =====
    
    connections_data = [
        ('Bourg Palette', 'Route 1'),
        ('Route 1', 'Jadielle'),
        ('Jadielle', 'Route 22'),
        ('Jadielle', 'Route 2'),
        ('Route 2', 'Forêt de Jade'),
        ('Forêt de Jade', 'Argenta'),
        ('Argenta', 'Route 3'),
        ('Route 3', 'Mont Sélénite'),
        ('Mont Sélénite', 'Route 4'),
        ('Route 4', 'Azuria'),
    ]
    
    print("\n🔗 Connexions...")
    for from_name, to_name in connections_data:
        from_zone = created_zones.get(from_name)
        to_zone = created_zones.get(to_name)
        
        if from_zone and to_zone:
            conn, created = ZoneConnection.objects.get_or_create(
                from_zone=from_zone,
                to_zone=to_zone,
                defaults={'is_bidirectional': True}
            )
            print(f"  {'✅' if created else '⏭️'} {from_name} ↔ {to_name}")
    
    # ===== SPAWN RATES =====
    
    print("\n🎲 Spawns...")
    
    # Route 1
    route1 = created_zones.get('Route 1')
    if route1:
        spawns = [
            ('Rattata', 50.0, 2, 4),
            ('Roucool', 50.0, 2, 4),
        ]
        
        for poke_name, rate, lv_min, lv_max in spawns:
            pokemon = Pokemon.objects.filter(name__icontains=poke_name).first()
            if pokemon:
                WildPokemonSpawn.objects.get_or_create(
                    zone=route1,
                    pokemon=pokemon,
                    defaults={
                        'spawn_rate': rate,
                        'level_min': lv_min,
                        'level_max': lv_max,
                        'encounter_type': 'grass'
                    }
                )
                print(f"  ✅ {poke_name} dans {route1.name}")
    
    # Forêt de Jade
    forest = created_zones.get('Forêt de Jade')
    if forest:
        spawns = [
            ('Chenipan', 25.0, 3, 5),
            ('Aspicot', 25.0, 3, 5),
            ('Roucool', 30.0, 4, 6),
            ('Pikachu', 20.0, 3, 5),
        ]
        
        for poke_name, rate, lv_min, lv_max in spawns:
            pokemon = Pokemon.objects.filter(name__icontains=poke_name).first()
            if pokemon:
                WildPokemonSpawn.objects.get_or_create(
                    zone=forest,
                    pokemon=pokemon,
                    defaults={
                        'spawn_rate': rate,
                        'level_min': lv_min,
                        'level_max': lv_max,
                        'encounter_type': 'grass'
                    }
                )
                print(f"  ✅ {poke_name} dans {forest.name}")
    
    print("\n✅ Carte Kanto initialisée !")


