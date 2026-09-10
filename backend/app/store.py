from uuid import uuid4

from app.models import CreateOrderRequest, Order, OrderStatus


class InMemoryOrderStore:
    """Temporary order storage with the same operations a database-backed store will expose."""

    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}

    def list_orders(self) -> list[Order]:
        return [order.model_copy(deep=True) for order in self._orders.values()]

    def create_order(self, request: CreateOrderRequest) -> Order:
        order = Order(
            order_id=f"ORD-{uuid4()}",
            customer_name=request.customer_name,
            delivery_address=request.delivery_address,
            order_summary=request.order_summary,
            status=OrderStatus.NEW,
        )
        self._orders[order.order_id] = order
        return order.model_copy(deep=True)

    def update_order_status(self, order_id: str, status: OrderStatus) -> Order | None:
        order = self._orders.get(order_id)

        if order is None:
            return None

        updated_order = order.model_copy(update={"status": status})
        self._orders[order_id] = updated_order
        return updated_order.model_copy(deep=True)

    def clear(self) -> None:
        self._orders.clear()
