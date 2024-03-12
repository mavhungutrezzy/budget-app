from django import template
import re


register = template.Library()


@register.filter(name='money_format')
def money_format(value):
    return '${:,.0f}'.format(value)


@register.filter
def class_name_display(value):
    value_class_name = value.__class__.__name__
    return ' '.join(re.sub('([a-z])([A-Z])', r'\1 \2', value_class_name).split())
