"""
Views for CAE_Web Core App.
"""

from django.template.response import TemplateResponse


def index(request):
    """
    Root project url.
    """
    return TemplateResponse(request, 'cae_web_core/index.html', {})


def calendar_test(request):
    return TemplateResponse(request, 'cae_web_core/calendar_test.html', {})
