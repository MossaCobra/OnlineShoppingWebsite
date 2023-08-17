from django import template

register = template.Library()


@register.filter(name='to_int')
def to_int(value):
    return int(value)


@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
