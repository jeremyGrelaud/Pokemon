"""
tests.py — Suite de tests unitaires pour myPokemonApp
======================================================

Organisation :
  1. Fixtures partagées (TestCase avec helpers)
  2. TestTrainerModel          — Trainer.spend_money / earn_money / has_badge / party props
  3. TestPlayablePokemonModel  — heal / cure_status / apply_status / reset_combat_stats
                                 is_fainted / needs_healing / hp_percent / display_name
  4. TestCalculateStats        — formule Gen-3 HP et stats normales
  5. TestExpFormulas           — exp_at_level pour chaque growth_rate
  6. TestNatureModifiers        — get_nature_modifiers (service pur, zéro DB)
  7. TestCaptureRate           — calculate_capture_rate (mocks uniquement)
  8. TestCalculateShakeCount   — calculate_shake_count (logique pure)
  9. TestHealTeamService       — heal_team bulk (integration légère)
 10. TestPokemonCenterHeal     — PokemonCenter.heal_trainer_team (integration légère)

Lancer avec :
    python manage.py test myPokemonApp.tests
"""

from unittest.mock import MagicMock, patch, PropertyMock

from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


# =============================================================================
# HELPERS PARTAGÉS
# =============================================================================

def make_trainer(username='Ash', trainer_type='player', money=3000):
    """Crée un Trainer en DB (nécessite les migrations)."""
    from myPokemonApp.models.Trainer import Trainer
    return Trainer.objects.create(username=username, trainer_type=trainer_type, money=money)


def make_pokemon_type(name='Normal'):
    """Crée un PokemonType, ou le récupère s'il existe déjà."""
    from myPokemonApp.models.PokemonType import PokemonType
    obj, _ = PokemonType.objects.get_or_create(name=name)
    return obj


def make_species(name='Bulbasaur', pokedex_number=1,
                 base_hp=45, base_attack=49, base_defense=49,
                 base_special_attack=65, base_special_defense=65, base_speed=45,
                 catch_rate=45, base_experience=64, growth_rate='medium_fast'):
    """Crée une espèce Pokémon minimale."""
    from myPokemonApp.models.Pokemon import Pokemon
    ptype = make_pokemon_type()
    obj, _ = Pokemon.objects.get_or_create(
        pokedex_number=pokedex_number,
        defaults=dict(
            name=name,
            primary_type=ptype,
            base_hp=base_hp, base_attack=base_attack, base_defense=base_defense,
            base_special_attack=base_special_attack,
            base_special_defense=base_special_defense,
            base_speed=base_speed,
            catch_rate=catch_rate, base_experience=base_experience,
            growth_rate=growth_rate,
        )
    )
    return obj


def make_playable_pokemon(trainer, species=None, level=10,
                           max_hp=50, current_hp=50,
                           status_condition=None, nature='Hardy'):
    """Crée un PlayablePokemon en DB."""
    from myPokemonApp.models.PlayablePokemon import PlayablePokemon
    if species is None:
        species = make_species()
    return PlayablePokemon.objects.create(
        species=species,
        trainer=trainer,
        level=level,
        max_hp=max_hp,
        current_hp=current_hp,
        attack=45, defense=45,
        special_attack=60, special_defense=60,
        speed=45,
        nature=nature,
        status_condition=status_condition,
        is_in_party=True,
        party_position=1,
    )


def make_move(name='Tackle', pp=35, power=40,
              accuracy=100, move_type='physical', damage_category='physical'):
    """Crée un PokemonMove minimal."""
    from myPokemonApp.models.PokemonMove import PokemonMove
    from myPokemonApp.models.PokemonType import PokemonType
    ptype = make_pokemon_type('Normal')
    obj, _ = PokemonMove.objects.get_or_create(
        name=name,
        defaults=dict(
            pp=pp, power=power, accuracy=accuracy,
            move_type=ptype, damage_category=damage_category,
        )
    )
    return obj


# =============================================================================
# 1. TRAINER MODEL
# =============================================================================

