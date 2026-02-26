#!/usr/bin/python3
"""
Views Django pour l'application Pokémon Gen 1
Adapté aux nouveaux modèles
"""

import json
from datetime import datetime, timedelta

from django.db.models import Count, Avg, Q
from django.db.models.functions import TruncDate
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models import *
from myPokemonApp.gameUtils import get_player_trainer


@login_required
def capture_journal_view(request):
    """Vue du journal de captures"""
    
    trainer = get_player_trainer(request.user)
    
    # Filtres
    search = request.GET.get('search', '')
    ball_filter = request.GET.get('ball', '')
    period_filter = request.GET.get('period', '')
    
    # Query de base
    captures = CaptureJournal.objects.filter(trainer=trainer)
    
    # Appliquer filtres
    if search:
        captures = captures.filter(
            Q(pokemon__species__name__icontains=search) |
            Q(pokemon__nickname__icontains=search)
        )
    
    if ball_filter:
        captures = captures.filter(ball_used__name__icontains=ball_filter)
    
    if period_filter == 'today':
        captures = captures.filter(captured_at__date=datetime.now().date())
    elif period_filter == 'week':
        week_ago = datetime.now() - timedelta(days=7)
        captures = captures.filter(captured_at__gte=week_ago)
    elif period_filter == 'month':
        month_ago = datetime.now() - timedelta(days=30)
        captures = captures.filter(captured_at__gte=month_ago)
    
    # Statistiques
    all_captures = CaptureJournal.objects.filter(trainer=trainer)
    all_attempts = CaptureAttempt.objects.filter(trainer=trainer)
    
    stats = {
        'total_captures': all_captures.count(),
        'unique_species': all_captures.values('pokemon__species').distinct().count(),
        'success_rate': 0,
        'critical_catches': all_captures.filter(is_critical_catch=True).count()
    }
    
    if all_attempts.count() > 0:
        success_count = all_attempts.filter(success=True).count()
        stats['success_rate'] = round((success_count / all_attempts.count()) * 100, 1)
    
    # Données pour graphique (30 derniers jours)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    daily_captures = all_captures.filter(
        captured_at__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('captured_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Préparer les données pour Chart.js
    chart_labels = []
    chart_data = []
    
    for i in range(30):
        date = (datetime.now() - timedelta(days=29-i)).date()
        chart_labels.append(date.strftime('%d/%m'))
        
        count = next((d['count'] for d in daily_captures if d['date'] == date), 0)
        chart_data.append(count)
    
    context = {
        'captures': captures[:50],  # Limiter à 50
        'stats': stats,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data)
    }
    
    return render(request, 'captures/capture_journal.html', context)