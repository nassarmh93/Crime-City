from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
    
@register.filter
def percentage(value, level):
    """Calculate percentage for XP bar"""
    try:
        total_needed = float(level) * 100
        return min(float(value) / total_needed * 100, 100)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def sum(value, arg):
    """Sum a property of all objects in a queryset"""
    try:
        return sum(getattr(obj, arg, 0) for obj in value)
    except (TypeError, AttributeError):
        return 0 