class TestTrainerModel(TestCase):
    """Tests sur les méthodes du modèle Trainer."""

    def setUp(self):
        self.trainer = make_trainer(money=1000)

    # --- spend_money -----------------------------------------------------------

    def test_spend_money_success(self):
        """Dépenser moins que le solde doit réussir et déduire le montant."""
        result = self.trainer.spend_money(400)
        self.trainer.refresh_from_db()
        self.assertTrue(result)
        self.assertEqual(self.trainer.money, 600)

    def test_spend_money_exact_amount(self):
        """Dépenser exactement le solde doit réussir et mettre le solde à 0."""
        result = self.trainer.spend_money(1000)
        self.trainer.refresh_from_db()
        self.assertTrue(result)
        self.assertEqual(self.trainer.money, 0)

    def test_spend_money_insufficient_funds(self):
        """Dépenser plus que le solde doit échouer sans modifier le montant."""
        result = self.trainer.spend_money(1500)
        self.trainer.refresh_from_db()
        self.assertFalse(result)
        self.assertEqual(self.trainer.money, 1000)  # inchangé

    def test_spend_money_zero(self):
        """Dépenser 0 doit réussir sans modifier le solde."""
        result = self.trainer.spend_money(0)
        self.trainer.refresh_from_db()
        self.assertTrue(result)
        self.assertEqual(self.trainer.money, 1000)

    # --- earn_money ------------------------------------------------------------

    def test_earn_money(self):
        """Gagner de l'argent doit créditer le solde."""
        self.trainer.earn_money(500)
        self.trainer.refresh_from_db()
        self.assertEqual(self.trainer.money, 1500)

    def test_earn_money_zero(self):
        """Gagner 0 ne doit pas modifier le solde."""
        self.trainer.earn_money(0)
        self.trainer.refresh_from_db()
        self.assertEqual(self.trainer.money, 1000)

    # --- has_badge -------------------------------------------------------------

    def test_has_badge_true(self):
        """Un trainer avec 3 badges doit avoir le badge d'ordre 3."""
        self.trainer.badges = 3
        self.trainer.save()
        self.assertTrue(self.trainer.has_badge(3))

    def test_has_badge_false(self):
        """Un trainer avec 2 badges ne doit pas avoir le badge d'ordre 3."""
        self.trainer.badges = 2
        self.trainer.save()
        self.assertFalse(self.trainer.has_badge(3))

    def test_has_badge_zero(self):
        """Sans badge, has_badge(1) doit retourner False."""
        self.trainer.badges = 0
        self.trainer.save()
        self.assertFalse(self.trainer.has_badge(1))

    # --- party / pc properties -------------------------------------------------

    def test_party_returns_in_party_pokemon(self):
        """La property party ne doit retourner que les Pokémon is_in_party=True."""
        from myPokemonApp.models.PlayablePokemon import PlayablePokemon
        species = make_species()
        # En équipe
        p1 = make_playable_pokemon(self.trainer, species=species)
        # Au PC
        p2 = make_playable_pokemon(self.trainer, species=species)
        p2.is_in_party = False
        p2.save()
        party_ids = list(self.trainer.party.values_list('id', flat=True))
        self.assertIn(p1.id, party_ids)
        self.assertNotIn(p2.id, party_ids)

    def test_party_count(self):
        """party_count doit compter uniquement les Pokémon dans l'équipe."""
        species = make_species()
        make_playable_pokemon(self.trainer, species=species)
        make_playable_pokemon(self.trainer, species=species)
        self.assertEqual(self.trainer.party_count, 2)

    def test_get_reward_gym_leader(self):
        """Un Gym Leader avec 2 badges doit donner 1000 + 2*500 = 2000₽."""
        self.trainer.trainer_type = 'gym_leader'
        self.trainer.badges = 2
        self.trainer.save()
        self.assertEqual(self.trainer.get_reward(), 2000)

    def test_get_reward_elite_four(self):
        """Un membre du Conseil des 4 doit toujours donner 5000₽."""
        self.trainer.trainer_type = 'elite_four'
        self.trainer.save()
        self.assertEqual(self.trainer.get_reward(), 5000)

    def test_get_reward_champion(self):
        """Le champion doit toujours donner 10000₽."""
        self.trainer.trainer_type = 'champion'
        self.trainer.save()
        self.assertEqual(self.trainer.get_reward(), 10000)

    def test_get_full_title_with_class(self):
        """get_full_title doit combiner npc_class et username."""
        self.trainer.npc_class = 'Gamin'
        self.trainer.save()
        self.assertEqual(self.trainer.get_full_title(), 'Gamin Ash')

    def test_get_full_title_without_class(self):
        """get_full_title sans npc_class doit retourner uniquement le username."""
        self.trainer.npc_class = ''
        self.trainer.save()
        self.assertEqual(self.trainer.get_full_title(), 'Ash')


# =============================================================================
# 2. PLAYABLE POKEMON MODEL
# =============================================================================

