from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.models import HighScore, User
from api.serializers import DashboardSerializer, UserSerializer
from api.permissions import IsLoggedInUserOrAdmin, IsAdminUser


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsLoggedInUserOrAdmin]
        elif self.action == 'list' or self.action == 'destroy':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class Dashboard(viewsets.ReadOnlyModelViewSet):
    serializer_class = DashboardSerializer
    queryset = HighScore.objects.all().order_by('moves_count', 'duration_time')[:10]

