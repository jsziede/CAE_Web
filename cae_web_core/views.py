"""
Views for CAE_Web Core App.
"""

from django.shortcuts import render


def index(request):
    """
    Root project url.
    """
    return render(request, 'cae_web_core/index.html')


def calendar_test(request):
    return render(request, "cae_web_core/calendar_test.html")
