"""
Custom template tags for CAE Web Core app.
"""

import math
from django import template
from django.utils import timezone


register = template.Library()


@register.inclusion_tag('cae_web_core/employee/shift_manager_tables.html', takes_context=True)
def employee_pay_period_tables(context):
    """
    Read through dates of provided shifts, and separate into appropriate tables.
    Method is run individually for each employee rendered to template.
    :return: Two tables of formatted shift data for web and a comprehensive third table for print views.
    """
    # Get week start and end dates.
    week_1_start = context['pay_period'].period_start
    week_1_end = week_1_start + timezone.timedelta(days=7)
    week_1_shifts = context['shifts'].filter(employee=context['user'], clock_in__lt=week_1_end)
    week_2_start = context['pay_period'].period_start + timezone.timedelta(days=8)
    week_2_end = context['pay_period'].period_end
    week_2_shifts = context['shifts'].filter(employee=context['user'], clock_in__gte=week_1_end)

    # Get time worked for week 1. Used in first table of web view.
    week_1_total_seconds = 0
    week_1_hms = (0, 0, 0)
    week_1_decimal = 0
    if week_1_shifts:
        for shift in week_1_shifts:
            week_1_total_seconds += shift.get_time_worked()
        week_1_hms = week_1_shifts[0].get_time_worked_as_hms(week_1_total_seconds)
        week_1_decimal = week_1_shifts[0].get_time_worked_as_decimal(week_1_total_seconds)

    # Get time worked for week 2. Used in second table of web view.
    week_2_total_seconds = 0
    week_2_hms = (0, 0, 0)
    week_2_decimal = 0
    if week_2_shifts:
        for shift in week_2_shifts:
            week_2_total_seconds += shift.get_time_worked()
        week_2_hms = week_2_shifts[0].get_time_worked_as_hms(week_2_total_seconds)
        week_2_decimal = week_2_shifts[0].get_time_worked_as_decimal(week_2_total_seconds)

    # Get total time worked during entire pay period. Used in print view.
    pay_period_total_seconds = week_1_total_seconds + week_2_total_seconds
    if context['shifts']:
        pay_period_hms = context['shifts'][0].get_time_worked_as_hms(pay_period_total_seconds)
        pay_period_decimal = context['shifts'][0].get_time_worked_as_decimal(pay_period_total_seconds)
    else:
        pay_period_hms = 0
        pay_period_decimal = 0

    return {
        'user': context['user'],
        'pay_period': context['pay_period'],

        'pay_period_shifts': context['shifts'].filter(employee=context['user']),
        'week_1_shifts': week_1_shifts,
        'week_2_shifts': week_2_shifts,

        'week_1_start': week_1_start,
        'week_1_end': week_1_end,
        'week_2_start': week_2_start,
        'week_2_end': week_2_end,

        'pay_period_hms': pay_period_hms,
        'pay_period_decimal': pay_period_decimal,
        'week_1_hms': week_1_hms,
        'week_1_decimal': week_1_decimal,
        'week_2_hms': week_2_hms,
        'week_2_decimal': week_2_decimal,
    }


@register.simple_tag
def print_time_worked_as_decimal(shift):
    """
    Gets decimal of hours worked in current shift.
    :return: Decimal of hours worked.
    """
    return shift.get_time_worked_as_decimal()


@register.simple_tag
def print_time_worked_as_hms(shift):
    """
    Gets tuple of hours/minutes/seconds worked in current shift.
    :return: Tuple of h/m/s worked.
    """
    time_worked_tuple = shift.get_time_worked_as_hms()
    return '{0:<2} / {1:<2} / {2:<2}'.format(time_worked_tuple[0], time_worked_tuple[1], time_worked_tuple[2])
