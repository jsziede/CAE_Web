from django import template

register = template.Library()

@register.filter(name='get_num')
def get_num(list, index):
    """
    Gets phone number in a user friendly format.
    """
    return list[index][1]

@register.filter(name='get_tel')
def get_tel(list, index):
    """
    Gets phone number in an HTML link format.
    """
    return list[index][0]