class TestPlayablePokemonModel(TestCase):
    """Tests sur les méthodes du modèle PlayablePokemon."""

    def setUp(self):
        self.trainer = make_trainer()
        self.species = make_species()
        self.pokemon = make_playable_pokemon(
            self.trainer, species=self.species,
            max_hp=100, current_hp=60,
        )

    def _refresh(self):
        self.pokemon.refresh_from_db()

    # --- heal ------------------------------------------------------------------

    def test_heal_full_no_arg(self):
        """heal() sans argument doit remettre les HP à max."""
        self.pokemon.heal()
        self._refresh()
        self.assertEqual(self.pokemon.current_hp, self.pokemon.max_hp)

    def test_heal_partial(self):
        """heal(20) doit ajouter exactement 20 HP."""
        self.pokemon.current_hp = 50
        self.pokemon.save()
        self.pokemon.heal(20)
        self._refresh()
        self.assertEqual(self.pokemon.current_hp, 70)

    def test_heal_capped_at_max(self):
        """heal() ne doit pas dépasser max_hp."""
        self.pokemon.current_hp = 90
        self.pokemon.save()
        self.pokemon.heal(50)
        self._refresh()
        self.assertEqual(self.pokemon.current_hp, 100)

    # --- cure_status -----------------------------------------------------------

    def test_cure_status_removes_poison(self):
        """cure_status() doit supprimer le statut et remettre sleep_turns à 0."""
        self.pokemon.status_condition = 'poison'
        self.pokemon.sleep_turns = 2
        self.pokemon.save()
        self.pokemon.cure_status()
        self._refresh()
        self.assertIsNone(self.pokemon.status_condition)
        self.assertEqual(self.pokemon.sleep_turns, 0)

    def test_cure_status_on_healthy_pokemon(self):
        """cure_status() sur un Pokémon sans statut ne doit pas provoquer d'erreur."""
        self.pokemon.status_condition = None
        self.pokemon.save()
        self.pokemon.cure_status()  # ne doit pas lever d'exception
        self._refresh()
        self.assertIsNone(self.pokemon.status_condition)

    # --- apply_status ----------------------------------------------------------

    def test_apply_status_on_healthy(self):
        """apply_status doit affecter le statut si le Pokémon est sain."""
        result = self.pokemon.apply_status('poison')
        self._refresh()
        self.assertTrue(result)
        self.assertEqual(self.pokemon.status_condition, 'poison')

    def test_apply_status_blocked_if_already_status(self):
        """apply_status doit échouer si un statut est déjà présent."""
        self.pokemon.status_condition = 'burn'
        self.pokemon.save()
        result = self.pokemon.apply_status('poison')
        self._refresh()
        self.assertFalse(result)
        self.assertEqual(self.pokemon.status_condition, 'burn')  # inchangé

    def test_apply_status_sleep_sets_sleep_turns(self):
        """apply_status('sleep') doit définir sleep_turns entre 1 et 3."""
        self.pokemon.apply_status('sleep')
        self._refresh()
        self.assertEqual(self.pokemon.status_condition, 'sleep')
        self.assertIn(self.pokemon.sleep_turns, [1, 2, 3])

    # --- reset_combat_stats ----------------------------------------------------

    def test_reset_combat_stats(self):
        """reset_combat_stats doit remettre tous les stages à 0."""
        self.pokemon.attack_stage = 3
        self.pokemon.defense_stage = -2
        self.pokemon.speed_stage = 6
        self.pokemon.save()
        self.pokemon.reset_combat_stats()
        self._refresh()
        for field in ['attack_stage', 'defense_stage', 'special_attack_stage',
                      'special_defense_stage', 'speed_stage', 'accuracy_stage', 'evasion_stage']:
            self.assertEqual(getattr(self.pokemon, field), 0, f"{field} devrait être 0")

    # --- is_fainted ------------------------------------------------------------

    def test_is_fainted_true(self):
        """Un Pokémon à 0 HP est considéré KO."""
        self.pokemon.current_hp = 0
        self.pokemon.save()
        self.assertTrue(self.pokemon.is_fainted())

    def test_is_fainted_false(self):
        """Un Pokémon avec des HP positifs n'est pas KO."""
        self.pokemon.current_hp = 1
        self.pokemon.save()
        self.assertFalse(self.pokemon.is_fainted())

    # --- needs_healing ---------------------------------------------------------

    def test_needs_healing_damaged(self):
        """Un Pokémon avec HP < max_hp nécessite des soins."""
        self.pokemon.current_hp = 50
        self.pokemon.max_hp = 100
        self.pokemon.save()
        self.assertTrue(self.pokemon.needs_healing)

    def test_needs_healing_status_only(self):
        """Un Pokémon à pleine santé mais avec un statut nécessite des soins."""
        self.pokemon.current_hp = 100
        self.pokemon.max_hp = 100
        self.pokemon.status_condition = 'paralysis'
        self.pokemon.save()
        self.assertTrue(self.pokemon.needs_healing)

    def test_needs_healing_false(self):
        """Un Pokémon à pleine santé sans statut ne nécessite pas de soins."""
        self.pokemon.current_hp = 100
        self.pokemon.max_hp = 100
        self.pokemon.status_condition = None
        self.pokemon.save()
        self.assertFalse(self.pokemon.needs_healing)

    # --- hp_percent ------------------------------------------------------------

    def test_hp_percent_full(self):
        """Un Pokémon à pleine santé doit afficher 100.0%."""
        self.pokemon.current_hp = 100
        self.pokemon.max_hp = 100
        self.pokemon.save()
        self.assertEqual(self.pokemon.hp_percent, 100.0)

    def test_hp_percent_half(self):
        """Un Pokémon à moitié de HP doit afficher ~50.0%."""
        self.pokemon.current_hp = 50
        self.pokemon.max_hp = 100
        self.pokemon.save()
        self.assertEqual(self.pokemon.hp_percent, 50.0)

    def test_hp_percent_zero_max(self):
        """hp_percent avec max_hp=0 doit retourner 0.0 sans ZeroDivisionError."""
        self.pokemon.max_hp = 0
        self.pokemon.save()
        self.assertEqual(self.pokemon.hp_percent, 0.0)

    # --- display_name ----------------------------------------------------------

    def test_display_name_with_nickname(self):
        """display_name doit retourner le surnom s'il est défini."""
        self.pokemon.nickname = 'Bulby'
        self.pokemon.save()
        self.assertEqual(self.pokemon.display_name, 'Bulby')

    def test_display_name_without_nickname(self):
        """display_name sans surnom doit retourner le nom de l'espèce."""
        self.pokemon.nickname = None
        self.pokemon.save()
        self.assertEqual(self.pokemon.display_name, self.species.name)

    def test_display_name_empty_nickname_uses_species(self):
        """Un surnom vide ('') est falsy → display_name retourne le nom de l'espèce."""
        self.pokemon.nickname = ''
        self.pokemon.save()
        # '' est falsy, la property fait `self.nickname or self.species.name`
        self.assertEqual(self.pokemon.display_name, self.species.name)


