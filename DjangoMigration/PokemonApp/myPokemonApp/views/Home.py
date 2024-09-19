from django.shortcuts import render
from .utils import *

# Create your views here.
class Home(generic.TemplateView):  
    template_name = "home.html"  