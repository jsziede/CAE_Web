from django import template

register = template.Library()

@register.filter(name='phone_number')
def phone_number(list, index):
    """
    Convert a 10 character string into (xxx) xxx-xxxx.
    """
    number = str(list[index])
    if(number == "None"):
        return "No phone number provided"
    else:
        first = number[0:3]
        second = number[3:6]
        third = number[6:10]
    return '(' + first + ')' + ' ' + second + '-' + third
