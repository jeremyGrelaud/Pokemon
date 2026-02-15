
"""
Script d'initialisation des PokeballItems
"""

import logging
from myPokemonApp.models import Item, PokeballItem, PokemonType
logging.basicConfig(level=logging.INFO)


def scriptToInitNewPokeBalls():
    """Initialise les PokeballItems pour toutes les Poké Balls existantes"""
    
    logging.info("[+] Initialisation des PokeballItems...")
    
    # Configuration des différentes balls
    pokeball_configs = {
        'Poké Ball': {
            'guaranteed_capture': False,
            'critical_catch_bonus': 0.0,
            'bonus_on_type': None,
            'bonus_on_status': ''
        },
        'Super Ball': {
            'guaranteed_capture': False,
            'critical_catch_bonus': 0.05,  # 5% chance de capture critique
            'bonus_on_type': None,
            'bonus_on_status': ''
        },
        'Ultra Ball': {
            'guaranteed_capture': False,
            'critical_catch_bonus': 0.1,  # 10% chance de capture critique
            'bonus_on_type': None,
            'bonus_on_status': ''
        },
        'Master Ball': {
            'guaranteed_capture': True,
            'critical_catch_bonus': 1.0,  # 100% capture critique
            'bonus_on_type': None,
            'bonus_on_status': ''
        },
        'Safari Ball': {
            'guaranteed_capture': False,
            'critical_catch_bonus': 0.0,
            'bonus_on_type': None,
            'bonus_on_status': ''
        },
        # Balls spéciales avec bonus
        'Filet Ball': {
            'guaranteed_capture': False,
            'critical_catch_bonus': 0.0,
            'bonus_on_type': 'Insecte',  # Bonus sur type Insecte et Eau
            'bonus_on_status': ''
        },
        'Scuba Ball': {
            'guaranteed_capture': False,
            'critical_catch_bonus': 0.0,
            'bonus_on_type': 'Eau',
            'bonus_on_status': ''
        },
        'Faiblo Ball': {
            'guaranteed_capture': False,
            'critical_catch_bonus': 0.0,
            'bonus_on_type': None,
            'bonus_on_status': ''  # Bonus si HP < 25% (géré dans calculate_capture_rate)
        },
        'Chrono Ball': {
            'guaranteed_capture': False,
            'critical_catch_bonus': 0.0,
            'bonus_on_type': None,
            'bonus_on_status': ''  # Bonus si combat long (géré dans calculate_capture_rate)
        },
        'Sombre Ball': {
            'guaranteed_capture': False,
            'critical_catch_bonus': 0.0,
            'bonus_on_type': None,
            'bonus_on_status': ''  # Bonus si nuit/grotte (géré dans calculate_capture_rate)
        },
        'Rapide Ball': {
            'guaranteed_capture': False,
            'critical_catch_bonus': 0.2,  # 20% si utilisé au 1er tour
            'bonus_on_type': None,
            'bonus_on_status': ''
        },
        'Bis Ball': {
            'guaranteed_capture': False,
            'critical_catch_bonus': 0.0,
            'bonus_on_type': None,
            'bonus_on_status': ''  # Bonus si déjà capturé (géré dans calculate_capture_rate)
        },
        'Luxe Ball': {
            'guaranteed_capture': False,
            'critical_catch_bonus': 0.0,
            'bonus_on_type': None,
            'bonus_on_status': ''  # Même taux qu'une Poké Ball mais améliore bonheur
        },
        'Honor Ball': {
            'guaranteed_capture': False,
            'critical_catch_bonus': 0.0,
            'bonus_on_type': None,
            'bonus_on_status': ''  # Même taux qu'une Poké Ball, donnée en cadeau
        },
    }
    
    created = 0
    updated = 0
    skipped = 0
    
    for ball_name, config in pokeball_configs.items():
        try:
            # Chercher l'item
            item = Item.objects.filter(name__icontains=ball_name).first()
            
            if not item:
                logging.warning(f"[!]  Item '{ball_name}' non trouvé, ignoré")
                skipped += 1
                continue
            
            # Vérifier si catch_rate_modifier est défini
            if not item.catch_rate_modifier or item.catch_rate_modifier == 0:
                # Définir des valeurs par défaut selon le type de ball
                if 'Master' in ball_name:
                    item.catch_rate_modifier = 255.0
                elif 'Hyper' in ball_name or 'Ultra' in ball_name:
                    item.catch_rate_modifier = 2.0
                elif 'Super' in ball_name or 'Great' in ball_name:
                    item.catch_rate_modifier = 1.5
                else:
                    item.catch_rate_modifier = 1.0
                
                item.save()
                logging.info(f"[+] Modifier {ball_name}: {item.catch_rate_modifier}x")
            
            # Récupérer le type si spécifié
            bonus_type = None
            if config['bonus_on_type']:
                bonus_type = PokemonType.objects.filter(name__icontains=config['bonus_on_type']).first()
                if not bonus_type:
                    logging.info(f"  ⚠️  Type '{config['bonus_on_type']}' non trouvé")
            
            # Créer ou mettre à jour PokeballItem
            pokeball_item, created_new = PokeballItem.objects.get_or_create(
                item=item,
                defaults={
                    'guaranteed_capture': config['guaranteed_capture'],
                    'critical_catch_bonus': config['critical_catch_bonus'],
                    'bonus_on_type': bonus_type,
                    'bonus_on_status': config['bonus_on_status']
                }
            )
            
            if created_new:
                created += 1
                logging.info(f"[+] Créé: {ball_name}")
            else:
                # Mettre à jour
                pokeball_item.guaranteed_capture = config['guaranteed_capture']
                pokeball_item.critical_catch_bonus = config['critical_catch_bonus']
                pokeball_item.bonus_on_type = bonus_type
                pokeball_item.bonus_on_status = config['bonus_on_status']
                pokeball_item.save()
                updated += 1
                logging.info(f"[+] Mis à jour: {ball_name}")
                
        except Exception as e:
            logging.error(f"[!] Erreur avec {ball_name}: {str(e)}")
            skipped += 1
    
    logging.info(f"\n Résumé:")
    logging.info(f"  - Créés: {created}")
    logging.info(f"  - Mis à jour: {updated}")
    logging.info(f"  - Ignorés: {skipped}")
    logging.info(f"  - Total: {created + updated + skipped}")
    
    # Afficher toutes les balls configurées
    logging.info(f"\n PokeballItems configurés:")
    for pb in PokeballItem.objects.all():
        logging.info(f"  • {pb.item.name}: {pb.item.catch_rate_modifier}x" + 
              (f" [MASTER BALL]" if pb.guaranteed_capture else "") +
              (f" [+{int(pb.critical_catch_bonus*100)}% critique]" if pb.critical_catch_bonus > 0 else "") +
              (f" [Bonus {pb.bonus_on_type.name}]" if pb.bonus_on_type else "") +
              (f" [Bonus {pb.bonus_on_status}]" if pb.bonus_on_status else ""))