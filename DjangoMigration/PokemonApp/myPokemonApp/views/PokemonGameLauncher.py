from django.shortcuts import render
from .utils import *

# Create your views here.
class PokemonGameLauncherView(generic.TemplateView):  
    template_name = "GameScreen.html"  
