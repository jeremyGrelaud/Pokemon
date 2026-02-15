#!/usr/bin/python3
"""
Views Django pour l'application Pokémon Gen 1
Adapté aux nouveaux modèles
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import  require_http_methods
from myPokemonApp.gameUtils import check_battle_end, heal_team
from django.db.models import Q

from ..models import *


# ============================================================================
# COMBATS
# ============================================================================

@method_decorator(login_required, name='dispatch')
class BattleListView(generic.ListView):
    """Liste des combats"""
    model = Battle
    template_name = "battle/battle_list.html"
    context_object_name = 'battles'
    paginate_by = 10
    
    def get_queryset(self):
        trainer = Trainer.objects.get(username=self.request.user.username)
        return Battle.objects.filter(
            Q(player_trainer=trainer) | Q(opponent_trainer=trainer)
        ).order_by('-created_at')


class BattleDetailView(generic.DetailView):
    """Détails d'un combat"""
    model = Battle
    template_name = "battle/battle_detail.html"
    context_object_name = 'battle'



# ============================================================================
# VUE DE COMBAT GRAPHIQUE
# ============================================================================

@method_decorator(login_required, name='dispatch')
class BattleGameView(generic.DetailView):
    """Vue du combat en mode graphique"""
    model = Battle
    # template_name = "battle/battle_game.html"
    template_name = "battle/battle_game_v2.html"
    context_object_name = 'battle'
    
    def get_queryset(self):
        # S'assurer que le joueur peut seulement voir ses propres combats
        trainer = get_object_or_404(Trainer, username=self.request.user.username)
        return Battle.objects.filter(player_trainer=trainer)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ajouter les informations nécessaires pour le combat
        battle = self.object
        
        # Vérifier que les Pokémon sont toujours valides
        if not battle.player_pokemon or not battle.opponent_pokemon:
            context['error'] = "Combat invalide: Pokémon manquant"
        
        return context


# ============================================================================
# API POUR LES ACTIONS DE COMBAT
# ============================================================================

