"""SQLAlchemy models and database session.
"""

import typing as t

from sqlalchemy import (
    create_engine,
    Column,
    String,
    JSON,
    Date,
    DateTime,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

from uptrain.utilities.utils import get_uuid, get_current_datetime


SQLBase = declarative_base()


class ModelDataset(SQLBase):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, nullable=False, default=get_uuid)
    created_at = Column(DateTime, default=get_current_datetime)
    name = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    rows_count = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "name", "version", name="uix_dataset"),
    )


class ModelPrompt(SQLBase):
    __tablename__ = "prompts"

    id = Column(String, primary_key=True, nullable=False, default=get_uuid)
    created_at = Column(DateTime, default=get_current_datetime)
    name = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    prompt = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("user_id", "name", "version", name="uix_prompt"),
    )


class ModelUser(SQLBase):
    __tablename__ = "users"

    id = Column(String, primary_key=True, nullable=False, default=get_uuid)
    created_at = Column(DateTime, default=get_current_datetime)
    updated_at = Column(DateTime, default=get_current_datetime)
    name = Column(String, nullable=False, index=True)
    is_active = Column(Boolean, default=True)

    __table_args__ = (UniqueConstraint("name", name="uix_user"),)


def create_database(db_url):
    """Create the database and tables, and return back a session factory."""
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )
    SQLBase.metadata.create_all(bind=engine)
    return SessionLocal
