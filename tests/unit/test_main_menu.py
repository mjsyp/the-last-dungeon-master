"""Unit tests for main menu manager."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.session import Base
from main_menu.manager import MainMenuManager
from models import Universe, Campaign, PlayerGroup, Character
from unittest.mock import patch


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


class TestMainMenuManager:
    """Tests for MainMenuManager."""
    
    def test_list_universes_empty(self, db_session):
        """Test listing universes when none exist."""
        manager = MainMenuManager(db_session)
        universes = manager.list_universes()
        
        assert universes == []
    
    def test_list_universes(self, db_session):
        """Test listing universes."""
        universe1 = Universe(name="Universe 1", description="First")
        universe2 = Universe(name="Universe 2", description="Second")
        db_session.add_all([universe1, universe2])
        db_session.commit()
        
        manager = MainMenuManager(db_session)
        universes = manager.list_universes()
        
        assert len(universes) == 2
        assert universes[0]["name"] in ["Universe 1", "Universe 2"]
        assert "id" in universes[0]
        assert "description" in universes[0]
    
    def test_get_universe(self, db_session):
        """Test getting a specific universe."""
        universe = Universe(name="Test Universe", description="Test")
        db_session.add(universe)
        db_session.commit()
        
        manager = MainMenuManager(db_session)
        result = manager.get_universe(str(universe.id))
        
        assert result is not None
        assert result["name"] == "Test Universe"
        assert result["description"] == "Test"
    
    def test_get_universe_not_found(self, db_session):
        """Test getting non-existent universe."""
        manager = MainMenuManager(db_session)
        result = manager.get_universe("nonexistent-id")
        
        assert result is None
    
    @patch('main_menu.manager.RAGIndexer')
    def test_create_universe(self, mock_indexer_class, db_session):
        """Test creating a universe."""
        mock_indexer = Mock()
        mock_indexer.index_lore_entity = Mock()  # Mock the method
        mock_indexer_class.return_value = mock_indexer
        
        manager = MainMenuManager(db_session)
        manager.indexer = mock_indexer  # Replace the indexer
        
        result = manager.create_universe(
            name="New Universe",
            description="A new universe",
            themes=["fantasy"]
        )
        
        assert result["name"] == "New Universe"
        assert result["description"] == "A new universe"
        assert result["themes"] == ["fantasy"]
        
        # Verify universe was created in database
        universe = db_session.query(Universe).filter_by(name="New Universe").first()
        assert universe is not None
        assert universe.description == "A new universe"
        
        # Verify indexing was called
        mock_indexer.index_lore_entity.assert_called_once()
    
    def test_list_campaigns(self, db_session):
        """Test listing campaigns."""
        universe = Universe(name="Test Universe")
        db_session.add(universe)
        db_session.commit()
        
        campaign1 = Campaign(name="Campaign 1", universe_id=universe.id)
        campaign2 = Campaign(name="Campaign 2", universe_id=universe.id)
        db_session.add_all([campaign1, campaign2])
        db_session.commit()
        
        manager = MainMenuManager(db_session)
        campaigns = manager.list_campaigns(universe_id=str(universe.id))
        
        assert len(campaigns) == 2
        assert all("id" in c for c in campaigns)
        assert all("name" in c for c in campaigns)
    
    @patch('main_menu.manager.RAGIndexer')
    def test_create_campaign(self, mock_indexer_class, db_session):
        """Test creating a campaign."""
        mock_indexer = Mock()
        mock_indexer.index_lore_entity = Mock()  # Mock the method
        mock_indexer_class.return_value = mock_indexer
        
        universe = Universe(name="Test Universe")
        db_session.add(universe)
        db_session.commit()
        
        manager = MainMenuManager(db_session)
        # Replace indexer after initialization
        original_indexer = manager.indexer
        manager.indexer = mock_indexer
        
        try:
            result = manager.create_campaign(
                universe_id=str(universe.id),
                name="New Campaign",
                genre="Fantasy"
            )
            
            assert result["name"] == "New Campaign"
            assert result["genre"] == "Fantasy"
            
            # Verify campaign was created
            campaign = db_session.query(Campaign).filter_by(name="New Campaign").first()
            assert campaign is not None
            
            # Verify indexing was called
            mock_indexer.index_lore_entity.assert_called_once()
        finally:
            manager.indexer = original_indexer
    
    def test_list_parties(self, db_session):
        """Test listing parties."""
        universe = Universe(name="Test Universe")
        db_session.add(universe)
        db_session.commit()
        
        party1 = PlayerGroup(name="Party 1", universe_id=universe.id)
        party2 = PlayerGroup(name="Party 2", universe_id=universe.id)
        db_session.add_all([party1, party2])
        db_session.commit()
        
        manager = MainMenuManager(db_session)
        parties = manager.list_parties(universe_id=str(universe.id))
        
        assert len(parties) == 2
        assert all("id" in p for p in parties)
        assert all("name" in p for p in parties)
    
    def test_list_characters(self, db_session):
        """Test listing characters."""
        universe = Universe(name="Test Universe")
        db_session.add(universe)
        db_session.commit()
        
        campaign = Campaign(name="Test Campaign", universe_id=universe.id)
        db_session.add(campaign)
        db_session.commit()
        
        character1 = Character(
            name="Character 1",
            universe_id=universe.id,
            campaign_id=campaign.id,
            role="PC"
        )
        character2 = Character(
            name="Character 2",
            universe_id=universe.id,
            role="NPC"
        )
        db_session.add_all([character1, character2])
        db_session.commit()
        
        manager = MainMenuManager(db_session)
        
        # List all characters in universe
        characters = manager.list_characters(universe_id=str(universe.id))
        assert len(characters) == 2
        
        # List characters in campaign
        characters = manager.list_characters(campaign_id=str(campaign.id))
        assert len(characters) == 1
        assert characters[0]["name"] == "Character 1"

