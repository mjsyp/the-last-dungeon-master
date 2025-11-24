# The Last Dungeon Master (DM-VA)

A voice-driven Dungeon Master Virtual Assistant that uses LLMs to run consistent, lore-aware tabletop RPG sessions.

## Architecture

The system is organized into four main layers:

1. **I/O & Orchestration** - Audio input/output, session management, mode switching
2. **World Model & Memory (Logbook)** - Database + RAG for persistent world state
3. **Narrative Engine** - LLM integration with dual-channel output (narration + state updates)
4. **Tools & Integrations** - Rules engine, dice rolling, etc. (future)

## Modes

- **Main Menu Mode** - Universe/campaign/party management
- **World Architect Mode** - Campaign/universe creation and setup
- **DM Story Mode** - Live session play
- **Rules Explanation Mode** - On-demand help and tutorials
- **World Edit Mode** - Player-driven edits with conflict resolution

## Tech Stack

- Python 3.11+
- SQLAlchemy (PostgreSQL)
- ChromaDB (vector store for RAG)
- OpenAI/Anthropic APIs (LLM)
- FastAPI (future API layer)

## Project Structure

```
.
├── core/              # Core domain models and interfaces
├── models/            # Database ORM models
├── rag/               # Vector indexing and retrieval
├── llm/               # LLM integration and prompt templates
├── audio/             # STT/TTS abstractions
├── orchestrator/      # Mode management and session orchestration
├── main_menu/         # Main menu and campaign management
├── config/            # Configuration management
└── main.py            # Entry point
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database:**
   - Install PostgreSQL if not already installed
   - Create a database: `createdb dm_va`
   - Or use an existing database

3. **Configure environment variables:**
   - Copy `.env.example` to `.env` (if it exists, or create one)
   - Set `DATABASE_URL` (e.g., `postgresql://user:password@localhost:5432/dm_va`)
   - Set `OPENAI_API_KEY` (required for LLM and embeddings)

4. **Initialize the database:**
   ```bash
   python setup.py
   ```
   Or manually:
   ```bash
   python -m core.db.init_db
   ```

5. **Start the web server:**
   ```bash
   python run_server.py
   ```
   
   Or for CLI mode:
   ```bash
   python main.py
   ```

6. **Access the application:**
   - Web interface: http://localhost:8000
   - API documentation: http://localhost:8000/docs
   - Interactive API: http://localhost:8000/redoc

## Quick Start

After setup, you can:

- Switch modes: `mode dm_story`
- Check state: `state`
- Process input: Just type your message (will be processed in current mode)
- Get help: `help`

## Development Status

✅ **Completed:**
- Core data models (all entities)
- Database initialization
- RAG indexing and retrieval
- LLM integration with all mode prompts
- Mode orchestrator and session management
- Audio I/O abstractions (STT/TTS interfaces)
- Main menu and campaign management

🚧 **In Progress / TODO:**
- Full integration of log_updates → database writes
- Complete world import from World Architect Mode
- Audio pipeline implementation (actual STT/TTS integration)
- Conflict resolution workflow in World Edit Mode
- Tutorial script loading from database
- API layer (FastAPI) for web interface
- Rules engine integration

