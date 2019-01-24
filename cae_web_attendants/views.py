from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from . import models

# Home page of the CAE_Web_Attendants app.
def attendants(request):
    # Gets all the objects from the RoomCheckout model to show on the home page.
    # perhaps only a certain number of models should be retrieved instead of all?
    room_checkout_list = models.RoomCheckout.objects.all()
    return TemplateResponse(request, 'cae_web_attendants/attendants.html', {
        'room_checkout_list': room_checkout_list,
    })
