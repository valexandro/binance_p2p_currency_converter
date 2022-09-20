from django import template

register = template.Library()


@register.filter
def divide(value, arg):
    """Divide value bu arg."""
    try:
        return round(float(value) / float(arg), 3)
    except (ValueError, ZeroDivisionError):
        return None
