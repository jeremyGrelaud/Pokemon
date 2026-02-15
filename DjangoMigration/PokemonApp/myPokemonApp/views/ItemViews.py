#!/usr/bin/python3
"""
Views Django pour l'application Pokémon Gen 1
Adapté aux nouveaux modèles
"""

from django.views import generic

from ..models import *


# ============================================================================
# OBJETS
# ============================================================================

class ItemListView(generic.ListView):
    """Liste des objets"""
    model = Item
    template_name = "items/item_list.html"
    context_object_name = 'items'
    
    def get_queryset(self):
        item_type = self.request.GET.get('itemType', '')
        queryset = Item.objects.all().order_by('item_type', 'price')
        
        if item_type:
            queryset = queryset.filter(item_type=item_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_types'] = Item.ITEM_TYPES
        context['selected_type'] = self.request.GET.get('itemType', '')
        return context

