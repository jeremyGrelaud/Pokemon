import logging
from myPokemonApp.models import GameSave, Trainer

logger = logging.getLogger(__name__)

_EMPTY = {
    'active_save':        None,
    'has_active_save':    False,
    'current_zone':       None,
    'sidebar_team':       [],
    'team_needs_healing': False,
}


def active_save(request):
    """
    Injecte dans chaque template :
      - active_save / has_active_save   — GameSave active
      - current_zone                    — Zone courante du joueur (PlayerLocation)
      - sidebar_team                    — Liste [{name, hp_pct, needs, status}] pour le widget HP sidebar
      - team_needs_healing              — True si au moins un Pokémon de l'équipe a besoin de soins

    Retourne des valeurs nulles si le joueur n'a pas encore de Trainer
    (nouveau compte avant choose_starter) sans déclencher d'erreur.
    """
    if not request.user.is_authenticated:
        return dict(_EMPTY)

    try:
        trainer = Trainer.objects.get(username=request.user.username)
        save    = GameSave.objects.filter(trainer=trainer, is_active=True).first()

        # ── Zone courante ────────────────────────────────────────────────────
        current_zone = None
        try:
            from myPokemonApp.models import PlayerLocation
            loc = PlayerLocation.objects.select_related('current_zone').get(trainer=trainer)
            current_zone = loc.current_zone
        except Exception:
            pass

        # ── Mini-équipe pour le widget HP de la sidebar ──────────────────────
        sidebar_team       = []
        team_needs_healing = False
        try:
            party = trainer.pokemon_team.filter(is_in_party=True).select_related('species')[:6]
            for p in party:
                hp_pct = int(p.current_hp / p.max_hp * 100) if p.max_hp else 0
                needs  = p.current_hp < p.max_hp or bool(p.status_condition)
                if needs:
                    team_needs_healing = True
                sidebar_team.append({
                    'name':   p.nickname or p.species.name,
                    'hp_pct': hp_pct,
                    'needs':  needs,
                    'status': p.status_condition or '',
                })
        except Exception:
            pass

        return {
            'active_save':        save,
            'has_active_save':    save is not None,
            'current_zone':       current_zone,
            'sidebar_team':       sidebar_team,
            'team_needs_healing': team_needs_healing,
        }

    except Trainer.DoesNotExist:
        return dict(_EMPTY)