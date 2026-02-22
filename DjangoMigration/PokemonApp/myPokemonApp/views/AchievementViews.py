"""
Vues pour le système de succès/achievements
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from myPokemonApp.models import *
from myPokemonApp.gameUtils import get_player_trainer

# ============================================================================
# ACHIEVEMENT TRACKING
# ============================================================================

def check_achievement(trainer, achievement_name, increment=1):
    """
    Vérifie et met à jour un achievement
    
    Args:
        trainer: Trainer
        achievement_name: str (nom de l'achievement)
        increment: int (montant à ajouter à la progression)
    
    Returns:
        dict: {'completed': bool, 'progress': int, 'total': int}
    """
    
    try:
        achievement = Achievement.objects.get(name=achievement_name)
    except Achievement.DoesNotExist:
        return {'completed': False, 'progress': 0, 'total': 0}
    
    # Récupérer ou créer le suivi
    trainer_achievement, created = TrainerAchievement.objects.get_or_create(
        trainer=trainer,
        achievement=achievement,
        defaults={'current_progress': 0}
    )
    
    # Si déjà complété, rien à faire
    if trainer_achievement.is_completed:
        return {
            'completed': True,
            'progress': trainer_achievement.current_progress,
            'total': achievement.required_value,
            'already_completed': True
        }
    
    # Incrémenter
    trainer_achievement.current_progress += increment
    trainer_achievement.save()
    
    # Vérifier complétion
    newly_completed = trainer_achievement.check_completion()
    
    return {
        'completed': newly_completed,
        'progress': trainer_achievement.current_progress,
        'total': achievement.required_value,
        'newly_completed': newly_completed,
        'reward_money': achievement.reward_money if newly_completed else 0,
        'reward_item': achievement.reward_item.name if (newly_completed and achievement.reward_item) else None
    }


def trigger_achievements_after_battle(trainer, battle_result):
    """
    Déclenche les achievements après un combat
    
    Args:
        trainer: Trainer
        battle_result: dict avec 'won', 'opponent_type', etc.
    """
    
    notifications = []
    
    if battle_result.get('won'):
        for achievement_name in ['Premier Combat', 'Combattant Aguerri', 'Vétéran']:
            result = check_achievement(trainer, achievement_name)
            if result.get('newly_completed'):
                notifications.append({
                    'title': f'🏆 {achievement_name}',
                    'message': f"Débloqué ! +{result['reward_money']}₽"
                })
    
    return notifications


def trigger_achievements_after_gym_win(trainer, badges_count):
    """
    Déclenche les achievements liés aux badges après une victoire contre un Champion d'Arène.

    Args:
        trainer: Trainer
        badges_count: int — nombre total de badges détenus après la victoire
    """
    notifications = []

    for achievement_name in ['Champion de Arène', 'Maître de la Ligue']:
        result = check_achievement(trainer, achievement_name)
        if result.get('newly_completed'):
            notifications.append({
                'title': f'🏅 {achievement_name}',
                'message': f"Débloqué ! +{result['reward_money']}₽"
            })

    return notifications


def trigger_achievements_after_capture(trainer):
    """Déclenche les achievements après une capture"""
    
    notifications = []
    
    # Premier Compagnon
    result = check_achievement(trainer, 'Premier Compagnon')
    if result.get('newly_completed'):
        notifications.append({
            'title': '🏆 Premier Compagnon',
            'message': f"Débloqué ! +{result['reward_money']}₽"
        })
    
    # Dresseur Complet (6 Pokémon)
    team_size = trainer.pokemon_team.count()
    if team_size == 6:
        result = check_achievement(trainer, 'Dresseur Complet')
        if result.get('newly_completed'):
            notifications.append({
                'title': '🏆 Dresseur Complet',
                'message': f"Débloqué ! +{result['reward_money']}₽"
            })
    
    # Maître Pokémon (Pokédex complet)
    pokedex_count = trainer.pokemon_team.values('species').distinct().count()
    if pokedex_count >= 151:
        result = check_achievement(trainer, 'Maître Pokémon')
        if result.get('newly_completed'):
            notifications.append({
                'title': '🏆 Maître Pokémon',
                'message': f"Débloqué ! +{result['reward_money']}₽"
            })
    
    return notifications


# ============================================================================
# VUES
# ============================================================================

@login_required
def achievements_list_view(request):
    """Liste de tous les achievements"""
    trainer = get_player_trainer(request.user)

    # prefetch_related évite le N+1 (une requête par achievement → 1 requête totale)
    all_achievements = Achievement.objects.all()
    progress_map = {
        ta.achievement_id: ta
        for ta in TrainerAchievement.objects.filter(trainer=trainer).select_related('achievement')
    }

    achievements_data = []
    total_completed   = 0

    for achievement in all_achievements:
        ta         = progress_map.get(achievement.id)
        current    = ta.current_progress if ta else 0
        completed  = ta.is_completed     if ta else False
        completed_at = ta.completed_at   if ta else None

        if completed:
            total_completed += 1

        achievements_data.append({
            'achievement':       achievement,
            'current':           current,
            'required':          achievement.required_value,
            'completed':         completed,
            'completed_at':      completed_at,
            'progress_percent':  int((current / achievement.required_value) * 100)
                                 if achievement.required_value > 0 else 0,
        })

    # Grouper par catégorie
    by_category = {}
    for data in achievements_data:
        cat = data['achievement'].category
        by_category.setdefault(cat, []).append(data)

    total_achievements = all_achievements.count()
    context = {
        'achievements':       achievements_data,
        'by_category':        by_category,
        'total_completed':    total_completed,
        'total_achievements': total_achievements,
        'completion_percent': int((total_completed / total_achievements) * 100)
                              if total_achievements > 0 else 0,
    }
    return render(request, 'achievements/achievements_list.html', context)


@login_required
def achievements_widget_view(request):
    """Widget AJAX pour afficher les achievements dans le navbar"""
    trainer = get_player_trainer(request.user)

    recent = TrainerAchievement.objects.filter(
        trainer=trainer, is_completed=True
    ).order_by('-completed_at')[:3]

    in_progress = TrainerAchievement.objects.filter(
        trainer=trainer, is_completed=False
    ).exclude(current_progress=0).order_by('-current_progress')[:3]

    return render(request, 'achievements/achievements_widget.html', {
        'recent':      recent,
        'in_progress': in_progress,
    })