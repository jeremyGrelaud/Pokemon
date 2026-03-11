#!/usr/bin/python3
"""
Vues Django — vue graphique du combat (rendu battle_game_v2.html).
"""

import logging

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import generic

from myPokemonApp.models.Battle import Battle
from myPokemonApp.models.Zone import PlayerLocation
from myPokemonApp.gameUtils import get_player_trainer

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class BattleGameView(generic.DetailView):
    """Vue du combat en mode graphique (template battle_game_v2)."""
    model               = Battle
    template_name       = 'battle/battle_game_v2.html'
    context_object_name = 'battle'

    def get_queryset(self):
        trainer = get_player_trainer(self.request.user)
        return Battle.objects.filter(player_trainer=trainer)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        battle  = self.object
        if not battle.player_pokemon or not battle.opponent_pokemon:
            context['error'] = "Combat invalide : Pokemon manquant"

        # Zone actuelle du joueur (pour les boutons "Retour" des modals)
        try:
            player_location = PlayerLocation.objects.get(trainer=battle.player_trainer)
            current_zone = player_location.current_zone
            context['current_zone'] = current_zone
        except PlayerLocation.DoesNotExist:
            current_zone = None
            context['current_zone'] = None

        zone_type = getattr(current_zone, 'zone_type', 'route') if current_zone else 'route'
        zone_name = (getattr(current_zone, 'name', '') or '').lower()

        def _pick_bg(ztype, zname):
            """Mapping zone_type/nom → (data-terrain CSS, fichier bg, couleur fallback)."""
            if ztype == 'route':
                if any(k in zname for k in ('desert', 'sable', 'sahara')):
                    return ('desert',        'bg-desert',        '#c9a227')
                if any(k in zname for k in ('montagne', 'mountain', 'pic', 'summit')):
                    return ('mountain',      'bg-mountain',      '#797d7f')
                if any(k in zname for k in ('thunder', 'foudre', 'orage', 'electr')):
                    return ('thunderplains', 'bg-thunderplains', '#2c3e50')
                return ('route',             'bg-route',         '#5cb85c')

            if ztype == 'city':
                return ('city',              'bg-city',          '#8fa8c8')

            if ztype == 'cave':
                if any(k in zname for k in ('glace', 'ice', 'gel', 'frost')):
                    return ('icecave',        'bg-icecave',       '#aed6f1')
                if any(k in zname for k in ('volcan', 'volcano', 'feu', 'fire', 'magma', 'lava')):
                    return ('volcanocave',    'bg-volcanocave',   '#7b241c')
                if any(k in zname for k in ('terre', 'earth', 'sable', 'sandy')):
                    return ('earthycave',     'bg-earthycave',    '#3d2b1f')
                return ('cave',               'bg-dampcave',      '#1a1a1a')

            if ztype == 'forest':
                return ('forest',            'bg-forest',        '#1b4332')

            if ztype == 'water':
                if any(k in zname for k in ('mer', 'sea', 'ocean', 'deep', 'abyssal', 'fond')):
                    return ('sea',            'bg-deepsea',       '#1a3a5c')
                if any(k in zname for k in ('plage', 'beach', 'rivage', 'shore')):
                    return ('beach',          'bg-beachshore',    '#70a8d8')
                return ('water',              'bg-river',         '#1a6699')

            if ztype == 'building':
                return ('city',              'bg-city',          '#2a2a2a')

            return ('route',                 'bg-meadow',        '#5cb85c')  # fallback

        terrain, bg_key, bg_fallback = _pick_bg(zone_type, zone_name)

        # Extension : .jpg uniquement pour bg-space, sinon .png
        bg_ext = '.jpg' if bg_key == 'bg-space' else '.png'

        context['battle_terrain']     = terrain
        context['battle_bg_png']      = f'/static/img/battle_backgrounds/{bg_key}{bg_ext}'
        context['battle_bg_fallback'] = bg_fallback

        # Rival : trainer_type == 'rival' → musique spéciale
        context['is_rival'] = (
            battle.opponent_trainer is not None
            and battle.opponent_trainer.trainer_type == 'rival'
        )

        # Pourcentage EXP correct (relatif au niveau actuel, pas cumulatif)
        pp = battle.player_pokemon
        if pp:
            exp_at_current = pp.exp_at_level(pp.level)
            exp_at_next    = pp.exp_for_next_level()
            exp_in_level   = max(0, (pp.current_exp or 0) - exp_at_current)
            exp_needed     = max(1, exp_at_next - exp_at_current)
            context['initial_exp_percent'] = int(min(100, (exp_in_level / exp_needed) * 100))
        else:
            context['initial_exp_percent'] = 0

        return context