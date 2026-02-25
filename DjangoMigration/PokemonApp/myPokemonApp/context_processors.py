import logging
from myPokemonApp.models import GameSave, Trainer

logger = logging.getLogger(__name__)


def active_save(request):
    """
    Injecte la GameSave active dans chaque template.
    Retourne des valeurs nulles si le joueur n'a pas encore de Trainer
    (nouveau compte avant choose_starter) sans déclencher d'erreur.
    """
    if not request.user.is_authenticated:
        return {'active_save': None, 'has_active_save': False}

    try:
        trainer = Trainer.objects.get(username=request.user.username)
        save = GameSave.objects.filter(trainer=trainer, is_active=True).first()
        return {
            'active_save':     save,
            'has_active_save': save is not None,
        }
    except Trainer.DoesNotExist:
        # Joueur authentifié mais pas encore de Trainer (avant choose_starter)
        return {'active_save': None, 'has_active_save': False}