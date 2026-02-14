from myPokemonApp.models import PokemonCenter, NurseDialogue
import logging

logging.basicConfig(level=logging.INFO)

def scriptToInitializePokeCenters():
    # Créer le centre principal
    center = PokemonCenter.objects.create(
        name="Centre Pokémon de Bourg Palette",
        location="Bourg Palette",
        nurse_name="Infirmière Joy",
        nurse_greeting="Bienvenue au Centre Pokémon ! Puis-je soigner vos Pokémon ?",
        nurse_healing_message="Vos Pokémon ont été complètement soignés ! Revenez quand vous voulez !",
        nurse_farewell="Nous espérons vous revoir bientôt !",
        is_available=True,
        healing_cost=0  # Gratuit
    )

    # Créer des dialogues variés
    dialogues_greeting = [
        "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
        "Bienvenue ! Vos Pokémon ont l'air fatigués.",
        "Oh, bonjour Dresseur ! Puis-je soigner votre équipe ?",
    ]

    for text in dialogues_greeting:
        NurseDialogue.objects.create(
            center=center,
            dialogue_type='greeting',
            text=text,
            rarity=5
        )

    dialogues_complete = [
        "Et voilà ! Vos Pokémon sont en pleine forme !",
        "Terminé ! Ils sont tous guéris maintenant.",
        "Parfait ! Vos Pokémon débordent d'énergie !",
        "C'est fait ! Prenez soin d'eux !",
    ]

    for text in dialogues_complete:
        NurseDialogue.objects.create(
            center=center,
            dialogue_type='complete',
            text=text,
            rarity=5
        )

    # Dialogues spéciaux selon badges
    NurseDialogue.objects.create(
        center=center,
        dialogue_type='greeting',
        text="Félicitations pour vos badges ! Vous progressez bien !",
        min_badges=3,
        max_badges=8,
        rarity=7
    )

    NurseDialogue.objects.create(
        center=center,
        dialogue_type='complete',
        text="Avec tous ces badges, vous êtes vraiment un Dresseur exceptionnel !",
        min_badges=6,
        max_badges=8,
        rarity=8
    )


    # Centre de Jadielle
    center2 = PokemonCenter.objects.create(
        name="Centre Pokémon de Jadielle",
        location="Jadielle",
        nurse_name="Infirmière Joy",
        nurse_greeting="Bienvenue à Jadielle ! Vos Pokémon ont besoin de soins ?",
        is_available=True,
        healing_cost=0
    )

    # Centre de Carmin sur Mer
    center3 = PokemonCenter.objects.create(
        name="Centre Pokémon de Carmin sur Mer",
        location="Carmin sur Mer",
        nurse_name="Infirmière Joy",
        nurse_greeting="Bonjour Marin ! Comment puis-je aider ?",
        is_available=True,
        healing_cost=0
    )

    logging.info("[+] Centre Pokémon créé avec succès !")
