"""
Vues pour le système de quêtes.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from myPokemonApp.models import Quest, QuestProgress
from myPokemonApp.gameUtils import get_player_trainer
from myPokemonApp.questEngine import (
    get_quest_log, get_active_quests, complete_quest, get_quest_progress
)


@login_required
def quest_log_view(request):
    """Journal de quêtes complet du joueur."""
    trainer = get_player_trainer(request.user)
    log = get_quest_log(trainer)

    return render(request, 'quests/quest_log.html', {
        'log': log,
        'active_count': len(log['active']),
        'completed_count': len(log['completed']),
    })


@login_required
def quest_widget_view(request):
    """Widget HTMX/iframe — quêtes actives uniquement (pour le dashboard)."""
    trainer = get_player_trainer(request.user)
    active = get_active_quests(trainer)[:5]   # max 5 dans le widget

    return render(request, 'quests/quest_widget.html', {
        'active_quests': active,
    })


@login_required
def quest_detail_view(request, quest_id):
    """Détail d'une quête."""
    trainer  = get_player_trainer(request.user)
    quest    = get_object_or_404(Quest, quest_id=quest_id)
    progress = get_quest_progress(trainer, quest_id)

    return render(request, 'quests/quest_detail.html', {
        'quest':    quest,
        'progress': progress,
    })