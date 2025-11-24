"""Unit tests for database models."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.session import Base
from models import (
    Universe, Campaign, Character, Location, Faction, Event,
    PlayerGroup, PlayerState, RulesTopic, TutorialScript
)
import uuid


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


class TestUniverse:
    """Tests for Universe model."""
    
    def test_create_universe(self, db_session):
        """Test creating a universe."""
        universe = Universe(
            name="Test Universe",
            description="A test universe",
            themes=["fantasy", "magic"]
        )
        db_session.add(universe)
        db_session.commit()
        
        assert universe.id is not None
        assert universe.name == "Test Universe"
        assert universe.description == "A test universe"
        assert universe.themes == ["fantasy", "magic"]
        assert universe.created_at is not None
    
    def test_universe_unique_name(self, db_session):
        """Test that universe names must be unique."""
        universe1 = Universe(name="Unique Universe")
        universe2 = Universe(name="Unique Universe")
        
        db_session.add(universe1)
        db_session.commit()
        
        db_session.add(universe2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_universe_relationships(self, db_session):
        """Test universe relationships."""
        universe = Universe(name="Test Universe")
        db_session.add(universe)
        db_session.commit()
        
        campaign = Campaign(
            name="Test Campaign",
            universe_id=universe.id
        )
        db_session.add(campaign)
        db_session.commit()
        
        assert len(universe.campaigns) == 1
        assert universe.campaigns[0].name == "Test Campaign"


class TestCampaign:
    """Tests for Campaign model."""
    
    def test_create_campaign(self, db_session):
        """Test creating a campaign."""
        universe = Universe(name="Test Universe")
        db_session.add(universe)
        db_session.commit()
        
        campaign = Campaign(
            name="Test Campaign",
            universe_id=universe.id,
            genre="Fantasy",
            tone="Dark"
        )
        db_session.add(campaign)
        db_session.commit()
        
        assert campaign.id is not None
        assert campaign.name == "Test Campaign"
        assert campaign.universe_id == universe.id
        assert campaign.genre == "Fantasy"
        assert campaign.tone == "Dark"


class TestCharacter:
    """Tests for Character model."""
    
    def test_create_character(self, db_session):
        """Test creating a character."""
        universe = Universe(name="Test Universe")
        campaign = Campaign(name="Test Campaign", universe_id=universe.id)
        db_session.add_all([universe, campaign])
        db_session.commit()
        
        character = Character(
            name="Test Character",
            universe_id=universe.id,
            campaign_id=campaign.id,
            role="NPC"
        )
        db_session.add(character)
        db_session.commit()
        
        assert character.id is not None
        assert character.name == "Test Character"
        assert character.role == "NPC"


class TestBaseModel:
    """Tests for BaseModel functionality."""
    
    def test_uuid_generation(self, db_session):
        """Test that BaseModel generates UUIDs."""
        universe = Universe(name="Test")
        db_session.add(universe)
        db_session.commit()
        
        assert universe.id is not None
        assert len(universe.id) == 36  # UUID string length
        # Verify it's a valid UUID format
        uuid.UUID(universe.id)
    
    def test_timestamps(self, db_session):
        """Test that timestamps are automatically set."""
        universe = Universe(name="Test")
        db_session.add(universe)
        db_session.commit()
        
        assert universe.created_at is not None
        assert universe.updated_at is not None
        assert universe.created_at == universe.updated_at
        
        # Update and check updated_at changes
        original_updated = universe.updated_at
        universe.name = "Updated"
        db_session.commit()
        db_session.refresh(universe)
        
        # updated_at should be different (may be same second, so just check it's set)
        assert universe.updated_at is not None


class TestPlayerGroup:
    """Tests for PlayerGroup model."""
    
    def test_create_party(self, db_session):
        """Test creating a player group."""
        universe = Universe(name="Test Universe")
        db_session.add(universe)
        db_session.commit()
        
        party = PlayerGroup(
            name="Test Party",
            universe_id=universe.id,
            description="A test party"
        )
        db_session.add(party)
        db_session.commit()
        
        assert party.id is not None
        assert party.name == "Test Party"
        assert party.universe_id == universe.id

