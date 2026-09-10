from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

import app.main as main_module
from app.database import Base
from app.db_models import OrderRecord
from app.store import SqlAlchemyOrderStore


def create_order_payload(**overrides: str) -> dict[str, str]:
    payload = {
        "customer_name": "Alex Johnson",
        "delivery_address": "10 Main Street",
        "order_summary": "Two vegetarian meals",
    }
    payload.update(overrides)
    return payload


@pytest.fixture
def database(
    tmp_path: Path,
) -> Iterator[tuple[sessionmaker[Session], Engine]]:
    database_url = f"sqlite:///{tmp_path / 'orders.db'}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    yield session_factory, engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def order_store(database: tuple[sessionmaker[Session], Engine]) -> SqlAlchemyOrderStore:
    session_factory, engine = database
    return SqlAlchemyOrderStore(session_factory, engine)


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, order_store: SqlAlchemyOrderStore) -> TestClient:
    monkeypatch.setattr(main_module, "order_store", order_store)
    return TestClient(main_module.app)


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


def test_list_orders_returns_persisted_orders(client: TestClient) -> None:
    first_order = client.post("/api/orders", json=create_order_payload()).json()
    second_order = client.post(
        "/api/orders",
        json=create_order_payload(customer_name="Blair Taylor"),
    ).json()

    response = client.get("/api/orders")
    returned_orders = {order["order_id"]: order for order in response.json()}

    assert response.status_code == 200
    assert returned_orders == {
        first_order["order_id"]: first_order,
        second_order["order_id"]: second_order,
    }


def test_update_order_status_persists_the_change(
    client: TestClient, database: tuple[sessionmaker[Session], Engine]
) -> None:
    created_order = client.post("/api/orders", json=create_order_payload()).json()

    response = client.patch(
        f"/api/orders/{created_order['order_id']}/status",
        json={"status": "Out for delivery"},
    )

    session_factory, _ = database
    with session_factory() as session:
        persisted_order = session.scalar(
            select(OrderRecord).where(OrderRecord.order_id == created_order["order_id"])
        )

    assert response.status_code == 200
    assert response.json()["status"] == "Out for delivery"
    assert persisted_order is not None
    assert persisted_order.status == "Out for delivery"


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
    orders_by_id = {order["order_id"]: order for order in client.get("/api/orders").json()}

    assert response.status_code == 200
    assert orders_by_id[first_order["order_id"]]["status"] == "Preparing"
    assert orders_by_id[second_order["order_id"]] == second_order


def test_order_survives_a_new_database_session(
    client: TestClient, database: tuple[sessionmaker[Session], Engine]
) -> None:
    created_order = client.post("/api/orders", json=create_order_payload()).json()

    session_factory, _ = database
    with session_factory() as session:
        persisted_order = session.scalar(
            select(OrderRecord).where(OrderRecord.order_id == created_order["order_id"])
        )

    assert persisted_order is not None
    assert persisted_order.customer_name == "Alex Johnson"


def test_persistence_layer_reads_previously_committed_data(
    order_store: SqlAlchemyOrderStore, database: tuple[sessionmaker[Session], Engine]
) -> None:
    session_factory, _ = database
    with session_factory() as session:
        session.add(
            OrderRecord(
                order_id="ORD-existing",
                customer_name="Casey Morgan",
                delivery_address="30 River Road",
                order_summary="One pasta",
                status="Delivered",
            )
        )
        session.commit()

    orders = order_store.list_orders()

    assert len(orders) == 1
    assert orders[0].order_id == "ORD-existing"
    assert orders[0].status == "Delivered"
