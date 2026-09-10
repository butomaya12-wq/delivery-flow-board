from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OrderRecord(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_name: Mapped[str] = mapped_column(String, nullable=False)
    delivery_address: Mapped[str] = mapped_column(String, nullable=False)
    order_summary: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
