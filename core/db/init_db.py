"""Database initialization utilities."""
from core.db.session import engine, Base
from models import (
    Universe, Campaign, Location, Character, Faction, Event, Session,
    PlayerGroup, GroupMember, PlayerState, RuleSystem, RulesTopic,
    TutorialScript, WorldChangeRequest, UserSession
)


def init_db():
    """Initialize database tables."""
    # Import all models to ensure they're registered
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


def drop_db():
    """Drop all database tables (use with caution!)."""
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_db()
    else:
        init_db()

