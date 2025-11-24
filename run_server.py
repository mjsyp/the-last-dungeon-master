"""Run the DM-VA web server."""
import uvicorn
from app import app

if __name__ == "__main__":
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

