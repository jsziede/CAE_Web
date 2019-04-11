from django import template

register = template.Library()

@register.filter(name='phone_number')
def phone_number(list, index):
    """
    Converts a PhoneNumber object into a string with the format (xxx) xxx-xxxx.
    """
    number = str(list[index])
    if(number == "None"):
        return "No phone number provided"
    else:
        first = number[2:5]
        second = number[5:8]
        third = number[8:12]
    return '(' + first + ')' + ' ' + second + '-' + third
