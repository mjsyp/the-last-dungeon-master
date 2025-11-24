"""Session model."""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel


class Session(BaseModel):
    """A play session."""
    __tablename__ = "sessions"
    
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    name = Column(String(255), nullable=True)  # e.g., "Session 1: Into the Ruins"
    players = Column(JSON, nullable=True)  # Array of player info
    start_real_datetime = Column(DateTime(timezone=True), nullable=True)
    end_real_datetime = Column(DateTime(timezone=True), nullable=True)
    gm_notes = Column(Text, nullable=True)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="sessions")
    events = relationship("Event", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Session(id={self.id}, name='{self.name}', campaign_id={self.campaign_id})>"

