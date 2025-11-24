"""Character model."""
from sqlalchemy import Column, String, Text, ForeignKey, ARRAY
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel


class Character(BaseModel):
    """A character (PC, NPC, villain, deity, etc.)."""
    __tablename__ = "characters"
    
    universe_id = Column(String(36), ForeignKey("universes.id"), nullable=False)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=True)
    name = Column(String(255), nullable=False)
    race = Column(String(100), nullable=True)
    class_name = Column(String(100), nullable=True)  # "class" is a Python keyword
    alignment = Column(String(50), nullable=True)
    role = Column(String(50), nullable=True)  # e.g., "PC", "NPC", "villain", "deity"
    summary = Column(Text, nullable=True)
    backstory = Column(Text, nullable=True)
    motivations = Column(JSON, nullable=True)  # Array of motivation strings
    current_location_id = Column(String(36), ForeignKey("locations.id"), nullable=True)
    relationships = Column(JSON, nullable=True)  # [{other_character_id, relation_type, notes}]
    
    # Relationships
    universe = relationship("Universe", back_populates="characters")
    campaign = relationship("Campaign", back_populates="characters")
    current_location = relationship("Location", foreign_keys=[current_location_id])
    
    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', role='{self.role}')>"

