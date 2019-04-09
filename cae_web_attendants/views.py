from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import modelformset_factory, inlineformset_factory
from django.utils import timezone
from django.db import IntegrityError, transaction

from . import forms, models
from cae_home import models as cae_home_models

@login_required
def attendants(request):
    """
    Gets all the checkouts from the RoomCheckout model to show on the page and provides a form to submit a new room checkout.
    """
    # Determines whether or not a new checkout submission was successful.
    # This variable is checked in the template language to determine the color of the panel heading.
    success = 0

    # Allows user to change the sorting of the room checkout table.
    # Default is by date from newest checkout to oldest.
    order_by = request.GET.get('order_by')
    direction = request.GET.get('direction')
    ordering = order_by
    page = request.GET.get('page')
    room_checkouts = get_paginated_models(direction, ordering, order_by, page, 50, models.RoomCheckout)

    form = forms.RoomCheckoutForm()

    # If user has submitted a room checkout form
    if request.method == 'POST':
        form = forms.RoomCheckoutForm(request.POST)

        if form.is_valid():
            form.save()
            success = 1
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

@login_required
def checklists(request):
    """
    Allows attendants to create, view, and submit room checklists.
    """
    # Determines whether or not a new checklist submission was successful.
    # This variable is checked in the template language to determine the color of the panel heading.
    success = 0

    """
    If user submitted a form.

    Each form on the checklist web page has a separate action
    value to differentiate themselves from the other forms that
    can be submitted via post request.
    """
    if request.method == 'POST':
        # If edit checklist form
        if request.POST['action'] == 'Edit':
            # Gets the instance pk
            pk = request.GET.get('edit')
            # Gets the checklist instance object
            instance = models.ChecklistInstance.objects.filter(pk=pk).first()
            # Formset of all checklist items that are being edited
            TaskFormset = modelformset_factory(
                models.ChecklistItem,
                fields=('task', 'completed')
            )
            formset = TaskFormset(request.POST, queryset=instance.task.all())
            success = handle_edit_checklist_form(pk, instance, formset)
        # If create instance form
        elif request.POST['action'] == 'Instance':
            form = forms.ChecklistInstanceForm(request.POST)
            success = handle_create_checklist_instance_form(form)
        elif request.POST['action'] == 'Template':
            # Retrieves the checklist template form from the user
            form = forms.ChecklistTemplateForm(request.POST)
            form.fields['room'].queryset = cae_home_models.Room.objects.filter(Q(department__name='CAE Center'))
            # Retrieves the checklist task formset from the user
            TaskFormset = modelformset_factory(
                models.ChecklistItem,
                fields=('task',),
            )
            formset = TaskFormset(request.POST, queryset=models.ChecklistItem.objects.none())
            success = handle_create_checklist_template_form(form, formset)


    # The name of the checklist template that was clicked on by the user.
    checklist_template_primary = request.GET.get('template')
    # Checks get request for a checklist instance based on its pk
    checklist_instance_primary = request.GET.get('checklist')
    # Checks get request for all checklist instances from a certain month
    # TODO: add button on page to filter by month
    # checklist_instance_month = request.GET.get('month')

    # Allows user to change the sorting of the checklist table.
    # Default is by date from newest checklist to oldest, with incomplete checklists appearing before completed
    order_by = request.GET.get('order_by')
    direction = request.GET.get('direction')
    ordering = order_by
    page = request.GET.get('page')
    checklist_instances = get_paginated_models(direction, ordering, order_by, page, 50, models.ChecklistInstance)

    # Determines which form, if any, to show on the page
    create_checklist = request.GET.get('create')
    form = None
    create_template = None
    create_instance = None
    # Pk of a checklist instance that is having its tasks edited
    edit_instance = request.GET.get('edit')
    formset = None
    # If user requested the checklist template creation form
    if create_checklist == "template":
        create_template = True
        # Get a normal form for the template and a formset for the template tasks
        form = forms.ChecklistTemplateForm()
        form.fields['room'].queryset = cae_home_models.Room.objects.filter(Q(department__name='CAE Center'))
        TaskFormset = modelformset_factory(
            models.ChecklistItem,
            fields=('task',),
            extra=1
        )
        # Make the new template task list be empty
        formset = TaskFormset(queryset=models.ChecklistItem.objects.none())
    elif create_checklist == "checklist":
        create_instance = True
        # Defaults the template option to the template the user is creating the checklist from
        form = forms.ChecklistInstanceForm(initial={'template': checklist_template_primary})
        form.fields['template'].queryset = models.ChecklistTemplate.objects.filter(pk=checklist_template_primary)
        form.fields['template'].disabled = True
        # Only show CAE Rooms
        form.fields['room'].queryset = cae_home_models.Room.objects.filter(Q(department__name='CAE Center'))
    # If user is marking checklist instance tasks as complete or not
    elif edit_instance:
        # Gets the checklist instance requested by the user
        instance = models.ChecklistInstance.objects.filter(pk=edit_instance).first()
        if instance:
            # Gets all the checklist items from the instance and puts them into a formset
            TaskFormset = modelformset_factory(
                models.ChecklistItem,
                fields=('task', 'completed'),
                extra=0)
            formset = TaskFormset(queryset=instance.task.all())
            for form in formset:
                form.fields['task'].disabled = True
            # Stores the checklist instance information so its data can be shown on the webpage
            edit_instance = instance
        else:
            edit_instance = None

    # Stores the checklist template item that was requested by the user, if it exists.
    focused_template = None
    focused_instance = None

    checklist_templates = models.ChecklistTemplate.objects.all()

    # Uses a get request to print out the contents of a checklist
    if request.method == 'GET':
        # .filter().first() will return object or None if doesn't exist
        focused_template = models.ChecklistTemplate.objects.filter(pk=checklist_template_primary).first()
        focused_instance = models.ChecklistInstance.objects.filter(pk=checklist_instance_primary).first()

    return TemplateResponse(request, 'cae_web_attendants/checklists.html', {
        'checklist_templates': checklist_templates,
        'checklist_instances': checklist_instances,
        'focused_template': focused_template,
        'focused_instance': focused_instance,
        'create_template': create_template,
        'create_instance': create_instance,
        'edit_instance': edit_instance,
        'order_by': order_by,
        'direction': direction,
        'form': form,
        'formset': formset,
        'success': success,
    })


