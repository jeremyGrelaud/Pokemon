#!/usr/bin/python3
"""
Views Django pour l'application Pokémon Gen 1
Adapté aux nouveaux modèles
"""

from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

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