@login_required
def battle_action_view(request, pk):
    """
    API pour exécuter les actions de combat
    Retourne du JSON pour mise à jour en temps réel
    """

    #TODO missing pokemon switch of the opponent if he has multiple pokemons


    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    #DEBUG
    print(f"[+] {request.POST}")

    
    battle = get_object_or_404(Battle, pk=pk)
    trainer = get_object_or_404(Trainer, username=request.user.username)
    
    # Vérifier que c'est bien le combat du joueur
    if battle.player_trainer != trainer:
        return JsonResponse({'error': 'Not your battle'}, status=403)
    
    # Vérifier que le combat est actif
    if not battle.is_active:
        return JsonResponse({'error': 'Battle already ended'}, status=400)
    
    action_type = request.POST.get('action')
    
    # Fonction helper pour créer response_data complète
    def build_response_data(battle):
        """Construit la réponse JSON avec TOUTES les infos"""
        return {
            'success': True,
            'log': [],
            # Player Pokemon - Info complète
            'player_pokemon': {
                'id': battle.player_pokemon.id,
                'name': battle.player_pokemon.nickname or battle.player_pokemon.species.name,
                'species_name': battle.player_pokemon.species.name,
                'level': battle.player_pokemon.level,
                'current_hp': battle.player_pokemon.current_hp,
                'max_hp': battle.player_pokemon.max_hp,
                'status': battle.player_pokemon.status_condition,
            },
            # Opponent Pokemon - Info complète
            'opponent_pokemon': {
                'id': battle.opponent_pokemon.id,
                'name': battle.opponent_pokemon.nickname or battle.opponent_pokemon.species.name,
                'species_name': battle.opponent_pokemon.species.name,
                'level': battle.opponent_pokemon.level,
                'current_hp': battle.opponent_pokemon.current_hp,
                'max_hp': battle.opponent_pokemon.max_hp,
                'status': battle.opponent_pokemon.status_condition,
            },
            # Backward compatibility
            'player_hp': battle.player_pokemon.current_hp,
            'player_max_hp': battle.player_pokemon.max_hp,
            'opponent_hp': battle.opponent_pokemon.current_hp,
            'opponent_max_hp': battle.opponent_pokemon.max_hp,
            'battle_ended': False
        }
    
    response_data = build_response_data(battle)

    print(response_data)
    
    try:
        if action_type == 'attack':
            # Exécuter une attaque
            move_id = request.POST.get('move_id')
            move = get_object_or_404(PokemonMove, pk=move_id)
            
            player_action = {'type': 'attack', 'move': move}
            
            # IA simple pour l'adversaire
            opponent_moves = battle.opponent_pokemon.moves.all()
            if opponent_moves:
                import random
                opponent_move = random.choice(opponent_moves)
                opponent_action = {'type': 'attack', 'move': opponent_move}
            else:
                struggle_move = get_object_or_404(PokemonMove, name="Struggle")
                opponent_action = {'type': 'attack', 'move': struggle_move}
            
            # Exécuter le tour
            battle.execute_turn(player_action, opponent_action)
            
        elif action_type == 'flee':
            # Tenter de fuir
            success = battle.attempt_flee()
            response_data['fled'] = success
            
            if success:
                response_data['log'] = ['Vous avez réussi à fuir!']
                response_data['battle_ended'] = True
            else:
                response_data['log'] = ['Echec dans la fuite!']
        
        elif action_type == 'switch':
            # Changer de Pokémon
            pokemon_id = request.POST.get('pokemon_id')
            new_pokemon = get_object_or_404(
                PlayablePokemon, 
                pk=pokemon_id, 
                trainer=trainer
            )
            
            player_action = {'type': 'switch', 'pokemon': new_pokemon}
            
            # L'adversaire attaque
            opponent_moves = battle.opponent_pokemon.moves.all()
            if opponent_moves:
                import random
                opponent_move = random.choice(opponent_moves)
                opponent_action = {'type': 'attack', 'move': opponent_move}
            else:
                struggle_move = get_object_or_404(PokemonMove, name="Struggle")
                opponent_action = {'type': 'attack', 'move': struggle_move}
            
            # Exécuter le tour (qui va faire le switch)
            battle.execute_turn(player_action, opponent_action)
            
        elif action_type == 'item':
            # Utiliser un objet
            selected_inventory_item = TrainerInventory.objects.get(
                pk=request.POST.get('item_id')
            )
            item = selected_inventory_item.item
            
            if item.item_type == 'pokeball': 
                # Capture
                player_action = {
                    'type': 'item', 
                    'item': item, 
                    'target': battle.opponent_pokemon
                }
            else:
                # Soin/Antidote sur son Pokémon
                player_action = {
                    'type': 'item', 
                    'item': item, 
                    'target': battle.player_pokemon
                }
            
            # L'adversaire attaque
            opponent_moves = battle.opponent_pokemon.moves.all()
            if opponent_moves:
                import random
                opponent_move = random.choice(opponent_moves)
                opponent_action = {'type': 'attack', 'move': opponent_move}
            else:
                struggle_move = get_object_or_404(PokemonMove, name="Struggle")
                opponent_action = {'type': 'attack', 'move': struggle_move}
            
            # Exécuter le tour (qui va utiliser l'objet)
            captured = battle.execute_turn(player_action, opponent_action)
            
            # Réduire l'inventaire
            from myPokemonApp.gameUtils import remove_item_from_trainer
            remove_item_from_trainer(battle.player_trainer, item, 1)
            
            if captured:
                response_data['battle_ended'] = True
        
        # Rafraîchir battle depuis DB
        battle.refresh_from_db()
        
        if response_data['battle_ended']: # If we ended battle via capture or fled
            # Reconstruire response_data avec les nouvelles valeurs
            response_data = build_response_data(battle)
            response_data['battle_ended']  = True
        else:
            response_data = build_response_data(battle)

        
        # Récupérer les logs récents
        if battle.battle_log:
            recent_logs = battle.battle_log[-5:]  # 5 derniers messages
            response_data['log'] = [entry['message'] for entry in recent_logs]
        
        # Vérifier si le combat est terminé
        is_ended, winner, message = check_battle_end(battle)
        
        if is_ended:
            battle.winner = winner
            battle.save()
            response_data['battle_ended'] = True
            response_data['winner'] = winner.username if winner else 'Draw'
            response_data['log'].append(message)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        response_data['success'] = False
        response_data['error'] = str(e)
        response_data['log'] = [f'Erreur: {str(e)}']
    
    print(f"[+] Response before return in battle actio view : {response_data}")
    return JsonResponse(response_data)


# ============================================================================
# CRÉER UN NOUVEAU COMBAT
# ============================================================================

