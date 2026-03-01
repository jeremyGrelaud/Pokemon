"""
Système de succès/achievements — version corrigée
=================================================

Corrections par rapport à l'ancienne version :

1. ANCIEN  check_achievement() faisait += increment à l'aveugle
   NOUVEAU sync_achievement(trainer, name, real_value) écrase avec la vraie valeur
   → Idempotent, pas d'over-counting, robuste aux relances

2. ANCIEN  "Collectionneur Débutant/Expert", "Connaisseur" n'étaient jamais déclenchés
   NOUVEAU trigger_achievements_after_capture() les inclut tous

3. ANCIEN  trigger_achievements_after_gym_win incrémentait +1 à chaque badge
   NOUVEAU il lit trainer.badges (la vraie valeur déjà incrémentée)

4. NOUVEAU trigger_achievements_after_level_up() pour "Niveau 50" / "Niveau 100"

5. NOUVEAU trigger_achievements_after_zone_visit() pour "Globe-Trotter"
   lit PlayerLocation.visited_zones.count() (M2M existant)

6. check_achievement() conservé comme alias de compatibilité descendante
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from myPokemonApp.models import (
    Achievement, TrainerAchievement,
    CaptureJournal, TrainerBattleHistory,
    PlayablePokemon,
)
from myPokemonApp.models.Trainer import TrainerInventory
from myPokemonApp.gameUtils import get_player_trainer


# =============================================================================
# HELPERS INTERNES
# =============================================================================

def _get_or_create_ta(trainer, achievement):
    ta, _ = TrainerAchievement.objects.get_or_create(
        trainer=trainer,
        achievement=achievement,
        defaults={'current_progress': 0},
    )
    return ta


def _grant_reward(trainer, achievement):
    """Verse argent + item récompense."""
    if achievement.reward_money > 0:
        trainer.money += achievement.reward_money
        trainer.save(update_fields=['money'])
    if achievement.reward_item:
        inv, _ = TrainerInventory.objects.get_or_create(
            trainer=trainer,
            item=achievement.reward_item,
        )
        inv.quantity += 1
        inv.save(update_fields=['quantity'])


def _try_complete(ta):
    """Complète l'achievement si le seuil est atteint. Retourne True si nouvellement complété."""
    if ta.is_completed:
        return False
    if ta.current_progress >= ta.achievement.required_value:
        ta.is_completed = True
        ta.completed_at = timezone.now()
        ta.save(update_fields=['is_completed', 'completed_at'])
        _grant_reward(ta.trainer, ta.achievement)
        return True
    return False


def _make_notif(name, reward_money):
    return {'title': f'🏆 {name}', 'message': f'Débloqué ! +{reward_money}₽'}


# =============================================================================
# FONCTION CENTRALE : sync_achievement
# =============================================================================

def sync_achievement(trainer, achievement_name, real_value):
    """
    Synchronise la progression d'un achievement avec la **vraie valeur** actuelle.

    Contrairement à l'ancien check_achievement() qui ajoutait +N sans plafond,
    cette fonction :
      - Ne fait monter le compteur que si real_value > current_progress
      (jamais reculer, jamais sur-compter)
      - Est idempotente : appeler deux fois avec real_value=5 donne 5, pas 10

    Args:
        trainer        : instance Trainer
        achievement_name : str  — doit correspondre à Achievement.name en base
        real_value     : int  — la vraie valeur actuelle (ex : total captures DB)

    Returns dict :
        {
          'newly_completed'  : bool,
          'already_completed': bool,
          'reward_money'     : int,
          'reward_item'      : str | None,
          'progress'         : int,
          'total'            : int,
        }
    """
    try:
        achievement = Achievement.objects.get(name=achievement_name)
    except Achievement.DoesNotExist:
        return {'newly_completed': False, 'progress': 0, 'total': 0}

    ta = _get_or_create_ta(trainer, achievement)

    if ta.is_completed:
        return {
            'newly_completed':   False,
            'already_completed': True,
            'progress':          ta.current_progress,
            'total':             achievement.required_value,
            'reward_money':      0,
            'reward_item':       None,
        }

    if real_value > ta.current_progress:
        ta.current_progress = real_value
        ta.save(update_fields=['current_progress'])

    newly_completed = _try_complete(ta)

    return {
        'newly_completed':   newly_completed,
        'already_completed': False,
        'reward_money':      achievement.reward_money if newly_completed else 0,
        'reward_item':       achievement.reward_item.name if (newly_completed and achievement.reward_item) else None,
        'progress':          ta.current_progress,
        'total':             achievement.required_value,
    }


