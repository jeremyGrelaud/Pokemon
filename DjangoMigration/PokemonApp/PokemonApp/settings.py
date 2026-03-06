"""
Django settings for PokemonApp project.

Les valeurs sensibles sont lues depuis secrets.yaml (à la racine du projet).
Ce fichier n'est jamais commité — seul secrets.yaml.example l'est.

Pour générer une SECRET_KEY :
    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
"""

from pathlib import Path
import os
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


# ─── Chargement de secrets.yaml ───────────────────────────────────────────────

_secrets_path = BASE_DIR / 'secrets.yaml'

if not _secrets_path.exists():
    raise FileNotFoundError(
        f"\n\n[ERREUR] Fichier secrets.yaml introuvable : {_secrets_path}\n"
        "Copiez secrets.yaml.example en secrets.yaml et remplir les valeurs.\n"
        "Commande : cp secrets.yaml.example secrets.yaml\n"
    )

with open(_secrets_path, encoding='utf-8') as _f:
    _secrets = yaml.safe_load(_f)


def _get_secret(key: str, default=None):
    """Récupère une valeur depuis secrets.yaml avec un message d'erreur clair."""
    value = _secrets.get(key, default)
    if value is None:
        raise KeyError(
            f"\n\n[ERREUR] Clé '{key}' manquante dans secrets.yaml.\n"
            f"  → Vérifier secrets.yaml.example pour la nomenclature.\n"
        )
    return value


# ─── Sécurité ─────────────────────────────────────────────────────────────────

SECRET_KEY    = _get_secret('secret_key')
DEBUG         = bool(_get_secret('debug', False))
ALLOWED_HOSTS = list(_get_secret('allowed_hosts', ['localhost', '127.0.0.1']))


# ─── Applications ─────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myPokemonApp',
    'django_tables2',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'myPokemonApp.middleware.starter_required.StarterRequiredMiddleware',
]

ROOT_URLCONF = 'PokemonApp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'template')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'myPokemonApp.context_processors.active_save',
            ],
        },
    },
]

WSGI_APPLICATION = 'PokemonApp.wsgi.application'


# ─── Base de données ──────────────────────────────────────────────────────────
#
# Optimisations SQLite appliquées via le signal `connection_created`.
#
#   WAL (Write-Ahead Logging)
#     Mode journal par défaut = DELETE → un seul writer, tous les readers bloqués.
#     WAL = les lecteurs ne bloquent jamais les écritures et vice-versa.
#     Essentiel pour un jeu où les combats écrivent pendant que d'autres pages lisent.
#
#   synchronous = NORMAL
#     Par défaut SQLite fait un fsync() à chaque commit (FULL) — très lent sur disque.
#     NORMAL synce uniquement aux checkpoints WAL, safe en pratique.
#
#   cache_size = -64000
#     Valeur négative = kilobytes. 64 Mo de pages SQLite gardées en RAM.
#
#   foreign_keys = ON
#     SQLite n'enforces PAS les FK par défaut — ce pragma corrige ce comportement.
#
#   temp_store = MEMORY
#     Les tables temporaires (ORDER BY, GROUP BY) sont créées en RAM.
#
#   mmap_size = 268435456
#     Memory-mapped I/O sur 256 Mo : réduit les syscalls de lecture.
#
#   CONN_MAX_AGE = 300
#     Réutilise la connexion SQLite 5 min — les PRAGMAs ne sont exécutés
#     qu'une fois par connexion, pas à chaque requête HTTP.

DATABASES = {
    'default': {
        'ENGINE':       'django.db.backends.sqlite3',
        'NAME':         BASE_DIR / 'db.sqlite3',
        'CONN_MAX_AGE': 300,
        'OPTIONS': {
            'timeout': 20,  # secondes avant OperationalError "database is locked"
        },
    }
}


# ─── PRAGMAs SQLite appliqués à chaque nouvelle connexion ────────────────────
# Le signal connection_created est le seul moyen fiable d'envoyer des PRAGMAs
# au backend SQLite de Django (init_command n'existe que pour MySQL).

from django.db.backends.signals import connection_created

def _apply_sqlite_pragmas(sender, connection, **kwargs):
    """
    Applique les PRAGMAs d'optimisation dès l'ouverture de chaque connexion SQLite.
    Ignoré automatiquement si le backend n'est pas SQLite (utile en CI/CD avec Postgres).
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


# ─── Validation des mots de passe ─────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ─── Internationalisation ─────────────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ─── Fichiers statiques ───────────────────────────────────────────────────────

STATIC_URL  = '/static/'
# STATIC_ROOT est requis par `collectstatic` pour le déploiement hors runserver.
# En dev, ce dossier n'est pas utilisé directement (Django sert depuis STATICFILES_DIRS).
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'template/static')
]


# ─── Divers ───────────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'