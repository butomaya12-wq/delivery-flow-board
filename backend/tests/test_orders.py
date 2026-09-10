import pytest
from fastapi.testclient import TestClient

from app.main import app, order_store


def create_order_payload(**overrides: str) -> dict[str, str]:
    payload = {
        "customer_name": "Alex Johnson",
        "delivery_address": "10 Main Street",
        "order_summary": "Two vegetarian meals",
    }
    payload.update(overrides)
    return payload


@pytest.fixture(autouse=True)
def reset_order_store() -> None:
    order_store.clear()
    yield
    order_store.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_list_orders_returns_empty_list_initially(client: TestClient) -> None:
    response = client.get("/api/orders")

    assert response.status_code == 200
    assert response.json() == []


def test_cors_allows_the_local_vite_origin(client: TestClient) -> None:
    response = client.options(
        "/api/orders",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_create_order_returns_created_order(client: TestClient) -> None:
    response = client.post("/api/orders", json=create_order_payload())

    assert response.status_code == 201
    assert response.json()["customer_name"] == "Alex Johnson"
    assert response.json()["delivery_address"] == "10 Main Street"
    assert response.json()["order_summary"] == "Two vegetarian meals"


def test_create_order_generates_order_id(client: TestClient) -> None:
    response = client.post("/api/orders", json=create_order_payload())

    assert response.status_code == 201
    assert response.json()["order_id"].startswith("ORD-")


def test_create_order_sets_new_status(client: TestClient) -> None:
    response = client.post("/api/orders", json=create_order_payload())

    assert response.status_code == 201
    assert response.json()["status"] == "New"


def test_create_order_rejects_missing_required_field(client: TestClient) -> None:
    response = client.post(
        "/api/orders",
        json={
            "customer_name": "Alex Johnson",
            "delivery_address": "10 Main Street",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field",
    ["customer_name", "delivery_address", "order_summary"],
)
def test_create_order_rejects_empty_required_string(
    client: TestClient, field: str
) -> None:
    response = client.post(
        "/api/orders",
        json=create_order_payload(**{field: ""}),
    )

    assert response.status_code == 422


def test_create_order_rejects_client_supplied_order_id_and_status(client: TestClient) -> None:
    response = client.post(
        "/api/orders",
        json=create_order_payload(order_id="ORD-client", status="Delivered"),
    )

    assert response.status_code == 422


def test_list_orders_returns_created_orders(client: TestClient) -> None:
    first_response = client.post("/api/orders", json=create_order_payload())
    second_response = client.post(
        "/api/orders",
        json=create_order_payload(customer_name="Blair Taylor"),
    )

    response = client.get("/api/orders")

    assert response.status_code == 200
    assert response.json() == [first_response.json(), second_response.json()]


def test_update_order_status_returns_updated_order(client: TestClient) -> None:
    created_order = client.post("/api/orders", json=create_order_payload()).json()

    response = client.patch(
        f"/api/orders/{created_order['order_id']}/status",
        json={"status": "Out for delivery"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Out for delivery"


def test_update_order_status_returns_not_found_for_unknown_order(client: TestClient) -> None:
    response = client.patch(
        "/api/orders/ORD-unknown/status",
        json={"status": "Delivered"},
    )

    assert response.status_code == 404


def test_update_order_status_rejects_invalid_status(client: TestClient) -> None:
    created_order = client.post("/api/orders", json=create_order_payload()).json()

    response = client.patch(
        f"/api/orders/{created_order['order_id']}/status",
        json={"status": "Out for Delivery"},
    )

    assert response.status_code == 422


def test_updating_order_does_not_modify_another_order(client: TestClient) -> None:
    first_order = client.post("/api/orders", json=create_order_payload()).json()
    second_order = client.post(
        "/api/orders",
        json=create_order_payload(
            customer_name="Blair Taylor",
            delivery_address="20 Market Street",
            order_summary="One soup",
        ),
    ).json()

    response = client.patch(
        f"/api/orders/{first_order['order_id']}/status",
        json={"status": "Preparing"},
    )

    assert response.status_code == 200
    orders_by_id = {order["order_id"]: order for order in client.get("/api/orders").json()}
    assert orders_by_id[first_order["order_id"]]["status"] == "Preparing"
    assert orders_by_id[second_order["order_id"]] == second_order
