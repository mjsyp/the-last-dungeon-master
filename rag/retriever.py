"""RAG retriever for querying vector store."""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from config.settings import settings
from rag.embedding import EmbeddingService


class RetrievedChunk:
    """A retrieved chunk with relevance score."""
    def __init__(self, text: str, metadata: Dict[str, Any], score: float):
        self.text = text
        self.metadata = metadata
        self.score = score


class RAGRetriever:
    """Retrieves relevant context from vector store for RAG."""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        self.lore_collection = self.client.get_or_create_collection(name="lore")
        self.rules_collection = self.client.get_or_create_collection(name="rules")
    
    def retrieve_lore_context(
        self,
        query: str,
        universe_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        limit: int = 10,
        min_score: float = 0.0
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant lore context for a query.
        
        Args:
            query: Natural language query
            universe_id: Filter to specific universe (optional)
            campaign_id: Filter to specific campaign (optional)
            limit: Maximum number of results
            min_score: Minimum similarity score threshold
        
        Returns:
            List of retrieved chunks sorted by relevance
        """
        query_embedding = self.embedding_service.embed_text(query)
        
        # Build where clause for filtering
        where_clause = {}
        if universe_id:
            where_clause["universe_id"] = str(universe_id)
        if campaign_id:
            where_clause["campaign_id"] = str(campaign_id)
        
        # Query collection
        if where_clause:
            results = self.lore_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause
            )
        else:
            results = self.lore_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
        
        # Convert to RetrievedChunk objects
        chunks = []
        if results["ids"] and len(results["ids"]) > 0:
            for i, doc_id in enumerate(results["ids"][0]):
                text = results["documents"][0][i]
                metadata = results["metadatas"][0][i]
                # ChromaDB returns distances (lower is better), convert to similarity score
                # Using a simple conversion: score = 1 / (1 + distance)
                distance = results["distances"][0][i] if "distances" in results else 0.0
                score = 1.0 / (1.0 + distance)
                
                if score >= min_score:
                    chunks.append(RetrievedChunk(text=text, metadata=metadata, score=score))
        
        return chunks
    
    def retrieve_rules_context(
        self,
        query: str,
        rule_system_id: Optional[str] = None,
        limit: int = 5,
        min_score: float = 0.0
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant rules context for a query.
        
        Args:
            query: Natural language query about rules
            rule_system_id: Filter to specific rule system (optional)
            limit: Maximum number of results
            min_score: Minimum similarity score threshold
        
        Returns:
            List of retrieved chunks sorted by relevance
        """
        query_embedding = self.embedding_service.embed_text(query)
        
        where_clause = {}
        if rule_system_id:
            where_clause["rule_system_id"] = str(rule_system_id)
        
        if where_clause:
            results = self.rules_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause
            )
        else:
            results = self.rules_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
        
        chunks = []
        if results["ids"] and len(results["ids"]) > 0:
            for i, doc_id in enumerate(results["ids"][0]):
                text = results["documents"][0][i]
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if "distances" in results else 0.0
                score = 1.0 / (1.0 + distance)
                
                if score >= min_score:
                    chunks.append(RetrievedChunk(text=text, metadata=metadata, score=score))
        
        return chunks
    
    def format_lore_context(self, chunks: List[RetrievedChunk]) -> str:
        """Format retrieved lore chunks into a readable context string."""
        if not chunks:
            return "No relevant lore found."
        
        lines = ["=== Relevant Lore Context ==="]
        for i, chunk in enumerate(chunks, 1):
            entity_type = chunk.metadata.get("entity_type", "unknown")
            entity_name = chunk.metadata.get("name", chunk.metadata.get("summary", "Unknown"))
            lines.append(f"\n[{i}] {entity_type.upper()}: {entity_name}")
            lines.append(f"    {chunk.text}")
            lines.append(f"    (Relevance: {chunk.score:.3f})")
        
        return "\n".join(lines)
    
    def format_rules_context(self, chunks: List[RetrievedChunk]) -> str:
        """Format retrieved rules chunks into a readable context string."""
        if not chunks:
            return "No relevant rules found."
        
        lines = ["=== Relevant Rules Context ==="]
        for i, chunk in enumerate(chunks, 1):
            entity_type = chunk.metadata.get("entity_type", "unknown")
            name = chunk.metadata.get("name", "Unknown")
            lines.append(f"\n[{i}] {entity_type.upper()}: {name}")
            lines.append(f"    {chunk.text}")
            lines.append(f"    (Relevance: {chunk.score:.3f})")
        
        return "\n".join(lines)

