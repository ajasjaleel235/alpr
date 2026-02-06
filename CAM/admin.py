from django.contrib import admin
from .models import CameraFeed, TrafficLog

admin.site.register(CameraFeed)
admin.site.register(TrafficLog)