import allure
import requests

from utils import REQUEST_TIMEOUT

pytestmark = allure.suite("Регистрация и вход")


@allure.title("API-01. Регистрация пользователя с новым именем")
def test_api_01_register_with_unique_username(base_url, username, password):
    payload = {
        "username": username,
        "password": password,
    }

    with allure.step("Зарегистрировать пользователя и проверить ответ"):
        response = requests.post(
            url=f"{base_url}/api/1/register",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 201, f"Полученный статус: {response.status_code}"

        body = response.json()

        assert isinstance(body["id"], int)
        assert body["username"] == username


@allure.title("API-02. Регистрация с уже занятым именем")
def test_api_02_register_with_duplicate_username(base_url, registered_user):
    payload = {
        "username": registered_user["username"],
        "password": registered_user["password"],
    }

    with allure.step("Проверить отказ при повторной регистрации"):
        response = requests.post(
            url=f"{base_url}/api/1/register",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 409

        body = response.json()

        assert body["error"] == "username is already registered"


@allure.title("API-03. Вход с корректным именем и паролем")
def test_api_03_authorize_with_valid_credentials(base_url, registered_user):
    payload = {
        "username": registered_user["username"],
        "password": registered_user["password"],
    }

    with allure.step("Войти и проверить выданный токен"):
        response = requests.post(
            url=f"{base_url}/api/1/autorize",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 200

        body = response.json()

        access_token = body["accessToken"]
        assert isinstance(access_token, str) and access_token
        assert body["tokenType"] == "Bearer"

    with allure.step("Проверить доступ с полученным токеном"):
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(
            url=f"{base_url}/api/1/{registered_user['id']}/item",
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 200


@allure.title("API-04. Вход с неверным паролем")
def test_api_04_authorize_with_wrong_password(base_url, registered_user, password):
    payload = {
        "username": registered_user["username"],
        "password": password,
    }

    with allure.step("Проверить отказ при неверном пароле"):
        response = requests.post(
            url=f"{base_url}/api/1/autorize",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 401

        body = response.json()

        assert "accessToken" not in body

        assert body["error"] == "invalid username or password"


@allure.title("API-05. Вход с незарегистрированным именем")
def test_api_05_authorize_with_unknown_username(base_url, username, password):
    payload = {
        "username": username,
        "password": password,
    }

    with allure.step("Проверить отказ для незарегистрированного имени"):
        response = requests.post(
            url=f"{base_url}/api/1/autorize",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 401

        body = response.json()

        assert "accessToken" not in body
