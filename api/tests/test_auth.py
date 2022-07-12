import pytest
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
)

from model_bakery import baker

from api.models import Game, User, UserProfile


@pytest.mark.django_db
def test_view_list_failure_without_authentication(client):
    """register user"""
    response = client.post(
        reverse("rest_register"),
        data=dict(
            username="first_user",
            email="first_user@gmail.com",
            password1="first_password",
            password2="first_password",
        ),
    )
    parsed_response = response.json()
    first_user = User.objects.get(id=parsed_response["user"]["pk"])
    """logout user"""
    response = client.post(reverse("rest_logout"))
    assert response.status_code == HTTP_200_OK

    response = client.get(reverse("gameplay-list"))
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_view_list_success_with_authentication(client):
    """register user"""
    response = client.post(
        reverse("rest_register"),
        data=dict(
            username="first_user",
            email="first_user@gmail.com",
            password1="first_password",
            password2="first_password",
        ),
    )
    parsed_response = response.json()
    first_user = User.objects.get(id=parsed_response["user"]["pk"])

    response = client.get(reverse("gameplay-list"))
    assert response.status_code == HTTP_200_OK


@pytest.mark.django_db
def test_view_detail_failure_without_authentication(client):
    """register user"""
    response = client.post(
        reverse("rest_register"),
        data=dict(
            username="first_user",
            email="first_user@gmail.com",
            password1="first_password",
            password2="first_password",
        ),
    )
    parsed_response = response.json()
    first_user = User.objects.get(id=parsed_response["user"]["pk"])
    response = client.post(
        reverse("rest_register"),
        data=dict(
            username="second_user",
            email="second_user@gmail.com",
            password1="second_password",
            password2="second_password",
        ),
    )
    parsed_response = response.json()
    second_user = User.objects.get(id=parsed_response["user"]["pk"])
    first_player = baker.make(
        UserProfile,
        user=first_user,
        title="first_user",
        address="first_addres",
        country="first_country",
        city="first_city",
    )
    second_player = baker.make(
        UserProfile,
        user=second_user,
        title="second_user",
        address="second_addres",
        country="second_country",
        city="second_city",
    )
    game = baker.make(
        Game,
        players=[first_player, second_player],
    )
    """logout user"""
    response = client.post(reverse("rest_logout"))
    assert response.status_code == HTTP_200_OK

    response = client.get(reverse("gameplay-detail", kwargs={"pk": game.id}))
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_view_detail_success_with_authentication(client):
    """register user"""
    response = client.post(
        reverse("rest_register"),
        data=dict(
            username="first_user",
            email="first_user@gmail.com",
            password1="first_password",
            password2="first_password",
        ),
    )
    parsed_response = response.json()
    first_user = User.objects.get(id=parsed_response["user"]["pk"])
    response = client.post(
        reverse("rest_register"),
        data=dict(
            username="second_user",
            email="second_user@gmail.com",
            password1="second_password",
            password2="second_password",
        ),
    )
    parsed_response = response.json()
    second_user = User.objects.get(id=parsed_response["user"]["pk"])
    first_player = baker.make(
        UserProfile,
        user=first_user,
        title="first_user",
        address="first_addres",
        country="first_country",
        city="first_city",
    )
    second_player = baker.make(
        UserProfile,
        user=second_user,
        title="second_user",
        address="second_addres",
        country="second_country",
        city="second_city",
    )
    game = baker.make(
        Game,
        players=[first_player, second_player],
    )
    response = client.get(reverse("gameplay-detail", kwargs={"pk": game.id}))
    assert response.status_code == HTTP_200_OK


@pytest.mark.django_db
def test_view_update_failure_without_authentication(client):
    """register user"""
    response = client.post(
        reverse("rest_register"),
        data=dict(
            username="first_user",
            email="first_user@gmail.com",
            password1="first_password",
            password2="first_password",
        ),
    )
    parsed_response = response.json()
    first_user = User.objects.get(id=parsed_response["user"]["pk"])

    response = client.post(
        reverse("rest_register"),
        data=dict(
            username="second_user",
            email="second_user@gmail.com",
            password1="second_password",
            password2="second_password",
        ),
    )
    parsed_response = response.json()
    second_user = User.objects.get(id=parsed_response["user"]["pk"])
    first_player = baker.make(
        UserProfile,
        user=first_user,
        title="first_user",
        address="first_addres",
        country="first_country",
        city="first_city",
    )
    second_player = baker.make(
        UserProfile,
        user=second_user,
        title="second_user",
        address="second_addres",
        country="second_country",
        city="second_city",
    )
    game = baker.make(
        Game,
        players=[first_player, second_player],
    )
    """logout user"""
    response = client.post(reverse("rest_logout"))
    assert response.status_code == HTTP_200_OK
    url = reverse("gameplay-detail", kwargs={"pk": game.id})
    response = client.patch(url, data={"move": 1})
    assert response.status_code == HTTP_401_UNAUTHORIZED