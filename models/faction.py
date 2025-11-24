"""Faction model."""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel


class Faction(BaseModel):
    """A faction or organization."""
    __tablename__ = "factions"
    
    universe_id = Column(String(36), ForeignKey("universes.id"), nullable=False)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    goals = Column(Text, nullable=True)
    members = Column(JSON, nullable=True)  # Array of character IDs
    
    # Relationships
    universe = relationship("Universe", back_populates="factions")
    campaign = relationship("Campaign", back_populates="factions")
    
    def __repr__(self):
        return f"<Faction(id={self.id}, name='{self.name}')>"

