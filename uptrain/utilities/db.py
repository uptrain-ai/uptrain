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


class ModelProjectDataset(SQLBase):
    __tablename__ = "project_datasets"

    id = Column(String, primary_key=True, nullable=False, default=get_uuid)
    created_at = Column(DateTime, default=get_current_datetime)
    name = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    project_id = Column(String, nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    rows_count = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("project_id", "name", "version", name="uix_dataset"),
    )


class ModelPrompt(SQLBase):
    __tablename__ = "prompts"

    id = Column(String, primary_key=True, nullable=False, default=get_uuid)
    project_id =  Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=get_current_datetime)
    name = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    prompt = Column(String, nullable=False)
    checks = Column(JSON, nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("project_id", "name", "version", name="uix_prompt"),
    )


class ModelProjectRun(SQLBase):
    __tablename__ = "project_runs"

    id = Column(String, primary_key=True, nullable=False, default=get_uuid)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=get_current_datetime)
    updated_at = Column(DateTime, default=get_current_datetime)
    address = Column(String, nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    dataset_id = Column(String, ForeignKey("project_datasets.id"), nullable=False)
    prompt_id =  Column(String, ForeignKey("prompts.id"), nullable=True, default=None)
    status = Column(String, nullable=True)
    run_type = Column(String, nullable=False)
    exp_column = Column(String, nullable=True, default = None)
    checks = Column(JSON, nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

class ModelProject(SQLBase):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, nullable=False, default=get_uuid)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=get_current_datetime)
    updated_at = Column(DateTime, default=get_current_datetime)
    dataset_id = Column(String, ForeignKey("project_datasets.id"), nullable=False)
    checks = Column(JSON, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)


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
