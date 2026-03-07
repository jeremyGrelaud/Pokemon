"""
Initialise les zones Arène (building) pour chaque ville de Kanto.
Chaque arène est une Zone de type 'building', connectée à sa ville,
avec des dresseurs NPC obligatoires à battre avant d'affronter le Champion.

Convention de nommage : "Arène d'Argenta", "Arène d'Azuria", etc.
Les dresseurs ont location = "Arène d'Argenta" et is_battle_required = True.

À appeler depuis initAllDatabase.py ou manage.py shell.
"""

import logging
from myPokemonApp.models import Zone, ZoneConnection, Pokemon, PokemonMove, Trainer
from myPokemonApp.gameUtils import create_npc_trainer

logging.basicConfig(level=logging.INFO)


# ─────────────────────────────────────────────────────────────────────────────
# Mapping ville française → nom de l'arène
# ─────────────────────────────────────────────────────────────────────────────
# (ville, nom_arène, order, lv_min, lv_max, desc, music, badges_requis)
# badges_requis = badge_order du GymLeader précédent (0 = accès libre)
GYM_ZONES = [
    (
        'Argenta',
        "Arène d'Argenta",
        7, 8, 12,
        "L'Arène d'Argenta, dirigée par Pierre, spécialiste des types Roche. "
        "Deux jeunes dresseurs Roc gardent l'accès au Champion.",
        'gym',
        0,   # Premier badge : accès libre
    ),
    (
        'Azuria',
        "Arène d'Azuria",
        11, 18, 21,
        "L'Arène d'Azuria, dirigée par Ondine, spécialiste des types Eau. "
        "Plusieurs Sirènes montent la garde avant la Reine des Eaux.",
        'gym',
        1,   # Badge Pierre requis
    ),
    (
        'Carmin sur Mer',
        "Arène de Carmin sur Mer",
        16, 20, 25,
        "L'Arène de Carmin sur Mer, dirigée par le Capitaine Surge, spécialiste des types Électrik. "
        "Des soldats patrouillent les couloirs.",
        'gym',
        2,   # Badge Ondine requis
    ),
    (
        'Céladopole',
        "Arène de Céladopole",
        22, 30, 35,
        "L'Arène de Céladopole, dirigée par Olga, spécialiste des types Plante. "
        "Un labyrinthe de cloisons et des Beautés masquent le chemin vers la Reine.",
        'gym',
        3,   # Badge Surge requis
    ),
    (
        'Parmanie',
        "Arène de Parmanie",
        28, 40, 46,
        "L'Arène de Parmanie, dirigée par Stella, spécialiste des types Poison. "
        "Les dresseurs entraînent leurs Pokémon Poison dans des cibles colorées.",
        'gym',
        4,   # Badge Olga requis
    ),
    (
        'Safrania',
        "Arène de Safrania",
        24, 35, 42,
        "L'Arène de Safrania, dirigée par Morgane, spécialiste des types Psy. "
        "Des téléporteurs désorientent les challengers.",
        'gym',
        4,   # Badge Olga requis (Safrania accessible après Céladopole)
    ),
    (
        "Cramois'Île",
        "Arène de Cramois'Île",
        34, 45, 50,
        "L'Arène de Cramois'Île, dirigée par Pyro, spécialiste des types Feu. "
        "Des questions de culture Pokémon bloquent les portes.",
        'gym',
        6,   # Badges 1-6 requis
    ),
    (
        'Jadielle',
        "Arène de Jadielle",
        3, 38, 50,
        "L'Arène de Jadielle, dirigée par Giovanni, maître des types Sol. "
        "Réservée aux dresseurs possédant les 7 premiers badges.",
        'gym',
        7,   # 7 badges requis
    ),
]


