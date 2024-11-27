from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """Ajoute une classe CSS à un champ de formulaire."""
    return value.as_widget(attrs={"class": arg})
