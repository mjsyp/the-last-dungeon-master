# DM-VA Architecture

## Overview

The Last Dungeon Master (DM-VA) is a voice-driven Dungeon Master Virtual Assistant that uses LLMs to run consistent, lore-aware tabletop RPG sessions.

## System Layers

### 1. I/O & Orchestration (`orchestrator/`, `audio/`)

- **Session Management**: Tracks active universe, campaign, party, mode, and turn state
- **Mode Switching**: Handles transitions between different operational modes
- **Audio Pipeline**: STT (speech-to-text) and TTS (text-to-speech) abstractions
- **Orchestrator**: Main coordinator that routes inputs to appropriate mode handlers

### 2. World Model & Memory (`models/`, `rag/`)

- **Database Models**: SQLAlchemy ORM models for all world entities
- **RAG System**: Vector indexing and retrieval for lore and rules
- **Logbook**: Persistent storage of world state, events, and history

### 3. Narrative Engine (`llm/`)

- **DM Brain**: High-level interface for LLM interactions
- **Prompt Templates**: Mode-specific prompts for consistent behavior
- **Dual-Channel Output**: Narration (for players) + structured updates (for database)

### 4. Tools & Integrations (`main_menu/`)

- **Campaign Management**: Universe, campaign, and party CRUD operations
- **World Import**: Import generated worlds from World Architect Mode
- **Future**: Rules engine, dice rolling, initiative tracking, etc.

## Data Flow

### DM Story Mode (Live Session)

```
Player Audio → STT → Text
                ↓
         Orchestrator
                ↓
    RAG Retrieval (lore context)
                ↓
         DM Brain (LLM)
                ↓
    Narration + log_updates
                ↓
    TTS → Audio + DB Updates + RAG Re-index
```

### World Edit Mode

```
Player Proposal → Parse Change
                    ↓
            RAG Conflict Check
                    ↓
            DM Brain (Conflict Analysis)
                    ↓
    Narration + Conflict Summary + Resolutions
                    ↓
    Player Chooses Resolution → Apply to DB + RAG
```

## Modes

1. **Main Menu Mode**: Universe/campaign/party selection and management
2. **World Architect Mode**: Generate or import worlds and campaigns
3. **DM Story Mode**: Live session play with lore consistency
4. **Rules Explanation Mode**: On-demand rules help
5. **Tutorial Mode**: Guided walkthroughs
6. **World Edit Mode**: Player-driven edits with conflict resolution

## Key Design Decisions

### Dual-Channel LLM Output

The LLM returns both:
- **Narration**: Natural language for players (TTS)
- **log_updates**: Structured JSON for database updates

This ensures consistency between what players hear and what's stored in the world model.

### RAG for Consistency

All lore (universes, campaigns, locations, characters, factions, events) is indexed in a vector store. Before each LLM call, relevant context is retrieved to ensure the DM never contradicts established lore.

### Mode Handlers

Each mode has a dedicated handler class that implements the `ModeHandler` interface. This makes it easy to:
- Add new modes
- Test modes independently
- Switch between modes cleanly

### Extensibility

- STT/TTS providers are swappable via abstract base classes
- LLM providers can be swapped (currently OpenAI, Anthropic support planned)
- Database models use SQLAlchemy for easy migration
- RAG uses ChromaDB but could be swapped for other vector stores

## Database Schema

See `models/` for full schema. Key entities:

- **Universe**: Top-level setting
- **Campaign**: Story within a universe
- **Location**: Places in the world
- **Character**: PCs, NPCs, etc.
- **Faction**: Organizations
- **Event**: Things that happened
- **Session**: Play sessions
- **PlayerGroup**: Parties
- **PlayerState**: Player stats/inventory/flags
- **WorldChangeRequest**: Proposed edits with conflict tracking

## RAG Indexing

Lore entities are chunked and embedded:
- **Lore Collection**: Universes, campaigns, locations, characters, factions, events
- **Rules Collection**: Rules topics and tutorial scripts

Metadata includes:
- `entity_type`: Type of entity
- `entity_id`: Database ID
- `universe_id`: For filtering
- `campaign_id`: For filtering
- Additional entity-specific metadata

## Future Enhancements

- Multi-speaker TTS for different NPC voices
- Rules engine integration (D&D 5e mechanics)
- Dice rolling and initiative tracking
- Map/visual integrations
- Session recording and playback
- Player character sheets management
- Quest tracking system

