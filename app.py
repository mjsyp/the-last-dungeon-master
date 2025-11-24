"""FastAPI web application for DM-VA."""
from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import os
from pathlib import Path

from core.db.session import SessionLocal, get_db
from orchestrator.orchestrator import Orchestrator
from orchestrator.session_state import Mode
from main_menu.manager import MainMenuManager


# Create FastAPI app
app = FastAPI(
    title="The Last Dungeon Master (DM-VA)",
    description="A voice-driven Dungeon Master Virtual Assistant",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Favicon endpoint (must be before static files mount to avoid conflicts)
@app.get("/favicon.ico")
async def favicon():
    """Serve favicon."""
    favicon_path = Path(__file__).parent / "web" / "favicon.ico"
    if favicon_path.exists():
        return Response(content=favicon_path.read_bytes(), media_type="image/x-icon")
    # Return a simple SVG favicon as fallback
    svg_favicon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="32" height="32">
  <text y=".9em" font-size="90" text-anchor="middle" x="50">🎲</text>
</svg>"""
    return Response(content=svg_favicon.encode(), media_type="image/svg+xml")

# Mount static files
# Note: StaticFiles must be mounted before other routes that might conflict
# IMPORTANT: Use absolute path to avoid issues when server runs from different directory
web_static_path = Path(__file__).parent.resolve() / "web" / "static"
if web_static_path.exists() and web_static_path.is_dir():
    try:
        static_dir = str(web_static_path)
        app.mount("/static", StaticFiles(directory=static_dir, html=False), name="static")
        print(f"✓ Static files mounted from: {static_dir}")
    except Exception as e:
        print(f"✗ Warning: Could not mount static files: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"✗ Warning: Static files directory not found at {web_static_path}")

# Note: In production, consider using dependency injection with proper session management
# For now, we create per-request instances which is safer for multi-user scenarios


def get_orchestrator(db: Session = Depends(get_db)) -> Orchestrator:
    """Get orchestrator instance (created per request)."""
    return Orchestrator(db)


def get_menu_manager(db: Session = Depends(get_db)) -> MainMenuManager:
    """Get menu manager instance (created per request)."""
    return MainMenuManager(db)


# Request/Response models
class PlayerInput(BaseModel):
    player_utterance: str
    player_id: Optional[str] = None


class ModeSwitch(BaseModel):
    mode: str


class UniverseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    themes: Optional[List[str]] = None


class CampaignCreate(BaseModel):
    universe_id: Optional[str] = None
    name: str
    genre: Optional[str] = None
    tone: Optional[str] = None
    core_themes: Optional[List[str]] = None
    summary: Optional[str] = None


class PartyCreate(BaseModel):
    universe_id: str
    name: str
    description: Optional[str] = None


class WorldArchitectInput(BaseModel):
    requirements: str


class RulesQuestion(BaseModel):
    question: str


class WorldEditInput(BaseModel):
    proposed_change: str
    player_id: str


class MainMenuInput(BaseModel):
    input: str


# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface."""
    html_path = Path(__file__).parent / "web" / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(), media_type="text/html")
    return HTMLResponse(content="""
    <html>
        <head><title>DM-VA</title></head>
        <body>
            <h1>The Last Dungeon Master (DM-VA)</h1>
            <p>API is running! Visit <a href="/docs">/docs</a> for API documentation.</p>
            <p>Web interface coming soon.</p>
        </body>
    </html>
    """, media_type="text/html")


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/state")
async def get_state(orchestrator: Orchestrator = Depends(get_orchestrator)):
    """Get current session state."""
    state = orchestrator.get_state()
    return {
        "current_mode": state.current_mode.value,
        "active_universe_id": str(state.active_universe_id) if state.active_universe_id else None,
        "active_campaign_id": str(state.active_campaign_id) if state.active_campaign_id else None,
        "active_party_id": str(state.active_party_id) if state.active_party_id else None,
        "turn_index": state.turn_index,
        "recent_history": state.recent_history[-5:],  # Last 5 entries
    }


