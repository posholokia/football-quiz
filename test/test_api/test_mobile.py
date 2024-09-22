import uuid
from test.http_request import (
    send_get,
    send_patch,
    send_post,
)

import loguru
import pytest


USER1_DEVICE = uuid.uuid4().hex
USER2_DEVICE = uuid.uuid4().hex
USER3_DEVICE = uuid.uuid4().hex


@pytest.mark.asyncio(loop_scope="session")
async def test_create_profile():
    tokens = [USER1_DEVICE, USER2_DEVICE, USER3_DEVICE]
    for i, token in enumerate(tokens):
        response = await send_post(
            url="/api/v1/create_profile/",
            json={
                "api_key": "string"
            },
            headers={"Device": token},
        )
        assert 201 == response.status_code
        assert {"id": i + 5, "name": f"Игрок-{i + 5}"} == response.json()


@pytest.mark.asyncio(loop_scope="session")
async def test_bad_device_header():
    response = await send_post(
        url="/api/v1/create_profile/",
        json={
            "api_key": "string"
        },
        headers={"Device": "USER_DEVICE"},
    )
    assert 401 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_get_profile_success():
    response = await send_get(
        url="/api/v1/get_profile/5/",
        headers={"Device": USER1_DEVICE},
    )
    assert 200 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_get_profile_fail():
    response = await send_get(
        url="/api/v1/get_profile/5/",
        headers={"Device": USER2_DEVICE},
    )
    assert 403 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_change_profile():
    response = await send_patch(
        url="/api/v1/change_profile/6/",
        json={
            "name": "string"
        },
        headers={"Device": USER2_DEVICE},
    )
    assert 200 == response.status_code
    assert {"id": 6, "name": "string"} == response.json()


@pytest.mark.asyncio(loop_scope="session")
async def test_add_user_statistic():
    response = await send_post(
        url="/api/v1/user_statistic/5/",
        json={
            "score": 32,
            "rights": 8,
            "wrongs": 2,
            "perfect_round": False,
        },
        headers={"Device": USER1_DEVICE},
    )
    assert 200 == response.status_code
    assert 3 == response.json()["place"]


@pytest.mark.asyncio(loop_scope="session")
async def test_add_second_user_statistic():
    response = await send_post(
        url="/api/v1/user_statistic/6/",
        json={
            "score": 21,
            "rights": 6,
            "wrongs": 4,
            "perfect_round": False,
        },
        headers={"Device": USER2_DEVICE},
    )
    assert 200 == response.status_code
    assert 5 == response.json()["place"]


@pytest.mark.asyncio(loop_scope="session")
async def test_add_third_user_statistic():
    response = await send_post(
        url="/api/v1/user_statistic/7/",
        json={
            "score": 38,
            "rights": 10,
            "wrongs": 0,
            "perfect_round": True,
        },
        headers={"Device": USER3_DEVICE},
    )
    assert 200 == response.status_code
    assert 2 == response.json()["place"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user1_statistic():
    good = {
        "score": 32,
        "rights": 8,
        "wrongs": 2,
        "id": 4,  # это id статистики, а не профиля
        "games": 1,
        "place": 4,
        "perfect_rounds": 0,
        "trend": 0,
        "title": {
            "best_of_the_day": 0,
            "best_of_the_month": 0
        },
    }
    response = await send_get(
        url="/api/v1/user_statistic/5/",
        headers={"Device": USER1_DEVICE},
    )
    assert 200 == response.status_code
    for attr, value in response.json().items():
        assert good[attr] == value


@pytest.mark.asyncio(loop_scope="session")
async def test_get_total_ladder():
    response = await send_get(
        url="/api/v1/ladder/top/?offset=1&limit=2&period=total",
        headers={"Device": USER3_DEVICE},
    )
    assert 200 == response.status_code
    assert 2 == len(response.json()["items"])
    assert 6 == response.json()["paginator"]["total"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_statistic_in_ladder():
    response = await send_get(
        url="/api/v1/user_statistic/7/ladder/?limit=3&period=total",
        headers={"Device": USER3_DEVICE},
    )
    assert 200 == response.status_code
    assert 3 == len(response.json()["items"])
    assert 7 == response.json()["items"][1]["profile"]["id"]
    assert 6 == response.json()["paginator"]["total"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_month_ladder():
    response = await send_get(
        url="/api/v1/ladder/top/?offset=0&limit=100&period=month",
        headers={"Device": USER2_DEVICE},
    )
    assert 200 == response.status_code
    assert 6 == len(response.json()["items"])
    assert 6 == response.json()["paginator"]["total"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_day_ladder():
    response = await send_get(
        url="/api/v1/ladder/top/?offset=2&limit=1&period=day",
        headers={"Device": USER1_DEVICE},
    )
    assert 200 == response.status_code
    assert 1 == len(response.json()["items"])
    assert 4 == response.json()["paginator"]["total"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_questions():
    response = await send_get(
        url="/api/v1/get_questions/?limit=20",
        headers={"Device": USER1_DEVICE},
    )
    assert 200 == response.status_code
    assert 20 == len(response.json())


@pytest.mark.asyncio(loop_scope="session")
async def test_get_complain_category():
    categories = [
        "Ошибка в содержании вопроса",
        "Ошибка в ответах",
        "Вопрос устарел/неактуален",
        "Орфографическая ошибка",
        "Другая причина",
    ]
    response = await send_get(
        url="/api/v1/complain/category/",
        headers={"Device": USER1_DEVICE},
    )
    assert 200 == response.status_code
    for cat in response.json():
        assert cat.get("id")
        assert cat.get("name") in categories


@pytest.mark.asyncio(loop_scope="session")
async def test_create_complain():
    response = await send_post(
        url="/api/v1/complain/",
        json={
            "text": "Слишком длинный вопрос",
            "question": 123,
            "category": 2,
            "profile": 5,
        },
        headers={"Device": USER1_DEVICE},
    )
    assert 204 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_get_settings():
    settings_attrs = [
        "time_round",
        "question_limit",
        "max_energy",
        "start_energy",
        "energy_for_ad",
        "round_cost",
        "question_skip_cost",
        "energy_perfect_round",
        "recovery_period",
        "recovery_value",
        "right_ratio",
        "wrong_ratio",
    ]
    response = await send_get(
        url="/api/v1/game_settings/",
        headers={"Device": USER1_DEVICE},
    )
    assert 200 == response.status_code
    for key in settings_attrs:
        assert key in response.json().keys()
