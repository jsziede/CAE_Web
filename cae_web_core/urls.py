"""
Urls for CAE_Web Core app.
"""

from django.conf.urls import include, url

from . import views


app_name = 'cae_web_core'
urlpatterns = [
# Home page.
    url(r'^$', views.index, name='index'),
    # TODO: Note, these schedule api urls are public. Should they be permission based?
    url(r'^schedule/', include('schedule.urls', namespace='schedule')),
    url(r'^calendar-test/$', views.calendar_test, name='calendar_test'),
]
