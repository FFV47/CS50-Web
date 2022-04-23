from django import template

register = template.Library()


@register.filter()
def add_class(value, arg):
    """
    Add CSS class to HTML tag
    """
    return value.as_widget(attrs={"class": arg})