# =============================================================================
# ALIAS DE COMPATIBILITÉ (ancienne API)
# =============================================================================

def check_achievement(trainer, achievement_name, increment=1):
    """
    Compatibilité descendante.
    Redirige vers sync_achievement() avec la vraie valeur depuis la DB.
    """
    # Achievements comptés depuis TrainerBattleHistory
    combat_names = {'Premier Combat', 'Combattant Aguerri', 'Vétéran'}
    # Achievements comptés depuis CaptureJournal (par nombre total)
    capture_count_names = {
        'Premier Compagnon', 'Collectionneur Débutant', 'Collectionneur Expert',
    }
    # Achievements comptés depuis CaptureJournal (espèces uniques)
    capture_species_names = {'Connaisseur', 'Maître Pokémon'}
    # Achievements liés aux badges
    badge_names = {'Champion de Arène', 'Maître de la Ligue'}

    if achievement_name in combat_names:
        wins = TrainerBattleHistory.objects.filter(player=trainer, player_won=True).count()
        return sync_achievement(trainer, achievement_name, wins)

    elif achievement_name in capture_count_names:
        total = CaptureJournal.objects.filter(trainer=trainer).count()
        return sync_achievement(trainer, achievement_name, total)

    elif achievement_name in capture_species_names:
        species = (
            CaptureJournal.objects.filter(trainer=trainer)
            .values('pokemon__species').distinct().count()
        )
        return sync_achievement(trainer, achievement_name, species)

    elif achievement_name in badge_names:
        return sync_achievement(trainer, achievement_name, trainer.badges)

    else:
        # Fallback incrémental pour achievements non encore migrés
        try:
            achievement = Achievement.objects.get(name=achievement_name)
        except Achievement.DoesNotExist:
            return {'newly_completed': False, 'progress': 0, 'total': 0}

        ta = _get_or_create_ta(trainer, achievement)
        if ta.is_completed:
            return {
                'newly_completed':   False,
                'already_completed': True,
                'progress':          ta.current_progress,
                'total':             achievement.required_value,
            }
        ta.current_progress += increment
        ta.save(update_fields=['current_progress'])
        newly_completed = _try_complete(ta)
        return {
            'newly_completed': newly_completed,
            'progress':        ta.current_progress,
            'total':           achievement.required_value,
            'reward_money':    achievement.reward_money if newly_completed else 0,
            'reward_item':     achievement.reward_item.name if (newly_completed and achievement.reward_item) else None,
        }


# =============================================================================
# TRIGGERS MÉTIER
# =============================================================================

def trigger_achievements_after_battle(trainer, battle_result):
    """Appelé après chaque combat. Lit le vrai total de victoires en DB."""
    notifications = []
    if not battle_result.get('won'):
        return notifications

    total_wins = TrainerBattleHistory.objects.filter(
        player=trainer, player_won=True
    ).count()

    for name, threshold in [
        ('Premier Combat',     1),
        ('Combattant Aguerri', 50),
        ('Vétéran',            100),
    ]:
        if total_wins >= threshold:
            r = sync_achievement(trainer, name, total_wins)
            if r.get('newly_completed'):
                notifications.append(_make_notif(name, r['reward_money']))

    return notifications


