"""
Urls for CAE_Web Core app.
"""

from django.conf.urls import include, url

from . import views


app_name = 'cae_web_attendants'
urlpatterns = [
    # Page for creating and viewing room checkouts
    url(r'^checkout', views.attendants, name='checkout'),
    # Page for creating and viewing room checklists
    url(r'^checklist', views.checklists, name='checklist'),
]
