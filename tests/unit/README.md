# Unit Tests

## Overview

Comprehensive unit test suite for DM-VA covering all major functionalities.

## Test Files

1. **test_models.py** - Database ORM models
   - Universe, Campaign, Character models
   - BaseModel UUID and timestamp functionality
   - PlayerGroup model

2. **test_session_state.py** - Session state management
   - Mode enum
   - SessionState dataclass operations
   - History management

3. **test_session_manager.py** - Session persistence
   - Loading and saving state
   - Serialization/deserialization
   - Multiple session isolation

4. **test_rag.py** - RAG system
   - EmbeddingService
   - RAGIndexer
   - RAGRetriever

5. **test_llm.py** - LLM integration
   - LLMClient
   - DMBrain
   - PromptTemplates

6. **test_audio.py** - Audio providers
   - Deepgram STT/TTS
   - Factory functions

7. **test_main_menu.py** - Main menu manager
   - CRUD operations for universes, campaigns, parties, characters

8. **test_orchestrator.py** - Orchestrator
   - Mode switching
   - Input routing
   - State persistence

9. **test_mode_handlers.py** - Mode handlers
   - All 6 mode handlers (DM Story, Rules, World Edit, etc.)

## Running Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_models.py -v

# Run with coverage
pytest tests/unit/ --cov=. --cov-report=html

# Run specific test
pytest tests/unit/test_models.py::TestUniverse::test_create_universe -v
```

## Test Coverage

- **Models**: ✅ Universe, Campaign, Character, BaseModel, PlayerGroup
- **Session State**: ✅ Mode enum, SessionState, history management
- **Session Manager**: ✅ Load/save, serialize/deserialize
- **RAG**: ✅ EmbeddingService, Indexer, Retriever
- **LLM**: ✅ LLMClient, DMBrain, PromptTemplates
- **Audio**: ✅ Deepgram STT/TTS, factory functions
- **Main Menu**: ✅ All CRUD operations
- **Orchestrator**: ✅ Mode switching, routing
- **Mode Handlers**: ✅ All 6 handlers

## Notes

- External dependencies (OpenAI, Deepgram, ChromaDB) are mocked
- Database tests use in-memory SQLite
- Tests are isolated and can run in any order
- Fixtures provide common setup (db_session, mocks)

