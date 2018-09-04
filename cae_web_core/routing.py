"""
Route handling for CAE Web Core app.
"""

from django.conf.urls import url

from . import consumers


websocket_urlpatterns = [
    url('^ws/caeweb/employee/my_hours/$', consumers.MyHoursConsumer),
]
