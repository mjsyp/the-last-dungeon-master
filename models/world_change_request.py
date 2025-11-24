"""World change request model."""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel


class WorldChangeRequest(BaseModel):
    """A player-proposed change to the world with conflict checking."""
    __tablename__ = "world_change_requests"
    
    universe_id = Column(String(36), ForeignKey("universes.id"), nullable=False)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=True)
    requested_by_player_id = Column(String(255), nullable=False)
    requested_in_session_id = Column(String(36), ForeignKey("sessions.id"), nullable=True)
    proposed_change_text = Column(Text, nullable=False)  # Raw natural language
    parsed_change_json = Column(JSON, nullable=True)  # Structured representation
    status = Column(String(50), nullable=False, default="pending")  # pending, accepted, rejected, needs_discussion, applied
    conflict_summary = Column(Text, nullable=True)  # Describes conflicts with existing lore
    resolved_change_json = Column(JSON, nullable=True)  # What actually gets applied
    
    # Relationships
    universe = relationship("Universe", back_populates="world_change_requests")
    campaign = relationship("Campaign", back_populates="world_change_requests")
    
    def __repr__(self):
        return f"<WorldChangeRequest(id={self.id}, status='{self.status}')>"

