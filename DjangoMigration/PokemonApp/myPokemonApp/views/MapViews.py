"""
Vues pour le système de carte et navigation
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from myPokemonApp.models import *
from myPokemonApp.gameUtils import get_random_wild_pokemon

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
    
    # Zones connectées : depuis + retour bidirectionnel
    outgoing = ZoneConnection.objects.filter(from_zone=zone).select_related('to_zone')
    incoming = ZoneConnection.objects.filter(
        to_zone=zone, is_bidirectional=True
    ).select_related('from_zone')

    # Construire une liste unifiée de "connexions" pour le template (to_zone = destination)
    connections = list(outgoing)
    seen_zone_ids = {c.to_zone_id for c in outgoing}
    for conn in incoming:
        if conn.from_zone_id not in seen_zone_ids:
            conn.to_zone = conn.from_zone
            connections.append(conn)
    
    # Pokémon sauvages
    wild_spawns = zone.wild_spawns.all()
    
    # Dresseurs
    trainers_in_zone = Trainer.objects.filter(
        is_npc=True,
        location=zone.name
    )

    # ----------------------------------------------------------------
    # Services de la zone
    # ----------------------------------------------------------------

    # Centre Pokémon lié à cette zone (recherche par nom de zone dans location)
    pokemon_center = None
    if zone.has_pokemon_center:
        pokemon_center = PokemonCenter.objects.filter(
            location__icontains=zone.name,
            is_available=True
        ).first()

    # Boutique / Pokemart lié à cette zone
    zone_shop = None
    if zone.has_shop:
        zone_shop = Shop.objects.filter(
            location__icontains=zone.name
        ).first()


    # Dictionnaire de correspondance  français -> anglais
    zone_translations = {
        "Argenta": "Pewter City",
        "Azuria": "Cerulean City",
        "Carmin sur Mer": "Vermilion City",
        "Céladopole": "Celadon City",
        "Jadielle": "Viridian City",
        "Safrania": "Saffron City",
        "Parmanie": "Fuchsia City",
        "Cramois'Ile": "Cinnabar Island",
    }

    english_zone_name = zone_translations.get(zone.name, zone.name).strip() # Si pas de traduction, garde le nom original

    # Gym Leader / Arène de cette zone
    gym_leader = None
    try:
        gym_leader = GymLeader.objects.filter(
            gym_city__icontains=english_zone_name
        ).first()
    except Exception:
        pass

    # ----------------------------------------------------------------
    
    context = {
        'zone': zone,
        'can_access': can_access,
        'access_reason': reason,
        'is_current': is_current,
        'connections': connections,
        'wild_spawns': wild_spawns,
        'trainers': trainers_in_zone,
        'current_zone': player_location.current_zone,
        # Services
        'pokemon_center': pokemon_center,
        'zone_shop': zone_shop,
        'gym_leader': gym_leader,
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
    from myPokemonApp.gameUtils import create_wild_pokemon, get_first_alive_pokemon

    trainer = get_object_or_404(Trainer, username=request.user.username)
    zone    = get_object_or_404(Zone, pk=zone_id)

    # Vérifier que c'est la zone actuelle
    player_location = PlayerLocation.objects.get(trainer=trainer)
    if player_location.current_zone != zone:
        messages.error(request, "Vous n'êtes pas dans cette zone !")
        return redirect('map_view')

    # Interdire si un combat actif existe déjà pour ce joueur
    active_battle = Battle.objects.filter(
        player_trainer=trainer, is_active=True
    ).first()
    if active_battle:
        messages.warning(request, "Un combat est déjà en cours !")
        return redirect('BattleGameView', pk=active_battle.id)

    # Type de rencontre (par défaut: grass)
    encounter_type = request.GET.get('type', 'grass')

    # Générer Pokémon selon spawn rates
    wild_species, level = get_random_wild_pokemon(zone, encounter_type)
    if not wild_species:
        messages.warning(request, "Aucun Pokémon trouvé dans cette zone.")
        return redirect('zone_detail', zone_id=zone.id)

    player_pokemon = get_first_alive_pokemon(trainer)
    if not player_pokemon:
        messages.error(request, "Vous n'avez pas de Pokémon en état de combattre !")
        return redirect('PokemonCenterListView')

    # Nettoyer les vieux Pokémon sauvages orphelins (pas dans un combat actif)
    # pour éviter l'accumulation en DB.
    wild_trainer_usernames = ('Wild', 'wild_pokemon')
    active_wild_pokemon_ids = Battle.objects.filter(
        is_active=True
    ).values_list('opponent_pokemon_id', flat=True)

    PlayablePokemon.objects.filter(
        trainer__username__in=wild_trainer_usernames
    ).exclude(
        id__in=active_wild_pokemon_ids
    ).delete()

    # Créer le Pokémon sauvage via gameUtils (stats + moves + fallback Tackle)
    wild_pokemon = create_wild_pokemon(wild_species, level, location=zone.name)

    # Créer le combat — opponent_trainer=None pour les combats sauvages,
    # exactement comme battle_create_wild_view, pour éviter :
    #   • le switch automatique vers d'autres Pokémon du wild_trainer
    #   • le calcul d'XP × 1.5 (bonus dresseur)
    #   • l'affichage de toute la "team" du wild_trainer dans l'historique
    battle = Battle.objects.create(
        player_trainer=trainer,
        opponent_trainer=None,
        player_pokemon=player_pokemon,
        opponent_pokemon=wild_pokemon,
        battle_type='wild',
        is_active=True,
    )

    messages.success(request, f"Un {wild_species.name} sauvage de niveau {level} apparaît !")
    return redirect('BattleGameView', pk=battle.id)