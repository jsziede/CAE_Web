from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

import json
from django.core.serializers.json import DjangoJSONEncoder

from . import forms, models
from cae_home import models as cae_home_models

# Home page of the CAE_Web_Attendants app.
@login_required
def attendants(request):
	# Gets all the objects from the RoomCheckout model to show on the home page.
	# perhaps only a certain number of models should be retrieved instead of all?
	room_checkout_list = models.RoomCheckout.objects.all()
	paginator = Paginator(room_checkout_list, 25)
	page = request.GET.get('page')
	room_checkouts = paginator.get_page(page)

	students = cae_home_models.WmuUser.objects.all()
	rooms = cae_home_models.Room.objects.all()
	form = forms.RoomCheckoutForm()
	room_checkout_loop_counter = 0

	if request.method == 'POST':
		form = forms.RoomCheckoutForm(request.POST)
		if form.is_valid():
			checkout = form.save()

	return TemplateResponse(request, 'cae_web_attendants/attendants.html', {
		'room_checkouts': room_checkouts,
		'students': students,
		'rooms': rooms,
		'form': form,
		'counter': room_checkout_loop_counter,
	})
