"""
Migration de données : peuple les champs ev_yield_* sur chaque Pokémon.

Source : _EV_YIELDS extrait de battle_service.py (FRLG / Bulbapedia, Gen 3+).
Tout Pokémon absent de cette table garde ses valeurs à 0 (défaut sûr).
"""

from django.db import migrations


_EV_YIELDS = {
    'Bulbasaur':   [('ev_yield_special_attack', 1)],
    'Ivysaur':     [('ev_yield_special_attack', 1), ('ev_yield_special_defense', 1)],
    'Venusaur':    [('ev_yield_special_attack', 2), ('ev_yield_special_defense', 1)],
    'Charmander':  [('ev_yield_speed', 1)],
    'Charmeleon':  [('ev_yield_speed', 1), ('ev_yield_attack', 1)],
    'Charizard':   [('ev_yield_speed', 3)],
    'Squirtle':    [('ev_yield_defense', 1)],
    'Wartortle':   [('ev_yield_defense', 1), ('ev_yield_special_defense', 1)],
    'Blastoise':   [('ev_yield_defense', 1), ('ev_yield_special_defense', 2)],
    'Caterpie':    [('ev_yield_hp', 1)],
    'Metapod':     [('ev_yield_defense', 1)],
    'Butterfree':  [('ev_yield_special_attack', 2), ('ev_yield_special_defense', 1)],
    'Weedle':      [('ev_yield_speed', 1)],
    'Kakuna':      [('ev_yield_defense', 1)],
    'Beedrill':    [('ev_yield_attack', 2), ('ev_yield_speed', 1)],
    'Pidgey':      [('ev_yield_speed', 1)],
    'Pidgeotto':   [('ev_yield_speed', 1), ('ev_yield_attack', 1)],
    'Pidgeot':     [('ev_yield_speed', 3)],
    'Rattata':     [('ev_yield_speed', 1)],
    'Raticate':    [('ev_yield_speed', 2)],
    'Spearow':     [('ev_yield_speed', 1)],
    'Fearow':      [('ev_yield_speed', 2)],
    'Ekans':       [('ev_yield_attack', 1)],
    'Arbok':       [('ev_yield_attack', 2)],
    'Pikachu':     [('ev_yield_speed', 2)],
    'Raichu':      [('ev_yield_speed', 3)],
    'Sandshrew':   [('ev_yield_defense', 1)],
    'Sandslash':   [('ev_yield_defense', 2)],
    'Nidoran♀':   [('ev_yield_hp', 1)],
    'Nidorina':    [('ev_yield_hp', 2)],
    'Nidoqueen':   [('ev_yield_hp', 3)],
    'Nidoran♂':   [('ev_yield_attack', 1)],
    'Nidorino':    [('ev_yield_attack', 2)],
    'Nidoking':    [('ev_yield_attack', 3)],
    'Clefairy':    [('ev_yield_hp', 2)],
    'Clefable':    [('ev_yield_hp', 3)],
    'Vulpix':      [('ev_yield_special_attack', 1)],
    'Ninetales':   [('ev_yield_special_attack', 2), ('ev_yield_speed', 1)],
    'Jigglypuff':  [('ev_yield_hp', 2)],
    'Wigglytuff':  [('ev_yield_hp', 3)],
    'Zubat':       [('ev_yield_speed', 1)],
    'Golbat':      [('ev_yield_speed', 2)],
    'Oddish':      [('ev_yield_special_attack', 1)],
    'Gloom':       [('ev_yield_special_attack', 1), ('ev_yield_special_defense', 1)],
    'Vileplume':   [('ev_yield_special_attack', 2), ('ev_yield_special_defense', 1)],
    'Paras':       [('ev_yield_attack', 1)],
    'Parasect':    [('ev_yield_attack', 2), ('ev_yield_defense', 1)],
    'Venonat':     [('ev_yield_special_defense', 1)],
    'Venomoth':    [('ev_yield_special_attack', 2), ('ev_yield_special_defense', 1)],
    'Diglett':     [('ev_yield_speed', 1)],
    'Dugtrio':     [('ev_yield_speed', 2)],
    'Meowth':      [('ev_yield_speed', 1)],
    'Persian':     [('ev_yield_speed', 2)],
    'Psyduck':     [('ev_yield_special_attack', 1)],
    'Golduck':     [('ev_yield_special_attack', 2)],
    'Mankey':      [('ev_yield_attack', 1)],
    'Primeape':    [('ev_yield_attack', 2)],
    'Growlithe':   [('ev_yield_attack', 1)],
    'Arcanine':    [('ev_yield_attack', 2), ('ev_yield_speed', 1)],
    'Poliwag':     [('ev_yield_speed', 1)],
    'Poliwhirl':   [('ev_yield_speed', 2)],
    'Poliwrath':   [('ev_yield_defense', 1), ('ev_yield_special_defense', 1)],
    'Abra':        [('ev_yield_special_attack', 1)],
    'Kadabra':     [('ev_yield_special_attack', 2)],
    'Alakazam':    [('ev_yield_special_attack', 3)],
    'Machop':      [('ev_yield_attack', 1)],
    'Machoke':     [('ev_yield_attack', 2)],
    'Machamp':     [('ev_yield_attack', 3)],
    'Bellsprout':  [('ev_yield_attack', 1)],
    'Weepinbell':  [('ev_yield_attack', 2)],
    'Victreebel':  [('ev_yield_attack', 3)],
    'Tentacool':   [('ev_yield_special_defense', 1)],
    'Tentacruel':  [('ev_yield_special_defense', 2)],
    'Geodude':     [('ev_yield_defense', 1)],
    'Graveler':    [('ev_yield_defense', 2)],
    'Golem':       [('ev_yield_defense', 3)],
    'Ponyta':      [('ev_yield_speed', 1)],
    'Rapidash':    [('ev_yield_speed', 2)],
    'Slowpoke':    [('ev_yield_hp', 1)],
    'Slowbro':     [('ev_yield_defense', 1), ('ev_yield_special_attack', 1)],
    'Magnemite':   [('ev_yield_special_attack', 1)],
    'Magneton':    [('ev_yield_special_attack', 2)],
    'Doduo':       [('ev_yield_attack', 1)],
    'Dodrio':      [('ev_yield_attack', 2)],
    'Seel':        [('ev_yield_special_defense', 1)],
    'Dewgong':     [('ev_yield_special_defense', 2)],
    'Grimer':      [('ev_yield_hp', 1)],
    'Muk':         [('ev_yield_hp', 2)],
    'Shellder':    [('ev_yield_defense', 1)],
    'Cloyster':    [('ev_yield_defense', 2)],
    'Gastly':      [('ev_yield_special_attack', 1)],
    'Haunter':     [('ev_yield_special_attack', 2)],
    'Gengar':      [('ev_yield_special_attack', 3)],
    'Onix':        [('ev_yield_defense', 1)],
    'Drowzee':     [('ev_yield_special_defense', 1)],
    'Hypno':       [('ev_yield_special_defense', 2)],
    'Krabby':      [('ev_yield_attack', 1)],
    'Kingler':     [('ev_yield_attack', 2)],
    'Voltorb':     [('ev_yield_speed', 1)],
    'Electrode':   [('ev_yield_speed', 2)],
    'Exeggcute':   [('ev_yield_special_attack', 1)],
    'Exeggutor':   [('ev_yield_special_attack', 2)],
    'Cubone':      [('ev_yield_defense', 1)],
    'Marowak':     [('ev_yield_defense', 2)],
    'Hitmonlee':   [('ev_yield_attack', 2)],
    'Hitmonchan':  [('ev_yield_special_defense', 2)],
    'Lickitung':   [('ev_yield_hp', 1)],
    'Koffing':     [('ev_yield_defense', 1)],
    'Weezing':     [('ev_yield_defense', 2)],
    'Rhyhorn':     [('ev_yield_defense', 1)],
    'Rhydon':      [('ev_yield_attack', 2)],
    'Chansey':     [('ev_yield_hp', 2)],
    'Tangela':     [('ev_yield_defense', 1)],
    'Kangaskhan':  [('ev_yield_hp', 2)],
    'Horsea':      [('ev_yield_special_attack', 1)],
    'Seadra':      [('ev_yield_special_attack', 2)],
    'Goldeen':     [('ev_yield_attack', 1)],
    'Seaking':     [('ev_yield_attack', 2)],
    'Staryu':      [('ev_yield_speed', 1)],
    'Starmie':     [('ev_yield_speed', 2)],
    'Mr. Mime':    [('ev_yield_special_defense', 2)],
    'Scyther':     [('ev_yield_attack', 1), ('ev_yield_speed', 1)],
    'Jynx':        [('ev_yield_special_attack', 2)],
    'Electabuzz':  [('ev_yield_special_attack', 2)],
    'Magmar':      [('ev_yield_special_attack', 2)],
    'Pinsir':      [('ev_yield_attack', 2)],
    'Tauros':      [('ev_yield_attack', 1), ('ev_yield_speed', 1)],
    'Magikarp':    [('ev_yield_speed', 1)],
    'Gyarados':    [('ev_yield_attack', 2)],
    'Lapras':      [('ev_yield_hp', 2)],
    'Ditto':       [('ev_yield_hp', 1)],
    'Eevee':       [('ev_yield_hp', 1)],
    'Vaporeon':    [('ev_yield_hp', 2)],
    'Jolteon':     [('ev_yield_speed', 2)],
    'Flareon':     [('ev_yield_attack', 2)],
    'Porygon':     [('ev_yield_special_attack', 1)],
    'Omanyte':     [('ev_yield_defense', 1)],
    'Omastar':     [('ev_yield_defense', 1), ('ev_yield_special_attack', 1)],
    'Kabuto':      [('ev_yield_defense', 1)],
    'Kabutops':    [('ev_yield_attack', 2)],
    'Aerodactyl':  [('ev_yield_speed', 2)],
    'Snorlax':     [('ev_yield_hp', 2)],
    'Articuno':    [('ev_yield_special_defense', 3)],
    'Zapdos':      [('ev_yield_special_attack', 3)],
    'Moltres':     [('ev_yield_special_attack', 3)],
    'Dratini':     [('ev_yield_attack', 1)],
    'Dragonair':   [('ev_yield_attack', 2)],
    'Dragonite':   [('ev_yield_attack', 3)],
    'Mewtwo':      [('ev_yield_special_attack', 3)],
    'Mew':         [('ev_yield_hp', 3)],
}


