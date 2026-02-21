#!/usr/bin/python3
"""
Views Django pour l'application Pokémon Gen 1
Adapté aux nouveaux modèles
"""

from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from myPokemonApp.gameUtils import get_or_create_player_trainer, create_starter_pokemon, give_item_to_trainer
from ..models import *

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
# DASHBOARD
# ============================================================================

@method_decorator(login_required, name='dispatch')
class DashboardView(generic.TemplateView):
    """Dashboard principal"""
    template_name = "dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        """Redirige vers la sélection du starter si le joueur n'a pas encore de Pokémon"""
        if request.user.is_authenticated:
            trainer = get_or_create_player_trainer(request.user)
            if not trainer.pokemon_team.exists():
                return redirect('choose_starter')
        return super().dispatch(request, *args, **kwargs)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer = get_or_create_player_trainer(self.request.user)
        
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
            'next_gym': next_gym,
            'first_team_pokemon': trainer.pokemon_team.filter(is_in_party=True).order_by('party_position').first(),
        })
        
        return context
    

# ============================================================================
# SÉLECTION DU STARTER
# ============================================================================

@login_required
def choose_starter_view(request):
    """
    Permet au nouveau joueur de choisir son Pokémon de départ.
    Lui donne aussi 5 Pokéballs de départ.
    """

    trainer = get_or_create_player_trainer(request.user)

    # Si le joueur a déjà un Pokémon, rediriger vers le dashboard
    if trainer.pokemon_team.exists():
        return redirect('home')

    # Les 3 starters Gen 1 (Bulbizarre #1, Salamèche #4, Carapuce #7)
    starters = Pokemon.objects.filter(pokedex_number__in=[1, 4, 7]).order_by('pokedex_number')

    if request.method == 'POST':
        starter_id = request.POST.get('starter_id')
        starter_species = get_object_or_404(Pokemon, pk=starter_id)

        # Sécurité : s'assurer que c'est bien un starter
        if starter_species.pokedex_number not in [1, 4, 7]:
            messages.error(request, "Pokémon invalide.")
            return redirect('choose_starter')

        # Créer le Pokémon de départ niveau 5
        create_starter_pokemon(
            species=starter_species,
            trainer=trainer,
        )

        # Donne les objets de départ
        give_item_to_trainer(trainer, Item.objects.get(name='Poke Ball'), 5)
        give_item_to_trainer(trainer, Item.objects.get(name='Potion'), 3)


        messages.success(
            request,
            f"Vous avez choisi {starter_species.name} ! Bonne aventure, {trainer.username} ! "
            f"Vous avez reçu 5 Pokéballs et 3 Potions."
        )
        return redirect('home')

    return render(request, 'choose_starter.html', {
        'starters': starters,
        'trainer': trainer,
    })