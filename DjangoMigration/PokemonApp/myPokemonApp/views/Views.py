#!/usr/bin/python3
"""
Views Django pour l'application Pokémon Gen 1
Adapté aux nouveaux modèles
"""

import bleach
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
import django_tables2 as tables
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_POST

from myPokemonApp.gameUtils import check_battle_end



from ..models import (
    Pokemon, 
    PokemonType,
    PokemonMove, 
    PlayablePokemon,
    PokemonMoveInstance,
    Trainer,
    GymLeader,
    Item,
    TrainerInventory,
    Battle,
    PokemonEvolution,
    PokemonLearnableMove
)



# ============================================================================
# CLASSE DE BASE
# ============================================================================

class GenericOverview(generic.ListView):
    """Classe de base pour les vues de liste"""
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = self.model.__name__.lower()
        return context


# ============================================================================
# POKÉDEX - POKÉMON TEMPLATES
# ============================================================================

class PokemonOverView(GenericOverview):
    """Vue liste de tous les Pokémon (templates)"""
    model = Pokemon
    template_name = "pokemon/pokedex.html"
    
    class PokedexTable(tables.Table):
        pokedex_number = tables.Column(verbose_name="#")
        name = tables.TemplateColumn(
            '<a href="{% url \'PokemonDetailView\' record.id %}">{{ record.name }}</a>',
            verbose_name="Nom"
        )
        primary_type = tables.TemplateColumn(
            '<span class="badge badge-type-{{record.primary_type.name}}">{{record.primary_type.name}}</span>',
            verbose_name="Type 1"
        )
        secondary_type = tables.TemplateColumn(
            '{% if record.secondary_type %}<span class="badge badge-type-{{record.secondary_type.name}}">{{record.secondary_type.name}}</span>{% endif %}',
            verbose_name="Type 2"
        )
        base_hp = tables.Column(verbose_name="HP")
        base_attack = tables.Column(verbose_name="ATK")
        base_defense = tables.Column(verbose_name="DEF")
        base_special_attack = tables.Column(verbose_name="SP.ATK")
        base_special_defense = tables.Column(verbose_name="SP.DEF")
        base_speed = tables.Column(verbose_name="SPD")
        total_stats = tables.Column(empty_values=(), verbose_name="Total")
        
        def render_total_stats(self, record):
            return (record.base_hp + record.base_attack + record.base_defense + 
                   record.base_special_attack + record.base_special_defense + record.base_speed)
        
        class Meta:
            model = Pokemon
            fields = ('pokedex_number', 'name', 'primary_type', 'secondary_type', 
                     'base_hp', 'base_attack', 'base_defense', 'base_special_attack',
                     'base_special_defense', 'base_speed', 'total_stats')
            attrs = {'class': 'table table-striped table-hover'}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtres
        pokemon_filter = Q()
        search_query = bleach.clean(self.request.GET.get('searchQuery', ''), tags=[], attributes={})
        type_filter = self.request.GET.get('typeFilter', '')
        gen_filter = self.request.GET.get('genFilter', 'all')
        
        if search_query:
            pokemon_filter.add(Q(name__icontains=search_query) | 
                             Q(pokedex_number__icontains=search_query), Q.AND)
        
        if type_filter:
            pokemon_filter.add(
                Q(primary_type__name=type_filter) | Q(secondary_type__name=type_filter), 
                Q.AND
            )
        
        # Génération (Gen 1 = 1-151)
        if gen_filter == 'gen1':
            pokemon_filter.add(Q(pokedex_number__lte=151), Q.AND)
        
        # Pagination
        queryset = Pokemon.objects.filter(pokemon_filter).distinct().order_by('pokedex_number')
        paginator = Paginator(queryset, 20)
        page_number = self.request.GET.get('page', 1)
        page_objects = paginator.get_page(page_number)
        
        # Table
        table = self.PokedexTable(page_objects)
        
        # Types pour le filtre
        types = PokemonType.objects.all().order_by('name')
        
        context.update({
            'table': table,
            'page_objects': page_objects,
            'searchQuery': search_query,
            'typeFilter': type_filter,
            'genFilter': gen_filter,
            'types': types,
            'total_count': Pokemon.objects.count()
        })
        
        return context


