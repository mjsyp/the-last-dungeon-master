"""Universe model."""
from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel


class Universe(BaseModel):
    """A universe/setting that can contain multiple campaigns."""
    __tablename__ = "universes"
    
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    themes = Column(JSON, nullable=True)  # e.g., ["gods vs mortals", "deep time"] - JSON for SQLite compatibility
    default_rule_system_id = Column(String(36), ForeignKey("rule_systems.id"), nullable=True)  # UUID as string for SQLite
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="universe", cascade="all, delete-orphan")
    locations = relationship("Location", back_populates="universe", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="universe", cascade="all, delete-orphan")
    factions = relationship("Faction", back_populates="universe", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="universe", cascade="all, delete-orphan")
    parties = relationship("PlayerGroup", back_populates="universe", cascade="all, delete-orphan")
    world_change_requests = relationship("WorldChangeRequest", back_populates="universe", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Universe(id={self.id}, name='{self.name}')>"

