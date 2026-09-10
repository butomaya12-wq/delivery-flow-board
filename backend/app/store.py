from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.db_models import OrderRecord
from app.models import CreateOrderRequest, Order, OrderStatus


class SqlAlchemyOrderStore:
    def __init__(self, session_factory: sessionmaker[Session], database_engine: Engine) -> None:
        self._session_factory = session_factory
        self._database_engine = database_engine

    def initialize(self) -> None:
        Base.metadata.create_all(bind=self._database_engine)

    def list_orders(self) -> list[Order]:
        with self._session_factory() as session:
            records = session.scalars(select(OrderRecord).order_by(OrderRecord.order_id)).all()
            return [self._to_api_order(record) for record in records]

    def create_order(self, request: CreateOrderRequest) -> Order:
        record = OrderRecord(
            order_id=f"ORD-{uuid4()}",
            customer_name=request.customer_name,
            delivery_address=request.delivery_address,
            order_summary=request.order_summary,
            status=OrderStatus.NEW.value,
        )

        with self._session_factory() as session:
            session.add(record)
            session.commit()
            session.refresh(record)
            return self._to_api_order(record)

    def update_order_status(self, order_id: str, status: OrderStatus) -> Order | None:
        with self._session_factory() as session:
            record = session.scalar(select(OrderRecord).where(OrderRecord.order_id == order_id))

            if record is None:
                return None

            record.status = status.value
            session.commit()
            session.refresh(record)
            return self._to_api_order(record)

    @staticmethod
    def _to_api_order(record: OrderRecord) -> Order:
        return Order(
            order_id=record.order_id,
            customer_name=record.customer_name,
            delivery_address=record.delivery_address,
            order_summary=record.order_summary,
            status=record.status,
        )
