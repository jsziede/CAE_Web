from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q

from . import forms, models
from cae_home import models as cae_home_models

# Gets all the checkouts from the RoomCheckout model to show on the page and provides a form to submit a new room checkout
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

    # Outputs checkout list in descending order
    if direction == 'desc':
        ordering = '-{}'.format(ordering)

    # Splits the room checkout list into pages using GET data
    checkouts_per_page = 50
    if order_by and direction:
        room_checkout_list = models.RoomCheckout.objects.all().order_by(ordering)
    else:
        room_checkout_list = models.RoomCheckout.objects.all()
    paginator = Paginator(room_checkout_list, checkouts_per_page)
    page = request.GET.get('page')
    room_checkouts = paginator.get_page(page)

    students = cae_home_models.WmuUser.objects.all()
    # Gets all computer classrooms at the CAE Center
    rooms = cae_home_models.Room.objects.filter(
        Q(room_type__exact=5) &
        Q(department__exact=3))
    form = forms.RoomCheckoutForm()
    room_checkout_loop_counter = 0

    # If user has submitted a room checkout form
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

# Allows attendants to create, view, and submit room checklists.
@login_required
def checklists(request):
    # Determines whether or not a new checklist submission was successful.
    # This variable is checked in the template language to determine the color of the panel heading.
    success = 0

    # Allows user to change the sorting of the checklist table.
    # Default is by date from newest checklist to oldest.
    order_by = request.GET.get('order_by')
    direction = request.GET.get('direction')
    ordering = order_by

    # Outputs checkout list in descending order
    if direction == 'desc':
        ordering = '-{}'.format(ordering)

    # Splits the room checkout list into pages using GET data
    checklists_per_page = 50
    if order_by and direction:
        checklist_instances_list = models.ChecklistInstance.objects.all().order_by(ordering)
    else:
        checklist_instances_list = models.ChecklistInstance.objects.all()
    paginator = Paginator(checklist_instances_list, checklists_per_page)
    page = request.GET.get('page')
    checklist_instances = paginator.get_page(page)

    # The name of the checklist template that was clicked on by the user.
    checklist_template_name = request.GET.get('name')
    # Checks get request for a checklist instance based on its pk
    checklist_instance_primary = request.GET.get('checklist')
    # Checks get request for all checklist instances from a certain month
    checklist_instance_month = request.GET.get('month')
    # Stores the checklist template item that was requested by the user, if it exists.
    focused_template = None
    focused_instance = None

    checklist_templates = models.ChecklistTemplate.objects.all()

    # Uses a get request to print out the contents of a checklist
    if request.method == 'GET':
        # .filter().first() will return object or None if doesn't exist
        focused_template = models.ChecklistTemplate.objects.filter(title=checklist_template_name).first()
        focused_instance = models.ChecklistInstance.objects.filter(pk=checklist_instance_primary).first()


    #form = forms.RoomCheckoutForm()

    # if request.method == 'POST':
    # 	form = forms.RoomCheckoutForm(request.POST)

    # 	if form.is_valid():
    # 		checkout = form.save()focused_checklist
    # 		success = 1
    # 	else:
    # 		success = -1

    return TemplateResponse(request, 'cae_web_attendants/checklists.html', {
        'checklist_templates': checklist_templates,
        'checklist_instances': checklist_instances,
        'focused_template': focused_template,
        'focused_instance': focused_instance,
        'order_by': order_by,
        'direction': direction,
        'success': success,
    })