@method_decorator(login_required, name='dispatch')
class BattleCreateView(generic.View):
    """Créer un nouveau combat"""
    
    def get(self, request):
        """Afficher le formulaire de création de combat"""
        trainer = get_object_or_404(Trainer, username=request.user.username)
        
        # Récupérer le premier Pokémon de l'équipe
        player_pokemon = trainer.pokemon_team.filter(
            is_in_party=True,
            current_hp__gt=0
        ).first()
        
        if not player_pokemon:
            return redirect('MyTeamView')
        

        fightableGymLeaders = list()
        for gymLeader in GymLeader.objects.all():
            if gymLeader.isChallengableByPlayer(player=trainer):
                fightableGymLeaders.append(gymLeader)
        
        context = {
            'trainer': trainer,
            'player_pokemon': player_pokemon,
            'gym_leaders': fightableGymLeaders
        }
        
        return render(request, 'battle/battle_create.html', context)
    
    def post(self, request):
        """Créer le combat"""
        trainer = get_object_or_404(Trainer, username=request.user.username)
        
        # Récupérer le premier Pokémon de l'équipe
        player_pokemon = trainer.pokemon_team.filter(
            is_in_party=True,
            current_hp__gt=0
        ).first()
        
        if not player_pokemon:
            return redirect('MyTeamView')
        
        # Type de combat
        battle_type = request.POST.get('battle_type', 'wild')
        
        # Créer un Pokémon adversaire (sauvage ou dresseur)
        if battle_type == 'wild':
            # Pokémon sauvage aléatoire
            import random
            
            wild_species = Pokemon.objects.order_by('?').first()
            wild_level = random.randint(
                max(1, player_pokemon.level - 3),
                player_pokemon.level + 3
            )
            
            # Créer le Pokémon sauvage
            wild_pokemon = PlayablePokemon.objects.create(
                species=wild_species,
                trainer=get_object_or_create_wild_trainer(),
                level=wild_level,
                original_trainer='Wild'
            )
            
            # Créer le combat
            battle = Battle.objects.create(
                battle_type='wild',
                player_trainer=trainer,
                opponent_trainer=None,
                player_pokemon=player_pokemon,
                opponent_pokemon=wild_pokemon
            )
        
        elif battle_type == 'gym':
            # Combat d'arène
            gym_leader_id = request.POST.get('gym_leader')
            
            gym_leader = get_object_or_404(GymLeader, pk=gym_leader_id)

            # Fully heal Gym leader Team at the begining of the fight
            heal_team(gym_leader.trainer)
            
            # Récupérer le premier Pokémon du champion
            opponent_pokemon = gym_leader.trainer.pokemon_team.first()
            
            if not opponent_pokemon:
                return redirect('GymLeaderListView')
            
            battle = Battle.objects.create(
                battle_type='gym',
                player_trainer=trainer,
                opponent_trainer=gym_leader.trainer,
                player_pokemon=player_pokemon,
                opponent_pokemon=opponent_pokemon
            )
        
        # Rediriger vers le combat
        return redirect('BattleGameView', pk=battle.id)


def get_object_or_create_wild_trainer():
    """Récupérer ou créer le trainer 'Wild' pour les Pokémon sauvages"""
    trainer, created = Trainer.objects.get_or_create(
        username='Wild',
        defaults={'trainer_type': 'wild'}
    )
    return trainer

# ============================================================================
# API - GET TRAINER TEAM ( seulement les 6 de l'équipe)
# ============================================================================

@login_required
@require_http_methods(["GET"])
def GetTrainerTeam(request):
    """
    Retourne l'équipe du dresseur (6 Pokémon max)
    Filtre sur is_in_party=True pour n'avoir que l'équipe active
    """
    trainer_id = request.GET.get('trainer_id')
    exclude_pokemon_id = request.GET.get('exclude_pokemon_id')
    
    trainer = get_object_or_404(Trainer, pk=trainer_id)
    
    # IMPORTANT: Filtrer sur is_in_party=True pour avoir SEULEMENT l'équipe (6 max)
    team = trainer.pokemon_team.filter(is_in_party=True)
    
    if exclude_pokemon_id:
        team = team.exclude(pk=exclude_pokemon_id)
    
    team_data = []
    for pokemon in team:
        team_data.append({
            'id': pokemon.id,
            'nickname': pokemon.nickname,
            'species': {
                'name': pokemon.species.name,
                'id': pokemon.species.id
            },
            'level': pokemon.level,
            'current_hp': pokemon.current_hp,
            'max_hp': pokemon.max_hp,
            'status_condition': pokemon.status_condition
        })
    
    return JsonResponse({
        'success': True,
        'team': team_data
    })


# ============================================================================
# API - GET TRAINER ITEMS
# ============================================================================

@login_required
@require_http_methods(["GET"])
def GetTrainerItems(request):
    """Retourne les objets du dresseur avec leurs quantités"""
    trainer_id = request.GET.get('trainer_id')
    trainer = get_object_or_404(Trainer, pk=trainer_id)
    
    inventory = TrainerInventory.objects.filter(trainer=trainer, quantity__gt=0)
    
    items_data = []
    for inv in inventory:
        items_data.append({
            'id': inv.id,
            'name': inv.item.name,
            'quantity': inv.quantity,
        })
    
    return JsonResponse({
        'success': True,
        'items': items_data
    })