class PokemonDetailView(generic.DetailView):
    """Vue détails d'un Pokémon (template)"""
    model = Pokemon
    template_name = "pokemon/pokemon_detail.html"
    context_object_name = 'pokemon'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pokemon = self.object
        
        # Évolutions
        evolutions_from = pokemon.evolutions_from.all()
        evolutions_to = pokemon.evolutions_to.all()
        
        # Capacités apprises par niveau
        learnable_moves = pokemon.learnable_moves.all().order_by('level_learned')
        
        # Stats totales
        total_stats = (pokemon.base_hp + pokemon.base_attack + pokemon.base_defense +
                      pokemon.base_special_attack + pokemon.base_special_defense + 
                      pokemon.base_speed)
        
        context.update({
            'evolutions_from': evolutions_from,
            'evolutions_to': evolutions_to,
            'learnable_moves': learnable_moves,
            'total_stats': total_stats
        })
        
        return context


# ============================================================================
# CAPACITÉS POKÉMON
# ============================================================================

class PokemonMoveOverView(GenericOverview):
    """Vue liste de toutes les capacités"""
    model = PokemonMove
    template_name = "pokemon/moves_list.html"
    
    class MovesTable(tables.Table):
        name = tables.TemplateColumn(
            '<a href="{% url \'PokemonMoveDetailView\' record.id %}">{{ record.name }}</a>'
        )
        type = tables.TemplateColumn(
            '<span class="badge badge-type-{{record.type.name}}">{{record.type.name}}</span>'
        )
        category = tables.Column()
        power = tables.Column()
        accuracy = tables.Column()
        pp = tables.Column()
        
        class Meta:
            model = PokemonMove
            fields = ('name', 'type', 'category', 'power', 'accuracy', 'pp')
            attrs = {'class': 'table table-striped table-hover'}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtres
        move_filter = Q()
        search_query = bleach.clean(self.request.GET.get('searchQuery', ''), tags=[], attributes={})
        type_filter = self.request.GET.get('typeFilter', '')
        category_filter = self.request.GET.get('categoryFilter', '')
        
        if search_query:
            move_filter.add(Q(name__icontains=search_query), Q.AND)
        
        if type_filter:
            move_filter.add(Q(type__name=type_filter), Q.AND)
        
        if category_filter:
            move_filter.add(Q(category=category_filter), Q.AND)
        
        # Pagination
        queryset = PokemonMove.objects.filter(move_filter).distinct().order_by('name')
        paginator = Paginator(queryset, 25)
        page_number = self.request.GET.get('page', 1)
        page_objects = paginator.get_page(page_number)
        
        table = self.MovesTable(page_objects)
        
        types = PokemonType.objects.all().order_by('name')
        
        context.update({
            'table': table,
            'page_objects': page_objects,
            'searchQuery': search_query,
            'typeFilter': type_filter,
            'categoryFilter': category_filter,
            'types': types
        })
        
        return context


class PokemonMoveDetailView(generic.DetailView):
    """Vue détails d'une capacité"""
    model = PokemonMove
    template_name = "pokemon/move_detail.html"
    context_object_name = 'move'


# ============================================================================
# ÉQUIPE DU JOUEUR
# ============================================================================

@method_decorator(login_required, name='dispatch')
class MyTeamView(generic.ListView):
    """Vue de l'équipe du joueur"""
    model = PlayablePokemon
    template_name = "trainer/my_team.html"
    context_object_name = 'team'
    
    def get_queryset(self):
        # Récupérer ou créer le trainer du joueur
        trainer, created = Trainer.objects.get_or_create(
            username=self.request.user.username,
            defaults={'trainer_type': 'player'}
        )
        return trainer.pokemon_team.filter(is_in_party=True).order_by('party_position')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        trainer, _ = Trainer.objects.get_or_create(
            username=self.request.user.username,
            defaults={'trainer_type': 'player'}
        )
        
        # PC (Pokémon en réserve)
        pc_pokemon = trainer.pokemon_team.filter(is_in_party=False).order_by('species__pokedex_number')
        
        # Inventaire
        inventory = trainer.inventory.all().select_related('item')
        
        context.update({
            'trainer': trainer,
            'pc_pokemon': pc_pokemon,
            'inventory': inventory
        })
        
        return context


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
# CHAMPIONS D'ARÈNE
# ============================================================================