def init_gym_zones():
    """Crée les zones Arène, les connecte à leurs villes et applique les restrictions de badges."""
    from myPokemonApp.models.Trainer import GymLeader
    logging.info("🏟️  Initialisation des zones Arène de Kanto...")

    for (city_name, arena_name, order, lv_min, lv_max, desc, music, badges_requis) in GYM_ZONES:
        # Créer la zone arène
        arena_zone, created = Zone.objects.get_or_create(
            name=arena_name,
            defaults={
                'zone_type': 'building',
                'description': desc,
                'order': order,
                'recommended_level_min': lv_min,
                'recommended_level_max': lv_max,
                'is_safe_zone': True,
                'has_pokemon_center': False,
                'has_shop': False,
                'has_floors': False,
                'music': music,
            }
        )

        # Appliquer (ou mettre à jour) le badge requis pour accéder à l'arène
        # badges_requis = badge_order du GymLeader à avoir battu (0 = libre)
        if badges_requis > 0:
            # Le required_badge pointe vers le GymLeader dont le badge_order == badges_requis
            gate_gym = GymLeader.objects.filter(badge_order=badges_requis).first()
            if gate_gym and arena_zone.required_badge != gate_gym:
                arena_zone.required_badge = gate_gym
                arena_zone.save(update_fields=['required_badge'])
                logging.info(f"  🔒 {arena_name} — badge requis : {gate_gym.badge_name} (ordre {badges_requis})")
        else:
            if arena_zone.required_badge is not None:
                arena_zone.required_badge = None
                arena_zone.save(update_fields=['required_badge'])
            logging.info(f"  🔓 {arena_name} — accès libre")

        logging.info(f"  {'✅' if created else '⭕'} {arena_name}")

        # Connexion bidirectionnelle ville ↔ arène
        city_zone = Zone.objects.filter(name=city_name).first()
        if city_zone:
            ZoneConnection.objects.get_or_create(
                from_zone=city_zone,
                to_zone=arena_zone,
                defaults={'is_bidirectional': True}
            )
            logging.info(f"  🔗 {city_name} ↔ {arena_name}")
        else:
            logging.warning(f"  [!] Ville introuvable : {city_name}")

    logging.info("✅ Zones Arène créées.")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_pokemon(name):
    return Pokemon.objects.filter(name=name).first()


def get_moves(move_names):
    moves = []
    for name in move_names:
        try:
            moves.append(PokemonMove.objects.get(name=name))
        except PokemonMove.DoesNotExist:
            logging.warning(f"[!] Move introuvable: {name}")
    return moves


def _gym_trainer(arena_name, username, npc_class, team_data, intro_text, is_required=True):
    """Crée ou met à jour un dresseur d'arène."""
    trainer, created = Trainer.objects.get_or_create(
        username=username,
        defaults={
            'trainer_type': 'trainer',
            'location': arena_name,
            'is_npc': True,
            'npc_class': npc_class,
            'is_battle_required': is_required,
            'intro_text': intro_text,
            'can_rebattle': False,
        }
    )
    if not created:
        trainer.location = arena_name
        trainer.is_npc = True
        trainer.npc_class = npc_class
        trainer.is_battle_required = is_required
        trainer.intro_text = intro_text
        trainer.save()

    # Construire l'équipe si elle est vide
    if not trainer.pokemon_team.exists():
        from myPokemonApp.models.PlayablePokemon import PlayablePokemon, PokemonMoveInstance
        import random
        NEUTRAL_NATURES = ['Hardy', 'Docile', 'Bashful', 'Quirky', 'Serious']
        for i, pdata in enumerate(team_data, 1):
            species = pdata['species']
            if species is None:
                continue
            pp = PlayablePokemon(
                species=species,
                trainer=trainer,
                level=pdata['level'],
                original_trainer=username,
                is_in_party=True,
                party_position=i,
                nature=random.choice(NEUTRAL_NATURES),
            )
            pp._skip_learn_moves = True
            pp.calculate_stats()
            pp.current_hp = pp.max_hp
            pp.save()
            for move in pdata.get('moves', []):
                if move:
                    PokemonMoveInstance.objects.get_or_create(
                        pokemon=pp, move=move,
                        defaults={'current_pp': move.pp}
                    )
    logging.info(f"    {'✅' if created else '⭕'} {npc_class} {username}")
    return trainer


# ─────────────────────────────────────────────────────────────────────────────
# Dresseurs de chaque arène
# ─────────────────────────────────────────────────────────────────────────────

def init_argenta_gym_trainers():
    """Arène d'Argenta — Pierre (Roche) — 2 Jeunes Roc obligatoires."""
    arena = "Arène d'Argenta"
    logging.info(f"  [{arena}]")

    _gym_trainer(
        arena_name=arena,
        username='Youngster Tommy',
        npc_class='Gamin',
        team_data=[
            {'species': get_pokemon('Geodude'), 'level': 10,
             'moves': get_moves(['Tackle', 'Defense Curl'])},
            {'species': get_pokemon('Geodude'), 'level': 10,
             'moves': get_moves(['Tackle', 'Defense Curl'])},
        ],
        intro_text="Je m'entraîne pour Pierre ! Tu ne passeras pas !",
        ai_flags=['basic', 'evaluate_attack']
    )

    _gym_trainer(
        arena_name=arena,
        username='Hiker Marcos',
        npc_class='Randonneur',
        team_data=[
            {'species': get_pokemon('Onix'), 'level': 11,
             'moves': get_moves(['Tackle', 'Screech'])},
        ],
        intro_text="La Roche résiste à tout ! Prouve ta valeur !",
        ai_flags=['basic', 'evaluate_attack']
    )


