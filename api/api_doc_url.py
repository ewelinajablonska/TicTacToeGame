from django.contrib.auth.decorators import login_required
from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
   openapi.Info(
      title="TicTacToe API",
      default_version='v1',
      description= """
      Here you find detailed description of the Tic-Tac_Toe Game public API.
      """,
   ),
   public=True,
   permission_classes=(permissions.IsAuthenticated,),
)

urlpatterns = [
   path('doc/', login_required(schema_view.with_ui('swagger', cache_timeout=0)), name='schema-swagger-ui'),
]