"""
Script d'initialisation des PokeballItems.

Les noms d'items correspondent exactement à ceux définis dans initialize_items()
(initializeItemsAndNpcs.py). Toute divergence → warning + skip.

Balls configurées :
  Basiques Gen 1  : Poke Ball, Great Ball, Ultra Ball, Master Ball, Safari Ball
  Spéciales       : Net Ball, Dive Ball, Nest Ball, Repeat Ball, Timer Ball,
                    Dusk Ball, Quick Ball, Heal Ball, Luxury Ball, Premier Ball,
                    Fast Ball, Level Ball, Lure Ball, Heavy Ball, Love Ball,
                    Moon Ball, Friend Ball, Cherry Ball, Sport Ball, Park Ball,
                    Dream Ball, Beast Ball
"""

import logging
from myPokemonApp.models import Item, PokeballItem, PokemonType

logging.basicConfig(level=logging.INFO)


def scriptToInitNewPokeBalls():
    """Initialise / met à jour les PokeballItems pour toutes les Poké Balls en DB."""

    logging.info("[+] Initialisation des PokeballItems...")

    # -------------------------------------------------------------------------
    # Configuration par nom d'item (exact, tel que créé par initialize_items())
    # -------------------------------------------------------------------------
    pokeball_configs = {

        # ── BASIQUES GEN 1 ────────────────────────────────────────────────────
        'Poke Ball': {
            'catch_rate_override':   None,   # utilise item.catch_rate_modifier (1.0)
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Ball standard.',
        },
        'Great Ball': {
            'catch_rate_override':   None,   # 1.5x défini dans l'item
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.05,   # +5% critique
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Meilleur taux que la Poké Ball.',
        },
        'Ultra Ball': {
            'catch_rate_override':   None,   # 2.0x défini dans l'item
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.10,   # +10% critique
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Ball ultra-performante.',
        },
        'Master Ball': {
            'catch_rate_override':   None,   # 255.0x défini dans l'item
            'guaranteed_capture':    True,
            'critical_catch_bonus':  1.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Capture à coup sûr.',
        },
        'Safari Ball': {
            'catch_rate_override':   None,   # 1.5x défini dans l'item
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Réservée à la Zone Safari.',
        },

        # ── BALLS SPÉCIALES ───────────────────────────────────────────────────
        'Net Ball': {
            'catch_rate_override':   3.0,    # ×3 sur Eau et Insecte, sinon ×1
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         'Eau',  # géré aussi pour Insecte côté calcul
            'bonus_on_status':       '',
            'notes': 'Bonus ×3 contre Eau et Insecte.',
        },
        'Dive Ball': {
            'catch_rate_override':   3.5,    # ×3.5 dans/sous l'eau, sinon ×1
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         'Eau',
            'bonus_on_status':       '',
            'notes': 'Efficace sous l\'eau ou contre Pokémon Eau.',
        },
        'Nest Ball': {
            # Formule : max(1, (40 - level) / 10) – géré dans calculate_capture_rate
            'catch_rate_override':   1.0,
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Plus efficace contre Pokémon de bas niveau (<30).',
        },
        'Repeat Ball': {
            'catch_rate_override':   3.0,    # ×3 si espèce déjà capturée, sinon ×1
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Bonus ×3 si l\'espèce a déjà été capturée.',
        },
        'Timer Ball': {
            # Formule : min(4, 1 + tour/10) – géré dans calculate_capture_rate
            'catch_rate_override':   1.0,
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Bonus croissant selon le nombre de tours (max ×4).',
        },
        'Dusk Ball': {
            'catch_rate_override':   3.5,    # ×3.5 la nuit/grotte, sinon ×1
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Efficace la nuit ou dans les grottes.',
        },
        'Quick Ball': {
            'catch_rate_override':   4.0,    # ×4 au tour 1, sinon ×1
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.20,   # +20% critique au tour 1
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Très efficace si utilisée au premier tour.',
        },
        'Heal Ball': {
            'catch_rate_override':   None,   # 1.0x — même taux que Poké Ball
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Soigne le statut du Pokémon capturé (taux standard).',
        },
        'Luxury Ball': {
            'catch_rate_override':   None,   # 1.0x — améliore l'amitié
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Augmente l\'amitié plus vite (taux standard).',
        },
        'Premier Ball': {
            'catch_rate_override':   None,   # 1.0x — commémorative
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Ball commémorative, taux identique à la Poké Ball.',
        },
        'Cherry Ball': {
            # Bonus contre Pokémon sans évolution ou évolution unique
            'catch_rate_override':   3.0,
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Efficace contre Pokémon à évolution unique.',
        },

        # ── BALLS SPÉCIALES AVANCÉES ─────────────────────────────────────────
        'Fast Ball': {
            # Bonus ×3 contre Pokémon avec Vitesse >= 100 (géré dans calculate_capture_rate)
            'catch_rate_override':   3.0,
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Bonus ×3 contre Pokémon rapides (Vitesse ≥ 100).',
        },
        'Level Ball': {
            # Formule : 4× si niveau joueur > 4× niveau cible, etc.
            'catch_rate_override':   1.0,
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Bonus selon le rapport de niveaux joueur/cible (max ×4).',
        },
        'Lure Ball': {
            'catch_rate_override':   3.0,    # ×3 contre Pokémon pêchés
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Efficace contre Pokémon pêchés.',
        },
        'Heavy Ball': {
            # Bonus selon le poids (géré dans calculate_capture_rate)
            'catch_rate_override':   1.0,
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Modificateur basé sur le poids du Pokémon.',
        },
        'Love Ball': {
            'catch_rate_override':   8.0,    # ×8 si sexe opposé au Pokémon du joueur
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': '×8 contre Pokémon du sexe opposé à l\'équipe.',
        },
        'Moon Ball': {
            'catch_rate_override':   4.0,    # ×4 contre Pokémon évoluant avec Pierre Lune
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': '×4 contre Pokémon évoluant avec une Pierre Lune.',
        },
        'Friend Ball': {
            'catch_rate_override':   None,   # 1.0x — amitié max à la capture
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Le Pokémon démarre avec une amitié maximale.',
        },

        # ── BALLS SPÉCIALES (non achetables) ─────────────────────────────────
        'Sport Ball': {
            'catch_rate_override':   None,   # 1.5x défini dans l'item
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Ball de concours Bug-Catching.',
        },
        'Park Ball': {
            'catch_rate_override':   None,   # 1.0x défini dans l'item
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Utilisée dans le Parc des Amis.',
        },
        'Dream Ball': {
            'catch_rate_override':   None,   # 3.0x défini dans l'item
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Utilisée dans le Monde des Rêves.',
        },
        'Beast Ball': {
            'catch_rate_override':   None,   # 0.1x défini dans l'item (Ultra-Chimères)
            'guaranteed_capture':    False,
            'critical_catch_bonus':  0.0,
            'bonus_on_type':         None,
            'bonus_on_status':       '',
            'notes': 'Spéciale pour les Ultra-Chimères (0.1× sinon).',
        },
    }

    # -------------------------------------------------------------------------
    # Traitement
    # -------------------------------------------------------------------------
    created = updated = skipped = 0

    for ball_name, cfg in pokeball_configs.items():
        try:
            item = Item.objects.filter(name=ball_name).first()
            if not item:
                logging.warning(f"[!] Item introuvable en DB : '{ball_name}' — ignoré")
                skipped += 1
                continue

            # Override du catch_rate_modifier si précisé dans la config
            if cfg['catch_rate_override'] is not None:
                if item.catch_rate_modifier != cfg['catch_rate_override']:
                    item.catch_rate_modifier = cfg['catch_rate_override']
                    item.save(update_fields=['catch_rate_modifier'])

            # Résolution du type bonus
            bonus_type = None
            if cfg['bonus_on_type']:
                bonus_type = PokemonType.objects.filter(
                    name__icontains=cfg['bonus_on_type']
                ).first()
                if not bonus_type:
                    logging.warning(f"  ⚠️  Type '{cfg['bonus_on_type']}' introuvable pour {ball_name}")

            pb_item, is_new = PokeballItem.objects.get_or_create(
                item=item,
                defaults={
                    'guaranteed_capture':   cfg['guaranteed_capture'],
                    'critical_catch_bonus': cfg['critical_catch_bonus'],
                    'bonus_on_type':        bonus_type,
                    'bonus_on_status':      cfg['bonus_on_status'],
                }
            )

            if is_new:
                created += 1
                logging.info(f"  ✅ Créé  : {ball_name} — {cfg['notes']}")
            else:
                pb_item.guaranteed_capture   = cfg['guaranteed_capture']
                pb_item.critical_catch_bonus = cfg['critical_catch_bonus']
                pb_item.bonus_on_type        = bonus_type
                pb_item.bonus_on_status      = cfg['bonus_on_status']
                pb_item.save()
                updated += 1
                logging.info(f"  ⭕ MàJ   : {ball_name} — {cfg['notes']}")

        except Exception as e:
            logging.error(f"  [✗] Erreur avec '{ball_name}' : {e}")
            skipped += 1

    # -------------------------------------------------------------------------
    # Résumé
    # -------------------------------------------------------------------------
    logging.info(f"\n📊 Résumé PokeballItems :")
    logging.info(f"   Créés        : {created}")
    logging.info(f"   Mis à jour   : {updated}")
    logging.info(f"   Ignorés/err  : {skipped}")
    logging.info(f"   Total traités: {created + updated + skipped}")

    logging.info(f"\n🎯 PokeballItems configurés :")
    for pb in PokeballItem.objects.select_related('item', 'bonus_on_type').order_by('item__name'):
        flags = []
        if pb.guaranteed_capture:
            flags.append('MASTER')
        if pb.critical_catch_bonus > 0:
            flags.append(f'+{int(pb.critical_catch_bonus * 100)}% critique')
        if pb.bonus_on_type:
            flags.append(f'Bonus {pb.bonus_on_type.name}')
        if pb.bonus_on_status:
            flags.append(f'Bonus statut={pb.bonus_on_status}')
        flag_str = '  [' + ', '.join(flags) + ']' if flags else ''
        logging.info(f"   • {pb.item.name:<18} {pb.item.catch_rate_modifier:.1f}×{flag_str}")