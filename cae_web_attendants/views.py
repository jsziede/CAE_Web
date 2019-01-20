from django.shortcuts import render
from django.template.response import TemplateResponse

def attendants(request):
    return TemplateResponse(request, 'cae_web_attendants/attendants.html', {})