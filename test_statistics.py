import uuid

import allure
import requests

from utils import REQUEST_TIMEOUT

pytestmark = allure.suite("Статистика")


@allure.title("API-13. Получение статистики существующего объявления в v1 и v2")
def test_api_13_get_statistics_for_existing_item(base_url, auth_headers, create_item):
    item_id, payload = create_item()

    for version in (1, 2):
        with allure.step(f"Сверить счётчики статистики v{version}"):
            response = requests.get(
                url=f"{base_url}/api/{version}/statistic/{item_id}",
                headers=auth_headers,
                timeout=REQUEST_TIMEOUT,
            )

            assert response.status_code == 200
            assert response.json() == [payload["statistics"]]


@allure.title("API-14. Получение статистики по неизвестному UUID в v1 и v2")
def test_api_14_get_statistics_for_unknown_item(base_url, auth_headers):
    item_id = str(uuid.uuid4())
    expected_error = {
        "result": {
            "message": f"statistic {item_id} not found",
            "messages": None,
        },
        "status": "404",
    }

    for version in (1, 2):
        with allure.step(f"Проверить ошибку для неизвестного UUID в v{version}"):
            response = requests.get(
                url=f"{base_url}/api/{version}/statistic/{item_id}",
                headers=auth_headers,
                timeout=REQUEST_TIMEOUT,
            )

            assert response.status_code == 404
            assert response.json() == expected_error
