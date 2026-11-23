import uuid

import allure
import pytest
import requests

from utils import (
    REQUEST_TIMEOUT,
    attach_item_creation_error,
    authorize_test_user,
    build_item_payload,
    generate_item_name,
    generate_password,
    generate_username,
    register_test_user,
)


@pytest.fixture(scope="session")
def base_url():
    return "https://qa-internship.avito.com"


@pytest.fixture(scope="function")
def username():
    return generate_username()


@pytest.fixture(scope="function")
def password():
    password = generate_password()
    return password


@pytest.fixture(scope="function")
def item_name():
    return generate_item_name()


@pytest.fixture(scope="function")
def registered_user(base_url, username):
    with allure.step("Зарегистрировать тестового пользователя"):
        return register_test_user(base_url, username)


@pytest.fixture(scope="function")
def auth_headers(base_url, registered_user):
    with allure.step("Получить токен тестового пользователя"):
        return authorize_test_user(base_url, registered_user)


@pytest.fixture(scope="function")
def second_user(base_url):
    with allure.step("Подготовить второго тестового пользователя"):
        user = register_test_user(base_url, generate_username())
        return user, authorize_test_user(base_url, user)


@pytest.fixture(scope="function")
def item_ids_to_delete():
    return set()


@pytest.fixture(scope="function")
def delete_item(base_url, item_ids_to_delete):
    def delete(item_id, headers):
        with allure.step("Удалить тестовое объявление"):
            response = requests.delete(
                url=f"{base_url}/api/2/item/{item_id}",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            assert response.status_code == 200
            item_ids_to_delete.discard(item_id)

    return delete


@pytest.fixture(scope="function")
def create_item(base_url, registered_user, auth_headers, delete_item, item_ids_to_delete):
    def create(payload=None, *, attach_error=False):
        if payload is None:
            payload = build_item_payload(registered_user["id"], generate_item_name())

        with allure.step("Создать тестовое объявление и получить UUID"):
            response = requests.post(
                url=f"{base_url}/api/1/item",
                json=payload,
                headers=auth_headers,
                timeout=REQUEST_TIMEOUT,
            )

            if attach_error and response.status_code != 200:
                attach_item_creation_error(response)

            assert response.status_code == 200

            body = response.json()

            assert isinstance(body["status"], str)
            item_id_text = body["status"].rsplit(" - ", 1)[-1]
            item_id = str(uuid.UUID(item_id_text))
            item_ids_to_delete.add(item_id)

            return item_id, payload

    yield create

    for item_id in item_ids_to_delete.copy():
        delete_item(item_id, auth_headers)
