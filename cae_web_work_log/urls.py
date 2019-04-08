"""
Urls for CAE Work Log App.
"""

from django.conf.urls import url

from . import views


app_name = 'cae_web_work_log'
urlpatterns = [
    url(r'^employee/work_log/$', views.index, name='index'),
    url(r'^employee/work_log/create/$', views.modify_entry, name='create_entry'),
    url(r'^employee/work_log/edit/(?P<pk>[0-9]+)/$', views.modify_entry, name='edit_entry'),
]
