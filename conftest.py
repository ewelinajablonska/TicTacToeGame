import pytest
from model_bakery import baker

from api.models import User, UserProfile


@pytest.fixture
def create_user(db, django_user_model):
    def make_user(**kwargs):
        return django_user_model.objects.create_user(**kwargs)

    return make_user
