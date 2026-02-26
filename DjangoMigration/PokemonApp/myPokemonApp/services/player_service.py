"""
myPokemonApp/services/player_service.py
=========================================
Helpers orientés « joueur » : récupération du Trainer, de sa position,
de ses dresseurs vaincus, etc.

Ces fonctions vivaient dans gameUtils.py (section 11 + quelques fonctions
de section 1). Elles dépendent uniquement des modèles → extraction sans risque.

Exports publics :
    get_player_trainer(user)                      → Trainer (404 si absent)
    get_or_create_player_trainer(user)            → Trainer
    get_player_location(trainer, create_if_missing=True) → PlayerLocation
    get_defeated_trainer_ids(trainer)             → set[int]
    trainer_is_at_zone_with(trainer, zone_attr)   → bool
    has_pokedex(trainer)                          → bool
    grant_pokedex(trainer)                        → None
    auto_reorganize_party(trainer)                → None
    organize_party(trainer, pokemon_order)        → None
    ZONE_TRANSLATIONS                             → dict[str, str]
"""

# Correspondance noms de zones français → gym_city anglais (tel qu'en base GymLeader)
# Source unique de vérité, importée depuis MapViews + BattleViews.
ZONE_TRANSLATIONS = {
    "Argenta":        "Pewter City",
    "Azuria":         "Cerulean City",
    "Carmin sur Mer": "Vermilion City",
    "Céladopole":     "Celadon City",
    "Jadielle":       "Viridian City",
    "Safrania":       "Saffron City",
    "Parmanie":       "Fuchsia City",
    "Cramois'Ile":    "Cinnabar Island",
}


# ─────────────────────────────────────────────────────────────────────────────
# Trainer lookup
# ─────────────────────────────────────────────────────────────────────────────

def get_player_trainer(user):
    """
    Récupère le Trainer du joueur connecté (404 si inexistant).

    À utiliser dans les vues où le Trainer est garanti d'exister déjà
    (après le flow choose_starter). Pour les nouveaux joueurs, préférer
    get_or_create_player_trainer().

    Usage :
        trainer = get_player_trainer(request.user)
    """
    from django.shortcuts import get_object_or_404
    from myPokemonApp.models import Trainer
    return get_object_or_404(Trainer, username=user.username)


def get_or_create_player_trainer(user):
    """
    Récupère ou crée le Trainer associé à un utilisateur Django.

    Centralise le pattern répété dans chaque vue :
        trainer, _ = Trainer.objects.get_or_create(
            username=request.user.username,
            defaults={'trainer_type': 'player'}
        )

    Usage :
        trainer = get_or_create_player_trainer(request.user)
    """
    from myPokemonApp.models import Trainer
    trainer, _ = Trainer.objects.get_or_create(
        username=user.username,
        defaults={'trainer_type': 'player'}
    )
    return trainer


# ─────────────────────────────────────────────────────────────────────────────
# Location
# ─────────────────────────────────────────────────────────────────────────────

def get_player_location(trainer, create_if_missing=True):
    """
    Récupère le PlayerLocation du trainer, en créant la position initiale
    (Bourg Palette ou première zone) si elle n'existe pas encore et que
    create_if_missing=True.

    Usage :
        location = get_player_location(trainer)
        current_zone = location.current_zone
    """
    from myPokemonApp.models import PlayerLocation, Zone

    try:
        return PlayerLocation.objects.get(trainer=trainer)
    except PlayerLocation.DoesNotExist:
        if not create_if_missing:
            return None
        start_zone = (
            Zone.objects.filter(name__icontains='Bourg Palette').first()
            or Zone.objects.first()
        )
        return PlayerLocation.objects.create(trainer=trainer, current_zone=start_zone)


