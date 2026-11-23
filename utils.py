import json
import uuid

import allure
import requests

REQUEST_TIMEOUT = (10, 60)


def build_item_payload(seller_id, item_name):
    return {
        "sellerID": seller_id,
        "name": item_name,
        "price": 1337,
        "statistics": {
            "likes": 67,
            "viewCount": 52,
            "contacts": 42,
        },
    }


def attach_item_creation_error(response):
    details = {"http_status": response.status_code}
    try:
        body = response.json()
    except requests.exceptions.JSONDecodeError:
        body = None

    if isinstance(body, dict):
        result = body.get("result")
        if isinstance(result, dict) and isinstance(result.get("message"), str):
            details["result"] = {"message": result["message"]}

    allure.attach(
        json.dumps(details, ensure_ascii=False, indent=2),
        name="Ответ при ошибке создания объявления",
        attachment_type=allure.attachment_type.JSON,
    )


def generate_password():
    return f"test_password_{uuid.uuid4().hex[:8]}"


def generate_username():
    return f"test_username_{uuid.uuid4().hex[:8]}"


def generate_item_name():
    return f"test_item_{uuid.uuid4().hex[:8]}"


def register_test_user(base_url, username):
    password = generate_password()

    payload = {
        "username": username,
        "password": password,
    }

    response = requests.post(
        url=f"{base_url}/api/1/register",
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 201

    body = response.json()

    return {
        "id": body["id"],
        "username": body["username"],
        "password": password,
    }


def authorize_test_user(base_url, user):
    payload = {
        "username": user["username"],
        "password": user["password"],
    }

    response = requests.post(
        url=f"{base_url}/api/1/autorize",
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200

    body = response.json()
    token = body["accessToken"]

    assert isinstance(token, str) and token
    assert body["tokenType"] == "Bearer"

    return {"Authorization": f"Bearer {token}"}


def assert_item_not_created(base_url, item_name, sellers, delete_item):
    created_items = []
    try:
        for user, headers in sellers:
            response = requests.get(
                url=f"{base_url}/api/1/{user['id']}/item",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            assert response.status_code == 200

            body = response.json()
            for item in body:
                if item["name"] == item_name:
                    created_items.append((item["id"], headers))

        assert not created_items
    finally:
        for item_id, headers in created_items:
            delete_item(item_id, headers)


def assert_bearer_token_required(response):
    assert response.status_code == 401
    assert response.json() == {"error": "valid bearer token is required"}