def handle_edit_checklist_form(pk, instance, formset):
    """
    Edits a collection of checklist tasks from one checklist instance to
    be set as either completed or not based on user input from the
    edit checklist form.
    """
    for form in formset:
        form.fields['task'].disabled = True
    if formset.is_valid():
        formset.save()
        try:
            with transaction.atomic():
                # Checks if the checklist instance was completed or not after the user submitted the edit
                completed = True
                # Looks for any unfinished tasks
                for form in formset:
                    if form.cleaned_data['completed'] == False:
                        completed = False
                # If checklist was not completed prior to submission
                if instance.date_completed == None:
                    # Mark it as completed if all tasks were completed
                    if completed == True:
                        instance.date_completed = timezone.now()
                        instance.save()
                # Else if checklist was completed prior to submission
                else:
                    # Mark it as incomplete if a tasks was marked as incomplete
                    if completed == False:
                        instance.date_completed = None
                        instance.save()
                success = 1
        # If the transaction failed
        except IntegrityError:
            success = -1
    else:
        success = -1
    return success

def handle_create_checklist_instance_form(form):
    """
    Creates a new checklist instance based on a checklist
    template that was selected by the user from the web page.
    """
    # If all form fields are valid
    if form.is_valid():
        # Gets the title of the template that the checklist was made from
        checklist_title = form.cleaned_data['template'].title
        # If the user input their own title for the checklist, then replace the inherited template title
        if form.cleaned_data['title']:
            checklist_title = form.cleaned_data['title']
        try:
            with transaction.atomic():
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
        # If the transaction failed
        except IntegrityError:
            success = -1
    # If form failed to validate then the form becomes red
    else:
        success = -1
    return success

def handle_create_checklist_template_form(form, formset):
    """
    Creates a new checklist instance based on a checklist
    template that was selected by the user from the web page.
    """
    try:
        with transaction.atomic():
            if form.is_valid():
                # Save the new base template, but not the tasks
                template = form.save()
                if formset.is_valid():
                    #TODO: Disallow empty formset.
                    for form in formset:
                        if form.is_valid() and form.has_changed():
                            # Save all the new tasks and add them to the newly created template
                            #TODO: Maybe allow user to select from existing tasks as well
                            new_task = models.ChecklistItem(task = form.cleaned_data['task'])
                            new_task.save()
                            template.checklist_item.add(new_task.pk)
                    success = 1
                else:
                    success = -1
            else:
                success = -1
    # If the transaction failed
    except IntegrityError:
        success = -1
    return success

def get_paginated_models(direction, ordering, order_by, page, per_page, model):
    """
    Gets a subset of consecutive models based on ordering. 
    """
    # Outputs checkout list in descending order
    if direction == 'desc':
        ordering = '-{}'.format(ordering)
    # Splits the room checkout list into pages using GET data
    if order_by and direction:
        instances_list = model.objects.all().order_by(ordering)
    else:
        instances_list = model.objects.all()
    paginator = Paginator(instances_list, per_page)

    return paginator.get_page(page)
