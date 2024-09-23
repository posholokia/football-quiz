from test.http_request import (
    send_delete,
    send_get,
    send_patch,
    send_post,
    send_put,
)
from test.test_api.fixture import (
    jwt_access_admin_token,
    jwt_access_token,
    jwt_refresh_admin_token,
    jwt_refresh_token,
)

import loguru
import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_success():
    response = await send_post(
        url="/api/v1/jwt/create/",
        json={
            "username": "admin",
            "password": "admin"
        },
    )
    assert 200 == response.status_code
    assert "access" in response.json()
    assert "refresh" in response.json()


@pytest.mark.asyncio(loop_scope="session")
async def test_auth_fail():
    response = await send_post(
        url="/api/v1/jwt/create/",
        json={
            "username": "admin",
            "password": "secret"
        },
    )
    assert 401 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_refresh_token_fail():
    response = await send_post(
        url="/api/v1/jwt/refresh/",
        json={
            "refresh": "super_refresh_token",
        },
    )
    assert 401 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_refresh_token_success(jwt_refresh_admin_token):
    refresh = await jwt_refresh_admin_token
    response = await send_post(
        url="/api/v1/jwt/refresh/",
        json={
            "refresh": refresh,
        },
    )
    assert 200 == response.status_code
    assert "access" in response.json()


