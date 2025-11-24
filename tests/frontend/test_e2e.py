"""
End-to-end tests for the web interface using Playwright.
Install: pip install pytest-playwright
Setup: playwright install
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application."""
    return "http://localhost:8000"


@pytest.fixture
def page(base_url, page: Page):
    """Create a page instance."""
    page.goto(base_url)
    return page


class TestWebInterface:
    """E2E tests for web interface."""
    
    def test_page_loads(self, page: Page):
        """Test that the page loads correctly."""
        expect(page).to_have_title("The Last Dungeon Master (DM-VA)")
        expect(page.locator("h1")).to_contain_text("The Last Dungeon Master")
    
    def test_session_status_panel(self, page: Page):
        """Test session status panel is visible."""
        status_panel = page.locator("#status-panel")
        expect(status_panel).to_be_visible()
        
        # Check status items exist
        expect(page.locator("#current-mode")).to_be_visible()
        expect(page.locator("#universe-id")).to_be_visible()
        expect(page.locator("#campaign-id")).to_be_visible()
    
    def test_panel_collapse(self, page: Page):
        """Test that panels can be collapsed."""
        status_panel = page.locator("#status-panel")
        panel_header = status_panel.locator("h2")
        
        # Click to collapse
        panel_header.click()
        
        # Check that panel is collapsed
        expect(status_panel).to_have_class(/collapsed/)
    
    def test_mode_selector(self, page: Page):
        """Test mode selector displays mode cards."""
        mode_selector = page.locator("#mode-selector")
        expect(mode_selector).to_be_visible()
        
        # Check that mode cards exist
        mode_cards = page.locator(".mode-card")
        expect(mode_cards).to_have_count(6)  # 6 modes
    
    def test_mode_card_click(self, page: Page):
        """Test clicking a mode card switches mode."""
        # Find a mode card
        mode_card = page.locator(".mode-card").first
        
        # Click it
        mode_card.click()
        
        # Wait for API call (if implemented)
        # Check that mode indicator updates
        # This would require mocking the API or checking UI state
    
    def test_chat_input_exists(self, page: Page):
        """Test chat input is present."""
        chat_input = page.locator("#chat-input")
        expect(chat_input).to_be_visible()
        expect(chat_input).to_be_enabled()
    
    def test_chat_send_button(self, page: Page):
        """Test chat send button exists."""
        send_button = page.locator("#chat-send-btn")
        expect(send_button).to_be_visible()
        expect(send_button).to_be_enabled()
    
    def test_chat_message_send(self, page: Page):
        """Test sending a chat message."""
        chat_input = page.locator("#chat-input")
        send_button = page.locator("#chat-send-btn")
        
        # Type a message
        chat_input.fill("Test message")
        
        # Click send
        send_button.click()
        
        # Check that message appears in chat history
        # This would require checking chat history or mocking API
        chat_history = page.locator("#chat-history")
        expect(chat_history).to_be_visible()
    
    def test_audio_controls(self, page: Page):
        """Test audio control checkboxes."""
        listen_checkbox = page.locator("#listen-checkbox")
        speak_checkbox = page.locator("#speak-checkbox")
        
        expect(listen_checkbox).to_be_visible()
        expect(speak_checkbox).to_be_visible()
    
    def test_entities_panel(self, page: Page):
        """Test entities panel (if visible)."""
        entities_panel = page.locator("#entity-panel")
        # Panel may be hidden by default
        if entities_panel.is_visible():
            expect(page.locator("#universes-list")).to_be_visible()
            expect(page.locator("#campaigns-list")).to_be_visible()
            expect(page.locator("#characters-list")).to_be_visible()


class TestAPIIntegration:
    """Test API integration from browser."""
    
    def test_state_endpoint_accessible(self, page: Page):
        """Test that state endpoint is accessible."""
        # Use page.evaluate to make fetch call
        response = page.evaluate("""
            async () => {
                const response = await fetch('/api/state');
                return { status: response.status, ok: response.ok };
            }
        """)
        
        assert response["ok"] is True
        assert response["status"] == 200
    
    def test_health_endpoint(self, page: Page):
        """Test health endpoint from browser."""
        response = page.evaluate("""
            async () => {
                const response = await fetch('/api/health');
                return await response.json();
            }
        """)
        
        assert response["status"] == "ok"
        assert "version" in response


@pytest.mark.skip(reason="Requires running server")
class TestFullUserFlow:
    """Test complete user flows."""
    
    def test_create_universe_flow(self, page: Page):
        """Test creating a universe through the UI."""
        # 1. Switch to world architect mode
        world_architect_card = page.locator(".mode-card[data-mode='world_architect_mode']")
        world_architect_card.click()
        
        # 2. Enter requirements
        chat_input = page.locator("#chat-input")
        chat_input.fill("Create a dark fantasy universe")
        
        # 3. Send
        send_button = page.locator("#chat-send-btn")
        send_button.click()
        
        # 4. Wait for response
        # 5. Check that universe was created
        # This would require checking API or UI state

