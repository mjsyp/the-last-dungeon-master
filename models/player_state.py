"""Player state model."""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel


class PlayerState(BaseModel):
    """Player state (inventory, quest flags, stats, etc.)."""
    __tablename__ = "player_states"
    
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    player_id = Column(String(255), nullable=False)  # Real-world player identifier
    character_id = Column(String(36), ForeignKey("characters.id"), nullable=False)
    stats = Column(JSON, nullable=True)  # e.g., {"AC": 16, "HP": 45, "max_HP": 50}
    inventory = Column(JSON, nullable=True)  # Array of items
    quest_flags = Column(JSON, nullable=True)  # Key-value flags
    
    # Relationships
    campaign = relationship("Campaign", back_populates="player_states")
    character = relationship("Character")
    
    def __repr__(self):
        return f"<PlayerState(id={self.id}, player_id='{self.player_id}', character_id={self.character_id})>"

