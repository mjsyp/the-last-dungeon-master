"""Base model with common fields."""
from sqlalchemy import Column, DateTime, String, func
import uuid
from core.db.session import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class BaseModel(Base, TimestampMixin):
    """Base model with UUID primary key and timestamps."""
    __abstract__ = True
    
    # Use String for UUID to support both PostgreSQL and SQLite
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)

