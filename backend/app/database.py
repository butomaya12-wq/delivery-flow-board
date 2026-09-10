import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent.parent / "delivery_flow_board.db"
DATABASE_URL = os.getenv(
    "DELIVERY_FLOW_BOARD_DATABASE_URL",
    f"sqlite:///{DEFAULT_DATABASE_PATH}",
)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
