"""
Urls for CAE_Web Core app.
"""

from django.conf.urls import include, url

from . import views


app_name = 'cae_web_core'
urlpatterns = [
    # Home page.
    url(r'^$', views.index, name='index'),

    # Employee Shift views.
    url(r'^employee/my_hours/$', views.my_hours, name='my_hours'),
    url(r'^employee/shifts/(?P<pk>[0-9]+)/$', views.shift_edit, name='shift_edit'),
    url(r'^employee/shift_manager/$', views.shift_manager_redirect, name='shift_manager_redirect'),
    url(r'^employee/shift_manager/(?P<pk>[0-9]+)/$', views.shift_manager, name='shift_manager'),
    url(r'^employee/schedule/$', views.employee_schedule, name='employee_schedule'),
    url(r'^employee/schedule/(?P<employee_type_pk>[0-9]+)/$', views.employee_schedule, name='employee_schedule'),

    # Room scheduler views.
    # TODO: Note, these schedule api urls are public. Should they be permission based?
    # TODO Response: Probably, yes. At least editing/adding them should be. Standard viewing probably should be public.
    url(r'^schedule/', include(('schedule.urls', 'schedule'), namespace='schedule')),
    url(r'^room-schedule/upload/$', views.upload_schedule, name='upload_schedule'),
    url(r'^room-schedule/(?P<room_type_slug>[-\w]+)/$', views.room_schedule, name='room_schedule'),
]
