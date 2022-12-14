from django.contrib import admin

from .models import Client, Message, Notification

admin.site.register(Client)
admin.site.register(Message)
admin.site.register(Notification)
