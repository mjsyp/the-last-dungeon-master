"""Main entry point for DM-VA."""
import sys
from core.db.session import SessionLocal
from orchestrator.orchestrator import Orchestrator
from orchestrator.session_state import Mode


def main():
    """Main entry point."""
    print("=== The Last Dungeon Master (DM-VA) ===")
    print("Initializing...")
    
    # Initialize database session
    db = SessionLocal()
    
    try:
        # Create orchestrator
        orchestrator = Orchestrator(db)
        
        print("\nSystem ready!")
        print("Current mode:", orchestrator.state.current_mode.value)
        print("\nAvailable commands:")
        print("  - 'help': Show help")
        print("  - 'mode <mode_name>': Switch mode")
        print("  - 'quit': Exit")
        print("\nModes: main_menu, world_architect, dm_story, rules_explanation, tutorial, world_edit")
        print("\nNote: For web interface, run: python run_server.py")
        
        # Simple CLI loop (for testing)
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "quit":
                    break
                
                if user_input.lower() == "help":
                    print("\nCommands:")
                    print("  help - Show this help")
                    print("  mode <mode> - Switch to a mode")
                    print("  state - Show current session state")
                    print("  quit - Exit")
                    continue
                
                if user_input.lower() == "state":
                    state = orchestrator.get_state()
                    print(f"\nCurrent Mode: {state.current_mode.value}")
                    print(f"Universe ID: {state.active_universe_id}")
                    print(f"Campaign ID: {state.active_campaign_id}")
                    print(f"Party ID: {state.active_party_id}")
                    continue
                
                if user_input.lower().startswith("mode "):
                    mode_name = user_input[5:].strip()
                    try:
                        new_mode = Mode(mode_name)
                        orchestrator.switch_mode(new_mode)
                        print(f"Switched to mode: {new_mode.value}")
                    except ValueError:
                        print(f"Unknown mode: {mode_name}")
                    continue
                
                # Process as input to current mode
                result = orchestrator.process_input({"player_utterance": user_input})
                print(f"\nResult: {result}")
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
    
    finally:
        db.close()
        print("\nGoodbye!")


if __name__ == "__main__":
    main()

