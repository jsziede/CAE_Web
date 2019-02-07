from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.db.models import Q

from . import forms, models
from cae_home import models as cae_home_models

# Home page of the CAE_Web_Attendants app.
def attendants(request):
	# Gets all the objects from the RoomCheckout model to show on the home page.
	# perhaps only a certain number of models should be retrieved instead of all?
	room_checkout_list = models.RoomCheckout.objects.all()
	students = cae_home_models.WmuUser.objects.all()
	rooms = cae_home_models.Room.objects.all()
	form = forms.RoomCheckoutForm()

	if request.method == 'POST':
		form = forms.RoomCheckoutForm(request.POST)
		if form.is_valid():
			checkout = form.save()

	return TemplateResponse(request, 'cae_web_attendants/attendants.html', {
		'room_checkout_list': room_checkout_list,
		'students': students,
		'rooms': rooms,
		'form': form
	})
