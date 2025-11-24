# Unit Test Plan

## Testable Functionalities

### 1. Models (Database ORM)
- [ ] Universe model - creation, relationships, serialization
- [ ] Campaign model - creation, relationships, universe association
- [ ] Character model - creation, relationships, campaign association
- [ ] Location model - creation, relationships
- [ ] Faction model - creation, relationships
- [ ] Event model - creation, relationships
- [ ] PlayerGroup model - creation, member management
- [ ] PlayerState model - creation, state management
- [ ] BaseModel - UUID generation, timestamps

### 2. Session State Management
- [ ] Mode enum - all mode values
- [ ] SessionState dataclass - initialization, reset, history management
- [ ] SessionState.add_to_history() - history maintenance
- [ ] SessionState.format_recent_history() - formatting

### 3. Session Manager
- [ ] SessionManager.load_state() - loading from database
- [ ] SessionManager.save_state() - saving to database
- [ ] SessionManager._serialize_state() - serialization
- [ ] SessionManager._deserialize_state() - deserialization

### 4. RAG System
- [ ] EmbeddingService - embedding generation
- [ ] RAGIndexer.index_entity() - indexing entities
- [ ] RAGIndexer.remove_entity() - removing entities
- [ ] RAGIndexer.reindex_all() - full reindexing
- [ ] RAGRetriever.retrieve_lore_context() - lore retrieval
- [ ] RAGRetriever.retrieve_rules_context() - rules retrieval
- [ ] RAGRetriever filtering by universe_id/campaign_id

### 5. LLM Integration
- [ ] LLMClient.generate() - text generation
- [ ] LLMClient.stream() - streaming generation
- [ ] DMBrain.process() - DM brain processing
- [ ] DMBrain.get_narration() - narration extraction
- [ ] DMBrain.get_log_updates() - log updates extraction
- [ ] PromptTemplates - all mode prompt templates

### 6. Audio (STT/TTS)
- [ ] STTProvider interface compliance
- [ ] DeepgramSTT.transcribe() - transcription
- [ ] DeepgramSTT.transcribe_stream() - streaming transcription
- [ ] TTSProvider interface compliance
- [ ] DeepgramTTS.synthesize() - speech synthesis
- [ ] MultiVoiceTTS - voice registration and switching
- [ ] get_stt_provider() - factory function
- [ ] get_tts_provider() - factory function

### 7. Orchestrator
- [ ] Orchestrator.switch_mode() - mode switching
- [ ] Orchestrator.process_input() - input routing
- [ ] Orchestrator state persistence

### 8. Mode Handlers
- [ ] DMStoryModeHandler.process() - story mode processing
- [ ] RulesExplanationModeHandler.process() - rules explanation
- [ ] WorldEditModeHandler.process() - world edit processing
- [ ] WorldArchitectModeHandler.process() - world generation
- [ ] TutorialModeHandler.process() - tutorial processing
- [ ] MainMenuModeHandler.process() - menu processing

### 9. Main Menu Manager
- [ ] MainMenuManager.list_universes() - listing universes
- [ ] MainMenuManager.get_universe() - getting universe
- [ ] MainMenuManager.create_universe() - creating universe
- [ ] MainMenuManager.list_campaigns() - listing campaigns
- [ ] MainMenuManager.create_campaign() - creating campaign
- [ ] MainMenuManager.list_parties() - listing parties
- [ ] MainMenuManager.create_party() - creating party
- [ ] MainMenuManager.list_characters() - listing characters

### 10. Configuration
- [ ] Settings - environment variable loading
- [ ] Settings - default values

