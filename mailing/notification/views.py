from rest_framework import viewsets

from .models import Client, Notification
from .serializers import (ClientSerializer, NotificationSerializer)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    http_method_names = ('post', 'patch', 'delete')


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')

    '''
    def create(self, request):
        breakpoint()

    def destroy(self, request):
        breakpoint()
    '''
