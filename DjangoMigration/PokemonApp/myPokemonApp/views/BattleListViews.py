#!/usr/bin/python3
"""
Vues Django — liste et détail des combats.
"""

from types import SimpleNamespace

from django.contrib.auth.decorators import login_required
from django.db.models import Case, Count, IntegerField, Prefetch, Q, When
from django.utils.decorators import method_decorator
from django.views import generic

from myPokemonApp.models.Battle import Battle
from myPokemonApp.models.GameSave import TrainerBattleHistory
from myPokemonApp.models.PlayablePokemon import PlayablePokemon
from myPokemonApp.gameUtils import get_player_trainer, get_or_create_player_trainer

import logging
logger = logging.getLogger(__name__)


# ── Utilitaires snapshot ──────────────────────────────────────────────────────

_STATUS_LABELS = {
    'poison':       'Empoisonné',
    'burn':         'Brûlé',
    'paralysis':    'Paralysé',
    'sleep':        'Endormi',
    'freeze':       'Gelé',
    'badly_poison': 'Gravement empoisonné',
}


def _snap_to_mock(entry, active_pokemon_id=None):
    """Convertit une entrée de battle_snapshot en mock compatible avec battle_detail.html."""
    species = SimpleNamespace(
        name=entry['species_name'],
        id=entry['species_id'],
        primary_type=SimpleNamespace(name=entry['primary_type']),
        secondary_type=(
            SimpleNamespace(name=entry['secondary_type'])
            if entry.get('secondary_type') else None
        ),
    )
    current_hp = entry.get('current_hp', 0)
    max_hp     = entry.get('max_hp', 0)
    status     = entry.get('status_condition') or None
    ko         = entry.get('ko', current_hp == 0)
    mock = SimpleNamespace(
        id=entry['id'],
        nickname=entry.get('nickname'),
        species=species,
        level=entry['level'],
        is_shiny=entry.get('is_shiny', False),
        attack=entry.get('attack'),
        defense=entry.get('defense'),
        speed=entry.get('speed'),
        max_hp=max_hp,
        current_hp=current_hp,
        ko=ko,
        status_condition=status,
        is_last_active=(entry['id'] == active_pokemon_id),
    )
    mock.get_status_condition_display = lambda: _STATUS_LABELS.get(status, status or '')
    return mock


# ── Vues ─────────────────────────────────────────────────────────────────────

@method_decorator(login_required, name='dispatch')
class BattleListView(generic.ListView):
    """Liste des combats du joueur connecté."""
    model               = Battle
    template_name       = 'battle/battle_list.html'
    context_object_name = 'battles'
    paginate_by         = 20

    def get_queryset(self):
        # Cache trainer sur self pour ne pas le recalculer dans get_context_data
        self._trainer = get_or_create_player_trainer(self.request.user)

        qs = (
            Battle.objects
            .filter(Q(player_trainer=self._trainer) | Q(opponent_trainer=self._trainer))
            .order_by('-created_at')
            .select_related(
                'player_trainer',
                'opponent_trainer',
                'winner',
                'player_pokemon__species',
                'opponent_pokemon__species',
            )
            .prefetch_related(
                Prefetch(
                    'opponent_trainer__pokemon_team',
                    queryset=PlayablePokemon.objects.select_related('species'),
                )
            )
        )

        result = self.request.GET.get('result', 'all')
        if result == 'win':
            qs = qs.filter(winner=self._trainer)
        elif result == 'loss':
            qs = qs.exclude(winner=self._trainer).exclude(winner__isnull=True)
        elif result == 'active':
            qs = qs.filter(is_active=True)

        battle_type = self.request.GET.get('type', 'all')
        if battle_type in ('wild', 'trainer', 'gym', 'elite_four'):
            qs = qs.filter(battle_type=battle_type)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer = getattr(self, '_trainer', None) or get_or_create_player_trainer(self.request.user)

        # 1 requête pour 4 counts
        stats = (
            Battle.objects
            .filter(Q(player_trainer=trainer) | Q(opponent_trainer=trainer))
            .aggregate(
                stat_total=Count('id'),
                stat_win=Count(
                    Case(When(winner=trainer, then=1), output_field=IntegerField())
                ),
                stat_loss=Count(
                    Case(
                        When(winner__isnull=False, then=1),
                        output_field=IntegerField(),
                    )
                ),
                stat_active=Count(
                    Case(When(is_active=True, then=1), output_field=IntegerField())
                ),
            )
        )
        # stat_loss tel que calculé inclut les victoires — on soustrait
        stats['stat_loss'] = stats['stat_loss'] - stats['stat_win']

        context.update(stats)
        context['result_filter'] = self.request.GET.get('result', 'all')
        context['type_filter']   = self.request.GET.get('type', 'all')

        for battle in context['battles']:
            if battle.battle_type == 'wild' and not battle.opponent_pokemon:
                snap    = battle.battle_snapshot if isinstance(battle.battle_snapshot, dict) else {}
                entries = snap.get('opponent_team', [])
                if entries:
                    e = entries[0]
                    battle.snap_opponent_name  = e.get('species_name', '?')
                    battle.snap_opponent_level = e.get('level', '?')
                    battle.snap_opponent_shiny = e.get('is_shiny', False)
                else:
                    battle.snap_opponent_name  = None
                    battle.snap_opponent_level = None
                    battle.snap_opponent_shiny = False

        return context


@method_decorator(login_required, name='dispatch')
class BattleDetailView(generic.DetailView):
    """Détails d'un combat terminé."""
    model               = Battle
    template_name       = 'battle/battle_detail.html'
    context_object_name = 'battle'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        battle  = self.object

        viewer     = get_player_trainer(self.request.user)
        player_won = (battle.winner == battle.player_trainer) if battle.winner else None

        snap               = battle.battle_snapshot if isinstance(battle.battle_snapshot, dict) else {}
        player_active_id   = battle.player_pokemon_id
        opponent_active_id = battle.opponent_pokemon_id

        # ── Équipe joueur ──────────────────────────────────────────────────────
        player_entries = snap.get('player_team')
        if player_entries:
            player_team = [_snap_to_mock(e, player_active_id) for e in player_entries]
        else:
            # Fallback legacy (combats antérieurs au champ battle_snapshot)
            bs = battle.battle_state if isinstance(battle.battle_state, dict) else {}
            used_ids = bs.get('player_used_ids', [])
            qs = battle.player_trainer.pokemon_team.select_related(
                'species', 'species__primary_type', 'species__secondary_type'
            )
            qs = qs.filter(id__in=used_ids) if used_ids else qs.filter(is_in_party=True)
            player_team = list(qs)
            for p in player_team:
                p.is_last_active = (p.id == player_active_id)

        # ── Équipe adversaire ──────────────────────────────────────────────────
        opponent_entries = snap.get('opponent_team')
        if opponent_entries:
            opponent_team = [_snap_to_mock(e, opponent_active_id) for e in opponent_entries]
        elif battle.opponent_pokemon:
            p = battle.opponent_pokemon
            p.is_last_active = True
            opponent_team = [p]
        else:
            opponent_team = []

        money_earned = 0
        try:
            history = TrainerBattleHistory.objects.get(
                battle=battle, player=battle.player_trainer
            )
            money_earned = history.money_earned
        except (TrainerBattleHistory.DoesNotExist, Exception):
            pass

        context.update({
            'viewer':        viewer,
            'player_won':    player_won,
            'player_team':   player_team,
            'opponent_team': opponent_team,
            'money_earned':  money_earned,
        })
        return context