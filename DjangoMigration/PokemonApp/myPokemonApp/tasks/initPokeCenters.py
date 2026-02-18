"""
Initialise tous les Centres Pokémon de Kanto Gen 1.
Un centre par ville, avec dialogues variés de l'Infirmière Joy.
"""

from myPokemonApp.models import PokemonCenter, NurseDialogue
import logging

logging.basicConfig(level=logging.INFO)


def _create_center(name, location, greeting, healing_msg=None, farewell=None):
    """Helper : crée un Centre Pokémon s'il n'existe pas déjà."""
    center, created = PokemonCenter.objects.get_or_create(
        name=name,
        defaults={
            'location': location,
            'nurse_name': "Infirmière Joy",
            'nurse_greeting': greeting,
            'nurse_healing_message': healing_msg or "Vos Pokémon ont été complètement soignés ! Revenez quand vous voulez !",
            'nurse_farewell': farewell or "Nous espérons vous revoir bientôt !",
            'is_available': True,
            'healing_cost': 0,
        }
    )
    logging.info(f"  {'✅' if created else '⭕'} {name}")
    return center


def _add_dialogues(center, dialogues_by_type):
    """
    Helper : ajoute des dialogues variés à un centre.
    dialogues_by_type = {
        'greeting': [('texte', rarity, min_badges, max_badges), ...],
        'complete': [...],
    }
    """
    for dialogue_type, entries in dialogues_by_type.items():
        for entry in entries:
            text = entry[0]
            rarity = entry[1] if len(entry) > 1 else 5
            min_b  = entry[2] if len(entry) > 2 else 0
            max_b  = entry[3] if len(entry) > 3 else 8
            NurseDialogue.objects.get_or_create(
                center=center,
                dialogue_type=dialogue_type,
                text=text,
                defaults={
                    'rarity': rarity,
                    'min_badges': min_b,
                    'max_badges': max_b,
                }
            )