def trigger_achievements_after_gym_win(trainer, badges_count):
    """
    Appelé après victoire contre un gym leader.
    badges_count = trainer.badges déjà mis à jour avant cet appel.
    """
    notifications = []
    for name, threshold in [
        ('Champion de Arène',  1),
        ('Maître de la Ligue', 8),
    ]:
        if badges_count >= threshold:
            r = sync_achievement(trainer, name, badges_count)
            if r.get('newly_completed'):
                notifications.append(_make_notif(name, r['reward_money']))
    return notifications


def trigger_achievements_after_capture(trainer):
    """
    Appelé après chaque capture réussie.
    Déclenche tous les achievements capture/collection en une passe.
    """
    notifications = []

    total_captures = CaptureJournal.objects.filter(trainer=trainer).count()
    unique_species = (
        CaptureJournal.objects.filter(trainer=trainer)
        .values('pokemon__species').distinct().count()
    )
    party_size = trainer.pokemon_team.filter(is_in_party=True).count()

    checks = [
        ('Premier Compagnon',        total_captures),
        ('Collectionneur Débutant',  total_captures),   # seuil 10
        ('Collectionneur Expert',    total_captures),   # seuil 50
        ('Connaisseur',              unique_species),   # seuil 50 espèces
        ('Maître Pokémon',           unique_species),   # seuil 151
        ('Dresseur Complet',         party_size),       # seuil 6
    ]

    for name, val in checks:
        r = sync_achievement(trainer, name, val)
        if r.get('newly_completed'):
            notifications.append(_make_notif(name, r['reward_money']))

    return notifications


def trigger_achievements_after_level_up(trainer, new_level):
    """
    Appelé depuis BattleViews._handle_attack() quand un Pokémon monte de niveau.
    Vérifie le niveau max dans toute l'équipe (PC inclus).
    """
    notifications = []

    max_level = (
        PlayablePokemon.objects
        .filter(trainer=trainer)
        .order_by('-level')
        .values_list('level', flat=True)
        .first()
    ) or new_level

    for name, threshold in [
        ('Niveau 50',  50),
        ('Niveau 100', 100),
    ]:
        if max_level >= threshold:
            r = sync_achievement(trainer, name, max_level)
            if r.get('newly_completed'):
                notifications.append(_make_notif(name, r['reward_money']))

    return notifications


def trigger_achievements_after_zone_visit(trainer):
    """
    Appelé depuis MapViews après chaque déplacement réussi.
    Lit PlayerLocation.visited_zones.count() (M2M existant).
    """
    notifications = []

    try:
        visited_count = trainer.player_location.visited_zones.count()
    except Exception:
        return notifications

    for name, threshold in [
        ('Explorateur',   10),
        ('Globe-Trotter', 30),
    ]:
        if visited_count >= threshold:
            r = sync_achievement(trainer, name, visited_count)
            if r.get('newly_completed'):
                notifications.append(_make_notif(name, r['reward_money']))

    return notifications


# =============================================================================
# VUES
# =============================================================================

