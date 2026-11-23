import allure
import requests

from utils import REQUEST_TIMEOUT

pytestmark = allure.suite("Сквозной сценарий")


@allure.title("API-23. Полный жизненный цикл объявления")
def test_api_23_item_lifecycle(base_url, auth_headers, create_item, delete_item):
    item_id, payload = create_item()
    item_url = f"{base_url}/api/1/item/{item_id}"

    with allure.step("Получить объявление и проверить сохранённые поля"):
        response = requests.get(
            url=item_url,
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

    with allure.step("Получить статистику и сверить счётчики"):
        response = requests.get(
            url=f"{base_url}/api/1/statistic/{item_id}",
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 200
        assert response.json() == [payload["statistics"]]

    delete_item(item_id, auth_headers)

    with allure.step("Убедиться, что объявление больше не доступно"):
        response = requests.get(
            url=item_url,
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 404
