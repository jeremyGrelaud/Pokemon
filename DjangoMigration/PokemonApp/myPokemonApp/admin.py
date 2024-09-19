from django.contrib import admin
from myPokemonApp.models import *

# Register your models here.

@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = ["name","level","type","hp","attack", "defense", "specialAttack", "specialDefense", "speed", "catchRate", "baseExperience"]
    list_display_links = ["name"]
    readonly_fields = ["name"]
    search_fields = ["name"]

#admin.site.register(Pokemon)
admin.site.register(PokemonMove)
admin.site.register(PokemonType)