from django.apps import AppConfig


class MypokemonappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myPokemonApp'

    def ready(self):
        """
        Point d'entrée Django pour connecter les signaux au démarrage.

        Le signal connection_created est utilisé ici pour appliquer les PRAGMAs
        d'optimisation SQLite dès l'ouverture de chaque connexion.
        C'est le seul endroit garanti d'être exécuté après l'initialisation
        complète de Django (modèles chargés, registry prêt).

        Note : init_command n'existe que pour MySQL/MariaDB — impossible à utiliser
        avec le backend SQLite de Django. Le signal est donc l'unique alternative fiable.
        """
        from django.db.backends.signals import connection_created

        def _apply_sqlite_pragmas(sender, connection, **kwargs):
            """
            Applique les PRAGMAs d'optimisation dès l'ouverture de chaque connexion SQLite.
            Ignoré automatiquement si le backend n'est pas SQLite (utile en CI/CD avec Postgres).

              WAL            : lecteurs et écrivains ne se bloquent plus mutuellement
              synchronous    : NORMAL — fsync uniquement aux checkpoints WAL
              cache_size     : 64 Mo de pages SQLite en RAM
              foreign_keys   : ON — SQLite n'enforce pas les FK par défaut
              temp_store     : MEMORY — ORDER BY / GROUP BY résolus en RAM
              mmap_size      : 256 Mo de I/O mappé en mémoire
            """
            if connection.vendor != 'sqlite':
                return
            with connection.cursor() as cursor:
                cursor.execute('PRAGMA journal_mode=WAL;')
                cursor.execute('PRAGMA synchronous=NORMAL;')
                cursor.execute('PRAGMA cache_size=-64000;')
                cursor.execute('PRAGMA foreign_keys=ON;')
                cursor.execute('PRAGMA temp_store=MEMORY;')
                cursor.execute('PRAGMA mmap_size=268435456;')

        connection_created.connect(_apply_sqlite_pragmas)