def init_azuria_gym_trainers():
    """Arène d'Azuria — Ondine (Eau) — 3 Sirènes obligatoires."""
    arena = "Arène d'Azuria"
    logging.info(f"  [{arena}]")

    _gym_trainer(
        arena_name=arena,
        username='Misty Jr. Lily',
        npc_class='Sirène',
        team_data=[
            {'species': get_pokemon('Horsea'), 'level': 18,
             'moves': get_moves(['Bubble', 'Smokescreen'])},
            {'species': get_pokemon('Shellder'), 'level': 18,
             'moves': get_moves(['Tackle', 'Withdraw'])},
        ],
        intro_text="Tu veux affronter Ondine ? Commence par me battre !",
        ai_flags=['basic', 'evaluate_attack', 'expert']
    )

    _gym_trainer(
        arena_name=arena,
        username='Swimmer Diana',
        npc_class='Nageuse',
        team_data=[
            {'species': get_pokemon('Poliwag'), 'level': 19,
             'moves': get_moves(['Bubble', 'Hypnosis'])},
        ],
        intro_text="Ces eaux sont ma demeure. Tu ne peux pas gagner !",
        ai_flags=['basic', 'evaluate_attack']
    )

    _gym_trainer(
        arena_name=arena,
        username='Lass Lola',
        npc_class='Fillette',
        team_data=[
            {'species': get_pokemon('Psyduck'), 'level': 20,
             'moves': get_moves(['Scratch', 'Tail Whip', 'Disable'])},
        ],
        intro_text="Ondine est ma championne préférée ! Je vais tout faire pour elle !",
        ai_flags=['basic', 'evaluate_attack']
    )


def init_carmin_gym_trainers():
    """Arène de Carmin sur Mer — Lt. Surge (Électrik) — 3 soldats."""
    arena = "Arène de Carmin sur Mer"
    logging.info(f"  [{arena}]")

    _gym_trainer(
        arena_name=arena,
        username='Soldier Rick',
        npc_class='Soldat',
        team_data=[
            {'species': get_pokemon('Pikachu'), 'level': 21,
             'moves': get_moves(['Thunder Shock', 'Growl', 'Thunder Wave'])},
        ],
        intro_text="Repos ! Qui va là ? Seuls les meilleurs passent ce couloir !",
        ai_flags=['basic', 'evaluate_attack']
    )

    _gym_trainer(
        arena_name=arena,
        username='Soldier James',
        npc_class='Soldat',
        team_data=[
            {'species': get_pokemon('Voltorb'), 'level': 21,
             'moves': get_moves(['Tackle', 'Screech', 'Sonic Boom'])},
            {'species': get_pokemon('Voltorb'), 'level': 21,
             'moves': get_moves(['Tackle', 'Screech', 'Sonic Boom'])},
        ],
        intro_text="Le Capitaine Surge m'a tout appris. En garde !",
        ai_flags=['basic', 'evaluate_attack']
    )

    _gym_trainer(
        arena_name=arena,
        username='Rocker Claude',
        npc_class='Rockeur',
        team_data=[
            {'species': get_pokemon('Magnemite'), 'level': 22,
             'moves': get_moves(['Thunder Shock', 'Supersonic', 'Thunder Wave'])},
        ],
        intro_text="L'électricité, c'est le rock ! Prêt pour le show ?",
        ai_flags=['basic', 'evaluate_attack']
    )


