"""
Admin views for CAE Web Work Log app.
"""

from django.contrib import admin

from . import models


admin.site.register(models.TimeFrameType)
admin.site.register(models.WorkLogSet)
admin.site.register(models.WorkLogEntry)
