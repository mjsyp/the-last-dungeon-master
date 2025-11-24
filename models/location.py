"""Location model."""
from sqlalchemy import Column, String, Text, ForeignKey, ARRAY
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel


class Location(BaseModel):
    """A location in the world (continent, city, tavern, dungeon, etc.)."""
    __tablename__ = "locations"
    
    universe_id = Column(String(36), ForeignKey("universes.id"), nullable=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=True)  # e.g., "continent", "city", "tavern", "dungeon"
    description = Column(Text, nullable=True)
    parent_location_id = Column(String(36), ForeignKey("locations.id"), nullable=True)
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # Relationships
    universe = relationship("Universe", back_populates="locations")
    campaign = relationship("Campaign", back_populates="locations")
    parent_location = relationship("Location", remote_side="Location.id", backref="child_locations")
    
    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}', type='{self.type}')>"

