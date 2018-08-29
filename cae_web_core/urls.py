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

    # Room scheduler views.
    # TODO: Note, these schedule api urls are public. Should they be permission based?
    # TODO Response: Probably, yes. At least editing/adding them should be. Standard viewing probably should be public.
    url(r'^schedule/', include('schedule.urls', namespace='schedule')),
    url(r'^room-schedule/api/$', views.api_room_schedule, name='api_room_schedule'),
    url(r'^calendar-test/$', views.calendar_test, name='calendar_test'),
]
