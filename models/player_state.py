"""Player state model."""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from models.base import BaseModel


class PlayerState(BaseModel):
    """Player state (inventory, quest flags, stats, etc.)."""
    __tablename__ = "player_states"
    
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    player_id = Column(String(255), nullable=False)  # Real-world player identifier
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    stats = Column(JSONB, nullable=True)  # e.g., {"AC": 16, "HP": 45, "max_HP": 50}
    inventory = Column(JSONB, nullable=True)  # Array of items
    quest_flags = Column(JSONB, nullable=True)  # Key-value flags
    
    # Relationships
    campaign = relationship("Campaign", back_populates="player_states")
    character = relationship("Character")
    
    def __repr__(self):
        return f"<PlayerState(id={self.id}, player_id='{self.player_id}', character_id={self.character_id})>"