def init_celadon_gym_trainers():
    """Arène de Céladopole — Olga (Plante) — 3 Beautés."""
    arena = "Arène de Céladopole"
    logging.info(f"  [{arena}]")

    _gym_trainer(
        arena_name=arena,
        username='Beauty Tamia',
        npc_class='Beauté',
        team_data=[
            {'species': get_pokemon('Oddish'), 'level': 29,
             'moves': get_moves(['Absorb', 'Poison Powder', 'Sleep Powder'])},
            {'species': get_pokemon('Bellsprout'), 'level': 29,
             'moves': get_moves(['Vine Whip', 'Wrap', 'Sleep Powder'])},
        ],
        intro_text="Tu veux entrer ? Il faut d'abord t'occuper de moi, chéri !",
        ai_flags=['basic', 'evaluate_attack']
    )

    _gym_trainer(
        arena_name=arena,
        username='Beauty Bridget',
        npc_class='Beauté',
        team_data=[
            {'species': get_pokemon('Weepinbell'), 'level': 30,
             'moves': get_moves(['Vine Whip', 'Growth', 'Wrap', 'Sleep Powder'])},
        ],
        intro_text="Le Jardin d'Olga est interdit aux faibles. En avant !",
        ai_flags=['basic', 'evaluate_attack']
    )

    _gym_trainer(
        arena_name=arena,
        username='Lass Kay',
        npc_class='Fillette',
        team_data=[
            {'species': get_pokemon('Gloom'), 'level': 32,
             'moves': get_moves(['Absorb', 'Acid', 'Sleep Powder', 'Petal Dance'])},
        ],
        intro_text="L'odeur de mes Pokémon Plante va t'endormir !",
        ai_flags=['basic', 'evaluate_attack']
    )


def init_parmanie_gym_trainers():
    """Arène de Parmanie — Stella (Poison) — 3 Ninjas/Cibles."""
    arena = "Arène de Parmanie"
    logging.info(f"  [{arena}]")

    _gym_trainer(
        arena_name=arena,
        username='Juggler Kayden',
        npc_class='Jongleur',
        team_data=[
            {'species': get_pokemon('Drowzee'), 'level': 38,
             'moves': get_moves(['Hypnosis', 'Pound', 'Confusion'])},
            {'species': get_pokemon('Hypno'), 'level': 38,
             'moves': get_moves(['Hypnosis', 'Pound', 'Confusion', 'Disable'])},
        ],
        intro_text="Il faut voir au-delà pour trouver Stella. Moi, je vais t'endormir !",
        ai_flags=['basic', 'evaluate_attack']
    )

    _gym_trainer(
        arena_name=arena,
        username='Juggler Irving',
        npc_class='Jongleur',
        team_data=[
            {'species': get_pokemon('Kadabra'), 'level': 38,
             'moves': get_moves(['Confusion', 'Psybeam', 'Recover'])},
        ],
        intro_text="Mes Pokémon sont insaisissables ! Attrape-les si tu peux !",
        ai_flags=['basic', 'evaluate_attack']
    )

    _gym_trainer(
        arena_name=arena,
        username='Tamer Phil',
        npc_class='Dompteur',
        team_data=[
            {'species': get_pokemon('Arbok'), 'level': 40,
             'moves': get_moves(['Wrap', 'Bite', 'Poison Sting', 'Glare'])},
            {'species': get_pokemon('Arbok'), 'level': 40,
             'moves': get_moves(['Wrap', 'Bite', 'Poison Sting', 'Glare'])},
        ],
        intro_text="Mes Cobras sont fidèles ! Ils te paralyseront !",
        ai_flags=['basic', 'evaluate_attack']
    )


def init_safrania_gym_trainers():
    """Arène de Safrania — Morgane (Psy) — 3 Médiums/Mages."""
    arena = "Arène de Safrania"
    logging.info(f"  [{arena}]")

    _gym_trainer(
        arena_name=arena,
        username='Psychic Mark',
        npc_class='Psyko',
        team_data=[
            {'species': get_pokemon('Kadabra'), 'level': 35,
             'moves': get_moves(['Confusion', 'Psybeam', 'Recover'])},
        ],
        intro_text="J'ai lu tes pensées. Tu vas perdre.",
        ai_flags=['basic', 'evaluate_attack', 'expert']
    )

    _gym_trainer(
        arena_name=arena,
        username='Medium Rebecca',
        npc_class='Médium',
        team_data=[
            {'species': get_pokemon('Slowpoke'), 'level': 37,
             'moves': get_moves(['Confusion', 'Disable', 'Headbutt'])},
            {'species': get_pokemon('Slowbro'), 'level': 37,
             'moves': get_moves(['Confusion', 'Disable', 'Withdraw', 'Headbutt'])},
        ],
        intro_text="L'esprit de Morgane t'observe. Tes intentions sont claires pour moi.",
        ai_flags=['basic', 'evaluate_attack', 'expert']
    )

    _gym_trainer(
        arena_name=arena,
        username='Psychic Franklin',
        npc_class='Psyko',
        team_data=[
            {'species': get_pokemon('Jynx'), 'level': 38,
             'moves': get_moves(['Confusion', 'Lovely Kiss', 'Psybeam', 'Ice Punch'])},
        ],
        intro_text="Mes pouvoirs psychiques sont sans limites dans cette arène !",
        ai_flags=['basic', 'evaluate_attack', 'expert']
    )


