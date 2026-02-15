import logging

def active_save(request):
    if request.user.is_authenticated:
        try:
            from myPokemonApp.models import GameSave, Trainer
            trainer = Trainer.objects.get(username=request.user.username)
            save = GameSave.objects.filter(
                trainer=trainer,
                is_active=True
            ).first()
            return {
                'active_save': save,
                'has_active_save': save is not None
            }
        except Exception as e:
            logging.error(f"Erreur: {e}")
    return {
        'active_save': None,
        'has_active_save': False
    }