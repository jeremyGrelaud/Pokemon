import logging
from django.db.models import Prefetch

from myPokemonApp.models.Trainer import Trainer
from myPokemonApp.models.PlayablePokemon import PlayablePokemon
from myPokemonApp.models.Battle import Battle
from myPokemonApp.models.Zone import PlayerLocation
from myPokemonApp.models.GameSave import GameSave

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

# Champs nécessaires pour le widget sidebar — on évite de charger tous les champs
_PARTY_FIELDS = (
    'id', 'nickname', 'current_hp', 'max_hp',
    'status_condition', 'party_position', 'is_shiny',
    'species_id',
)


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
        # ── Requête principale : Trainer + toutes ses relations ────
        trainer = (
            Trainer.objects
            .filter(user=request.user)
            .prefetch_related(
                # GameSaves actives — on filtre côté DB, pas en Python
                Prefetch(
                    'game_saves',
                    queryset=GameSave.objects.filter(is_active=True).order_by('-last_saved'),
                    to_attr='active_saves_list',
                ),
                # Équipe active — select_related('species') pour le nom + sprite
                Prefetch(
                    'pokemon_team',
                    queryset=PlayablePokemon.objects
                        .filter(is_in_party=True)
                        .select_related('species')
                        .order_by('party_position'),
                    to_attr='active_party',
                ),
                # Combat en cours — on limite à 1 résultat via slicing après prefetch
                Prefetch(
                    'battles_as_player',
                    queryset=Battle.objects
                        .filter(is_active=True)
                        .order_by('-created_at'),
                    to_attr='active_battles_list',
                ),
            )
            .get(user=request.user)
        )

    except Trainer.DoesNotExist:
        # Utilisateur connecté mais sans Trainer associé (compte créé sans profil)
        return dict(_EMPTY)
    except Exception:
        logger.warning(
            "context_processors.active_save: erreur inattendue pour user=%s",
            getattr(request.user, 'pk', '?'),
            exc_info=True,
        )
        return dict(_EMPTY)

    # ── GameSave active ───────────────────────────────────────────────────────
    save = trainer.active_saves_list[0] if trainer.active_saves_list else None

    # ── Zone courante (PlayerLocation) ────────────────────────────────────────
    current_zone = None
    try:
        loc = (
            PlayerLocation.objects
            .select_related('current_zone')
            .only('trainer_id', 'current_zone') # On charge seulement les champs nous intéressant
            .get(trainer=trainer)
        )
        current_zone = loc.current_zone
    except PlayerLocation.DoesNotExist:
        pass  # Normal : le joueur n'a pas encore de localisation
    except Exception:
        logger.warning(
            "context_processors.active_save: impossible de charger PlayerLocation "
            "pour trainer_id=%s",
            trainer.pk,
            exc_info=True,
        )

    # ── Sidebar équipe ────────────────────────────────────────────────────────
    sidebar_team        = []
    team_needs_healing  = False
    lead_pokemon_sprite = None

    for i, p in enumerate(trainer.active_party[:6]):
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
            safe    = (
                p.species.name
                .lower()
                .replace(' ', '-')
                .replace("'", '')
                .replace('.', '')
            )
            lead_pokemon_sprite = f'img/sprites_gen5/{variant}/{safe}.png'

    # ── Combat en cours ───────────────────────────────────────────────────────
    active_battle = (
        trainer.active_battles_list[0] if trainer.active_battles_list else None
    )

    return {
        'active_save':          save,
        'has_active_save':      save is not None,
        'current_zone':         current_zone,
        'sidebar_team':         sidebar_team,
        'team_needs_healing':   team_needs_healing,
        'active_battle':        active_battle,
        'lead_pokemon_sprite':  lead_pokemon_sprite,
    }