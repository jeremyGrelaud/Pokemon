"""
Commande de management Django : init_db
========================================

Initialise une base de données Pokémon vierge dans le bon ordre.

Usage :
    python manage.py init_db                    # initialisation complète
    python manage.py init_db --step 12          # une seule étape
    python manage.py init_db --from-step 10     # reprendre à partir de l'étape 10
    python manage.py init_db --no-stop          # continue même en cas d'erreur
    python manage.py init_db --list             # affiche la liste des étapes
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Initialise la base de données Pokémon (types, moves, pokémon, NPCs, zones…)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--step',
            type=int,
            default=None,
            metavar='N',
            help="Exécuter uniquement l'étape N",
        )
        parser.add_argument(
            '--from-step',
            type=int,
            default=None,
            dest='from_step',
            metavar='N',
            help="Reprendre à partir de l'étape N (incluse)",
        )
        parser.add_argument(
            '--no-stop',
            action='store_true',
            dest='no_stop',
            help="Continuer même si une étape échoue (rapport en fin d'exécution)",
        )
        parser.add_argument(
            '--list',
            action='store_true',
            dest='list_steps',
            help="Afficher la liste des étapes sans les exécuter",
        )

    def handle(self, *args, **options):
        from myPokemonApp.tasks.initAllDatabase import initAllDatabase, STEPS

        # ── Mode liste ────────────────────────────────────────────────────────
        if options['list_steps']:
            self.stdout.write(self.style.HTTP_INFO("\nÉtapes disponibles :"))
            for step_num, label, *_ in STEPS:
                self.stdout.write(f"  [{step_num:2d}] {label}")
            self.stdout.write("")
            return

        # ── Sélection des étapes ──────────────────────────────────────────────
        step     = options['step']
        from_step = options['from_step']
        stop_on_error = not options['no_stop']

        if step is not None and from_step is not None:
            raise CommandError("--step et --from-step sont mutuellement exclusifs.")

        # Filtre sur les étapes à exécuter
        step_filter = None
        if step is not None:
            step_filter = lambda n: n == step
        elif from_step is not None:
            step_filter = lambda n: n >= from_step

        # ── Exécution ─────────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS("\n🎮 Initialisation de la base de données Pokémon\n"))

        try:
            initAllDatabase(
                stop_on_error=stop_on_error,
                step_filter=step_filter,
                stdout=self,   # passe self pour que initAllDatabase utilise self.stdout
            )
        except RuntimeError as e:
            raise CommandError(str(e))

        self.stdout.write(self.style.SUCCESS("\n✅  Terminé !\n"))