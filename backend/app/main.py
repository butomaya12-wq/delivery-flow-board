from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, status
from fastapi.middleware.cors import CORSMiddleware

from app.models import CreateOrderRequest, Order, UpdateOrderStatusRequest
from app.store import InMemoryOrderStore


app = FastAPI(title="Delivery Flow Board API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type"],
)
order_store = InMemoryOrderStore()


@app.get(
    "/api/orders",
    operation_id="listOrders",
    response_model=list[Order],
    responses={500: {"description": "Server failure."}},
)
def list_orders() -> list[Order]:
    return order_store.list_orders()


@app.post(
    "/api/orders",
    operation_id="createOrder",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {"description": "Validation failure."},
        500: {"description": "Server failure."},
    },
)
def create_order(request: CreateOrderRequest) -> Order:
    return order_store.create_order(request)


@app.patch(
    "/api/orders/{order_id}/status",
    operation_id="updateOrderStatus",
    response_model=Order,
    responses={
        404: {"description": "Order not found."},
        422: {"description": "Validation failure or unsupported status."},
        500: {"description": "Server failure."},
    },
)
def update_order_status(
    order_id: Annotated[str, Path(min_length=1)],
    request: UpdateOrderStatusRequest,
) -> Order:
    updated_order = order_store.update_order_status(order_id, request.status)

    if updated_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return updated_order
