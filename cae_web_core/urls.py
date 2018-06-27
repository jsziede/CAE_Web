"""
Urls for CAE_Web Core app.
"""

from django.conf.urls import url

from . import views


app_name = 'cae_web_core'
urlpatterns = [
# Home page.
    url(r'^$', views.index, name='index')
]
