import allure
import requests

from utils import (
    REQUEST_TIMEOUT,
    assert_bearer_token_required,
    assert_item_not_created,
    build_item_payload,
)

pytestmark = allure.suite("Проверки доступа")

UNAUTHORIZED_CASES: tuple[tuple[str, dict[str, str]], ...] = (
    ("Запрос без токена", {}),
    ("Запрос с невалидным токеном", {"Authorization": "Bearer invalid"}),
)


@allure.title("API-16. Создание объявления требует валидного токена")
def test_api_16_create_item_requires_valid_token(
    base_url,
    registered_user,
    auth_headers,
    item_name,
    delete_item,
):
    payload = build_item_payload(registered_user["id"], item_name)
    sellers = ((registered_user, auth_headers),)

    for step_name, headers in UNAUTHORIZED_CASES:
        with allure.step(step_name):
            response = requests.post(
                url=f"{base_url}/api/1/item",
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            assert_item_not_created(base_url, item_name, sellers, delete_item)
            assert_bearer_token_required(response)


@allure.title("API-17. Получение объявления требует валидного токена")
def test_api_17_get_item_requires_valid_token(base_url, create_item):
    item_id, _ = create_item()

    for step_name, headers in UNAUTHORIZED_CASES:
        with allure.step(step_name):
            response = requests.get(
                url=f"{base_url}/api/1/item/{item_id}",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            assert_bearer_token_required(response)


@allure.title("API-18. Получение списка продавца требует валидного токена")
def test_api_18_get_seller_items_requires_valid_token(base_url, registered_user, create_item):
    create_item()

    for step_name, headers in UNAUTHORIZED_CASES:
        with allure.step(step_name):
            response = requests.get(
                url=f"{base_url}/api/1/{registered_user['id']}/item",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            assert_bearer_token_required(response)


@allure.title("API-19. Получение статистики v1 требует валидного токена")
def test_api_19_get_statistics_v1_requires_valid_token(base_url, create_item):
    item_id, _ = create_item()

    for step_name, headers in UNAUTHORIZED_CASES:
        with allure.step(step_name):
            response = requests.get(
                url=f"{base_url}/api/1/statistic/{item_id}",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            assert_bearer_token_required(response)


@allure.title("API-20. Получение статистики v2 требует валидного токена")
def test_api_20_get_statistics_v2_requires_valid_token(base_url, create_item):
    item_id, _ = create_item()

    for step_name, headers in UNAUTHORIZED_CASES:
        with allure.step(step_name):
            response = requests.get(
                url=f"{base_url}/api/2/statistic/{item_id}",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            assert_bearer_token_required(response)


@allure.title("API-21. Удаление объявления требует валидного токена")
def test_api_21_delete_item_requires_valid_token(
    base_url,
    auth_headers,
    create_item,
    item_ids_to_delete,
):
    item_id, _ = create_item()

    for step_name, headers in UNAUTHORIZED_CASES:
        with allure.step(step_name):
            delete_response = requests.delete(
                url=f"{base_url}/api/2/item/{item_id}",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            response = requests.get(
                url=f"{base_url}/api/1/item/{item_id}",
                headers=auth_headers,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 404:
                item_ids_to_delete.discard(item_id)

            assert_bearer_token_required(delete_response)
            assert response.status_code == 200

            body = response.json()
            if isinstance(body, list):
                assert len(body) == 1
                body = body[0]

            assert body["id"] == item_id
