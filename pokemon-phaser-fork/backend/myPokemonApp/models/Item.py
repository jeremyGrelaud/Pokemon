#!/usr/bin/python3
"""! @brief Item.py model — avec support TM (CT) et CS (CTs secrètes / Hidden Machine)
"""

from django.db import models


class Item(models.Model):
    """Objet utilisable (potions, balls, objets d'évolution, TM, CS, etc.)"""

    ITEM_TYPES = [
        ('potion',   'Potion'),
        ('pokeball', 'Poké Ball'),
        ('evolution','Pierre d\'évolution'),
        ('status',   'Soin de statut'),
        ('battle',   'Objet de combat'),
        ('held',     'Objet tenu'),
        ('key',      'Objet clé'),
        ('tm',       'CT (Capsule Technique)'),
        ('cs',       'CS (Capsule Secrète)'),
    ]

    name        = models.CharField(max_length=50)
    description = models.TextField()
    item_type   = models.CharField(max_length=20, choices=ITEM_TYPES)
    price       = models.IntegerField(default=0)

    # ── Effets potions ───────────────────────────────────────────────────────
    heal_amount    = models.IntegerField(default=0)   # HP restaurés
    heal_percentage= models.IntegerField(default=0)   # % HP restaurés
    cures_status   = models.BooleanField(default=False)
    specific_status= models.CharField(max_length=20, blank=True, null=True)

    # ── Poké Balls ──────────────────────────────────────────────────────────
    catch_rate_modifier = models.FloatField(default=1.0)

    # ── Évolutions ──────────────────────────────────────────────────────────
    evolves_pokemon = models.CharField(max_length=50, blank=True, null=True)

    # ── Objet tenu ──────────────────────────────────────────────────────────
    held_effect = models.CharField(max_length=100, blank=True, null=True)

    # ── TM / CS ─────────────────────────────────────────────────────────────
    # Le move que cette CT/CS enseigne.
    # NULL pour tous les autres types d'objets.
    tm_move = models.ForeignKey(
        'PokemonMove',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tm_items',
        verbose_name='Capacité enseignée',
    )
    # Numéro officiel (ex: 001 pour CT01 / CS01)
    tm_number = models.IntegerField(null=True, blank=True, verbose_name='Numéro CT/CS')

    # Les TM sont réutilisables à l'infini en Gen 9 — les CS aussi.
    # On garde is_consumable=False par défaut pour TM/CS.
    is_consumable = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "Objet"
        verbose_name_plural = "Objets"
        ordering = ['item_type', 'tm_number', 'name']

    def __str__(self):
        if self.item_type in ('tm', 'cs') and self.tm_move:
            prefix = 'CT' if self.item_type == 'tm' else 'CS'
            num    = str(self.tm_number).zfill(3) if self.tm_number else '???'
            return f"{prefix}{num} {self.tm_move.name}"
        return self.name

    # ────────────────────────────────────────────────────────────────────────
    # Méthode principale d'utilisation
    # ────────────────────────────────────────────────────────────────────────

    def use_on_pokemon(self, pokemon):
        """Utilise l'objet sur un Pokémon. Retourne un message résultat."""
        poke_name = pokemon.nickname or pokemon.species.name

        if self.item_type == 'potion':
            healed = min(self.heal_amount, pokemon.max_hp - pokemon.current_hp)
            pokemon.current_hp += healed
            pokemon.save()
            return {'success': True, 'message': f"{poke_name} a récupéré {healed} HP!"}

        elif self.item_type == 'status' and self.cures_status:
            if self.specific_status:
                if pokemon.status == self.specific_status:
                    pokemon.status = None
                    pokemon.save()
                    return {'success': True, 'message': f"{poke_name} est guéri de {self.specific_status}!"}
                return {'success': False, 'message': f"{poke_name} n'est pas affecté par {self.specific_status}."}
            else:
                old_status = pokemon.status
                pokemon.status = None
                pokemon.save()
                return {'success': True, 'message': f"{poke_name} est guéri de {old_status}!"}

        elif self.item_type == 'evolution':
            result = pokemon.check_stone_evolution(self)
            return {'success': True, 'message': result}

        elif self.item_type in ('tm', 'cs'):
            return self.teach_move_to_pokemon(pokemon)

        return {'success': False, 'message': "Aucun effet."}

    # ────────────────────────────────────────────────────────────────────────
    # Logique TM / CS
    # ────────────────────────────────────────────────────────────────────────

    def can_teach(self, playable_pokemon):
        """
        Vérifie si cette CT/CS peut être enseignée à ce PlayablePokemon.

        Règles :
        1. L'item doit être de type tm ou cs et posséder un tm_move.
        2. Le Pokémon (species) doit avoir une entrée PokemonLearnableMove
           avec learn_method='tm' pour ce move (restrictions Gen 9).
        3. Le Pokémon ne doit pas déjà connaître le move.
        """
        if self.item_type not in ('tm', 'cs') or not self.tm_move:
            return False, "Cet objet n'est pas une CT/CS valide."

        from .PokemonLearnableMove import PokemonLearnableMove

        # Vérification compatibilité Gen 9
        can_learn = PokemonLearnableMove.objects.filter(
            pokemon=playable_pokemon.species,
            move=self.tm_move,
            learn_method='tm',
        ).exists()

        print(can_learn)

        if not can_learn:
            poke_name = playable_pokemon.nickname or playable_pokemon.species.name
            return False, f"{poke_name} ne peut pas apprendre {self.tm_move.name} par CT/CS."

        # Déjà dans la liste des moves ?
        already_knows = playable_pokemon.moves.filter(id=self.tm_move.id).exists()
        if already_knows:
            poke_name = playable_pokemon.nickname or playable_pokemon.species.name
            return False, f"{poke_name} connaît déjà {self.tm_move.name}."

        return True, "OK"

    def teach_move_to_pokemon(self, playable_pokemon, replace_move=None):
        """
        Enseigne le move de la CT/CS au PlayablePokemon.

        - replace_move : instance de PokemonMove à remplacer si l'équipe est pleine (4 moves).
        - Les CT/CS sont réutilisables (Gen 9), donc is_consumable doit être False.
        """
        poke_name = playable_pokemon.nickname or playable_pokemon.species.name

        can, reason = self.can_teach(playable_pokemon)
        if not can:
            return {'success': False, 'message': reason}

        # Détermine la source selon le type de l'objet (CT ou CS)
        source = 'hm' if self.item_type == 'cs' else 'tm'
        success = playable_pokemon.learn_move(self.tm_move, replace_move=replace_move, source=source)

        if success:
            return {
                'success': True,
                'message': f"{poke_name} a appris {self.tm_move.name}!",
                'move': self.tm_move,
            }
        else:
            return {
                'success': False,
                'message': (
                    f"{poke_name} connaît déjà 4 capacités. "
                    "Choisissez une capacité à oublier."
                ),
                'needs_replace': True,
                'move': self.tm_move,
            }