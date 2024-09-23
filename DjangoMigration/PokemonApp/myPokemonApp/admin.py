from django.contrib import admin
from myPokemonApp.models import *

# Register your models here.

@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = ["name","level","type","hp","attack", "defense", "specialAttack", "specialDefense", "speed", "catchRate", "baseExperience"]
    list_display_links = ["name"]
    readonly_fields = ["name"]
    search_fields = ["name"]
@admin.register(PokemonLearnableMove)
class PokemonLearnableMoveAdmin(admin.ModelAdmin):
    list_display = ["pokemon_name", "move_name", "LearnableAtLevel"]
    readonly_fields = ["pokemon", "move", "LearnableAtLevel"]
    search_fields = ["pokemon", "move", "LearnableAtLevel"]

    def pokemon_name(self, obj):
        return obj.pokemon.name
    pokemon_name.short_description = 'Pokemon Name'

    def move_name(self, obj):
        return obj.move.name
    move_name.short_description = 'Move Name'


admin.site.register(PokemonMove)
admin.site.register(PokemonType)
admin.site.register(Trainer)
admin.site.register(PlayablePokemon)