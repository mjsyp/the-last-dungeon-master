"""Event model."""
from sqlalchemy import Column, String, Text, ForeignKey, ARRAY, Integer
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel


class Event(BaseModel):
    """An event that occurred in the world."""
    __tablename__ = "events"
    
    universe_id = Column(String(36), ForeignKey("universes.id"), nullable=False)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=True)
    session_turn_index = Column(Integer, nullable=True)  # Which turn in the session
    time_in_world = Column(String(255), nullable=True)  # e.g., "12th Day of the Ember Moon, 1032 AE"
    summary = Column(String(500), nullable=False)
    full_text = Column(Text, nullable=True)
    involved_locations = Column(JSON, nullable=True)  # Array of location IDs
    involved_characters = Column(JSON, nullable=True)  # Array of character IDs
    tags = Column(JSON, nullable=True)  # e.g., ["battle", "social", "travel", "mystery"]
    
    # Relationships
    universe = relationship("Universe", back_populates="events")
    campaign = relationship("Campaign", back_populates="events")
    session = relationship("Session", back_populates="events")
    
    def __repr__(self):
        return f"<Event(id={self.id}, summary='{self.summary[:50]}...')>"

