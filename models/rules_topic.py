"""Rules topic model."""
from sqlalchemy import Column, String, Text, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from models.base import BaseModel


class RulesTopic(BaseModel):
    """A rules topic for explanations and tutorials."""
    __tablename__ = "rules_topics"
    
    rule_system_id = Column(UUID(as_uuid=True), ForeignKey("rule_systems.id"), nullable=False)
    name = Column(String(255), nullable=False)  # e.g., "advantage & disadvantage"
    summary = Column(Text, nullable=True)
    full_text = Column(Text, nullable=False)
    examples = Column(JSONB, nullable=True)  # {simple: "...", intermediate: "...", advanced: "..."}
    tags = Column(JSONB, nullable=True)  # e.g., ["combat", "social", "exploration"]
    
    def __repr__(self):
        return f"<RulesTopic(id={self.id}, name='{self.name}')>"

