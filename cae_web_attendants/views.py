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

    form = forms.RoomCheckoutForm()

    # If user has submitted a room checkout form
    if request.method == 'POST':
        form = forms.RoomCheckoutForm(request.POST)

        if form.is_valid():
            form.save()
            success = 1
            print(form.fields['checkout_date'])
        else:
            success = -1

    # Gets all computer classrooms at the CAE Center that are valid for checking out
    complex_query = (
        (
            Q(room_type__slug='classroom') | Q(room_type__slug='computer-classroom')
        )
        & Q(department__name='CAE Center')
    )
    form.fields['room'].queryset = cae_home_models.Room.objects.filter(complex_query)

    # TODO: Set current employee as the default employee using the view rather than a script 

    return TemplateResponse(request, 'cae_web_attendants/attendants.html', {
        'room_checkouts': room_checkouts,
        'form': form,
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

    # If user submitted a form
    if request.method == 'POST':
        # Gets form with filled out data from user
        form = forms.ChecklistInstanceForm(request.POST)
        
        # If all form fields are valid
        if form.is_valid():
            # Gets the title of the template that the checklist was made from
            checklist_title = form.cleaned_data['template'].title
            # If the user input their own title for the checklist, then replace the inherited template title
            if form.cleaned_data['title']:
                checklist_title = form.cleaned_data['title']
            # Create a new checklist instance using cleaned data from the form
            checklist = models.ChecklistInstance(template = form.cleaned_data['template'],
                room = form.cleaned_data['room'],
                employee = form.cleaned_data['employee'],
                title = checklist_title)
            checklist.save()
            # Gets the list of tasks that are used for the template
            tasks = form.cleaned_data['template'].checklist_item.all()
            # For each task
            for task in tasks:
                # Inserts a new ChecklistItem with the same title as the template task
                new_task = models.ChecklistItem(task = task.task, completed = False)
                new_task.save()
                # Add new task to the checklist instance
                checklist.task.add(new_task.pk)
            # Make the form become green
            success = 1
        # If form failed to validate then the form becomes red
        else:
            success = -1

    # The name of the checklist template that was clicked on by the user.
    checklist_template_name = request.GET.get('template')
    # Checks get request for a checklist instance based on its pk
    checklist_instance_primary = request.GET.get('checklist')
    # Checks get request for all checklist instances from a certain month
    # TODO: add button on page to filter by month
    checklist_instance_month = request.GET.get('month')

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

    # Determines which form, if any, to show on the page
    create_checklist = request.GET.get('create')
    form = None
    create_template = None
    create_instance = None
    if create_checklist == "template":
        create_template = True
        #form = forms.RoomCheckoutForm()
    elif create_checklist == "checklist":
        create_instance = True
        # Defaults the template option to the template the user is creating the checklist from
        form = forms.ChecklistInstanceForm(initial={'template': checklist_template_name})
        form.fields["template"].queryset = models.ChecklistTemplate.objects.filter(pk=checklist_template_name)
        # Only show CAE Rooms
        complex_query = (
        (
            Q(room_type__slug='classroom') | Q(room_type__slug='computer-classroom')
        )
        & Q(department__name='CAE Center')
    )
    form.fields['room'].queryset = cae_home_models.Room.objects.filter(complex_query)

    # Stores the checklist template item that was requested by the user, if it exists.
    focused_template = None
    focused_instance = None

    checklist_templates = models.ChecklistTemplate.objects.all()

    # Uses a get request to print out the contents of a checklist
    if request.method == 'GET':
        # .filter().first() will return object or None if doesn't exist
        focused_template = models.ChecklistTemplate.objects.filter(pk=checklist_template_name).first()
        focused_instance = models.ChecklistInstance.objects.filter(pk=checklist_instance_primary).first()

    return TemplateResponse(request, 'cae_web_attendants/checklists.html', {
        'checklist_templates': checklist_templates,
        'checklist_instances': checklist_instances,
        'focused_template': focused_template,
        'focused_instance': focused_instance,
        'create_template': create_template,
        'create_instance': create_instance,
        'order_by': order_by,
        'direction': direction,
        'form': form,
        'success': success,
    })
