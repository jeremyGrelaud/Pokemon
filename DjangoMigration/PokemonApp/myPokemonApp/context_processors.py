import logging
from myPokemonApp.models import GameSave, Trainer

logger = logging.getLogger(__name__)

_EMPTY = {
    'active_save':          None,
    'has_active_save':      False,
    'current_zone':         None,
    'sidebar_team':         [],
    'team_needs_healing':   False,
    'active_battle':        None,
    'lead_pokemon_sprite':  None,
}


def active_save(request):
    """
    Injecte dans chaque template :
      - active_save / has_active_save   — GameSave active
      - current_zone                    — Zone courante du joueur (PlayerLocation)
      - sidebar_team                    — Liste [{name, hp_pct, needs, status}]
      - team_needs_healing              — True si au moins un Pokémon a besoin de soins
      - active_battle                   — Combat Battle en cours (is_active=True), ou None
      - lead_pokemon_sprite             — Chemin relatif du sprite du Pokémon de tête
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
        sidebar_team        = []
        team_needs_healing  = False
        lead_pokemon_sprite = None
        try:
            party = trainer.pokemon_team.filter(
                is_in_party=True
            ).select_related('species').order_by('party_position')[:6]
            for i, p in enumerate(party):
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
                if i == 0:
                    variant = 'shiny' if p.is_shiny else 'normal'
                    safe    = p.species.name.lower().replace(' ', '-').replace("'", '').replace('.', '')
                    lead_pokemon_sprite = f'img/sprites_gen5/{variant}/{safe}.png'
        except Exception:
            pass

        # ── Combat en cours ──────────────────────────────────────────────────
        active_battle = None
        try:
            from myPokemonApp.models import Battle
            active_battle = Battle.objects.filter(
                player_trainer=trainer, is_active=True
            ).order_by('-created_at').first()
        except Exception:
            pass

        return {
            'active_save':          save,
            'has_active_save':      save is not None,
            'current_zone':         current_zone,
            'sidebar_team':         sidebar_team,
            'team_needs_healing':   team_needs_healing,
            'active_battle':        active_battle,
            'lead_pokemon_sprite':  lead_pokemon_sprite,
        }

    except Trainer.DoesNotExist:
        return dict(_EMPTY)