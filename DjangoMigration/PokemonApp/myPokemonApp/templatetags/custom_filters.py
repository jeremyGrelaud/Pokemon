from django import template
from django.utils import timezone
from datetime import timedelta
import re, bleach
from django.template.defaultfilters import date as lazy_date
from django.template.loader import render_to_string

from django_tables2.templatetags.django_tables2 import Node
from django.template.loader import get_template, select_template
import django_tables2 as tables

register = template.Library()


@register.filter(name="removeFromURL")
def removeFromURL(fullUrlPath, argToRemove):
    """Reads full URL Path and remove 'argToRemove' from path
    ex: toto.com/?vendor=tata -> toto.com/?"""
    # Chunk : /cve/?vendor=microsoft&product=windows&searchQuery=
    
    # 1. Clean url 
    fullUrlPath = bleach.clean(fullUrlPath, tags=[], attributes={})

    # 2. Retrieve args
    urlPath, *urlArgs = fullUrlPath.split("?")

    # 3. If multiple '?', it is unusual access -> return current page
    if len(urlArgs)!=1:
        return fullUrlPath
    
    # 4. Iterate througt args
    # Chunk vendor=microsoft
    newUrlArgs = []
    for arg in urlArgs[0].split("&amp;"):
        key, *value = arg.split("=")

        # 5. If multiple '=', it is unusual access -> return current page
        if len(value) != 1: 
            return fullUrlPath
        
        # 6. If not to remove, then add to arg paths
        if key!=argToRemove:
            if key=="page":
                newUrlArgs.append("page=1") 
            else:
                newUrlArgs.append(arg) 
    
    return f"{urlPath}?{'&'.join(newUrlArgs)}"


@register.tag
def optimized_render_table(parser, token):
    bits = token.split_contents()
    bits.pop(0)

    table = parser.compile_filter(bits.pop(0))
    template = parser.compile_filter(bits.pop(0)) if bits else None
    pageObjects = parser.compile_filter(bits.pop(0)) if bits else None

    return OptimizedRenderTableNode(table, template, pageObjects)

class OptimizedRenderTableNode(Node):
    """
    parameters:
        table (~.Table): the table to render
        template (str or list): Name[s] of template to render
    """

    def __init__(self, table, template_name=None, pageObjects=None):
        super().__init__()
        self.table = table
        self.template_name = template_name
        self.pageObjects = pageObjects

    def render(self, context):
        table = self.table.resolve(context)
        pageObjects = self.pageObjects.resolve(context)

        request = context.get("request")

        if isinstance(table, tables.Table):
            pass
        elif hasattr(table, "model"):
            queryset = table

            table = tables.table_factory(model=queryset.model)(queryset, request=request)
        else:
            raise ValueError(f"Expected table or queryset, not {type(table).__name__}")

        if self.template_name:
            template_name = self.template_name.resolve(context)
        else:
            template_name = table.template_name

        if isinstance(template_name, str):
            template = get_template(template_name)
        else:
            # assume some iterable was given
            template = select_template(template_name)

        try:
            table.context = context
            table.before_render(request)

            return template.render(context={"table": table, "pageObjects" : pageObjects}, request=request)
        finally:
            del table.context


@register.filter
def mul(value, arg):
    """Multiplie value par arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
    
@register.filter
def lower(value):
    """Convertit une chaîne de caractères en minuscules."""
    try:
        return value.lower()
    except AttributeError:
        return value
    
@register.filter(name="gymleaderescape")
def gymleaderescape(value):
    """Supprime les espaces et les points d'une chaîne de caractères."""
    if not isinstance(value, str):
        return value
    return value.replace(" ", "").replace(".", "")


@register.filter(name='floatformat')
def floatformat(value, decimal_places=0):
    """Formate la valeur en float avec le nombre de décimales spécifié."""
    try:
        return f"{float(value):.{decimal_places}f}"
    except (ValueError, TypeError):
        return value
    
@register.filter(name='is_available_for_trainer')
def is_available_for_trainer(item, trainer):
    return item.is_available_for_trainer(trainer)