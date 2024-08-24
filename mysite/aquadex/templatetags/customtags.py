from django import template
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.utils.text import slugify
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def IncludeHeatmap(scientificName):
    slugifiedName = slugify(scientificName)
    templateName = f'aquadex/heatmap_{slugifiedName}.html'
    try:
        return mark_safe(render_to_string(templateName))
    except TemplateDoesNotExist:
        return mark_safe('<p>No heatmap available for this species.</p>')

@register.filter
def GetHeatmap(scientific_name):
    return IncludeHeatmap(scientific_name)