def populate_ev_yields(apps, schema_editor):
    Pokemon = apps.get_model('myPokemonApp', 'Pokemon')
    to_update = []

    for pokemon in Pokemon.objects.filter(name__in=_EV_YIELDS.keys()):
        yields = _EV_YIELDS[pokemon.name]
        # Reset à 0 avant de remplir (idempotent)
        pokemon.ev_yield_hp              = 0
        pokemon.ev_yield_attack          = 0
        pokemon.ev_yield_defense         = 0
        pokemon.ev_yield_special_attack  = 0
        pokemon.ev_yield_special_defense = 0
        pokemon.ev_yield_speed           = 0
        for field, amount in yields:
            setattr(pokemon, field, amount)
        to_update.append(pokemon)

    if to_update:
        Pokemon.objects.bulk_update(
            to_update,
            fields=[
                'ev_yield_hp', 'ev_yield_attack', 'ev_yield_defense',
                'ev_yield_special_attack', 'ev_yield_special_defense', 'ev_yield_speed',
            ]
        )


def reverse_ev_yields(apps, schema_editor):
    """Remet tous les EV yields à 0 (reverse propre)."""
    Pokemon = apps.get_model('myPokemonApp', 'Pokemon')
    Pokemon.objects.all().update(
        ev_yield_hp=0, ev_yield_attack=0, ev_yield_defense=0,
        ev_yield_special_attack=0, ev_yield_special_defense=0, ev_yield_speed=0,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('myPokemonApp', '0011_pokemon_ev_yield_attack_pokemon_ev_yield_defense_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_ev_yields, reverse_code=reverse_ev_yields),
    ]