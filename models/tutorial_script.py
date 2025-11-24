"""Tutorial script model."""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from models.base import BaseModel


class TutorialScript(BaseModel):
    """A tutorial script for guided walkthroughs."""
    __tablename__ = "tutorial_scripts"
    
    rule_system_id = Column(UUID(as_uuid=True), ForeignKey("rule_systems.id"), nullable=False)
    name = Column(String(255), nullable=False)  # e.g., "Combat Basics Walkthrough"
    description = Column(Text, nullable=True)
    steps = Column(JSONB, nullable=False)  # Array of step objects
    
    def __repr__(self):
        return f"<TutorialScript(id={self.id}, name='{self.name}')>"

