"""
Système de sauvegarde COMPLET avec snapshot et restore
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
import logging
from myPokemonApp.models import *
import json

# ============================================================================
# SNAPSHOT - Sauvegarder l'état complet
# ============================================================================

def create_game_snapshot(trainer, save):
    """
    Crée un snapshot complet de l'état du jeu
    
    Returns:
        dict: Snapshot JSON-serializable
    """
    
    snapshot = {
        'version': '1.0',
        'created_at': timezone.now().isoformat(),
        
        # Trainer info
        'trainer': {
            'money': trainer.money,
            'badges': trainer.badges,
            'location': save.current_location,
        },
        
        # Pokémon team
        'pokemon_team': [],
        
        # Inventory
        'inventory': [],
        
        # Defeated trainers
        'defeated_trainers': list(save.defeated_trainers),
        
        # Story flags
        'story_flags': dict(save.story_flags),
    }
    
    # ===== SAUVEGARDER POKÉMON =====
    for pokemon in trainer.pokemon_team.all():
        pokemon_data = {
            'species_id': pokemon.species.id,
            'species_name': pokemon.species.name,
            'nickname': pokemon.nickname,
            'level': pokemon.level,
            'current_hp': pokemon.current_hp,
            'max_hp': pokemon.max_hp,
            'attack': pokemon.attack,
            'defense': pokemon.defense,
            'special_attack': pokemon.special_attack,
            'special_defense': pokemon.special_defense,
            'speed': pokemon.speed,
            'status_condition': pokemon.status_condition,
            'is_in_party': pokemon.is_in_party,
            'current_exp': pokemon.current_exp,
            'exp_for_next_level': pokemon.exp_for_next_level(),
            
            # Moves avec PP
            'moves': []
        }
        
        # Sauvegarder les moves
        for move_instance in pokemon.pokemonmoveinstance_set.all():
            pokemon_data['moves'].append({
                'move_id': move_instance.move.id,
                'move_name': move_instance.move.name,
                'current_pp': move_instance.current_pp,
            })
        
        snapshot['pokemon_team'].append(pokemon_data)
    
    # ===== SAUVEGARDER INVENTAIRE =====
    for inventory_item in trainer.inventory.all():
        snapshot['inventory'].append({
            'item_id': inventory_item.item.id,
            'item_name': inventory_item.item.name,
            'quantity': inventory_item.quantity
        })
    
    return snapshot


# ============================================================================
# RESTORE - Restaurer l'état complet
# ============================================================================

def restore_game_snapshot(trainer, snapshot):
    """
    Restaure l'état complet du jeu depuis un snapshot
    
    Args:
        trainer: Trainer
        snapshot: dict (JSON snapshot)
    """
    
    # ===== RESTAURER TRAINER INFO =====
    trainer.money = snapshot['trainer']['money']
    trainer.badges = snapshot['trainer']['badges']
    trainer.save()
    
    # ===== SUPPRIMER POKÉMON ACTUELS =====
    trainer.pokemon_team.all().delete()
    
    # ===== RESTAURER POKÉMON =====
    for poke_data in snapshot['pokemon_team']:
        try:
            species = Pokemon.objects.get(id=poke_data['species_id'])
        except Pokemon.DoesNotExist:
            continue
        
        # Recréer le Pokémon
        restored_pokemon = PlayablePokemon.objects.create(
            species=species,
            nickname=poke_data.get('nickname'),
            level=poke_data['level'],
            trainer=trainer,
            current_hp=poke_data['current_hp'],
            max_hp=poke_data['max_hp'],
            attack=poke_data['attack'],
            defense=poke_data['defense'],
            special_attack=poke_data['special_attack'],
            special_defense=poke_data['special_defense'],
            speed=poke_data['speed'],
            status_condition=poke_data.get('status_condition'),
            is_in_party=poke_data['is_in_party'],
            current_exp=poke_data.get('current_exp', 0),
        )
        
        # Restaurer les moves
        for move_data in poke_data['moves']:
            try:
                move = PokemonMove.objects.get(id=move_data['move_id'])
                # Check if the move already exists for the Pokemon
                exists = PokemonMoveInstance.objects.filter(
                    pokemon=restored_pokemon,
                    move=move
                ).exists()

                if not exists:
                    PokemonMoveInstance.objects.get_or_create(
                        pokemon=restored_pokemon,
                        move=move,
                        current_pp=move_data['current_pp'],
                    )
            except PokemonMove.DoesNotExist:
                continue
    
    # ===== SUPPRIMER INVENTAIRE ACTUEL =====
    trainer.inventory.all().delete()
    
    # ===== RESTAURER INVENTAIRE =====
    for item_data in snapshot['inventory']:
        try:
            item = Item.objects.get(id=item_data['item_id'])
            TrainerInventory.objects.create(
                trainer=trainer,
                item=item,
                quantity=item_data['quantity']
            )
        except Item.DoesNotExist:
            continue


# ============================================================================
# VUES DE SAUVEGARDE
# ============================================================================

@login_required
def save_select_view(request):
    """Écran de sélection de sauvegarde (3 slots)"""
    
    trainer = get_object_or_404(Trainer, username=request.user.username)
    
    # Récupérer les 3 slots
    saves = []
    for slot in range(1, 4):
        save = GameSave.objects.filter(trainer=trainer, slot=slot).first()
        saves.append({
            'slot': slot,
            'save': save,
            'exists': save is not None
        })
    
    return render(request, 'saves/save_select.html', {
        'saves': saves,
        'trainer': trainer
    })


@login_required
def save_create_view(request, slot):
    """Créer une nouvelle sauvegarde dans un slot"""
    
    trainer = get_object_or_404(Trainer, username=request.user.username)
    existing = GameSave.objects.filter(trainer=trainer, slot=slot).first()
    
    if request.method == 'POST':
        save_name = request.POST.get('save_name', f'Aventure {slot}')
        
        # Supprimer ancienne save si existe
        if existing:
            existing.delete()
        
        # Créer nouvelle save
        save = GameSave.objects.create(
            trainer=trainer,
            slot=slot,
            save_name=save_name,
            current_location='Bourg Palette',
            last_pokemon_center='Bourg Palette',
            play_time=0,
            story_flags={},
            defeated_trainers=[]
        )
        
        # ===== CRÉER SNAPSHOT INITIAL =====
        snapshot = create_game_snapshot(trainer, save)
        save.game_snapshot = snapshot  # Stocker dans JSONField
        save.save()
        
        # Marquer comme active
        GameSave.objects.filter(trainer=trainer).update(is_active=False)
        save.is_active = True
        save.save()
        
        logging.info(request, f"Nouvelle partie '{save_name}' créée !")
        return redirect('home')
    
    return render(request, 'saves/save_create.html', {
        'slot': slot,
        'existing': existing
    })


@login_required
def save_load_view(request, save_id):
    """
    Charger une sauvegarde
    IMPORTANT: Restaure TOUT l'état du jeu
    """
    
    trainer = get_object_or_404(Trainer, username=request.user.username)
    save = get_object_or_404(GameSave, pk=save_id, trainer=trainer)
    
    # ===== RESTAURER SNAPSHOT =====
    if save.game_snapshot:
        try:
            restore_game_snapshot(trainer, save.game_snapshot)
            logging.info(request, f"Sauvegarde '{save.save_name}' chargée !")
        except Exception as e:
            logging.error(request, f"Erreur lors du chargement: {str(e)}")
            return redirect('save_select')
    else:
        logging.warning(request, "Cette sauvegarde n'a pas de snapshot. Chargement sans restauration.")
    
    # Marquer comme active
    GameSave.objects.filter(trainer=trainer).update(is_active=False)
    save.is_active = True
    
    # Restaurer location
    save.current_location = save.game_snapshot.get('trainer', {}).get('location', 'Bourg Palette')
    save.save()
    
    return redirect('home')


@login_required
def save_game_view(request, save_id):
    """
    Sauvegarder manuellement
    IMPORTANT: Crée un snapshot complet
    """
    
    trainer = get_object_or_404(Trainer, username=request.user.username)
    save = get_object_or_404(GameSave, pk=save_id, trainer=trainer)
    
    # Créer snapshot
    snapshot = create_game_snapshot(trainer, save)
    
    # Sauvegarder
    save.game_snapshot = snapshot
    
    # Mettre à jour temps de jeu
    time_since_last = (timezone.now() - save.last_saved).seconds
    save.play_time += time_since_last
    
    save.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Partie sauvegardée !',
        'play_time': save.get_play_time_display(),
        'snapshot_size': len(json.dumps(snapshot))
    })


@login_required
def auto_save_view(request, save_id):
    """
    Auto-save AJAX
    IMPORTANT: Crée un snapshot complet périodiquement
    """
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    trainer = get_object_or_404(Trainer, username=request.user.username)
    save = get_object_or_404(GameSave, pk=save_id, trainer=trainer)
    
    # Mettre à jour position
    if request.POST.get('location'):
        save.current_location = request.POST.get('location')
    
    # Créer snapshot
    snapshot = create_game_snapshot(trainer, save)
    save.game_snapshot = snapshot
    
    # Incrémenter temps de jeu
    time_since_last = (timezone.now() - save.last_saved).seconds
    save.play_time += time_since_last
    
    save.save()
    
    return JsonResponse({
        'success': True,
        'snapshot_created': True
    })


@login_required
def save_slots_list_view(request):
    """API JSON pour le modal de sauvegarde"""
    
    trainer = get_object_or_404(Trainer, username=request.user.username)
    active_save = GameSave.objects.filter(trainer=trainer, is_active=True).first()
    
    slots = []
    for slot_num in range(1, 4):
        save = GameSave.objects.filter(trainer=trainer, slot=slot_num).first()
        
        slot_data = {
            'slot': slot_num,
            'exists': save is not None,
            'is_current': save == active_save if save else False,
            'save_id': save.id if save else None,
            'name': save.save_name if save else f'Slot {slot_num}',
        }
        
        if save:
            slot_data.update({
                'play_time': save.get_play_time_display(),
                'badges': save.badges_count,
                'money': save.money,
                'location': save.current_location
            })
        
        slots.append(slot_data)
    
    return JsonResponse({'success': True, 'slots': slots})


@login_required
def save_create_quick_view(request, slot):
    """Créer rapidement une sauvegarde (pour modal)"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})
    
    trainer = get_object_or_404(Trainer, username=request.user.username)
    save_name = request.POST.get('save_name', f'Aventure {slot}')
    
    # Supprimer ancienne save
    existing = GameSave.objects.filter(trainer=trainer, slot=slot).first()
    if existing:
        existing.delete()
    
    # Créer save
    save = GameSave.objects.create(
        trainer=trainer,
        slot=slot,
        save_name=save_name,
        current_location='Bourg Palette',
        play_time=0,
        story_flags={},
        defeated_trainers=[]
    )
    
    # Snapshot
    snapshot = create_game_snapshot(trainer, save)
    save.game_snapshot = snapshot
    save.save()
    
    return JsonResponse({
        'success': True,
        'save_id': save.id,
        'message': f"Sauvegarde '{save_name}' créée !"
    })