@app.post("/api/mode/switch")
async def switch_mode(
    mode_switch: ModeSwitch,
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Switch to a different mode."""
    try:
        new_mode = Mode(mode_switch.mode)
        orchestrator.switch_mode(new_mode)
        return {"status": "success", "mode": new_mode.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {mode_switch.mode}")


@app.post("/api/dm-story/input")
async def dm_story_input(
    input_data: PlayerInput,
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Process input in DM Story Mode."""
    if orchestrator.state.current_mode != Mode.DM_STORY:
        orchestrator.switch_mode(Mode.DM_STORY)
    
    result = orchestrator.process_input({
        "player_utterance": input_data.player_utterance,
        "player_id": input_data.player_id
    })
    return result


@app.post("/api/world-architect/generate")
async def world_architect_generate(
    input_data: WorldArchitectInput,
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Generate world in World Architect Mode."""
    if orchestrator.state.current_mode != Mode.WORLD_ARCHITECT:
        orchestrator.switch_mode(Mode.WORLD_ARCHITECT)
    
    result = orchestrator.process_input({
        "requirements": input_data.requirements
    })
    return result


@app.post("/api/rules/explain")
async def rules_explain(
    question: RulesQuestion,
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Explain rules in Rules Explanation Mode."""
    if orchestrator.state.current_mode != Mode.RULES_EXPLANATION:
        orchestrator.switch_mode(Mode.RULES_EXPLANATION)
    
    result = orchestrator.process_input({
        "question": question.question
    })
    return result


@app.post("/api/world-edit/propose")
async def world_edit_propose(
    input_data: WorldEditInput,
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Propose a world edit in World Edit Mode."""
    if orchestrator.state.current_mode != Mode.WORLD_EDIT:
        orchestrator.switch_mode(Mode.WORLD_EDIT)
    
    result = orchestrator.process_input({
        "proposed_change": input_data.proposed_change,
        "player_id": input_data.player_id
    })
    return result


@app.post("/api/main-menu/input")
async def main_menu_input(
    input_data: MainMenuInput,
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Process input in Main Menu Mode."""
    if orchestrator.state.current_mode != Mode.MAIN_MENU:
        orchestrator.switch_mode(Mode.MAIN_MENU)
    
    result = orchestrator.process_input({
        "input": input_data.input
    })
    return result


# Main Menu / Management Endpoints

@app.get("/api/universes")
async def list_universes(
    menu_manager: MainMenuManager = Depends(get_menu_manager)
):
    """List all universes."""
    return menu_manager.list_universes()


@app.get("/api/universes/{universe_id}")
async def get_universe(
    universe_id: str,
    menu_manager: MainMenuManager = Depends(get_menu_manager)
):
    """Get a specific universe."""
    universe = menu_manager.get_universe(universe_id)
    if not universe:
        raise HTTPException(status_code=404, detail="Universe not found")
    return universe


@app.post("/api/universes")
async def create_universe(
    universe_data: UniverseCreate,
    menu_manager: MainMenuManager = Depends(get_menu_manager)
):
    """Create a new universe."""
    return menu_manager.create_universe(
        name=universe_data.name,
        description=universe_data.description,
        themes=universe_data.themes
    )


@app.get("/api/campaigns")
async def list_campaigns(
    universe_id: Optional[str] = None,
    menu_manager: MainMenuManager = Depends(get_menu_manager)
):
    """List campaigns, optionally filtered by universe."""
    return menu_manager.list_campaigns(universe_id=universe_id)


@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    menu_manager: MainMenuManager = Depends(get_menu_manager)
):
    """Get a specific campaign."""
    campaign = menu_manager.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@app.post("/api/campaigns")
async def create_campaign(
    campaign_data: CampaignCreate,
    menu_manager: MainMenuManager = Depends(get_menu_manager)
):
    """Create a new campaign."""
    return menu_manager.create_campaign(
        universe_id=campaign_data.universe_id,
        name=campaign_data.name,
        genre=campaign_data.genre,
        tone=campaign_data.tone,
        core_themes=campaign_data.core_themes,
        summary=campaign_data.summary
    )


@app.get("/api/parties")
async def list_parties(
    universe_id: Optional[str] = None,
    menu_manager: MainMenuManager = Depends(get_menu_manager)
):
    """List parties, optionally filtered by universe."""
    return menu_manager.list_parties(universe_id=universe_id)


@app.post("/api/parties")
async def create_party(
    party_data: PartyCreate,
    menu_manager: MainMenuManager = Depends(get_menu_manager)
):
    """Create a new party."""
    return menu_manager.create_party(
        universe_id=party_data.universe_id,
        name=party_data.name,
        description=party_data.description
    )


@app.post("/api/session/set-universe")
async def set_active_universe(
    universe_id: str,
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Set the active universe."""
    orchestrator.set_active_universe(universe_id)
    return {"status": "success", "universe_id": universe_id}


@app.post("/api/session/set-campaign")
async def set_active_campaign(
    campaign_id: str,
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Set the active campaign."""
    orchestrator.set_active_campaign(campaign_id)
    return {"status": "success", "campaign_id": campaign_id}


@app.post("/api/session/set-party")
async def set_active_party(
    party_id: str,
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Set the active party."""
    orchestrator.set_active_party(party_id)
    return {"status": "success", "party_id": party_id}


# Audio endpoints

@app.post("/api/stt/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...)
):
    """Transcribe audio using STT."""
    from audio.stt import get_stt_provider
    
    # Read audio data
    audio_data = await audio.read()
    
    if not audio_data:
        raise HTTPException(status_code=400, detail="No audio data provided")
    
    # Transcribe using Deepgram
    stt = get_stt_provider("deepgram")
    transcript = stt.transcribe(audio_data)
    
    return {"transcript": transcript}


@app.post("/api/tts/synthesize")
async def synthesize_speech(
    request: Request
):
    """Synthesize text to speech using TTS."""
    from audio.tts import get_tts_provider
    from fastapi.responses import Response
    import json
    
    # Get JSON body
    body = await request.json()
    text = body.get("text", "")
    voice = body.get("voice")
    
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    # Synthesize using Deepgram
    tts = get_tts_provider("deepgram")
    audio_bytes = tts.synthesize(text, voice=voice, encoding="linear16", container="wav")
    
    # Return audio as response
    return Response(
        content=audio_bytes,
        media_type="audio/wav"
    )


@app.get("/api/characters")
async def list_characters(
    universe_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    menu_manager: MainMenuManager = Depends(get_menu_manager)
):
    """List characters, optionally filtered by universe or campaign."""
    return menu_manager.list_characters(universe_id=universe_id, campaign_id=campaign_id)


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("The Last Dungeon Master (DM-VA) - Web Server")
    print("=" * 60)
    print("\nStarting server...")
    print("Access the web interface at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

