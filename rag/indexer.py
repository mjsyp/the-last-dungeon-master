"""RAG indexer for converting database entities to vector embeddings."""
from typing import List, Dict, Any, Optional
import uuid
from sqlalchemy.orm import Session
import chromadb
from chromadb.config import Settings as ChromaSettings
from config.settings import settings
from rag.embedding import EmbeddingService
from models import (
    Universe, Campaign, Location, Character, Faction, Event,
    RulesTopic, TutorialScript
)


class LoreChunk:
    """A chunk of lore content with metadata."""
    def __init__(
        self,
        text: str,
        entity_type: str,
        entity_id: str,
        universe_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.text = text
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.universe_id = universe_id
        self.campaign_id = campaign_id
        self.metadata = metadata or {}


class RAGIndexer:
    """Indexes database entities into vector store for RAG retrieval."""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Separate collections for lore and rules
        self.lore_collection = self.client.get_or_create_collection(
            name="lore",
            metadata={"description": "Lore content from universes, campaigns, locations, characters, factions, events"}
        )
        
        self.rules_collection = self.client.get_or_create_collection(
            name="rules",
            metadata={"description": "Rules content from rules_topics and tutorial_scripts"}
        )
    
    def _chunk_entity(self, entity: Any, entity_type: str) -> List[LoreChunk]:
        """Convert a database entity into one or more text chunks."""
        chunks = []
        
        if entity_type == "universe":
            text_parts = []
            if entity.name:
                text_parts.append(f"Universe: {entity.name}")
            if entity.description:
                text_parts.append(f"Description: {entity.description}")
            if entity.themes:
                text_parts.append(f"Themes: {', '.join(entity.themes)}")
            
            if text_parts:
                chunks.append(LoreChunk(
                    text="\n".join(text_parts),
                    entity_type="universe",
                    entity_id=str(entity.id),
                    universe_id=str(entity.id),
                    metadata={"name": entity.name}
                ))
        
        elif entity_type == "campaign":
            text_parts = []
            if entity.name:
                text_parts.append(f"Campaign: {entity.name}")
            if entity.description or entity.summary:
                text_parts.append(f"Summary: {entity.summary or entity.description}")
            if entity.genre:
                text_parts.append(f"Genre: {entity.genre}")
            if entity.tone:
                text_parts.append(f"Tone: {entity.tone}")
            if entity.core_themes:
                text_parts.append(f"Core Themes: {', '.join(entity.core_themes)}")
            
            if text_parts:
                chunks.append(LoreChunk(
                    text="\n".join(text_parts),
                    entity_type="campaign",
                    entity_id=str(entity.id),
                    universe_id=str(entity.universe_id) if entity.universe_id else None,
                    campaign_id=str(entity.id),
                    metadata={"name": entity.name, "genre": entity.genre, "tone": entity.tone}
                ))
        
        elif entity_type == "location":
            text_parts = []
            if entity.name:
                text_parts.append(f"Location: {entity.name}")
            if entity.type:
                text_parts.append(f"Type: {entity.type}")
            if entity.description:
                text_parts.append(f"Description: {entity.description}")
            
            if text_parts:
                chunks.append(LoreChunk(
                    text="\n".join(text_parts),
                    entity_type="location",
                    entity_id=str(entity.id),
                    universe_id=str(entity.universe_id) if entity.universe_id else None,
                    campaign_id=str(entity.campaign_id) if entity.campaign_id else None,
                    metadata={"name": entity.name, "type": entity.type}
                ))
        
        elif entity_type == "character":
            text_parts = []
            if entity.name:
                text_parts.append(f"Character: {entity.name}")
            if entity.role:
                text_parts.append(f"Role: {entity.role}")
            if entity.race:
                text_parts.append(f"Race: {entity.race}")
            if entity.class_name:
                text_parts.append(f"Class: {entity.class_name}")
            if entity.alignment:
                text_parts.append(f"Alignment: {entity.alignment}")
            if entity.summary:
                text_parts.append(f"Summary: {entity.summary}")
            if entity.backstory:
                text_parts.append(f"Backstory: {entity.backstory}")
            if entity.motivations:
                text_parts.append(f"Motivations: {', '.join(entity.motivations)}")
            
            if text_parts:
                chunks.append(LoreChunk(
                    text="\n".join(text_parts),
                    entity_type="character",
                    entity_id=str(entity.id),
                    universe_id=str(entity.universe_id),
                    campaign_id=str(entity.campaign_id) if entity.campaign_id else None,
                    metadata={"name": entity.name, "role": entity.role}
                ))
        
        elif entity_type == "faction":
            text_parts = []
            if entity.name:
                text_parts.append(f"Faction: {entity.name}")
            if entity.description:
                text_parts.append(f"Description: {entity.description}")
            if entity.goals:
                text_parts.append(f"Goals: {entity.goals}")
            
            if text_parts:
                chunks.append(LoreChunk(
                    text="\n".join(text_parts),
                    entity_type="faction",
                    entity_id=str(entity.id),
                    universe_id=str(entity.universe_id),
                    campaign_id=str(entity.campaign_id) if entity.campaign_id else None,
                    metadata={"name": entity.name}
                ))
        
        elif entity_type == "event":
            text_parts = []
            if entity.summary:
                text_parts.append(f"Event: {entity.summary}")
            if entity.full_text:
                text_parts.append(f"Details: {entity.full_text}")
            if entity.time_in_world:
                text_parts.append(f"Time: {entity.time_in_world}")
            if entity.tags:
                text_parts.append(f"Tags: {', '.join(entity.tags)}")
            
            if text_parts:
                chunks.append(LoreChunk(
                    text="\n".join(text_parts),
                    entity_type="event",
                    entity_id=str(entity.id),
                    universe_id=str(entity.universe_id),
                    campaign_id=str(entity.campaign_id) if entity.campaign_id else None,
                    metadata={
                        "summary": entity.summary,
                        "time_in_world": entity.time_in_world,
                        "tags": entity.tags
                    }
                ))
        
        return chunks
    
    def index_lore_entity(self, entity: Any, entity_type: str):
        """Index a single lore entity into the vector store."""
        chunks = self._chunk_entity(entity, entity_type)
        
        if not chunks:
            return
        
        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_service.embed_texts(texts)
        
        # Prepare documents for ChromaDB
        ids = [f"{entity_type}_{chunk.entity_id}_{i}" for i, chunk in enumerate(chunks)]
        metadatas = []
        for chunk in chunks:
            meta = {
                "entity_type": chunk.entity_type,
                "entity_id": chunk.entity_id,
            }
            if chunk.universe_id:
                meta["universe_id"] = chunk.universe_id
            if chunk.campaign_id:
                meta["campaign_id"] = chunk.campaign_id
            meta.update(chunk.metadata)
            metadatas.append(meta)
        
        # Add to collection
        self.lore_collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
    
    def index_rules_topic(self, topic: RulesTopic):
        """Index a rules topic into the vector store."""
        text_parts = []
        if topic.name:
            text_parts.append(f"Rules Topic: {topic.name}")
        if topic.summary:
            text_parts.append(f"Summary: {topic.summary}")
        if topic.full_text:
            text_parts.append(f"Full Text: {topic.full_text}")
        if topic.examples:
            text_parts.append(f"Examples: {topic.examples}")
        
        if not text_parts:
            return
        
        text = "\n".join(text_parts)
        embedding = self.embedding_service.embed_text(text)
        
        self.rules_collection.add(
            ids=[f"rules_topic_{topic.id}"],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "entity_type": "rules_topic",
                "entity_id": str(topic.id),
                "rule_system_id": str(topic.rule_system_id),
                "name": topic.name,
                "tags": topic.tags or []
            }]
        )
    
    def index_tutorial_script(self, script: TutorialScript):
        """Index a tutorial script into the vector store."""
        text_parts = []
        if script.name:
            text_parts.append(f"Tutorial: {script.name}")
        if script.description:
            text_parts.append(f"Description: {script.description}")
        if script.steps:
            text_parts.append(f"Steps: {script.steps}")
        
        if not text_parts:
            return
        
        text = "\n".join(text_parts)
        embedding = self.embedding_service.embed_text(text)
        
        self.rules_collection.add(
            ids=[f"tutorial_script_{script.id}"],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "entity_type": "tutorial_script",
                "entity_id": str(script.id),
                "rule_system_id": str(script.rule_system_id),
                "name": script.name
            }]
        )
    
    def remove_entity(self, entity_type: str, entity_id: str):
        """Remove an entity from the lore index."""
        # ChromaDB: query to find matching IDs, then delete
        # Note: ChromaDB where clause syntax uses $and, $or, etc.
        try:
            results = self.lore_collection.get(
                where={"$and": [{"entity_type": entity_type}, {"entity_id": str(entity_id)}]}
            )
            if results["ids"]:
                self.lore_collection.delete(ids=results["ids"])
        except Exception:
            # Fallback: try without $and (older ChromaDB versions)
            try:
                results = self.lore_collection.get(
                    where={"entity_type": entity_type, "entity_id": str(entity_id)}
                )
                if results["ids"]:
                    self.lore_collection.delete(ids=results["ids"])
            except Exception as e:
                # If query fails, try to delete by prefix pattern
                # This is a fallback - ideally we'd track IDs better
                pass
    
    def reindex_entity(self, entity: Any, entity_type: str):
        """Remove and re-index an entity (for updates)."""
        self.remove_entity(entity_type, str(entity.id))
        self.index_lore_entity(entity, entity_type)