class GymLeaderListView(generic.ListView):
    """Liste des Champions d'Arène"""
    model = GymLeader
    template_name = "gym/gym_leaders.html"
    context_object_name = 'gym_leaders'
    
    def get_queryset(self):
        return GymLeader.objects.all().order_by('badge_order').select_related('trainer', 'specialty_type')


class GymLeaderDetailView(generic.DetailView):
    """Détails d'un Champion d'Arène"""
    model = GymLeader
    template_name = "gym/gym_leader_detail.html"
    context_object_name = 'gym_leader'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Équipe du champion
        team = self.object.trainer.pokemon_team.all()
        
        context['team'] = team
        return context


# ============================================================================
# OBJETS
# ============================================================================

class ItemListView(generic.ListView):
    """Liste des objets"""
    model = Item
    template_name = "items/item_list.html"
    context_object_name = 'items'
    
    def get_queryset(self):
        item_type = self.request.GET.get('itemType', '')
        queryset = Item.objects.all().order_by('item_type', 'price')
        
        if item_type:
            queryset = queryset.filter(item_type=item_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_types'] = Item.ITEM_TYPES
        context['selected_type'] = self.request.GET.get('itemType', '')
        return context


# ============================================================================
# DASHBOARD
# ============================================================================

@method_decorator(login_required, name='dispatch')
class DashboardView(generic.TemplateView):
    """Dashboard principal"""
    template_name = "dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer le trainer
        trainer, created = Trainer.objects.get_or_create(
            username=self.request.user.username,
            defaults={'trainer_type': 'player'}
        )
        
        # Statistiques
        total_pokemon = Pokemon.objects.count()
        team_size = trainer.pokemon_team.filter(is_in_party=True).count()
        total_caught = trainer.pokemon_team.count()
        badges = trainer.badges
        
        # Derniers combats
        recent_battles = Battle.objects.filter(
            player_trainer=trainer
        ).order_by('-created_at')[:5]
        
        # Prochains gym leaders
        next_gym = GymLeader.objects.filter(
            badge_order__gt=badges
        ).order_by('badge_order').first()
        
        context.update({
            'trainer': trainer,
            'total_pokemon': total_pokemon,
            'team_size': team_size,
            'total_caught': total_caught,
            'badges': badges,
            'recent_battles': recent_battles,
            'next_gym': next_gym
        })
        
        return context
    







# ============================================================================
# VUE DE COMBAT GRAPHIQUE
# ============================================================================

@method_decorator(login_required, name='dispatch')
class BattleGameView(generic.DetailView):
    """Vue du combat en mode graphique"""
    model = Battle
    template_name = "battle/battle_game.html"
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
        
        context = {
            'trainer': trainer,
            'player_pokemon': player_pokemon
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

@login_required
def get_trainer_items(request):
    trainer_id = request.GET.get('trainer_id')

    inventory = TrainerInventory.objects.filter(
        trainer=Trainer.objects.get(pk=trainer_id),
        quantity__gt=0
    )

    items = []
    
    if not inventory.exists():
        return JsonResponse({})
    
    
    items = []
    # Récupérer les objets du sac du dresseur
    for item in inventory:
        items.append({'id': item.pk , 'name': item.item.name, 'quantity':item.quantity })

    return JsonResponse({'items': items})

@login_required
def get_trainer_team(request):
    trainer_id = request.GET.get('trainer_id')
    exclude_pokemon_id = request.GET.get('exclude_pokemon_id')
    # Récupérer les Pokémon de l'équipe (hors Pokémon actuel)
    trainersPokemons = PlayablePokemon.objects.filter(
        trainer=Trainer.objects.get(pk=trainer_id),
    ).exclude(pk=exclude_pokemon_id)

    team = []
    for poke in trainersPokemons:
        team.append(
            {'id': poke.pk, 'nickname': poke.nickname, 'species': {'name' : poke.species.name }, 'level': poke.level, 'current_hp': poke.current_hp, 'max_hp': poke.max_hp}
        )
    
    return JsonResponse({'team': team})




@login_required
@require_POST
def heal_pokemon_api(request):
    """
    API pour soigner un Pokémon (restaure HP et PP)
    """
    try:
        data = json.loads(request.body)
        pokemon_id = data.get('pokemon_id')
        
        # Récupérer le Pokémon
        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id)
        
        # Vérifier que le Pokémon appartient au joueur
        trainer = get_object_or_404(Trainer, username=request.user.username)
        if pokemon.trainer != trainer:
            return JsonResponse({
                'success': False,
                'error': 'Ce Pokémon ne vous appartient pas'
            })
        
        # Soigner le Pokémon
        pokemon.heal()  # Restaure HP
        pokemon.cure_status()  # Retire les statuts
        pokemon.restore_all_pp()  # Restaure PP
        pokemon.reset_combat_stats()  # Reset les modificateurs de combat
        
        return JsonResponse({
            'success': True,
            'message': f'{pokemon} a été soigné!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_POST
def heal_all_pokemon_api(request):
    """
    API pour soigner tous les Pokémon de l'équipe
    """
    try:
        trainer = get_object_or_404(Trainer, username=request.user.username)
        
        # Récupérer tous les Pokémon de l'équipe
        team_pokemon = trainer.pokemon_team.filter(is_in_party=True)
        
        healed_count = 0
        for pokemon in team_pokemon:
            pokemon.heal()
            pokemon.cure_status()
            pokemon.restore_all_pp()
            pokemon.reset_combat_stats()
            healed_count += 1
        
        return JsonResponse({
            'success': True,
            'healed_count': healed_count,
            'message': f'{healed_count} Pokémon ont été soignés!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_POST
def send_to_pc_api(request):
    """
    API pour envoyer un Pokémon au PC
    """
    try:
        data = json.loads(request.body)
        pokemon_id = data.get('pokemon_id')
        
        # Récupérer le Pokémon
        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id)
        
        # Vérifier que le Pokémon appartient au joueur
        trainer = get_object_or_404(Trainer, username=request.user.username)
        if pokemon.trainer != trainer:
            return JsonResponse({
                'success': False,
                'error': 'Ce Pokémon ne vous appartient pas'
            })
        
        # Vérifier qu'il reste au moins 1 Pokémon dans l'équipe
        team_count = trainer.pokemon_team.filter(is_in_party=True).count()
        if team_count <= 1:
            return JsonResponse({
                'success': False,
                'error': 'Vous devez garder au moins 1 Pokémon dans votre équipe'
            })
        
        # Envoyer au PC
        pokemon.is_in_party = False
        pokemon.party_position = None
        pokemon.save()
        
        # Réorganiser les positions
        reorganize_party_positions(trainer)
        
        return JsonResponse({
            'success': True,
            'message': f'{pokemon} a été envoyé au PC'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_POST
def add_to_party_api(request):
    """
    API pour ajouter un Pokémon du PC à l'équipe
    """
    try:
        data = json.loads(request.body)
        pokemon_id = data.get('pokemon_id')
        
        # Récupérer le Pokémon
        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id)
        
        # Vérifier que le Pokémon appartient au joueur
        trainer = get_object_or_404(Trainer, username=request.user.username)
        if pokemon.trainer != trainer:
            return JsonResponse({
                'success': False,
                'error': 'Ce Pokémon ne vous appartient pas'
            })
        
        # Vérifier que l'équipe n'est pas pleine
        team_count = trainer.pokemon_team.filter(is_in_party=True).count()
        if team_count >= 6:
            return JsonResponse({
                'success': False,
                'error': 'Votre équipe est complète (6/6)'
            })
        
        # Ajouter à l'équipe
        pokemon.is_in_party = True
        pokemon.save()
        
        # Réorganiser les positions
        reorganize_party_positions(trainer)
        
        return JsonResponse({
            'success': True,
            'message': f'{pokemon} a été ajouté à l\'équipe'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def reorganize_party_positions(trainer):
    """
    Réorganise les positions des Pokémon dans l'équipe (1-6)
    """
    team_pokemon = trainer.pokemon_team.filter(is_in_party=True).order_by('party_position', 'id')
    
    for position, pokemon in enumerate(team_pokemon, start=1):
        pokemon.party_position = position
        pokemon.save()