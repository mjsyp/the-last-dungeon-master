"""Database compatibility helpers for SQLite and PostgreSQL."""
from sqlalchemy import String, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY as PG_ARRAY, JSONB as PG_JSONB
from config.settings import settings
import json


# Detect database type from URL
def is_postgresql():
    """Check if using PostgreSQL."""
    return settings.database_url.startswith('postgresql')


# Type compatibility
if is_postgresql():
    UUID = PG_UUID(as_uuid=True)
    ARRAY = PG_ARRAY
    JSONB = PG_JSONB
else:
    # SQLite compatibility
    UUID = String(36)  # Store UUID as string
    ARRAY = JSON  # Store arrays as JSON
    JSONB = JSON  # JSONB becomes JSON


def uuid_column(**kwargs):
    """Create a UUID column compatible with both databases."""
    if is_postgresql():
        return PG_UUID(as_uuid=True, **kwargs)
    else:
        return String(36, **kwargs)


def array_column(item_type, **kwargs):
    """Create an array column compatible with both databases."""
    if is_postgresql():
        return PG_ARRAY(item_type, **kwargs)
    else:
        return JSON(**kwargs)


def jsonb_column(**kwargs):
    """Create a JSONB/JSON column compatible with both databases."""
    if is_postgresql():
        return PG_JSONB(**kwargs)
    else:
        return JSON(**kwargs)