def scriptToInitializePokeCenters():
    """Crée tous les Centres Pokémon de Kanto avec leurs dialogues."""

    logging.info("🏥 Initialisation des Centres Pokémon de Kanto...")

    # =========================================================================
    # BOURG PALETTE
    # =========================================================================
    c = _create_center(
        "Centre Pokémon de Bourg Palette",
        "Bourg Palette",
        "Bienvenue au Centre Pokémon ! Puis-je soigner vos Pokémon ?"
    )
    _add_dialogues(c, {
        'greeting': [
            ("Bienvenue au Centre Pokémon ! Puis-je soigner vos Pokémon ?", 5),
            ("Bonjour ! Vos Pokémon ont l'air fatigués. Laissez-moi les soigner !", 5),
            ("Oh, un jeune Dresseur ! Bienvenue dans votre premier Centre Pokémon !", 7, 0, 0),
            ("Vous avez bien progressé ! Vos Pokémon méritent un peu de repos.", 6, 2, 8),
        ],
        'complete': [
            ("Vos Pokémon sont en pleine forme ! Bonne chance dans votre aventure !", 5),
            ("Et voilà ! Tous vos Pokémon sont soignés et prêts à se battre !", 5),
            ("Parfait ! Prenez bien soin d'eux, Dresseur !", 5),
        ],
    })

    # =========================================================================
    # JADIELLE
    # =========================================================================
    c = _create_center(
        "Centre Pokémon de Jadielle",
        "Jadielle",
        "Bienvenue à Jadielle ! Vos Pokémon ont besoin de soins ?"
    )
    _add_dialogues(c, {
        'greeting': [
            ("Bienvenue à Jadielle ! C'est ici que commence votre véritable aventure.", 5),
            ("La Route 1 vous a fatigué ? Laissez-moi m'occuper de vos Pokémon !", 5),
            ("Vous allez défier Pierre à l'Arène d'Argenta ? Préparez-vous bien !", 7, 0, 0),
        ],
        'complete': [
            ("Soins terminés ! Bonne route vers Argenta !", 5),
            ("Vos Pokémon sont en forme ! Attention aux Roucool sur la Route 1 !", 5),
        ],
    })

    # =========================================================================
    # ARGENTA
    # =========================================================================
    c = _create_center(
        "Centre Pokémon d'Argenta",
        "Argenta",
        "Bienvenue à Argenta, ville des pierres et des fossiles !"
    )
    _add_dialogues(c, {
        'greeting': [
            ("Bienvenue à Argenta ! Pierre, le Champion d'Arène, vous attend.", 5, 0, 0),
            ("Bien soigné ? Le Mont Sélénite vous attend après l'Arène !", 6, 1, 8),
            ("Vous avez le Badge Pierre ! Félicitations !", 7, 1, 8),
        ],
        'complete': [
            ("Prêts pour l'Arène ! Géodude et Onix sont coriaces, attention !", 6, 0, 0),
            ("Vos Pokémon pétillent de santé !", 5),
        ],
    })

    # =========================================================================
    # AZURIA
    # =========================================================================
    c = _create_center(
        "Centre Pokémon d'Azuria",
        "Azuria",
        "Bienvenue à Azuria ! Les eaux du lac brillent de mille reflets."
    )
    _add_dialogues(c, {
        'greeting': [
            ("Azuria est une belle ville, n'est-ce pas ? Laissez-moi soigner vos Pokémon !", 5),
            ("Vous venez du Mont Sélénite ? Vous devez être épuisé ! Vite, venez ici !", 6),
            ("Ondine garde jalousement son badge. Préparez des Pokémon Électrik ou Plante !", 7, 0, 1),
            ("Le Tunnel Roche vous attend à l'est. C'est sombre là-dedans…", 6, 2, 8),
        ],
        'complete': [
            ("Soins terminés ! Bonne chance face à Ondine !", 5),
            ("Tout est parfait ! Les Pokémon sauvages du lac sont forts, soyez prudent !", 5),
        ],
    })

    # =========================================================================
    # CARMIN SUR MER
    # =========================================================================
    c = _create_center(
        "Centre Pokémon de Carmin sur Mer",
        "Carmin sur Mer",
        "Bonjour Dresseur ! Le port est animé aujourd'hui. Puis-je aider vos Pokémon ?"
    )
    _add_dialogues(c, {
        'greeting': [
            ("Le SS Anne est au port ! Vous devriez y monter avant qu'il parte.", 7, 0, 2),
            ("Capitaine, le Champion d'Arène, utilise des Pokémon Électrik. Méfiez-vous !", 6, 0, 2),
            ("Bien le bonjour, Dresseur ! Vos Pokémon ont besoin d'un peu de repos ?", 5),
        ],
        'complete': [
            ("Soins terminés ! Bonne chance pour l'Arène de Carmin !", 5),
            ("Vos Pokémon sont en pleine forme ! Le port vous réserve des surprises…", 5),
        ],
    })

    # =========================================================================
    # LAVANVILLE
    # =========================================================================
    c = _create_center(
        "Centre Pokémon de Lavanville",
        "Lavanville",
        "Bienvenue à Lavanville… une ville paisible malgré sa réputation."
    )
    _add_dialogues(c, {
        'greeting': [
            ("La Tour Pokémon est hantée, dit-on… Soyez prudent si vous y allez.", 7),
            ("Bienvenue à Lavanville. Cette ville porte le deuil de nombreux Pokémon.", 6),
            ("Les Spectreux de la Tour n'aiment pas les étrangers. Avez-vous le Scope Sylphe ?", 7, 0, 4),
        ],
        'complete': [
            ("Soins terminés. Les âmes de la Tour veillent sur vous…", 5),
            ("Vos Pokémon sont guéris ! Courage pour la Tour Pokémon.", 5),
        ],
    })

    # =========================================================================
    # CÉLADOPOLE
    # =========================================================================
    c = _create_center(
        "Centre Pokémon de Céladopole",
        "Céladopole",
        "Bienvenue à Céladopole, la grande ville aux mille boutiques !"
    )
    _add_dialogues(c, {
        'greeting': [
            ("Le Grand Magasin est à deux pas ! On y trouve vraiment tout.", 5),
            ("Olga, la Championne d'Arène, adore les Pokémon Plante. Prenez un Pokémon Feu !", 6, 0, 4),
            ("La Centrale au nord a été abandonnée… bizarre, non ?", 7, 4, 8),
        ],
        'complete': [
            ("Soins terminés ! Profitez de Céladopole !", 5),
            ("Vos Pokémon pétillent de santé ! Bonne chance contre Olga !", 5),
        ],
    })

    # =========================================================================
    # SAFRANIA
    # =========================================================================
    c = _create_center(
        "Centre Pokémon de Safrania",
        "Safrania",
        "Bienvenue à Safrania, la ville qui ne dort jamais !"
    )
    _add_dialogues(c, {
        'greeting': [
            ("La Tour Sylphe est occupée par la Team Rocket ! Soyez prudent !", 7, 0, 6),
            ("Morgane utilise des Pokémon Psy très puissants. Préparez-vous !", 6, 0, 6),
            ("Maintenant que la Tour Sylphe est libérée, les affaires reprennent !", 5, 6, 8),
        ],
        'complete': [
            ("Soins terminés ! Bonne chance dans la grande ville !", 5),
            ("Vos Pokémon sont en forme ! La Tour Sylphe vous attend peut-être…", 5),
        ],
    })

    # =========================================================================
    # FUCHSIA
    # =========================================================================
    c = _create_center(
        "Centre Pokémon de Fuchsia",
        "Fuchsia",
        "Bienvenue à Fuchsia ! Le zoo Safari est tout proche !"
    )
    _add_dialogues(c, {
        'greeting': [
            ("La Zone Safari est une attraction unique ! Avez-vous vos tickets ?", 6),
            ("Stella, la Championne, maîtrise les Pokémon Poison. Méfiez-vous !", 6, 0, 6),
            ("Les Routes du Vélo passent par ici. Avez-vous une Bicyclette ?", 5),
        ],
        'complete': [
            ("Soins terminés ! Bonne chasse dans la Zone Safari !", 5),
            ("Vos Pokémon sont en pleine forme ! Bonne chance contre Stella !", 5),
        ],
    })

    # =========================================================================
    # CRAMOIS'ÎLE
    # =========================================================================
    c = _create_center(
        "Centre Pokémon de Cramois'Île",
        "Cramois'Île",
        "Bienvenue sur Cramois'Île ! La chaleur du volcan réchauffe l'atmosphère."
    )
    _add_dialogues(c, {
        'greeting': [
            ("Le Laboratoire Pokémon de l'île fait des recherches fascinantes !", 5),
            ("Pyro utilise des Pokémon Feu redoutables. Misez sur l'Eau !", 6, 0, 8),
            ("Les Fossiles ressuscités viennent de ce laboratoire, saviez-vous ?", 7),
        ],
        'complete': [
            ("Soins terminés ! Attention au volcan !", 5),
            ("Vos Pokémon sont guéris ! Bonne chance contre Pyro !", 5),
        ],
    })

    # =========================================================================
    # PLATEAU INDIGO
    # =========================================================================
    c = _create_center(
        "Centre Pokémon du Plateau Indigo",
        "Plateau Indigo",
        "Vous avez atteint le sommet ! Bienvenue au Plateau Indigo, Dresseur !"
    )
    _add_dialogues(c, {
        'greeting': [
            ("Vous êtes ici ? Alors vous avez les 8 badges ! Impressionnant !", 8, 8, 8),
            ("Le Conseil des 4 vous attend. Préparez-vous bien — ils sont impitoyables.", 7, 8, 8),
            ("Seuls les meilleurs Dresseurs arrivent jusqu'ici. Vous en faites partie !", 8, 8, 8),
        ],
        'complete': [
            ("Soins terminés ! Que la chance soit avec vous face au Conseil des 4 !", 8),
            ("Vos Pokémon sont en pleine forme ! C'est maintenant que tout se joue !", 8),
        ],
    })

    logging.info("\n✅ Centres Pokémon de Kanto initialisés !")