@pytest.mark.asyncio(loop_scope="session")
async def test_blacklisted_token(jwt_refresh_admin_token):
    refresh = await jwt_refresh_admin_token
    response = await send_post(
        url="/api/v1/jwt/blacklist/",
        json={
            "refresh": refresh},
    )
    assert 204 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_get_game_settings(jwt_access_admin_token):
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
    access = await jwt_access_admin_token
    response = await send_get(
        url="/api/v1/admin/settings/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 200 == response.status_code
    for key in settings_attrs:
        assert key in response.json().keys()


@pytest.mark.asyncio(loop_scope="session")
async def test_get_game_settings_perms(jwt_access_token):
    access = await jwt_access_token
    response = await send_get(
        url="/api/v1/admin/settings/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 403 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_game_settings(jwt_access_admin_token):
    access = await jwt_access_admin_token
    response = await send_patch(
        url="/api/v1/admin/settings/",
        json={
            "round_cost": 75,
            "right_ratio": 1.7
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 200 == response.status_code
    assert 75 == response.json()["round_cost"]
    assert 1.7 == response.json()["right_ratio"]


@pytest.mark.asyncio(loop_scope="session")
async def test_patch_game_settings_perms(jwt_access_token):
    access = await jwt_access_token
    response = await send_patch(
        url="/api/v1/admin/settings/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 403 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_get_question_list(jwt_access_admin_token):
    access = await jwt_access_admin_token
    response = await send_get(
        url="/api/v1/admin/question/?page=200&limit=100",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 200 == response.status_code
    assert 100 == len(response.json()["items"])
    assert 427 == response.json()["paginator"]["pages"]
    for item in response.json()["items"]:
        assert item.get("answers")


@pytest.mark.asyncio(loop_scope="session")
async def test_get_question_list_perms(jwt_access_token):
    access = await jwt_access_token
    response = await send_get(
        url="/api/v1/admin/question/?page=200&limit=100",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 403 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_question(jwt_access_admin_token):
    access = await jwt_access_admin_token
    response = await send_delete(
        url="/api/v1/admin/question/200/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 204 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_question_perms(jwt_access_token):
    access = await jwt_access_token
    response = await send_delete(
        url="/api/v1/admin/question/200/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 403 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_create_question(jwt_access_admin_token):
    access = await jwt_access_admin_token
    response = await send_post(
        url="/api/v1/admin/question/",
        json={
            "text": "Кто проживает на дне океана?",
            "published": True,
            "answers": [
                {
                    "text": "Губка Боб",
                    "right": True
                },
                {
                    "text": "Ариель",
                    "right": False
                },
                {
                    "text": "Грубоководный аппарат 'Титан'",
                    "right": False
                },
                {
                    "text": "Мегалодон",
                    "right": False
                },
            ]
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 200 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_create_question_perms(jwt_access_token):
    access = await jwt_access_token
    response = await send_post(
        url="/api/v1/admin/question/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 403 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_create_question_no_right_answer(jwt_access_admin_token):
    access = await jwt_access_admin_token
    response = await send_post(
        url="/api/v1/admin/question/",
        json={
            "text": "Кто проживает на дне океана?",
            "published": True,
            "answers": [
                {
                    "text": "Губка Боб",
                    "right": False
                },
                {
                    "text": "Ариель",
                    "right": False
                },
                {
                    "text": "Грубоководный аппарат 'Титан'",
                    "right": False
                },
                {
                    "text": "Мегалодон",
                    "right": False
                },
            ]
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 400 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_create_question_no_four_answer(jwt_access_admin_token):
    access = await jwt_access_admin_token
    response = await send_post(
        url="/api/v1/admin/question/",
        json={
            "text": "Кто проживает на дне океана?",
            "published": True,
            "answers": [
                {
                    "text": "Губка Боб",
                    "right": True
                },
                {
                    "text": "Ариель",
                    "right": False
                },
                {
                    "text": "Грубоководный аппарат 'Титан'",
                    "right": False
                },
            ]
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 400 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_bulk_create_question(jwt_access_admin_token):
    access = await jwt_access_admin_token
    js = []
    for i in range(1, 500):
        q = {
            "text": f"Вопрос массового создания {i}",
            "published": True,
            "answers": [
                {
                    "text": f"Неправильный ответ1 на вопрос {i}",
                    "right": False
                },
                {
                    "text": f"Неправильный ответ2 на вопрос {i}",
                    "right": False
                },
                {
                    "text": f"Правильный ответ на вопрос {i}",
                    "right": True
                },
                {
                    "text": f"Неправильный ответ3 на вопрос {i}",
                    "right": False
                }
            ]
        }
        js.append(q)

    response = await send_post(
        url="/api/v1/admin/question/bulk_create/",
        json=js,
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 204 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_bulk_create_question_perms(jwt_access_token):
    access = await jwt_access_token
    response = await send_post(
        url="/api/v1/admin/question/bulk_create/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 403 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_edit_question(jwt_access_admin_token):
    access = await jwt_access_admin_token
    response = await send_put(
        url="/api/v1/admin/question/42611/",
        json={
            "id": 42611,
            "text": "Кто проживает на дне океана?",
            "published": True,
            "complaints": 0,
            "answers": [
                {
                    "id": 170449,
                    "text": "Губка Боб квадратные штаны",
                    "right": True
                },
                {
                    "id": 170450,
                    "text": "Ариель",
                    "right": False
                },
                {
                    "id": 170451,
                    "text": "Грубоководный аппарат 'Титан'",
                    "right": False
                },
                {
                    "id": 170452,
                    "text": "Мегалодон",
                    "right": False
                }
            ]
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 200 == response.status_code
    assert "Губка Боб квадратные штаны" == response.json()["answers"][0]["text"]


@pytest.mark.asyncio(loop_scope="session")
async def test_edit_question_perms(jwt_access_token):
    access = await jwt_access_token
    response = await send_put(
        url="/api/v1/admin/question/42611/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 403 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_get_one_question(jwt_access_admin_token):
    access = await jwt_access_admin_token
    response = await send_get(
        url="/api/v1/admin/question/2346/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 200 == response.status_code
    assert "Лучший бомбардир ПСЖ за всю историю?" == response.json()["text"]
    assert 5 == len(response.json()["complaints"])


@pytest.mark.asyncio(loop_scope="session")
async def test_get_one_question_perms(jwt_access_token):
    access = await jwt_access_token
    response = await send_get(
        url="/api/v1/admin/question/2346/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 403 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_get_complaints(jwt_access_admin_token):
    access = await jwt_access_admin_token
    response = await send_get(
        url="/api/v1/admin/complaint/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 200 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_get_complaints_perms(jwt_access_token):
    access = await jwt_access_token
    response = await send_get(
        url="/api/v1/admin/complaint/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 403 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_complaint(jwt_access_admin_token):
    access = await jwt_access_admin_token
    response = await send_delete(
        url="/api/v1/admin/complaint/1/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 204 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_complaint_perms(jwt_access_token):
    access = await jwt_access_token
    response = await send_delete(
        url="/api/v1/admin/complaint/1/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 403 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_get_profiles(jwt_access_admin_token):
    access = await jwt_access_admin_token
    response = await send_get(
        url="/api/v1/admin/profiles/?page=1&limit=2",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 200 == response.status_code
    assert 2 == len(response.json()["items"])


@pytest.mark.asyncio(loop_scope="session")
async def test_get_profiles_perms(jwt_access_token):
    access = await jwt_access_token
    response = await send_get(
        url="/api/v1/admin/profiles/?page=1&limit=2",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 403 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_search_profiles(jwt_access_admin_token):
    access = await jwt_access_admin_token
    response = await send_get(
        url="/api/v1/admin/profiles/?page=1&limit=2&search=знайка",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 200 == response.status_code
    assert 2 == len(response.json()["items"])
    assert 1 == response.json()["paginator"]["pages"]


@pytest.mark.asyncio(loop_scope="session")
async def test_search_profiles_perms(jwt_access_token):
    access = await jwt_access_token
    response = await send_get(
        url="/api/v1/admin/profiles/?page=1&limit=2&search=знайка",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 403 == response.status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_profile_name(jwt_access_admin_token):
    access = await jwt_access_admin_token
    response = await send_post(
        url="/api/v1/admin/profiles/reset_name/2/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 200 == response.status_code
    assert "Игрок-2" == response.json()["name"]


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_profile_name_perms(jwt_access_token):
    access = await jwt_access_token
    response = await send_post(
        url="/api/v1/admin/profiles/reset_name/2/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert 403 == response.status_code
