from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


NonEmptyString = Annotated[str, Field(min_length=1)]


class OrderStatus(str, Enum):
    NEW = "New"
    PREPARING = "Preparing"
    OUT_FOR_DELIVERY = "Out for delivery"
    DELIVERED = "Delivered"


class Order(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: NonEmptyString
    customer_name: NonEmptyString
    delivery_address: NonEmptyString
    order_summary: NonEmptyString
    status: OrderStatus


class CreateOrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_name: NonEmptyString
    delivery_address: NonEmptyString
    order_summary: NonEmptyString


class UpdateOrderStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: OrderStatus
