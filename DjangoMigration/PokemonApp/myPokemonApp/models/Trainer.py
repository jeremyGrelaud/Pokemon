#!/usr/bin/python3
"""! @brief Pokemon.py model
"""

from django.db import models
from .Item import Item
from .PokemonMove import PokemonMove
from .PokemonType import PokemonType
class Trainer(models.Model):
    """Dresseur de base"""
    
    TRAINER_TYPES = [
        ('player', 'Joueur'),
        ('rival', 'Rival'),
        ('gym_leader', 'Champion d\'Arène'),
        ('elite_four', 'Conseil des 4'),
        ('champion', 'Maître'),
        ('trainer', 'Dresseur'),
        ('wild', 'Sauvage'),
    ]
    
    username = models.CharField(max_length=50)
    trainer_type = models.CharField(max_length=20, choices=TRAINER_TYPES)
    
    # Inventaire
    money = models.IntegerField(default=3000)
    
    # Badges
    badges = models.IntegerField(default=0)
    
    # Position dans le jeu (pour les NPCs)
    location = models.CharField(max_length=100, blank=True, null=True)
    
    # Pour les NPCs
    is_defeated = models.BooleanField(default=False)
    can_rebattle = models.BooleanField(default=False)
    
    # Dialogue
    intro_text = models.TextField(blank=True, null=True)
    defeat_text = models.TextField(blank=True, null=True)
    victory_text = models.TextField(blank=True, null=True)

    is_npc = models.BooleanField(default=False)
    is_battle_required = models.BooleanField(
        default=False,
        help_text="Ce dresseur bloque le passage et doit être battu avant de quitter la zone."
    )
    npc_class = models.CharField(max_length=50, blank=True)  # "Gamin", "Scout", etc.
    sprite_name = models.CharField(max_length=100, blank=True)

    
    class Meta:
        verbose_name = "Dresseur"
        verbose_name_plural = "Dresseurs"
    
    def __str__(self):
        return f"{self.username} ({self.get_trainer_type_display()})"
    
    def has_available_pokemon(self):
        """Vérifie si le dresseur a des Pokémon non KO"""
        return self.pokemon_team.filter(current_hp__gt=0).exists()
    
    def get_reward(self):
        """Calcule la récompense à donner en cas de défaite"""
        if self.trainer_type == 'gym_leader':
            return 1000 + (self.badges * 500)
        elif self.trainer_type == 'elite_four':
            return 5000
        elif self.trainer_type == 'champion':
            return 10000
        else:
            highest_level = self.pokemon_team.aggregate(
                models.Max('level')
            )['level__max'] or 1
            return highest_level * 100

    def get_full_title(self):
        if self.npc_class:
            return f"{self.npc_class} {self.username}"
        return self.username

    # ------------------------------------------------------------------
    # Statut de defaite per-joueur
    # ------------------------------------------------------------------

    def is_defeated_by_player(self, player_trainer) -> bool:
        """
        Retourne True si CE joueur a deja vaincu ce Trainer NPC.

        La source de verite est GameSave.defeated_trainers (liste d IDs JSON),
        qui est strictement per-joueur. On ne se base PAS sur Trainer.is_defeated
        qui est un booleen global inutilisable en contexte multi-joueur.

        Performance : dans les vues qui iterent sur N trainers, preferer
        get_defeated_trainer_ids(player_trainer) pour recuperer le set
        d IDs en une seule requete, puis tester npc.id in defeated_ids.
        """
        from .GameSave import GameSave
        save = GameSave.objects.filter(trainer=player_trainer, is_active=True).first()
        if save is None:
            return False
        return self.id in save.defeated_trainers

    # ------------------------------------------------------------------
    # Helpers badges
    # ------------------------------------------------------------------

    def has_badge(self, badge_order: int) -> bool:
        """Retourne True si le trainer a obtenu le badge d'ordre badge_order."""
        return self.badges >= badge_order

    # ------------------------------------------------------------------
    # Helpers équipe / PC — évitent de réécrire le filtre partout
    # ------------------------------------------------------------------

    @property
    def party(self):
        """QuerySet des Pokémon actifs, triés par position."""
        return self.pokemon_team.filter(is_in_party=True).order_by('party_position')

    @property
    def pc(self):
        """QuerySet des Pokémon en réserve (PC)."""
        return self.pokemon_team.filter(is_in_party=False)

    @property
    def party_count(self) -> int:
        """Nombre de Pokémon dans l'équipe active."""
        return self.pokemon_team.filter(is_in_party=True).count()

    @property
    def pc_count(self) -> int:
        """Nombre de Pokémon dans le PC."""
        return self.pokemon_team.filter(is_in_party=False).count()

    # ------------------------------------------------------------------
    # Helpers argent — garantissent un .save() systématique
    # ------------------------------------------------------------------

    def spend_money(self, amount: int) -> bool:
        """Dépense amount₽. Retourne False si fonds insuffisants."""
        if self.money < amount:
            return False
        self.money -= amount
        self.save(update_fields=['money'])
        return True

    def earn_money(self, amount: int) -> None:
        """Crédite amount₽ sur le solde du trainer."""
        self.money += amount
        self.save(update_fields=['money'])