@login_required
def achievements_list_view(request):
    """Page Succès + Stats du joueur."""
    trainer = get_player_trainer(request.user)

    # ── Stats réelles depuis les modèles DB ───────────────────────────────
    total_wins   = TrainerBattleHistory.objects.filter(player=trainer, player_won=True).count()
    total_losses = TrainerBattleHistory.objects.filter(player=trainer, player_won=False).count()
    total_battles = total_wins + total_losses
    win_rate = round(total_wins / total_battles * 100, 1) if total_battles else 0

    total_captures = CaptureJournal.objects.filter(trainer=trainer).count()
    unique_species = (
        CaptureJournal.objects.filter(trainer=trainer)
        .values('pokemon__species').distinct().count()
    )
    critical_catches = CaptureJournal.objects.filter(trainer=trainer, is_critical_catch=True).count()

    from myPokemonApp.models.CaptureSystem import CaptureAttempt
    total_attempts   = CaptureAttempt.objects.filter(trainer=trainer).count()
    success_attempts = CaptureAttempt.objects.filter(trainer=trainer, success=True).count()
    capture_rate_pct = round(success_attempts / total_attempts * 100, 1) if total_attempts else 0

    best_pokemon = (
        PlayablePokemon.objects
        .filter(trainer=trainer)
        .order_by('-level')
        .select_related('species')
        .first()
    )

    try:
        visited_count = trainer.player_location.visited_zones.count()
    except Exception:
        visited_count = 0

    from myPokemonApp.models.GameSave import GameSave
    from myPokemonApp.models.Quest import QuestProgress
    save = GameSave.objects.filter(trainer=trainer, is_active=True).first()

    quests_completed = QuestProgress.objects.filter(trainer=trainer, state='completed').count()
    quests_active    = QuestProgress.objects.filter(trainer=trainer, state='active').count()
    quests_total     = QuestProgress.objects.filter(trainer=trainer).exclude(state='locked').count()

    stats = {
        'total_wins':        total_wins,
        'total_losses':      total_losses,
        'total_battles':     total_battles,
        'win_rate':          win_rate,
        'total_captures':    total_captures,
        'unique_species':    unique_species,
        'critical_catches':  critical_catches,
        'capture_rate_pct':  capture_rate_pct,
        'total_attempts':    total_attempts,
        'best_pokemon':      best_pokemon,
        'zones_visited':     visited_count,
        'zones_total':       30,
        'badges':            trainer.badges,
        'money':             trainer.money,
        'quests_completed':  quests_completed,
        'quests_active':     quests_active,
        'quests_total':      quests_total,
        'party_count':       trainer.pokemon_team.filter(is_in_party=True).count(),
        'pc_count':          trainer.pokemon_team.filter(is_in_party=False).count(),
        'play_time':         save.get_play_time_display() if save else '0h00m',
    }

    # ── Achievements ───────────────────────────────────────────────────────
    all_achievements = Achievement.objects.all()
    progress_map = {
        ta.achievement_id: ta
        for ta in TrainerAchievement.objects.filter(trainer=trainer).select_related('achievement')
    }

    achievements_data = []
    total_completed = 0

    for ach in all_achievements:
        ta           = progress_map.get(ach.id)
        current      = ta.current_progress if ta else 0
        completed    = ta.is_completed     if ta else False
        completed_at = ta.completed_at     if ta else None
        if completed:
            total_completed += 1
        pct = min(100, int(current / ach.required_value * 100)) if ach.required_value else 0

        achievements_data.append({
            'achievement':      ach,
            'current':          current,
            'required':         ach.required_value,
            'completed':        completed,
            'completed_at':     completed_at,
            'progress_percent': pct,
        })

    by_category = {}
    for d in achievements_data:
        by_category.setdefault(d['achievement'].category, []).append(d)

    total_achievements = all_achievements.count()

    return render(request, 'achievements/achievements_list.html', {
        'achievements':       achievements_data,
        'by_category':        by_category,
        'total_completed':    total_completed,
        'total_achievements': total_achievements,
        'completion_percent': int(total_completed / total_achievements * 100) if total_achievements else 0,
        'stats':              stats,
        'trainer':            trainer,
    })


@login_required
def achievements_widget_view(request):
    """Widget AJAX navbar."""
    trainer = get_player_trainer(request.user)
    recent = (
        TrainerAchievement.objects
        .filter(trainer=trainer, is_completed=True)
        .select_related('achievement')
        .order_by('-completed_at')[:3]
    )
    in_progress = (
        TrainerAchievement.objects
        .filter(trainer=trainer, is_completed=False)
        .exclude(current_progress=0)
        .select_related('achievement')
        .order_by('-current_progress')[:3]
    )
    return render(request, 'achievements/achievements_widget.html', {
        'recent':      recent,
        'in_progress': in_progress,
    })