def init_cramois_gym_trainers():
    """Arène de Cramois'Île — Pyro (Feu) — 2 Pompiers."""
    arena = "Arène de Cramois'Île"
    logging.info(f"  [{arena}]")

    _gym_trainer(
        arena_name=arena,
        username='Blaine Jr. Bruno',
        npc_class='Pompier',
        team_data=[
            {'species': get_pokemon('Growlithe'), 'level': 44,
             'moves': get_moves(['Bite', 'Flamethrower', 'Fire Blast'])},
        ],
        intro_text="Réponds à ma question ou affronte mes Pokémon !",
        ai_flags=['basic', 'evaluate_attack', 'expert']
    )

    _gym_trainer(
        arena_name=arena,
        username='Super Nerd Erik',
        npc_class='Super Nerd',
        team_data=[
            {'species': get_pokemon('Ponyta'), 'level': 45,
             'moves': get_moves(['Tackle', 'Ember', 'Stomp', 'Fire Spin'])},
            {'species': get_pokemon('Magmar'), 'level': 45,
             'moves': get_moves(['Ember', 'Fire Punch', 'Smog', 'Confuse Ray'])},
        ],
        intro_text="La chaleur de ces volcans a trempé mes Pokémon comme de l'acier !",
        ai_flags=['basic', 'evaluate_attack']
    )


def init_jadielle_gym_trainers():
    """Arène de Jadielle — Giovanni (Sol) — 3 membres Rocket."""
    arena = "Arène de Jadielle"
    logging.info(f"  [{arena}]")

    _gym_trainer(
        arena_name=arena,
        username='Cooltrainer Warren',
        npc_class='As Dresseur',
        team_data=[
            {'species': get_pokemon('Rhyhorn'), 'level': 45,
             'moves': get_moves(['Horn Attack', 'Stomp', 'Tail Whip'])},
            {'species': get_pokemon('Sandslash'), 'level': 45,
             'moves': get_moves(['Slash', 'Sand Attack', 'Poison Sting'])},
        ],
        intro_text="Giovanni m'a confié la garde de cette arène. Prouve ta valeur !",
        ai_flags=['basic', 'evaluate_attack', 'expert']
    )

    _gym_trainer(
        arena_name=arena,
        username='Cooltrainer Naomi',
        npc_class='As Dresseuse',
        team_data=[
            {'species': get_pokemon('Dugtrio'), 'level': 47,
             'moves': get_moves(['Dig', 'Sand Attack', 'Slash', 'Earthquake'])},
        ],
        intro_text="Tu crois avoir les 7 badges ? Giovanni va tout changer !",
        ai_flags=['basic', 'evaluate_attack', 'expert']
    )

    _gym_trainer(
        arena_name=arena,
        username='Rocket Domino',
        npc_class='Rocket',
        team_data=[
            {'species': get_pokemon('Nidoking'), 'level': 48,
             'moves': get_moves(['Poison Sting', 'Thrash', 'Earthquake', 'Horn Drill'])},
        ],
        intro_text="La Team Rocket ne laisse personne approcher Giovanni !",
        ai_flags=['basic', 'evaluate_attack', 'expert', 'setup_first_turn']
    )


# ─────────────────────────────────────────────────────────────────────────────
# Fonction principale
# ─────────────────────────────────────────────────────────────────────────────

def run_gym_initialization():
    """Lance l'initialisation complète des arènes."""
    logging.info("=" * 70)
    logging.info("INITIALISATION DES ARÈNES DE KANTO")
    logging.info("=" * 70)

    # 1. Créer les zones arène
    init_gym_zones()

    # 2. Créer les dresseurs
    logging.info("\n👥 Dresseurs des arènes...")
    init_argenta_gym_trainers()
    init_azuria_gym_trainers()
    init_carmin_gym_trainers()
    init_celadon_gym_trainers()
    init_parmanie_gym_trainers()
    init_safrania_gym_trainers()
    init_cramois_gym_trainers()
    init_jadielle_gym_trainers()

    total = Trainer.objects.filter(
        is_npc=True,
        location__startswith='Arène'
    ).count()
    logging.info(f"\n✅ {total} dresseurs d'arène créés/vérifiés.")
    logging.info("=" * 70)