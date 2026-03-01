"""
Middleware qui garantit que tout utilisateur authentifié a choisi
son Pokémon de départ avant d'accéder au reste du site.
"""

from django.shortcuts import redirect
from django.urls import resolve, reverse, NoReverseMatch

# URLs accessibles SANS avoir de starter
EXEMPT_URL_NAMES = {
    # Auth
    "login",
    "account_logout",
    "choose_starter", # Choix du starter lui-même
}

EXEMPT_PATH_PREFIXES = (
    "/admin/",
    "/static/",
    "/media/",
)


class StarterRequiredMiddleware:
    """
    Pour tout utilisateur authentifié sans Pokémon dans son équipe,
    redirige vers la page de choix du starter — sauf pour les URLs
    listées dans EXEMPT_URL_NAMES / EXEMPT_PATH_PREFIXES.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._needs_redirect(request):
            return redirect(reverse("choose_starter"))
        return self.get_response(request)


    def _needs_redirect(self, request) -> bool:
        """Retourne True si la requête doit être bloquée."""

        # 1. Seulement les utilisateurs connectés
        if not request.user.is_authenticated:
            return False

        # 2. Chemins autorisés
        path = request.path_info
        if any(path.startswith(prefix) for prefix in EXEMPT_PATH_PREFIXES):
            return False

        # 3. URLs autorisées
        try:
            url_name = resolve(path).url_name
        except Exception:
            return False

        if url_name in EXEMPT_URL_NAMES:
            return False

        # 4. Vérifier si le trainer a un Pokémon
        from myPokemonApp.services.player_service import get_or_create_player_trainer
        trainer = get_or_create_player_trainer(request.user)
        if trainer.pokemon_team.exists():
            return False 

        # Pas de starter -> redirection
        return True