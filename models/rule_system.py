"""Rule system model."""
from sqlalchemy import Column, String, Text, Integer
from models.base import BaseModel


class RuleSystem(BaseModel):
    """A rule system (e.g., D&D 5e, custom rules)."""
    __tablename__ = "rule_systems"
    
    name = Column(String(255), nullable=False, unique=True)
    complexity_level = Column(Integer, nullable=False, default=3)  # 1-5
    rules_reference_source = Column(Text, nullable=True)  # e.g., SRD URL, custom file path
    
    def __repr__(self):
        return f"<RuleSystem(id={self.id}, name='{self.name}')>"

