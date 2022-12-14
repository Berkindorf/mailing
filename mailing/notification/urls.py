from django.urls import include, path
from rest_framework import routers

from .views import (ClientViewSet, NotificationViewSet)

router_v1 = routers.DefaultRouter()

router_v1.register(
    r'client', ClientViewSet, basename='client',
)

router_v1.register(
    r'notification', NotificationViewSet, basename='notification',
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
