
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import (
    HTTP_200_OK,
)

from api.mixins import SerializerActionClassMixin
from api.models import Game, HighScore
from api.serializers import (
    DashboardSerializer,
    GamePlayPartialUpdateSerializer,
    GamePlaySerializer,
)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class DashboardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows highscores to be seen.
    """

    serializer_class = DashboardSerializer
    queryset = HighScore.objects.all().order_by("moves_count", "duration_time")[:10]


class GamePlayViewSet(
    SerializerActionClassMixin,
    viewsets.ModelViewSet,
):
    """
    API endpoint that allows games to be created, read, updated and deleted.
    """

    serializer_class = GamePlaySerializer
    queryset = Game.objects.all()
    permission_classes = [IsAuthenticated]

    serializer_action_classes = {"partial_update": GamePlayPartialUpdateSerializer}

    @swagger_auto_schema(
        operation_description="cutomize response view in swagger for PATCH method",
        request_body=GamePlayPartialUpdateSerializer,
        responses=openapi.Responses(
            {
                HTTP_200_OK: openapi.Response(
                    description="Game status updated successfully.",
                    schema=openapi.Schema(
                        title="GamePlayPartialUpdate",
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "player1_id": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Items(
                                    type=openapi.TYPE_INTEGER,
                                    title="played moves",
                                ),
                            ),
                            "player2_id": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Items(
                                    type=openapi.TYPE_INTEGER,
                                    title="played moves",
                                ),
                            ),
                        },
                        required=["move"],
                    ),
                )
            }
        ),
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)