class GymLeader(models.Model):
    """Champion d'Arène avec informations spécifiques"""
    
    trainer = models.OneToOneField(
        Trainer,
        on_delete=models.CASCADE,
        related_name='gym_info'
    )
    
    gym_name = models.CharField(max_length=50)
    gym_city = models.CharField(max_length=50)
    badge_name = models.CharField(max_length=50)
    specialty_type = models.ForeignKey(
        PokemonType,
        on_delete=models.CASCADE,
        related_name='gym_leaders'
    )
    
    badge_order = models.IntegerField(unique=True)  # 1-8
    
    # TM donné en récompense
    tm_reward = models.ForeignKey(
        PokemonMove,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "Champion d'Arène"
        verbose_name_plural = "Champions d'Arène"
        ordering = ['badge_order']
    
    def __str__(self):
        return f"{self.trainer.username} - {self.gym_name} ({self.gym_city})"
    
    def isChallengableByPlayer(self, player_trainer) -> bool:
        """
        Retourne True si le joueur peut defier cet Arena Leader.
        - Utilise is_defeated_by_player() (per-joueur) au lieu de trainer.is_defeated (global).
        - Verifie que le joueur possede les badges requis (badge_order - 1).
        """
        if self.trainer.is_defeated_by_player(player_trainer):
            return False
        required_badges = self.badge_order - 1
        return player_trainer.badges >= required_badges



class TrainerInventory(models.Model):
    """Inventaire d'un dresseur"""
    
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        related_name='inventory'
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        unique_together = ['trainer', 'item']
        verbose_name = "Inventaire"
    
    def __str__(self):
        return f"{self.trainer.username} - {self.item.name} x{self.quantity}"


# ─────────────────────────────────────────────────────────────────────────────
# RIVAL — Modèle par template + instance per-player
# ─────────────────────────────────────────────────────────────────────────────

class RivalTemplate(models.Model):
    """
    Template statique d'un combat de rival.

    Peuplé une seule fois au lancement du serveur (init script), indépendamment
    des joueurs. Stocke la définition du combat (quest_id, combat_order, starter
    requis du rival, dialogues) mais PAS de Trainer ni de Pokémon — ceux-ci
    sont créés à la demande par PlayerRival.spawn_for_player().
    """

    STARTER_CHOICES = [
        ('Bulbasaur',  'Bulbizarre'),
        ('Charmander', 'Salamèche'),
        ('Squirtle',   'Carapuce'),
        ('any',        'Indépendant du starter'),
    ]

    # Identifiant stable (= quest_id associé).
    # Pas unique seul : 3 templates existent par quest_id (un par starter joueur).
    # La contrainte d'unicité est (quest_id, player_starter_match) via Meta.
    quest_id     = models.CharField(max_length=60)
    combat_order = models.IntegerField(default=0, help_text="Ordre chronologique (1=Bourg Palette, 2=Route 22…)")

    # Quel starter le rival utilise pour CE combat et QUEL starter joueur
    # déclenche cette version. 'any' = valable pour tout starter joueur.
    rival_starter        = models.CharField(max_length=20, choices=STARTER_CHOICES, default='any')
    player_starter_match = models.CharField(
        max_length=20, choices=STARTER_CHOICES, default='any',
        help_text="Starter joueur qui active cette version. 'any' = toutes versions."
    )

    # Dialogues
    intro_text    = models.TextField(blank=True)
    defeat_text   = models.TextField(blank=True)
    victory_text  = models.TextField(blank=True)
    pre_battle_text  = models.TextField(blank=True)
    post_battle_text = models.TextField(blank=True)

    # Argent gagné par le joueur
    money_reward = models.IntegerField(default=175)

    # Données de l'équipe (JSON) :
    # [{"species": "Charmander", "level": 5, "moves": ["Scratch","Growl"],
    #   "fixed_ivs": {"iv_hp":10,...}, "fixed_nature": "Hardy"}, ...]
    team_data = models.JSONField(default=list)

    class Meta:
        verbose_name = 'Template Rival'
        verbose_name_plural = 'Templates Rival'
        ordering = ['combat_order', 'player_starter_match']
        # 3 templates peuvent exister par quest_id (un par starter joueur).
        # La combinaison (quest_id, player_starter_match) doit être unique.
        unique_together = [('quest_id', 'player_starter_match')]

    def __str__(self):
        return f"[Template] {self.quest_id} (rival={self.rival_starter}, vs={self.player_starter_match})"


class PlayerRival(models.Model):
    """
    Instance de combat rival pour UN joueur spécifique.

    Créée dans choose_starter_view() dès que le joueur choisit son starter :
    on itère sur tous les RivalTemplate dont player_starter_match correspond
    et on matérialise un Trainer + son équipe pour ce joueur.

    Ainsi chaque joueur possède ses propres Trainer NPC rival, isolés
    des autres joueurs, avec des noms uniques (ex: "Rival_alice_pallet").
    """

    player   = models.ForeignKey(
        Trainer, on_delete=models.CASCADE,
        related_name='rival_instances',
        help_text="Trainer joueur propriétaire de cette instance."
    )
    template = models.ForeignKey(
        RivalTemplate, on_delete=models.CASCADE,
        related_name='player_instances',
    )
    trainer  = models.OneToOneField(
        Trainer, on_delete=models.CASCADE,
        related_name='rival_info',
        null=True, blank=True,
        help_text="Trainer NPC matérialisé pour ce joueur (créé à spawn_for_player)."
    )

    class Meta:
        unique_together = ['player', 'template']
        verbose_name = 'Instance Rival (joueur)'
        verbose_name_plural = 'Instances Rival (joueur)'

    def __str__(self):
        return f"Rival de {self.player.username} — {self.template.quest_id}"

    # ------------------------------------------------------------------
    # Méthode de spawn : crée le Trainer NPC + son équipe
    # ------------------------------------------------------------------

    def spawn_for_player(self):
        """
        Matérialise un Trainer NPC unique pour ce joueur depuis le template.

        - Nom unique : "Rival_{player.username}_{quest_id}" (tronqué à 50 chars)
        - IVs/nature fixes tirés du template (team_data)
        - Idempotent : ne recrée pas si self.trainer existe déjà

        Retourne le Trainer NPC créé (ou existant).
        """
        if self.trainer_id:
            return self.trainer  # déjà matérialisé

        from myPokemonApp.models import Pokemon, PokemonMove
        from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance
        import random

        tmpl = self.template

        # ── Nom unique par joueur ─────────────────────────────────────────────
        raw_name = f"Rival_{self.player.username}_{tmpl.quest_id}"
        npc_name = raw_name[:50]

        npc = Trainer.objects.create(
            username=npc_name,
            trainer_type='rival',
            location='',          # sera mis à jour par RivalEncounter
            is_npc=True,
            npc_class='Rival',
            can_rebattle=False,
            money=tmpl.money_reward,
            intro_text=tmpl.intro_text,
            defeat_text=tmpl.defeat_text,
            victory_text=tmpl.victory_text,
        )

        # ── Équipe ────────────────────────────────────────────────────────────
        NATURE_MODIFIERS = {
            'Lonely':('attack','defense'),'Brave':('attack','speed'),
            'Adamant':('attack','special_attack'),'Naughty':('attack','special_defense'),
            'Bold':('defense','attack'),'Relaxed':('defense','speed'),
            'Impish':('defense','special_attack'),'Lax':('defense','special_defense'),
            'Timid':('speed','attack'),'Hasty':('speed','defense'),
            'Jolly':('speed','special_attack'),'Naive':('speed','special_defense'),
            'Modest':('special_attack','attack'),'Mild':('special_attack','defense'),
            'Quiet':('special_attack','speed'),'Rash':('special_attack','special_defense'),
            'Calm':('special_defense','attack'),'Gentle':('special_defense','defense'),
            'Sassy':('special_defense','speed'),'Careful':('special_defense','special_attack'),
        }
        NEUTRAL_NATURES = {
            'Hardy','Docile','Bashful','Quirky','Serious'
        }
        ALL_NATURES = list(NATURE_MODIFIERS.keys()) + list(NEUTRAL_NATURES)

        from myPokemonApp.models import PlayablePokemon

        for i, pdata in enumerate(tmpl.team_data, 1):
            try:
                species = Pokemon.objects.get(name=pdata['species'])
            except Pokemon.DoesNotExist:
                continue

            # IVs : fixed_ivs du template ou aléatoire 0-20
            raw_ivs = pdata.get('fixed_ivs') or {
                stat: random.randint(0, 20)
                for stat in ('iv_hp','iv_attack','iv_defense',
                             'iv_special_attack','iv_special_defense','iv_speed')
            }
            nature = pdata.get('fixed_nature') or random.choice(ALL_NATURES)

            pokemon = PlayablePokemon(
                species=species,
                trainer=npc,
                level=pdata.get('level', 5),
                original_trainer=npc_name,
                is_in_party=True,
                party_position=i,
                nature=nature,
                **raw_ivs,
            )
            pokemon._skip_learn_moves = True   # évite learn_initial_moves (bug corrigé)
            pokemon.calculate_stats()
            pokemon.current_hp = pokemon.max_hp
            pokemon.save()

            # Moves
            seen = set()
            for move_name in pdata.get('moves', []):
                try:
                    move = PokemonMove.objects.get(name=move_name)
                    if move.id not in seen:
                        seen.add(move.id)
                        PokemonMoveInstance.objects.get_or_create(
                            pokemon=pokemon, move=move,
                            defaults={'current_pp': move.pp}
                        )
                except PokemonMove.DoesNotExist:
                    pass

        # ── Lier et persister ─────────────────────────────────────────────────
        self.trainer = npc
        self.save(update_fields=['trainer'])
        return npc