"""Campaign model."""
from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel


class Campaign(BaseModel):
    """A campaign within a universe."""
    __tablename__ = "campaigns"
    
    universe_id = Column(String(36), ForeignKey("universes.id"), nullable=True)  # UUID as string
    name = Column(String(255), nullable=False)
    genre = Column(String(100), nullable=True)  # e.g., "high fantasy", "sci-fi"
    tone = Column(String(100), nullable=True)  # e.g., "gritty", "whimsical", "horror"
    core_themes = Column(JSON, nullable=True)  # e.g., ["power vs corruption", "survival"] - JSON for SQLite
    rule_system_id = Column(String(36), ForeignKey("rule_systems.id"), nullable=True)  # UUID as string
    summary = Column(Text, nullable=True)
    
    # Relationships
    universe = relationship("Universe", back_populates="campaigns")
    locations = relationship("Location", back_populates="campaign", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="campaign", cascade="all, delete-orphan")
    factions = relationship("Faction", back_populates="campaign", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="campaign", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="campaign", cascade="all, delete-orphan")
    player_states = relationship("PlayerState", back_populates="campaign", cascade="all, delete-orphan")
    world_change_requests = relationship("WorldChangeRequest", back_populates="campaign", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.name}', universe_id={self.universe_id})>"

