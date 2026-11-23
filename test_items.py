import uuid

import allure
import pytest
import requests

from utils import REQUEST_TIMEOUT, assert_item_not_created, build_item_payload

pytestmark = allure.suite("Объявления")


@allure.title("API-06. Создание объявления со своим sellerID")
def test_api_06_create_item_with_own_seller_id(base_url, auth_headers, create_item):
    item_id, payload = create_item()

    with allure.step("Получить объявление и сверить его данные"):
        response = requests.get(
            url=f"{base_url}/api/1/item/{item_id}",
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 200

        body = response.json()
        if isinstance(body, list):
            assert len(body) == 1
            body = body[0]

        assert body["id"] == item_id
        assert body["name"] == payload["name"]
        assert body["price"] == payload["price"]
        assert body.get("sellerID", body.get("sellerId")) == payload["sellerID"]


@allure.title("API-07. Одинаковые объявления получают разные UUID")
def test_api_07_create_identical_items_with_different_ids(
    base_url,
    registered_user,
    auth_headers,
    create_item,
):
    first_item_id, payload = create_item()
    second_item_id, _ = create_item(payload)

    with allure.step("Сравнить UUID и проверить оба объявления в списке"):
        assert first_item_id != second_item_id

        response = requests.get(
            url=f"{base_url}/api/1/{registered_user['id']}/item",
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 200

        body = response.json()
        item_ids = {item["id"] for item in body}

        assert first_item_id in item_ids
        assert second_item_id in item_ids


@allure.title("API-08. Создание объявления с sellerID другого пользователя")
def test_api_08_create_item_with_another_seller_id(
    base_url,
    registered_user,
    auth_headers,
    second_user,
    item_name,
    delete_item,
):
    other_user, other_headers = second_user
    payload = build_item_payload(other_user["id"], item_name)
    sellers = ((registered_user, auth_headers), (other_user, other_headers))

    with allure.step("Отправить запрос с sellerID другого пользователя"):
        create_response = requests.post(
            url=f"{base_url}/api/1/item",
            json=payload,
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT,
        )

    with allure.step("Проверить отказ и отсутствие нового объявления"):
        assert_item_not_created(base_url, item_name, sellers, delete_item)
        assert create_response.status_code == 400


@allure.title("API-09. X-UserId не меняет владельца объявления")
def test_api_09_create_item_with_x_user_id(
    base_url,
    registered_user,
    auth_headers,
    second_user,
    item_name,
    delete_item,
):
    other_user, other_headers = second_user
    payload = build_item_payload(other_user["id"], item_name)
    sellers = ((registered_user, auth_headers), (other_user, other_headers))
    headers = {**auth_headers, "X-UserId": str(other_user["id"])}

    with allure.step("Отправить запрос с заголовком X-UserId"):
        create_response = requests.post(
            url=f"{base_url}/api/1/item",
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )

    with allure.step("Проверить отказ и отсутствие нового объявления"):
        assert_item_not_created(base_url, item_name, sellers, delete_item)
        assert create_response.status_code == 400


@allure.title("API-10. Создание объявления с нечисловой ценой")
@allure.tag("BUG-01")
def test_api_10_create_item_with_non_numeric_price(
    base_url,
    registered_user,
    auth_headers,
    item_name,
    delete_item,
):
    payload = build_item_payload(registered_user["id"], item_name)
    payload["price"] = "abc"

    with allure.step("Отправить объявление с нечисловой ценой"):
        response = requests.post(
            url=f"{base_url}/api/1/item",
            json=payload,
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT,
        )

    with allure.step("Проверить отказ и отсутствие нового объявления"):
        assert_item_not_created(
            base_url, item_name, ((registered_user, auth_headers),), delete_item
        )
        assert response.status_code == 400
        assert response.json()["status"] == "не передано тело объявления"


@allure.title("API-11. Получение объявления по неизвестному UUID")
def test_api_11_get_item_with_unknown_id(base_url, auth_headers):
    item_id = str(uuid.uuid4())

    with allure.step("Запросить объявление по неизвестному UUID"):
        response = requests.get(
            url=f"{base_url}/api/1/item/{item_id}",
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 404


@allure.title("API-12. Список объявлений нового продавца пуст")
def test_api_12_get_items_for_new_seller(base_url, registered_user, auth_headers):
    with allure.step("Проверить пустой список нового продавца"):
        response = requests.get(
            url=f"{base_url}/api/1/{registered_user['id']}/item",
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 200

        assert response.json() == []


@allure.title("API-15. Удаление существующего объявления")
def test_api_15_delete_existing_item(base_url, auth_headers, create_item, delete_item):
    item_id, _ = create_item()
    delete_item(item_id, auth_headers)

    with allure.step("Проверить, что удалённое объявление недоступно"):
        response = requests.get(
            url=f"{base_url}/api/1/item/{item_id}",
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 404


@pytest.mark.parametrize("counter", ("likes", "viewCount", "contacts", "all_counters"))
@allure.title("API-22. Создание объявления с нулевыми счётчиками статистики ({counter})")
@allure.tag("BUG-03")
def test_api_22_create_item_with_zero_statistics(
    base_url,
    registered_user,
    auth_headers,
    item_name,
    create_item,
    counter,
):
    payload = build_item_payload(registered_user["id"], item_name)
    statistics = payload["statistics"]
    counters = statistics if counter == "all_counters" else (counter,)
    for field in counters:
        statistics[field] = 0

    item_id, _ = create_item(payload, attach_error=True)

    with allure.step("Проверить сохранённые счётчики статистики"):
        response = requests.get(
            url=f"{base_url}/api/1/statistic/{item_id}",
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 200
        assert response.json() == [payload["statistics"]]
