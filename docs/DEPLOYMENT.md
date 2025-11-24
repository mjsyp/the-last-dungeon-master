# DM-VA Deployment Guide

## Prerequisites

- Python 3.11+
- PostgreSQL (or SQLite for development)
- OpenAI API key
- Deepgram API key (for STT/TTS)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd the-last-dungeon-master
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database URL
   ```

4. **Initialize the database:**
   ```bash
   python scripts/init_db.py
   ```

## Running the Application

### Development Mode

```bash
python app.py
```

The server will start on http://localhost:8000

### Production Mode

For production, use a proper ASGI server like Gunicorn with Uvicorn workers:

```bash
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Environment Variables

See `.env.example` for all required environment variables.

## Database Setup

### PostgreSQL

1. Create a database:
   ```sql
   CREATE DATABASE dm_va;
   ```

2. Update `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/dm_va
   ```

### SQLite (Development)

For development, you can use SQLite:
```
DATABASE_URL=sqlite:///./data/db/dm_va.db
```

## Data Directory

The application stores data in the `data/` directory:
- `data/db/` - SQLite databases (if using SQLite)
- `data/chroma/` - ChromaDB vector store data

Make sure this directory is writable by the application.

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running
- Check `DATABASE_URL` is correct
- Ensure database exists and user has permissions

### API Key Issues

- Verify all required API keys are set in `.env`
- Check API keys are valid and have sufficient credits

### ChromaDB Issues

- Ensure `data/chroma/` directory exists and is writable
- Check disk space is available

