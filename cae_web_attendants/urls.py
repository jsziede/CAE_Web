"""
Urls for CAE_Web Core app.
"""

from django.conf.urls import include, url

from . import views


app_name = 'cae_web_attendants'
urlpatterns = [
    # Home page.
    url(r'^checkout', views.attendants, name='checkout'),
]
