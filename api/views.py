from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.models import Game, HighScore, User
from api.serializers import DashboardSerializer, GamePlayPartialSerializer, GamePlaySerializer, MoveSerializer, UserSerializer
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


class DashboardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows highscores to be seen.
    """
    serializer_class = DashboardSerializer
    queryset = HighScore.objects.all().order_by('moves_count', 'duration_time')[:10]


class GamePlayViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows games to be created, read. TODO not updated
    """
    serializer_class = GamePlaySerializer
    queryset = Game.objects.all()

    serializer_action_classes = {
        'partial_update': GamePlayPartialSerializer
    }

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)