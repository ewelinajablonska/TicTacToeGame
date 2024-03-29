from django.conf.urls import include
from rest_framework import routers
from api.views import GamePlayViewSet
from django.urls import re_path
from . import views

router = routers.DefaultRouter()
router.register(r"play", GamePlayViewSet, basename="gameplay")

urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"^dj-rest-auth/", include("dj_rest_auth.urls")),
    re_path(r"^dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    re_path(
        r"^dashboard", views.DashboardViewSet.as_view({"get": "list"}), name="dashboard"
    ),
]
