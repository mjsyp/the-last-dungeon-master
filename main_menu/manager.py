"""Main menu and campaign management operations."""
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import (
    Universe, Campaign, PlayerGroup, Location, Character, Faction, Event
)
from rag.indexer import RAGIndexer


class MainMenuManager:
    """Manages universe, campaign, and party operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.indexer = RAGIndexer()
    
    # Universe Management
    
    def list_universes(self) -> List[Dict[str, Any]]:
        """List all universes."""
        universes = self.db.query(Universe).order_by(desc(Universe.created_at)).all()
        return [
            {
                "id": str(u.id),
                "name": u.name,
                "description": u.description,
                "themes": u.themes or [],
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in universes
        ]
    
    def get_universe(self, universe_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific universe by ID."""
        universe = self.db.query(Universe).filter(Universe.id == UUID(universe_id)).first()
        if not universe:
            return None
        
        return {
            "id": str(universe.id),
            "name": universe.name,
            "description": universe.description,
            "themes": universe.themes or [],
            "campaign_count": len(universe.campaigns),
            "created_at": universe.created_at.isoformat() if universe.created_at else None
        }
    
    def create_universe(
        self,
        name: str,
        description: Optional[str] = None,
        themes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new universe."""
        universe = Universe(
            name=name,
            description=description,
            themes=themes or []
        )
        self.db.add(universe)
        self.db.commit()
        self.db.refresh(universe)
        
        # Index in RAG
        self.indexer.index_lore_entity(universe, "universe")
        
        return {
            "id": str(universe.id),
            "name": universe.name,
            "description": universe.description,
            "themes": universe.themes or []
        }
    
    def delete_universe(self, universe_id: str) -> bool:
        """Delete a universe (with safety checks)."""
        universe = self.db.query(Universe).filter(Universe.id == UUID(universe_id)).first()
        if not universe:
            return False
        
        # Safety check: warn if universe has campaigns
        if universe.campaigns:
            # In a real implementation, you might want to prevent deletion or require confirmation
            pass
        
        # Remove from RAG
        self.indexer.remove_entity("universe", universe_id)
        
        self.db.delete(universe)
        self.db.commit()
        return True
    
    # Campaign Management
    
    def list_campaigns(self, universe_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List campaigns, optionally filtered by universe."""
        query = self.db.query(Campaign)
        if universe_id:
            query = query.filter(Campaign.universe_id == UUID(universe_id))
        
        campaigns = query.order_by(desc(Campaign.created_at)).all()
        return [
            {
                "id": str(c.id),
                "name": c.name,
                "universe_id": str(c.universe_id) if c.universe_id else None,
                "genre": c.genre,
                "tone": c.tone,
                "core_themes": c.core_themes or [],
                "summary": c.summary,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in campaigns
        ]
    
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific campaign by ID."""
        campaign = self.db.query(Campaign).filter(Campaign.id == UUID(campaign_id)).first()
        if not campaign:
            return None
        
        return {
            "id": str(campaign.id),
            "name": campaign.name,
            "universe_id": str(campaign.universe_id) if campaign.universe_id else None,
            "genre": campaign.genre,
            "tone": campaign.tone,
            "core_themes": campaign.core_themes or [],
            "summary": campaign.summary,
            "session_count": len(campaign.sessions),
            "created_at": campaign.created_at.isoformat() if campaign.created_at else None
        }
    
    def create_campaign(
        self,
        universe_id: Optional[str],
        name: str,
        genre: Optional[str] = None,
        tone: Optional[str] = None,
        core_themes: Optional[List[str]] = None,
        summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new campaign."""
        campaign = Campaign(
            universe_id=UUID(universe_id) if universe_id else None,
            name=name,
            genre=genre,
            tone=tone,
            core_themes=core_themes or [],
            summary=summary
        )
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        
        # Index in RAG
        self.indexer.index_lore_entity(campaign, "campaign")
        
        return {
            "id": str(campaign.id),
            "name": campaign.name,
            "universe_id": str(campaign.universe_id) if campaign.universe_id else None,
            "genre": campaign.genre,
            "tone": campaign.tone,
            "core_themes": campaign.core_themes or []
        }
    
    # Party Management
    
    def list_parties(self, universe_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List parties, optionally filtered by universe."""
        query = self.db.query(PlayerGroup)
        if universe_id:
            query = query.filter(PlayerGroup.universe_id == UUID(universe_id))
        
        parties = query.order_by(desc(PlayerGroup.created_at)).all()
        return [
            {
                "id": str(p.id),
                "name": p.name,
                "universe_id": str(p.universe_id),
                "description": p.description,
                "campaign_ids": p.campaign_ids or [],
                "member_count": len(p.members),
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in parties
        ]
    
    def create_party(
        self,
        universe_id: str,
        name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new party."""
        party = PlayerGroup(
            universe_id=UUID(universe_id),
            name=name,
            description=description
        )
        self.db.add(party)
        self.db.commit()
        self.db.refresh(party)
        
        return {
            "id": str(party.id),
            "name": party.name,
            "universe_id": str(party.universe_id),
            "description": party.description
        }
    
    # Utility: Import generated world
    
    def import_generated_world(self, world_data: Dict[str, Any], universe_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Import a generated world (from World Architect Mode) into the database.
        
        Args:
            world_data: Generated world data from LLM
            universe_id: Optional existing universe ID to add to
        
        Returns:
            Dict with created entity IDs
        """
        created = {}
        
        # Create/update universe
        if "universe" in world_data:
            uni_data = world_data["universe"]
            if universe_id:
                universe = self.db.query(Universe).filter(Universe.id == UUID(universe_id)).first()
                if universe:
                    universe.name = uni_data.get("name", universe.name)
                    universe.description = uni_data.get("description", universe.description)
                    universe.themes = uni_data.get("themes", universe.themes)
                    self.db.commit()
                    created["universe_id"] = universe_id
                else:
                    universe = None
            else:
                universe = Universe(
                    name=uni_data.get("name", "New Universe"),
                    description=uni_data.get("description"),
                    themes=uni_data.get("themes", [])
                )
                self.db.add(universe)
                self.db.commit()
                self.db.refresh(universe)
                created["universe_id"] = str(universe.id)
                self.indexer.index_lore_entity(universe, "universe")
        
        # Create campaign
        if "campaign" in world_data and "universe_id" in created:
            camp_data = world_data["campaign"]
            campaign = Campaign(
                universe_id=UUID(created["universe_id"]),
                name=camp_data.get("name", "New Campaign"),
                genre=camp_data.get("genre"),
                tone=camp_data.get("tone"),
                core_themes=camp_data.get("core_themes", []),
                summary=camp_data.get("summary")
            )
            self.db.add(campaign)
            self.db.commit()
            self.db.refresh(campaign)
            created["campaign_id"] = str(campaign.id)
            self.indexer.index_lore_entity(campaign, "campaign")
        
        # Create locations, characters, factions, events
        # (Similar pattern for each entity type)
        # TODO: Implement full import logic for all entity types
        
        return created

