import bleach
from django.shortcuts import render
from .utils import *
import logging

# Create your views here.


class PokemonMoveOverView(GenericOverview):
    model = PokemonMove

    class GenericTable(tables.Table):
        name = tables.TemplateColumn('''<a href="{% url 'PokemonMoveView' record.id %}">{{ record.name }}</a>''')
        pp = tables.TemplateColumn('<span class="text-{{record.pp}}">{{record.pp| default:"Unknown"}} </span>')
        attackPower = tables.TemplateColumn('<span class="text-{{record.attackPower}}">{{record.attackPower| default:"None"}} </span>')
        accuracy = tables.TemplateColumn('<span class="text-{{record.accuracy}}">{{record.accuracy| default:"Unknown"}} </span>')
        type = tables.TemplateColumn('<span class="text-{{record.type}}">{{record.type| default:"Unknown"}} </span>')
        effect = tables.TemplateColumn('<span class="text-{{record.effect}}">{{record.effect| default:"Unknown"}} </span>')

        """ 
        ('<i class="fas {%if record.active%} fa-check-circle text-success {% else %} fa-times-circle text-danger {% endif %}"></i>')
        """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = self.GenericTable(self.get_queryset())
        table.paginate(page=self.request.GET.get("page", 1), per_page=10)

        context['table'] = table
        return context




class PokemonMoveView(generic.DeleteView):  
    template_name = "pokemonMoveDetails.html" 
    model = PokemonMove 


    def get_context_data(self, **kwargs):
        context = dict()
        
        # Custom filters
        """
        alertFilter = Q()
        searchQuery = bleach.clean(self.request.GET.get('searchQuery', ''), tags=[], attributes={})
        """
        pk = self.kwargs.pop('pk')
        Obj = PokemonMove.objects.get_or_create(pk=pk)[0]
        logging.info(f"[+] {Obj}")
        print(f"[+] {Obj}")
    
        context['Move'] = Obj
        return context    