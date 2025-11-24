# Changelog

All notable changes to The Last Dungeon Master (DM-VA) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-19

### Added

#### Core Architecture
- Project structure with modular organization
- Configuration management system (`config/settings.py`)
- Database session management with SQLAlchemy
- PostgreSQL database support

#### Data Models
- Complete ORM models for all world entities:
  - `Universe` - Top-level settings and worlds
  - `Campaign` - Stories within universes
  - `Location` - Places in the world (continents, cities, dungeons, etc.)
  - `Character` - PCs, NPCs, villains, deities
  - `Faction` - Organizations and groups
  - `Event` - World events and history
  - `Session` - Play session records
  - `PlayerGroup` / `GroupMember` - Party management
  - `PlayerState` - Player stats, inventory, quest flags
  - `RuleSystem` - Rule system definitions
  - `RulesTopic` - Rules explanations and tutorials
  - `TutorialScript` - Guided tutorial walkthroughs
  - `WorldChangeRequest` - Player-proposed edits with conflict tracking

#### RAG System
- Vector embedding service using OpenAI
- RAG indexer for converting database entities to embeddings
- RAG retriever for querying relevant lore and rules context
- Separate vector collections for lore and rules
- Metadata filtering by universe_id and campaign_id
- Support for ChromaDB vector store

#### LLM Integration
- LLM client wrapper (OpenAI, extensible to Anthropic)
- Prompt templates for all operational modes:
  - DM Story Mode - Live session play
  - World Architect Mode - World/campaign generation
  - Rules Explanation Mode - On-demand rules help
  - World Edit Mode - Player-driven edits with conflict resolution
  - Tutorial Mode - Guided walkthroughs
- DM Brain high-level interface
- Dual-channel output system (narration + structured log_updates)

#### Orchestrator
- Session state management
- Mode switching system with 6 operational modes
- Mode handler base class and implementations:
  - DM Story Mode Handler
  - Rules Explanation Mode Handler
  - World Edit Mode Handler
  - World Architect Mode Handler
  - Tutorial Mode Handler
  - Main Menu Mode Handler

#### Audio I/O
- STT (Speech-to-Text) provider abstraction
- TTS (Text-to-Speech) provider abstraction
- OpenAI Whisper STT implementation structure
- OpenAI TTS implementation
- Multi-voice TTS wrapper for different NPC voices

#### Main Menu & Campaign Management
- Universe CRUD operations
- Campaign CRUD operations
- Party/PlayerGroup CRUD operations
- World import framework from generated data
- RAG indexing integration

#### Documentation
- Comprehensive README with setup instructions
- Architecture documentation (ARCHITECTURE.md)
- Implementation status tracking (IMPLEMENTATION_STATUS.md)
- Project structure documentation

#### Utilities
- Database initialization script
- Setup script with environment validation
- Main entry point with CLI interface
- Git repository initialization

### Technical Details
- Python 3.11+ support
- SQLAlchemy ORM with PostgreSQL
- ChromaDB for vector storage
- OpenAI API integration for LLM and embeddings
- Modular, extensible architecture
- Clean separation of concerns

### Known Limitations / Future Work
- Database write integration for log_updates (structure in place)
- Complete world import implementation
- Audio pipeline file handling
- Conflict resolution workflow completion
- Tutorial script loading from database
- API layer (FastAPI) for web interface
- Rules engine integration (D&D 5e mechanics)
- Dice rolling and initiative tracking

---

## [Unreleased]

### Planned
- FastAPI REST API layer
- WebSocket support for real-time audio
- Complete audio pipeline implementation
- Session recording and playback
- Quest tracking system
- Map/visual integrations
- Multi-speaker TTS for NPCs
- Rules engine with D&D 5e mechanics

[0.1.0]: https://github.com/mjsyp/the-last-dungeon-master/releases/tag/v0.1.0

