"""Unit tests for RAG system."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from rag.embedding import EmbeddingService
from rag.indexer import RAGIndexer, LoreChunk
from rag.retriever import RAGRetriever, RetrievedChunk
from models import Universe, Campaign


class TestEmbeddingService:
    """Tests for EmbeddingService."""
    
    @patch('rag.embedding.openai.OpenAI')
    def test_embed_text(self, mock_openai_class):
        """Test embedding a single text."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_client.embeddings.create.return_value = mock_response
        
        service = EmbeddingService()
        embedding = service.embed_text("test text")
        
        assert embedding == [0.1, 0.2, 0.3]
        mock_client.embeddings.create.assert_called_once()
    
    @patch('rag.embedding.openai.OpenAI')
    def test_embed_texts_batch(self, mock_openai_class):
        """Test embedding multiple texts."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1, 0.2]),
            Mock(embedding=[0.3, 0.4])
        ]
        mock_client.embeddings.create.return_value = mock_response
        
        service = EmbeddingService()
        embeddings = service.embed_texts(["text1", "text2"])
        
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2]
        assert embeddings[1] == [0.3, 0.4]


class TestLoreChunk:
    """Tests for LoreChunk."""
    
    def test_lore_chunk_creation(self):
        """Test creating a LoreChunk."""
        chunk = LoreChunk(
            text="Test lore",
            entity_type="character",
            entity_id="123",
            universe_id="456",
            campaign_id="789"
        )
        
        assert chunk.text == "Test lore"
        assert chunk.entity_type == "character"
        assert chunk.entity_id == "123"
        assert chunk.universe_id == "456"
        assert chunk.campaign_id == "789"
        assert chunk.metadata == {}


class TestRAGIndexer:
    """Tests for RAGIndexer."""
    
    @patch('rag.indexer.chromadb.PersistentClient')
    @patch('rag.indexer.EmbeddingService')
    def test_index_entity(self, mock_embedding_class, mock_chroma_class):
        """Test indexing an entity."""
        mock_embedding = Mock()
        mock_embedding.embed_texts.return_value = [[0.1, 0.2, 0.3]]  # Returns list of embeddings
        mock_embedding_class.return_value = mock_embedding
        
        mock_collection = Mock()
        mock_collection.add = Mock()  # Ensure add is a mock
        mock_client = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma_class.return_value = mock_client
        
        indexer = RAGIndexer()
        indexer.embedding_service = mock_embedding  # Replace embedding service
        indexer.lore_collection = mock_collection  # Replace collection
        
        # Mock a universe entity
        universe = Mock()
        universe.id = "universe-123"
        universe.name = "Test Universe"
        universe.description = "A test universe"
        universe.themes = ["fantasy"]
        
        indexer.index_lore_entity(universe, "universe")
        
        # Verify embedding was called (embed_texts for batch)
        mock_embedding.embed_texts.assert_called()
        # Verify collection.add was called
        assert mock_collection.add.called
    
    @patch('rag.indexer.chromadb.PersistentClient')
    @patch('rag.indexer.EmbeddingService')
    def test_remove_entity(self, mock_embedding_class, mock_chroma_class):
        """Test removing an entity from index."""
        mock_collection = Mock()
        mock_collection.get = Mock(return_value={"ids": ["id1", "id2"]})
        mock_collection.delete = Mock()
        mock_client = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma_class.return_value = mock_client
        
        indexer = RAGIndexer()
        indexer.lore_collection = mock_collection  # Replace collection
        indexer.remove_entity("universe", "entity-123")
        
        # Verify get was called to find entities
        assert mock_collection.get.called
        # Verify delete was called if IDs were found
        assert mock_collection.delete.called


class TestRAGRetriever:
    """Tests for RAGRetriever."""
    
    @patch('rag.retriever.chromadb.PersistentClient')
    @patch('rag.retriever.EmbeddingService')
    def test_retrieve_lore_context(self, mock_embedding_class, mock_chroma_class):
        """Test retrieving lore context."""
        mock_embedding = Mock()
        mock_embedding.embed_text.return_value = [0.1, 0.2, 0.3]
        mock_embedding_class.return_value = mock_embedding
        
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["id1", "id2"]],
            "documents": [["doc1", "doc2"]],
            "metadatas": [[{"entity_type": "character"}, {"entity_type": "location"}]],
            "distances": [[0.1, 0.2]]
        }
        
        mock_client = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma_class.return_value = mock_client
        
        retriever = RAGRetriever()
        results = retriever.retrieve_lore_context("test query", limit=2)
        
        assert len(results) == 2
        assert isinstance(results[0], RetrievedChunk)
        assert results[0].text == "doc1"
        # Score = 1.0 / (1.0 + distance) = 1.0 / 1.1 ≈ 0.909
        assert abs(results[0].score - (1.0 / 1.1)) < 0.01
    
    @patch('rag.retriever.chromadb.PersistentClient')
    @patch('rag.retriever.EmbeddingService')
    def test_retrieve_with_filters(self, mock_embedding_class, mock_chroma_class):
        """Test retrieving with universe/campaign filters."""
        mock_embedding = Mock()
        mock_embedding.embed_text.return_value = [0.1, 0.2, 0.3]
        mock_embedding_class.return_value = mock_embedding
        
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }
        
        mock_client = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma_class.return_value = mock_client
        
        retriever = RAGRetriever()
        retriever.retrieve_lore_context(
            "query",
            universe_id="universe-123",
            campaign_id="campaign-456"
        )
        
        # Verify query was called with where clause
        call_args = mock_collection.query.call_args
        assert "where" in call_args.kwargs
        where_clause = call_args.kwargs["where"]
        assert "$and" in where_clause or "universe_id" in str(where_clause)

