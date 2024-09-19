import bleach
from django.shortcuts import render
from .utils import *
import logging

# Create your views here.


class PokemonOverView(GenericOverview):
    model = Pokemon

    class GenericTable(tables.Table):
        name = tables.TemplateColumn('''<a href="{% url 'PokemonView' record.id %}">{{ record.name }}</a>''')
        level = tables.TemplateColumn('<span class="text-{{record.level}}">{{record.level| default:"Unknown"}} </span>')
        type = tables.TemplateColumn('<span class="text-{{record.type}}">{{record.type| default:"Unknown"}} </span>')
        hp = tables.TemplateColumn('<span class="text-{{record.hp}}">{{record.hp| default:"Unknown"}} </span>')
        atk = tables.TemplateColumn('<span class="text-{{record.attack}}">{{record.attack| default:"Unknown"}} </span>')
        defence = tables.TemplateColumn('<span class="text-{{record.defense}}">{{record.defense| default:"Unknown"}} </span>')
        speAtk = tables.TemplateColumn('<span class="text-{{record.specialAttack}}">{{record.specialAttack| default:"Unknown"}} </span>')
        speDef = tables.TemplateColumn('<span class="text-{{record.specialDefense}}">{{record.specialDefense| default:"Unknown"}} </span>')
        spd =  tables.TemplateColumn('<span class="text-{{record.speed}}">{{record.speed| default:"Unknown"}} </span>')
        catchRate = tables.TemplateColumn('<span class="text-{{record.catchRate}}">{{record.catchRate| default:"Unknown"}} </span>')
        baseExp = tables.TemplateColumn('<span class="text-{{record.baseExperience}}">{{record.baseExperience| default:"Unknown"}} </span>')

        """ 
        ('<i class="fas {%if record.active%} fa-check-circle text-success {% else %} fa-times-circle text-danger {% endif %}"></i>')
        """


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = self.GenericTable(self.get_queryset())


        # Custom filters
        pokemonFilter = Q()
        searchQuery = bleach.clean(self.request.GET.get('searchQuery', ''), tags=[], attributes={})

        if searchQuery:
            pokemonFilter.add(Q(name__icontains=searchQuery), Q.AND)


        paginator = Paginator(Pokemon.objects.filter(pokemonFilter).distinct().order_by("id"), 10)
        pageNumber = self.request.GET.get("page", 1)
        pageObjects = paginator.get_page(pageNumber)
        paginatedObjects = self.GenericTable(pageObjects)

        
        #table.paginate(page=self.request.GET.get("page", 1), per_page=10)

        context['table'] = paginatedObjects
        context['pageObjects'] = pageObjects
        
        return context




class PokemonView(generic.DeleteView):  
    template_name = "pokemonDetails.html" 
    model = Pokemon 


    def get_context_data(self, **kwargs):
        context = dict()
        

        pk = self.kwargs.pop('pk')
        PokemonObj = Pokemon.objects.get_or_create(pk=pk)[0]
        logging.info(f"[+] {PokemonObj}")
        print(f"[+] {PokemonObj}")
    
        context['Pokemon'] = PokemonObj
        return context    