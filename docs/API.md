# DM-VA API Documentation

## Overview

The DM-VA API provides endpoints for interacting with the Dungeon Master Virtual Assistant system.

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

**GET** `/api/health`

Returns the health status of the API.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### Session State

**GET** `/api/state`

Get the current session state.

**Response:**
```json
{
  "current_mode": "main_menu_mode",
  "active_universe_id": null,
  "active_campaign_id": null,
  "active_party_id": null,
  "turn_index": 0
}
```

### Mode Switching

**POST** `/api/mode/switch`

Switch to a different operational mode.

**Request Body:**
```json
{
  "mode": "dm_story_mode"
}
```

### DM Story Mode

**POST** `/api/dm-story/input`

Process player input in DM Story mode.

**Request Body:**
```json
{
  "player_utterance": "I attack the goblin"
}
```

### World Architect Mode

**POST** `/api/world-architect/generate`

Generate a new world or campaign.

**Request Body:**
```json
{
  "requirements": "A dark fantasy world with magic"
}
```

### Rules Explanation

**POST** `/api/rules/explain`

Get an explanation of game rules.

**Request Body:**
```json
{
  "question": "How does combat work?"
}
```

### World Edit Mode

**POST** `/api/world-edit/propose`

Propose a change to the world.

**Request Body:**
```json
{
  "proposed_change": "Add a new city",
  "player_id": "user1"
}
```

### Audio Endpoints

**POST** `/api/stt/transcribe`

Transcribe audio to text.

**Request:** Multipart form data with `audio` file

**Response:**
```json
{
  "transcript": "Hello, this is a test"
}
```

**POST** `/api/tts/synthesize`

Synthesize text to speech.

**Request Body:**
```json
{
  "text": "Hello, this is a test",
  "voice": "aura-asteria-en"
}
```

**Response:** Audio file (WAV format)

## Interactive Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

