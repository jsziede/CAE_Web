"""
Urls for CAE Work Log App.
"""

from django.conf.urls import url

from . import views


app_name = 'cae_web_work_log'
urlpatterns = [
    url(r'^employee/work_log/$', views.index, name='index'),
    url(r'^employee/work_log/create/$', views.create_entry, name='create'),
    # url(r'^employee/work_log/(?P<pk>[0-9]+)/$', views.work_log, name='work_log'),
]
