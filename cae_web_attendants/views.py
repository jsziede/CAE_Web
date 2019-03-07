from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from . import forms, models
from cae_home import models as cae_home_models

# Gets all the objects from the RoomCheckout model to show on the home page and provides a form to submit a new room checkout
@login_required
def attendants(request):
	# Determines whether or not a new checkout submission was successful.
	# This variable is checked in the template language to determine the color of the panel heading.
	success = 0

	# Allows user to change the sorting of the room checkout table.
	# Default is by date from newest checkout to oldest.
	order_by = request.GET.get('order_by')
	direction = request.GET.get('direction')
	ordering = order_by

	if direction == 'desc':
		ordering = '-{}'.format(ordering)

	# Splits the room checkout list into pages using GET data
	checkouts_per_page = 25
	if order_by and direction:
		room_checkout_list = models.RoomCheckout.objects.all().order_by(ordering)
	else:
		room_checkout_list = models.RoomCheckout.objects.all()
	paginator = Paginator(room_checkout_list, checkouts_per_page)
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
			success = 1
		else:
			success = -1

	return TemplateResponse(request, 'cae_web_attendants/attendants.html', {
		'room_checkouts': room_checkouts,
		'students': students,
		'rooms': rooms,
		'form': form,
		'counter': room_checkout_loop_counter,
		'order_by': order_by,
		'direction': direction,
		'success': success,
	})
