"""Setup script for initializing the DM-VA system."""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.db.init_db import init_db
from config.settings import settings


def check_env():
    """Check that required environment variables are set."""
    required = ["OPENAI_API_KEY", "DATABASE_URL"]
    missing = []
    
    for var in required:
        if not getattr(settings, var.lower(), None):
            missing.append(var)
    
    if missing:
        print("ERROR: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment.")
        return False
    
    return True


def main():
    """Main setup function."""
    print("=== DM-VA Setup ===")
    print("\n1. Checking environment...")
    
    if not check_env():
        sys.exit(1)
    
    print("   ✓ Environment variables set")
    
    print("\n2. Creating database tables...")
    try:
        init_db()
        print("   ✓ Database tables created")
    except Exception as e:
        print(f"   ✗ Error creating database: {e}")
        print("\nMake sure PostgreSQL is running and DATABASE_URL is correct.")
        sys.exit(1)
    
    print("\n3. Creating ChromaDB directory...")
    chroma_dir = Path(settings.chroma_persist_dir)
    chroma_dir.mkdir(parents=True, exist_ok=True)
    print(f"   ✓ ChromaDB directory: {chroma_dir}")
    
    print("\n=== Setup Complete ===")
    print("\nYou can now run the system with: python app.py")


if __name__ == "__main__":
    main()