# =============================================================================
# 3. CALCUL DES STATS (formule Gen 3)
# =============================================================================

class TestCalculateStats(TestCase):
    """Vérifie la formule de calcul de stats Gen 3 dans PlayablePokemon.calculate_stats."""

    def setUp(self):
        self.trainer = make_trainer()
        self.species = make_species(
            base_hp=45, base_attack=49, base_defense=49,
            base_special_attack=65, base_special_defense=65, base_speed=45
        )
        self.pokemon = make_playable_pokemon(
            self.trainer, species=self.species, level=50
        )
        # IVs et EVs à 0 pour simplifier les calculs
        for field in ['iv_hp', 'iv_attack', 'iv_defense',
                      'iv_special_attack', 'iv_special_defense', 'iv_speed',
                      'ev_hp', 'ev_attack', 'ev_defense',
                      'ev_special_attack', 'ev_special_defense', 'ev_speed']:
            setattr(self.pokemon, field, 0)
        self.pokemon.nature = 'Hardy'  # nature neutre
        self.pokemon.save()

    def _expected_hp(self, base, iv, ev, level):
        """Formule Gen 3 HP : floor((2*base + iv + floor(ev/4)) * L / 100) + L + 10"""
        return int(((2 * base + iv + ev // 4) * level) // 100) + level + 10

    def _expected_stat(self, base, iv, ev, level):
        """Formule Gen 3 stat : floor((2*base + iv + floor(ev/4)) * L / 100) + 5"""
        return int(((2 * base + iv + ev // 4) * level) // 100) + 5

    def test_max_hp_calculation(self):
        """max_hp doit correspondre à la formule Gen 3."""
        self.pokemon.calculate_stats()
        expected = self._expected_hp(
            self.species.base_hp, 0, 0, self.pokemon.level
        )
        self.assertEqual(self.pokemon.max_hp, expected)

    def test_attack_calculation(self):
        """attack doit correspondre à la formule Gen 3 (nature neutre)."""
        self.pokemon.calculate_stats()
        expected = self._expected_stat(
            self.species.base_attack, 0, 0, self.pokemon.level
        )
        self.assertEqual(self.pokemon.attack, expected)

    def test_speed_calculation(self):
        """speed doit correspondre à la formule Gen 3 (nature neutre)."""
        self.pokemon.calculate_stats()
        expected = self._expected_stat(
            self.species.base_speed, 0, 0, self.pokemon.level
        )
        self.assertEqual(self.pokemon.speed, expected)

    def test_nature_adamant_boosts_attack_reduces_spatk(self):
        """Nature Adamant : attack ×1.1, special_attack ×0.9."""
        self.pokemon.nature = 'Adamant'
        self.pokemon.save()
        self.pokemon.calculate_stats()
        base_attack = self._expected_stat(self.species.base_attack, 0, 0, self.pokemon.level)
        base_spatk  = self._expected_stat(self.species.base_special_attack, 0, 0, self.pokemon.level)
        self.assertEqual(self.pokemon.attack,          int(base_attack * 1.1))
        self.assertEqual(self.pokemon.special_attack,  int(base_spatk  * 0.9))

    def test_neutral_nature_no_modifier(self):
        """Nature Hardy (neutre) : aucune stat ne doit être modifiée."""
        self.pokemon.nature = 'Hardy'
        self.pokemon.calculate_stats()
        base_atk = self._expected_stat(self.species.base_attack, 0, 0, self.pokemon.level)
        self.assertEqual(self.pokemon.attack, base_atk)

    def test_ivs_increase_stats(self):
        """Avec IV=31 en HP, max_hp doit être plus élevé qu'avec IV=0."""
        self.pokemon.iv_hp = 0
        self.pokemon.calculate_stats()
        hp_no_iv = self.pokemon.max_hp

        self.pokemon.iv_hp = 31
        self.pokemon.calculate_stats()
        hp_with_iv = self.pokemon.max_hp

        self.assertGreater(hp_with_iv, hp_no_iv)

    def test_stat_minimum_is_one(self):
        """Une stat calculée ne peut pas être inférieure à 1."""
        # Pokémon niveau 1, base très faible → stat plancher
        self.pokemon.level = 1
        self.pokemon.nature = 'Hardy'
        self.pokemon.calculate_stats()
        for stat in ['attack', 'defense', 'special_attack', 'special_defense', 'speed']:
            self.assertGreaterEqual(getattr(self.pokemon, stat), 1)


# =============================================================================
# 4. FORMULES EXP
# =============================================================================

class TestExpFormulas(TestCase):
    """Vérifie exp_at_level et exp_for_next_level pour chaque growth_rate."""

    def setUp(self):
        self.trainer = make_trainer()

    def _make_pokemon(self, growth_rate, level=50):
        species = make_species(pokedex_number=9000 + hash(growth_rate) % 1000,
                               name=f'Test_{growth_rate}', growth_rate=growth_rate)
        return make_playable_pokemon(self.trainer, species=species, level=level)

    def test_medium_fast_level_100(self):
        """medium_fast : XP au niveau 100 = 100³ = 1 000 000."""
        p = self._make_pokemon('medium_fast', level=100)
        self.assertEqual(p.exp_at_level(100), 100 ** 3)

    def test_fast_level_100(self):
        """fast : XP au niveau 100 = 4/5 × 100³ = 800 000."""
        p = self._make_pokemon('fast', level=100)
        self.assertEqual(p.exp_at_level(100), int(4 * 100 ** 3 / 5))

    def test_slow_level_100(self):
        """slow : XP au niveau 100 = 5/4 × 100³ = 1 250 000."""
        p = self._make_pokemon('slow', level=100)
        self.assertEqual(p.exp_at_level(100), int(5 * 100 ** 3 / 4))

    def test_exp_at_level_1_is_zero(self):
        """exp_at_level(1) doit retourner 0 quel que soit le growth_rate."""
        for rate in ['fast', 'medium_fast', 'medium_slow', 'slow']:
            p = self._make_pokemon(rate)
            self.assertEqual(p.exp_at_level(1), 0, f"Échec pour growth_rate={rate}")

    def test_exp_at_level_strictly_increasing(self):
        """L'XP requise doit être strictement croissante de 2 à 100."""
        p = self._make_pokemon('medium_fast')
        exps = [p.exp_at_level(n) for n in range(2, 101)]
        for i in range(len(exps) - 1):
            self.assertLess(exps[i], exps[i + 1],
                            f"exp non croissante entre niveaux {i+2} et {i+3}")

    def test_exp_for_next_level_at_100_returns_sentinel(self):
        """À niveau 100 (max), exp_for_next_level() doit retourner la sentinelle 10_000_000."""
        p = self._make_pokemon('medium_fast', level=100)
        self.assertEqual(p.exp_for_next_level(), 10_000_000)

    def test_exp_for_next_level_greater_than_current_threshold(self):
        """exp_for_next_level() doit être > exp_at_level(current_level)."""
        p = self._make_pokemon('medium_fast', level=20)
        self.assertGreater(p.exp_for_next_level(), p.exp_at_level(20))


# =============================================================================
# 5. NATURES (service pur — zéro DB)
# =============================================================================

class TestNatureModifiers(TestCase):
    """Teste get_nature_modifiers — fonction pure, pas de DB."""

    def _get(self, nature):
        from myPokemonApp.services.trainer_service import get_nature_modifiers
        return get_nature_modifiers(nature)

    def test_adamant(self):
        self.assertEqual(self._get('Adamant'), ('attack', 'special_attack'))

    def test_modest(self):
        self.assertEqual(self._get('Modest'), ('special_attack', 'attack'))

    def test_timid(self):
        self.assertEqual(self._get('Timid'), ('speed', 'attack'))

    def test_jolly(self):
        self.assertEqual(self._get('Jolly'), ('speed', 'special_attack'))

    def test_neutral_hardy(self):
        """Hardy est neutre → (None, None)."""
        self.assertEqual(self._get('Hardy'), (None, None))

    def test_neutral_unknown(self):
        """Une nature inconnue doit retourner (None, None)."""
        self.assertEqual(self._get('Docile'), (None, None))

    def test_bold(self):
        self.assertEqual(self._get('Bold'), ('defense', 'attack'))

    def test_calm(self):
        self.assertEqual(self._get('Calm'), ('special_defense', 'attack'))


# =============================================================================
# 6. TAUX DE CAPTURE (mocks — zéro DB)
# =============================================================================

class TestCaptureRate(TestCase):
    """
    Teste calculate_capture_rate avec des mocks pour éviter toute DB.
    On injecte directement les dépendances (pokemon, ball).
    """

    def _make_mock_pokemon(self, catch_rate=45, hp_ratio=1.0):
        """Pokémon mock avec catch_rate et hp_ratio configurables."""
        species = MagicMock()
        species.catch_rate = catch_rate
        pokemon = MagicMock()
        pokemon.species = species
        return pokemon

    def _make_mock_ball(self, catch_rate_modifier=1.0):
        ball = MagicMock()
        ball.catch_rate_modifier = catch_rate_modifier
        return ball

    def _call(self, pokemon, ball, hp_percent=1.0, status=None):
        from myPokemonApp.services.capture_service import calculate_capture_rate
        return calculate_capture_rate(pokemon, ball, hp_percent, status)

    @patch('myPokemonApp.services.capture_service.PokeballItem')
    def test_master_ball_guarantees_capture(self, MockPokeball):
        """Master Ball → taux de capture = 1.0."""
        mock_pb = MagicMock()
        mock_pb.guaranteed_capture = True
        MockPokeball.objects.get.return_value = mock_pb

        pokemon = self._make_mock_pokemon()
        ball    = self._make_mock_ball()
        result  = self._call(pokemon, ball)
        self.assertEqual(result, 1.0)

    @patch('myPokemonApp.services.capture_service.PokeballItem')
    def test_low_hp_increases_capture_rate(self, MockPokeball):
        """Un Pokémon à faibles HP doit avoir un taux de capture plus élevé."""
        MockPokeball.objects.get.side_effect = Exception('DoesNotExist')

        pokemon = self._make_mock_pokemon(catch_rate=45)
        ball    = self._make_mock_ball(catch_rate_modifier=1.0)

        rate_full = self._call(pokemon, ball, hp_percent=1.0)
        rate_low  = self._call(pokemon, ball, hp_percent=0.1)
        self.assertGreater(rate_low, rate_full)

    @patch('myPokemonApp.services.capture_service.PokeballItem')
    def test_sleep_status_boosts_capture(self, MockPokeball):
        """Le statut 'sleep' (×2.0) doit augmenter le taux vs aucun statut."""
        MockPokeball.objects.get.side_effect = Exception('DoesNotExist')

        pokemon  = self._make_mock_pokemon(catch_rate=45)
        ball     = self._make_mock_ball()
        rate_no  = self._call(pokemon, ball, hp_percent=0.5, status=None)
        rate_slp = self._call(pokemon, ball, hp_percent=0.5, status='sleep')
        self.assertGreater(rate_slp, rate_no)

    @patch('myPokemonApp.services.capture_service.PokeballItem')
    def test_paralysis_boosts_less_than_sleep(self, MockPokeball):
        """Paralysie (×1.5) doit donner un taux inférieur au sommeil (×2.0)."""
        MockPokeball.objects.get.side_effect = Exception('DoesNotExist')

        pokemon      = self._make_mock_pokemon(catch_rate=45)
        ball         = self._make_mock_ball()
        rate_sleep   = self._call(pokemon, ball, hp_percent=0.5, status='sleep')
        rate_para    = self._call(pokemon, ball, hp_percent=0.5, status='paralysis')
        self.assertGreater(rate_sleep, rate_para)

    @patch('myPokemonApp.services.capture_service.PokeballItem')
    def test_rate_capped_at_1(self, MockPokeball):
        """Le taux de capture ne doit jamais dépasser 1.0."""
        MockPokeball.objects.get.side_effect = Exception('DoesNotExist')

        pokemon = self._make_mock_pokemon(catch_rate=255)
        ball    = self._make_mock_ball(catch_rate_modifier=10.0)
        result  = self._call(pokemon, ball, hp_percent=0.01, status='sleep')
        self.assertLessEqual(result, 1.0)

    @patch('myPokemonApp.services.capture_service.PokeballItem')
    def test_rate_always_non_negative(self, MockPokeball):
        """Le taux de capture doit toujours être ≥ 0."""
        MockPokeball.objects.get.side_effect = Exception('DoesNotExist')
        pokemon = self._make_mock_pokemon(catch_rate=1)
        ball    = self._make_mock_ball(catch_rate_modifier=1.0)
        result  = self._call(pokemon, ball, hp_percent=1.0)
        self.assertGreaterEqual(result, 0.0)


# =============================================================================
# 7. CALCULATE_SHAKE_COUNT (logique pure — zéro DB ni mock)
# =============================================================================

class TestCalculateShakeCount(TestCase):
    """
    Teste calculate_shake_count.
    Fonction déterministe une fois le random fixé, mais on peut tester les bornes.
    """

    def _call(self, rate):
        from myPokemonApp.services.capture_service import calculate_shake_count
        return calculate_shake_count(rate)

    def test_rate_1_always_captures(self):
        """Taux 1.0 doit toujours capturer (3 shakes, success=True)."""
        for _ in range(20):
            shakes, success = self._call(1.0)
            self.assertEqual(shakes, 3)
            self.assertTrue(success)

    def test_rate_0_never_captures(self):
        """Taux 0.0 doit toujours échouer (0 shakes, success=False)."""
        for _ in range(20):
            shakes, success = self._call(0.0)
            self.assertEqual(shakes, 0)
            self.assertFalse(success)

    def test_shakes_in_range(self):
        """Le nombre de shakes doit toujours être compris entre 0 et 3."""
        for rate in [0.1, 0.3, 0.5, 0.7, 0.9]:
            for _ in range(10):
                shakes, _ = self._call(rate)
                self.assertIn(shakes, [0, 1, 2, 3])

    def test_success_implies_3_shakes(self):
        """En cas de succès, le nombre de shakes doit être exactement 3."""
        import random as rng
        rng.seed(42)
        for rate in [0.5, 0.8, 0.95]:
            for _ in range(30):
                shakes, success = self._call(rate)
                if success:
                    self.assertEqual(shakes, 3)

    def test_return_types(self):
        """calculate_shake_count doit retourner (int, bool)."""
        shakes, success = self._call(0.5)
        self.assertIsInstance(shakes, int)
        self.assertIsInstance(success, bool)


# =============================================================================
# 8. HEAL_TEAM SERVICE (intégration légère)
# =============================================================================

class TestHealTeamService(TestCase):
    """Vérifie que heal_team restaure HP, statut, stages et PP."""

    def setUp(self):
        self.trainer = make_trainer()
        self.species = make_species()
        self.move    = make_move(pp=35)

    def _make_damaged_pokemon(self, current_hp=20, status='poison'):
        p = make_playable_pokemon(
            self.trainer, species=self.species,
            max_hp=100, current_hp=current_hp, status_condition=status
        )
        p.attack_stage = 3
        p.save()
        from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance
        PokemonMoveInstance.objects.create(pokemon=p, move=self.move, current_pp=5)
        return p

    def test_heal_team_restores_hp(self):
        """heal_team doit remettre les HP à max_hp pour chaque Pokémon."""
        from myPokemonApp.services.trainer_service import heal_team
        p = self._make_damaged_pokemon(current_hp=20)
        heal_team(self.trainer)
        p.refresh_from_db()
        self.assertEqual(p.current_hp, p.max_hp)

    def test_heal_team_clears_status(self):
        """heal_team doit supprimer le statut de chaque Pokémon."""
        from myPokemonApp.services.trainer_service import heal_team
        p = self._make_damaged_pokemon(status='burn')
        heal_team(self.trainer)
        p.refresh_from_db()
        self.assertIsNone(p.status_condition)

    def test_heal_team_resets_stages(self):
        """heal_team doit remettre les stages de stat à 0."""
        from myPokemonApp.services.trainer_service import heal_team
        p = self._make_damaged_pokemon()
        heal_team(self.trainer)
        p.refresh_from_db()
        self.assertEqual(p.attack_stage, 0)

    def test_heal_team_restores_pp(self):
        """heal_team doit restaurer les PP de tous les moves à leur maximum."""
        from myPokemonApp.services.trainer_service import heal_team
        from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance
        p = self._make_damaged_pokemon()
        heal_team(self.trainer)
        mi = PokemonMoveInstance.objects.get(pokemon=p, move=self.move)
        self.assertEqual(mi.current_pp, self.move.pp)

    def test_heal_team_empty_team_no_error(self):
        """heal_team sur une équipe vide ne doit pas lever d'exception."""
        from myPokemonApp.services.trainer_service import heal_team
        empty_trainer = make_trainer(username='EmptyTrainer')
        try:
            heal_team(empty_trainer)
        except Exception as e:
            self.fail(f"heal_team a levé une exception sur une équipe vide : {e}")


# =============================================================================
# 9. POKEMON CENTER — heal_trainer_team (intégration)
# =============================================================================

class TestPokemonCenterHeal(TestCase):
    """Vérifie PokemonCenter.heal_trainer_team via la couche modèle."""

    def setUp(self):
        from myPokemonApp.models.PokemonCenter import PokemonCenter
        self.trainer = make_trainer(money=5000)
        self.species = make_species(pokedex_number=2, name='Charmander')
        self.move    = make_move(name='Ember', pp=25)
        self.center  = PokemonCenter.objects.create(
            name='Centre Pokémon Test',
            location='Pallet Town',
            healing_cost=0,          # gratuit pour simplifier
        )

    def _make_hurt_pokemon(self, current_hp=10, status='paralysis'):
        from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance
        p = make_playable_pokemon(
            self.trainer, species=self.species,
            max_hp=80, current_hp=current_hp, status_condition=status
        )
        PokemonMoveInstance.objects.create(pokemon=p, move=self.move, current_pp=3)
        return p

    def test_heal_returns_success(self):
        """heal_trainer_team doit retourner {'success': True, ...}."""
        self._make_hurt_pokemon()
        result = self.center.heal_trainer_team(self.trainer)
        self.assertTrue(result['success'])

    def test_heal_restores_hp(self):
        """heal_trainer_team doit remettre les HP à max."""
        p = self._make_hurt_pokemon(current_hp=10)
        self.center.heal_trainer_team(self.trainer)
        p.refresh_from_db()
        self.assertEqual(p.current_hp, p.max_hp)

    def test_heal_clears_status(self):
        """heal_trainer_team doit supprimer le statut."""
        p = self._make_hurt_pokemon(status='freeze')
        self.center.heal_trainer_team(self.trainer)
        p.refresh_from_db()
        self.assertIsNone(p.status_condition)

    def test_heal_restores_pp(self):
        """heal_trainer_team doit restaurer les PP à leur maximum."""
        from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance
        p = self._make_hurt_pokemon()
        self.center.heal_trainer_team(self.trainer)
        mi = PokemonMoveInstance.objects.get(pokemon=p, move=self.move)
        self.assertEqual(mi.current_pp, self.move.pp)

    def test_heal_increments_center_counter(self):
        """heal_trainer_team doit incrémenter le compteur total_healings du centre."""
        self._make_hurt_pokemon()
        before = self.center.total_healings
        self.center.heal_trainer_team(self.trainer)
        self.center.refresh_from_db()
        self.assertEqual(self.center.total_healings, before + 1)

    def test_heal_records_visit(self):
        """heal_trainer_team doit créer un enregistrement CenterVisit."""
        from myPokemonApp.models.PokemonCenter import CenterVisit
        self._make_hurt_pokemon()
        before = CenterVisit.objects.filter(trainer=self.trainer, center=self.center).count()
        self.center.heal_trainer_team(self.trainer)
        after = CenterVisit.objects.filter(trainer=self.trainer, center=self.center).count()
        self.assertEqual(after, before + 1)

    def test_heal_deducts_cost_from_trainer(self):
        """Si healing_cost > 0, le montant doit être déduit du solde du Trainer."""
        self.center.healing_cost = 300
        self.center.save()
        self._make_hurt_pokemon()
        initial_money = self.trainer.money
        self.center.heal_trainer_team(self.trainer)
        self.trainer.refresh_from_db()
        self.assertEqual(self.trainer.money, initial_money - 300)