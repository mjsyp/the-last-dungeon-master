"""Player group/party model."""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from models.base import BaseModel


class PlayerGroup(BaseModel):
    """A player group/party."""
    __tablename__ = "player_groups"
    
    universe_id = Column(UUID(as_uuid=True), ForeignKey("universes.id"), nullable=False)
    name = Column(String(255), nullable=False)  # e.g., "The Ember Company"
    description = Column(Text, nullable=True)
    campaign_ids = Column(JSONB, nullable=True)  # Array of campaign IDs this group has participated in
    
    # Relationships
    universe = relationship("Universe", back_populates="parties")
    members = relationship("GroupMember", back_populates="party", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PlayerGroup(id={self.id}, name='{self.name}')>"


class GroupMember(BaseModel):
    """Association between a player group and its members."""
    __tablename__ = "group_members"
    
    party_id = Column(UUID(as_uuid=True), ForeignKey("player_groups.id"), nullable=False)
    player_id = Column(String(255), nullable=False)  # Real-world player identifier
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id"), nullable=True)
    joined_at = Column(DateTime(timezone=True), nullable=True)
    left_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    party = relationship("PlayerGroup", back_populates="members")
    character = relationship("Character")
    
    def __repr__(self):
        return f"<GroupMember(id={self.id}, party_id={self.party_id}, player_id='{self.player_id}')>"

