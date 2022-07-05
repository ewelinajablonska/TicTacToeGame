
from django.conf.urls import include
from rest_framework import routers
from api.views import UserViewSet
from django.urls import re_path
from . import views

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    re_path(r'^', include(router.urls)),
    re_path(r'^dj-rest-auth/', include('dj_rest_auth.urls')),
    re_path(r'^dashboard', views.Dashboard.as_view({"get": "list"}), name='dashboard'),
]