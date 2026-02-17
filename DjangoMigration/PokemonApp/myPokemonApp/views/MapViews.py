"""
Vues pour le système de carte et navigation
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from myPokemonApp.models import *
from myPokemonApp.gameUtils import get_random_wild_pokemon
from myPokemonApp.gameUtils import learn_moves_up_to_level

# ============================================================================
# MAP OVERVIEW
# ============================================================================

@login_required
def map_view(request):
    """Vue de la carte Kanto avec zones"""
    
    trainer = get_object_or_404(Trainer, username=request.user.username)
    
    # Position actuelle
    try:
        player_location = PlayerLocation.objects.get(trainer=trainer)
    except PlayerLocation.DoesNotExist:
        # Créer position initiale
        start_zone = Zone.objects.filter(name__icontains='Bourg Palette').first()
        if not start_zone:
            start_zone = Zone.objects.first()
        
        player_location = PlayerLocation.objects.create(
            trainer=trainer,
            current_zone=start_zone
        )
    
    # Toutes les zones
    all_zones = Zone.objects.all()
    
    # Zones accessibles
    accessible_zones = []
    for zone in all_zones:
        can_access, reason = zone.is_accessible_by(trainer)
        accessible_zones.append({
            'zone': zone,
            'accessible': can_access,
            'reason': reason,
            'visited': player_location.visited_zones.filter(id=zone.id).exists()
        })
    
    context = {
        'current_zone': player_location.current_zone,
        'zones': accessible_zones,
        'player_location': player_location
    }
    
    return render(request, 'map/map_overview.html', context)


@login_required
def zone_detail_view(request, zone_id):
    """Détail d'une zone avec options"""
    
    trainer = get_object_or_404(Trainer, username=request.user.username)
    zone = get_object_or_404(Zone, pk=zone_id)
    
    # Vérifier accès
    can_access, reason = zone.is_accessible_by(trainer)
    
    # Position actuelle
    player_location = PlayerLocation.objects.get(trainer=trainer)
    is_current = player_location.current_zone == zone
    
    # Zones connectées
    connections = ZoneConnection.objects.filter(from_zone=zone)
    
    # Pokémon sauvages
    wild_spawns = zone.wild_spawns.all()
    
    # Dresseurs
    trainers_in_zone = Trainer.objects.filter(
        is_npc=True,
        location=zone.name
    )
    
    context = {
        'zone': zone,
        'can_access': can_access,
        'access_reason': reason,
        'is_current': is_current,
        'connections': connections,
        'wild_spawns': wild_spawns,
        'trainers': trainers_in_zone,
        'current_zone': player_location.current_zone
    }
    
    return render(request, 'map/zone_detail.html', context)

from myPokemonApp.views.AchievementViews import check_achievement

@login_required
def travel_to_zone_view(request, zone_id):
    """Voyager vers une zone"""
    
    trainer = get_object_or_404(Trainer, username=request.user.username)
    zone = get_object_or_404(Zone, pk=zone_id)
    
    player_location = PlayerLocation.objects.get(trainer=trainer)
    
    success, message = player_location.travel_to(zone)
    
    if success:
        messages.success(request, message)

        # TRIGGER ACHIEVEMENTS
        # Compter zones visitées
        visited_count = player_location.visited_zones.count()
        
        if visited_count >= 10:
            result = check_achievement(trainer, 'Explorateur')
            if result.get('newly_completed'):
                messages.success(request, f"🏆 Explorateur débloqué ! +{result['reward_money']}₽")

        
        # Mettre à jour la save active
        try:
            save = GameSave.objects.filter(trainer=trainer, is_active=True).first()
            if save:
                save.current_location = zone.name
                save.save()
        except:
            pass
    else:
        messages.error(request, message)
    
    return redirect('zone_detail', zone_id=zone.id)


@login_required
def wild_encounter_view(request, zone_id):
    """Déclencher une rencontre sauvage dans une zone"""
    
    trainer = get_object_or_404(Trainer, username=request.user.username)
    zone = get_object_or_404(Zone, pk=zone_id)
    
    # Vérifier que c'est la zone actuelle
    player_location = PlayerLocation.objects.get(trainer=trainer)
    if player_location.current_zone != zone:
        messages.error(request, "Vous n'êtes pas dans cette zone !")
        return redirect('map_view')
    
    # Type de rencontre (par défaut: grass)
    encounter_type = request.GET.get('type', 'grass')
    
    # Générer Pokémon selon spawn rates
    wild_species, level = get_random_wild_pokemon(zone, encounter_type)
    
    if not wild_species:
        messages.warning(request, "Aucun Pokémon trouvé dans cette zone.")
        return redirect('zone_detail', zone_id=zone.id)
    
    # Créer le combat (même logique que battle_create_wild_view)
    player_pokemon = trainer.pokemon_team.filter(
        is_in_party=True,
        current_hp__gt=0
    ).first()
    
    if not player_pokemon:
        messages.error(request, "Vous n'avez pas de Pokémon en état de combattre !")
        return redirect('pokemon_center')
    
    # Trainer wild
    wild_trainer, _ = Trainer.objects.get_or_create(
        username='wild_pokemon',
        defaults={'trainer_type': 'wild', 'is_npc': True}
    )
    
    # Créer Pokémon sauvage
    wild_pokemon = PlayablePokemon.objects.create(
        species=wild_species,
        level=level,
        trainer=wild_trainer,
        is_in_party=True
    )
    
    wild_pokemon.calculate_stats()
    wild_pokemon.current_hp = wild_pokemon.max_hp
    wild_pokemon.save()
    
    # Ajouter moves
    learn_moves_up_to_level(wild_pokemon, wild_pokemon.level)

    # Si pas de moves appris, donner Tackle
    if not wild_pokemon.pokemonmoveinstance_set.exists():
        tackle = PokemonMove.objects.filter(name__icontains='Charge').first()
        if not tackle:
            tackle = PokemonMove.objects.first()
        
        if tackle:
            PokemonMoveInstance.objects.create(
                pokemon=wild_pokemon,
                move=tackle,
                current_pp=tackle.pp,
            )

    
    # Créer combat
    battle = Battle.objects.create(
        player_trainer=trainer,
        opponent_trainer=wild_trainer,
        player_pokemon=player_pokemon,
        opponent_pokemon=wild_pokemon,
        is_active=True
    )
    
    messages.success(request, f"Un {wild_species.name} sauvage de niveau {level} apparaît !")
    
    return redirect('BattleGameView', pk=battle.id)