def trainer_is_at_zone_with(trainer, zone_attr: str) -> bool:
    """
    Retourne True si le trainer se trouve dans une zone possédant l'attribut
    booléen zone_attr (ex. 'has_shop', 'has_pokemon_center').

    Si le trainer n'a pas de PlayerLocation connue, retourne True par défaut
    pour ne pas bloquer les joueurs sans position.

    Usage :
        if not trainer_is_at_zone_with(trainer, 'has_shop'):
            return redirect('map_view')
    """
    location = get_player_location(trainer, create_if_missing=False)
    if location is None:
        return True  # pas de position connue → on ne bloque pas
    return bool(getattr(location.current_zone, zone_attr, False))


# ─────────────────────────────────────────────────────────────────────────────
# Save / progression
# ─────────────────────────────────────────────────────────────────────────────

def get_defeated_trainer_ids(player_trainer) -> set:
    """
    Retourne le set des IDs de Trainers NPC vaincus par ce joueur.

    Récupère la save active en une seule requête DB et retourne
    un set Python pour des tests d'appartenance en O(1).

    À utiliser dans les vues qui itèrent sur N trainers pour éviter
    le N+1 que produirait npc.is_defeated_by_player() dans une boucle.

    Usage :
        defeated_ids = get_defeated_trainer_ids(trainer)
        for npc in trainers:
            is_beaten = npc.id in defeated_ids
    """
    from myPokemonApp.models.GameSave import GameSave
    save = GameSave.objects.filter(trainer=player_trainer, is_active=True).first()
    if save is None:
        return set()
    return set(save.defeated_trainers)


def has_pokedex(player_trainer) -> bool:
    """
    Retourne True si le joueur a reçu son Pokédex.
    Vérifie le story_flag 'has_pokedex' dans la GameSave active.

    Usage :
        if not has_pokedex(trainer):
            return HttpResponseForbidden(...)
    """
    from myPokemonApp.models.GameSave import GameSave
    save = GameSave.objects.filter(trainer=player_trainer, is_active=True).first()
    return bool(save and save.story_flags.get('has_pokedex', False))


def grant_pokedex(player_trainer) -> None:
    """
    Donne le Pokédex au joueur en posant le story_flag 'has_pokedex'
    sur sa GameSave active. Si aucune save n'existe, en crée une au slot 1.

    À appeler dès que le joueur choisit son starter.

    Usage :
        grant_pokedex(trainer)
    """
    from myPokemonApp.models.GameSave import GameSave
    save = GameSave.objects.filter(trainer=player_trainer, is_active=True).first()
    if save is None:
        save, _ = GameSave.objects.get_or_create(
            trainer=player_trainer,
            slot=1,
            defaults={'is_active': True}
        )
    save.set_story_flag('has_pokedex', True)


# ─────────────────────────────────────────────────────────────────────────────
# Équipe / PC
# ─────────────────────────────────────────────────────────────────────────────

def auto_reorganize_party(trainer) -> None:
    """
    Réassigne des positions séquentielles (1-6) aux Pokémon de l'équipe
    active dans leur ordre courant (party_position, id).

    À appeler après un dépôt au PC ou un ajout depuis le PC pour garantir
    que les positions restent continues et sans trous.
    """
    for position, pokemon in enumerate(
        trainer.pokemon_team.filter(is_in_party=True).order_by('party_position', 'id'),
        start=1,
    ):
        pokemon.party_position = position
        pokemon.save(update_fields=['party_position'])


def organize_party(trainer, pokemon_order: list) -> None:
    """
    Réordonne l'équipe du dresseur selon une liste d'IDs fournie par le client
    (drag-and-drop).

    pokemon_order = [pokemon_id_1, pokemon_id_2, ...]

    Distinct de auto_reorganize_party() qui réordonne l'existant sans changer
    l'ordre.
    """
    for position, pokemon_id in enumerate(pokemon_order, 1):
        pokemon = trainer.pokemon_team.get(id=pokemon_id)
        pokemon.party_position = position
        pokemon.save(update_fields=['party_position'])