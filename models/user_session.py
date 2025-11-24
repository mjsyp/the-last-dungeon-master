"""User session model for storing orchestrator state."""
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql import func
from models.base import BaseModel


class UserSession(BaseModel):
    """Stores orchestrator session state."""
    __tablename__ = "user_sessions"
    
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    state_json = Column(JSON, nullable=False)  # Serialized SessionState
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, session_id='{self.session_id}')>"

