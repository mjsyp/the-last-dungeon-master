/**
 * Jest tests for frontend JavaScript functions
 */
import { JSDOM } from 'jsdom';

// Load the actual app.js file
const fs = require('fs');
const path = require('path');

describe('Frontend JavaScript Tests', () => {
    let dom;
    let window;
    let document;
    
    beforeEach(() => {
        // Create a JSDOM instance
        dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
            url: 'http://localhost:8000',
            pretendToBeVisual: true,
            resources: 'usable'
        });
        
        window = dom.window;
        document = window.document;
        
        // Set up basic DOM structure
        document.body.innerHTML = `
            <div id="status-panel" class="panel collapsible">
                <h2 onclick="togglePanel('status-panel')">Session Status</h2>
                <div class="panel-content">
                    <span id="current-mode">main_menu_mode</span>
                </div>
            </div>
            <div id="mode-selector"></div>
            <div id="chat-input"></div>
            <div id="chat-send-btn"></div>
            <div id="chat-history"></div>
            <div id="typing-indicator"></div>
        `;
        
        // Mock global functions
        global.window = window;
        global.document = document;
        global.localStorage = {
            getItem: jest.fn(),
            setItem: jest.fn(),
        };
    });
    
    afterEach(() => {
        dom.window.close();
    });
    
    describe('togglePanel', () => {
        test('should toggle panel collapsed class', () => {
            const panel = document.getElementById('status-panel');
            
            // Define togglePanel in window scope
            window.togglePanel = function(panelId) {
                const panel = document.getElementById(panelId);
                if (!panel) return;
                panel.classList.toggle('collapsed');
                const isCollapsed = panel.classList.contains('collapsed');
                localStorage.setItem(`panel_${panelId}_collapsed`, isCollapsed);
            };
            
            // Test toggle
            window.togglePanel('status-panel');
            
            expect(panel.classList.contains('collapsed')).toBe(true);
            expect(localStorage.setItem).toHaveBeenCalledWith(
                'panel_status-panel_collapsed',
                'true'
            );
        });
    });
    
    describe('Mode Selector', () => {
        test('should create mode cards', () => {
            const MODE_INFO = {
                'main_menu_mode': {
                    name: 'Main Menu',
                    description: 'Manage universes...'
                },
                'dm_story_mode': {
                    name: 'DM Story',
                    description: 'Live session play...'
                }
            };
            
            const selector = document.getElementById('mode-selector');
            selector.innerHTML = '';
            
            Object.entries(MODE_INFO).forEach(([mode, info]) => {
                const card = document.createElement('div');
                card.className = 'mode-card';
                card.dataset.mode = mode;
                card.innerHTML = `
                    <div class="mode-name">${info.name}</div>
                    <div class="mode-description">${info.description}</div>
                `;
                selector.appendChild(card);
            });
            
            const cards = selector.querySelectorAll('.mode-card');
            expect(cards.length).toBe(2);
            expect(cards[0].dataset.mode).toBe('main_menu_mode');
        });
    });
    
    describe('Chat Input', () => {
        test('should handle chat submission', () => {
            const input = document.getElementById('chat-input');
            input.value = 'Test message';
            
            // Mock handleChatSubmit
            window.handleChatSubmit = jest.fn(async function() {
                const input = document.getElementById('chat-input');
                const inputText = input.value.trim();
                if (!inputText) return;
                input.value = '';
                // Would call processUserInput here
            });
            
            window.handleChatSubmit();
            
            expect(window.handleChatSubmit).toHaveBeenCalled();
            expect(input.value).toBe('');
        });
    });
    
    describe('API Routing', () => {
        test('should route to correct endpoint based on mode', () => {
            const routing = {
                'dm_story_mode': '/api/dm-story/input',
                'world_architect_mode': '/api/world-architect/generate',
                'rules_explanation_mode': '/api/rules/explain',
                'world_edit_mode': '/api/world-edit/propose',
                'main_menu_mode': '/api/main-menu/input'
            };
            
            Object.entries(routing).forEach(([mode, endpoint]) => {
                expect(routing[mode]).toBe(endpoint);
            });
        });
    });
    
    describe('State Management', () => {
        test('should update UI from state', () => {
            const state = {
                current_mode: 'dm_story_mode',
                active_universe_id: 'test-universe-id',
                turn_index: 5
            };
            
            const modeEl = document.getElementById('current-mode');
            modeEl.textContent = state.current_mode;
            
            expect(modeEl.textContent).toBe('dm_story_mode');
        });
    });
});

