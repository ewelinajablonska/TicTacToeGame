import pytest
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
)

from model_bakery import baker

from api.models import Game, User, UserProfile

"""
    TODO: tests failed:
     - GET with incorrect 'pk'
     - POST with incorrect 'pk' or incorrect data values:
        * no exist player
        * too many or too much players
        * get incorrect default data 
     - PATCH with 'move':
        * out of range
        * already played
        * when game is finished
"""


@pytest.mark.django_db
def test_view_play_success(client):
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

    url = reverse("gameplay-list")
    response = client.get(url)

    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["id"] == game.id


@pytest.mark.django_db
def test_create_play_success(client):
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

    data = {
        "max_players_number": 2,
        "board_size": 3,
        "is_done": False,
        "has_winner": False,
        "game_status": {},
        "current_player": "",
        "players": [first_player.id, second_player.id],
    }
    url = reverse("gameplay-list")

    response = client.post(url, data=data)
    parsed_response = response.json()
    new_game = Game.objects.get(id=parsed_response["id"])

    assert response.status_code == HTTP_201_CREATED
    assert new_game.max_players_number == data["max_players_number"]
    assert new_game.board_size == data["board_size"]
    assert new_game.is_done == data["is_done"]
    assert new_game.has_winner == data["has_winner"]
    assert list(new_game.players.values_list("id", flat=True)) == data["players"]


@pytest.mark.django_db
def test_update_play_success(client):
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
    data = {
        "max_players_number": 2,
        "board_size": 3,
        "is_done": False,
        "has_winner": False,
        "game_status": {},
        "current_player": "",
        "players": [first_player.id, second_player.id],
    }
    url = reverse("gameplay-list")
    response = client.post(url, data=data)
    parsed_response = response.json()
    new_game = Game.objects.get(id=parsed_response["id"])

    url = reverse("gameplay-detail", kwargs={"pk": new_game.id})

    response = client.patch(url, data={"move": 1}, content_type="application/json")
    parsed_response = response.json()
    new_game.refresh_from_db()

    assert response.status_code == HTTP_200_OK
    assert parsed_response == new_game.game_status
