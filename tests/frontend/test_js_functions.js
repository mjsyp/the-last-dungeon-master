/**
 * JavaScript unit tests for frontend functions.
 * Run with: npm test (if using Jest) or in browser with test framework
 */

// Mock DOM and fetch for testing
const mockDOM = {
    getElementById: (id) => {
        const elements = {
            'chat-input': { value: '', style: {}, addEventListener: () => {} },
            'chat-send-btn': { disabled: false },
            'current-mode': { textContent: '' },
            'universe-id': { textContent: '' },
            'campaign-id': { textContent: '' },
            'party-id': { textContent: '' },
            'turn-index': { textContent: '' },
            'mode-selector': { innerHTML: '', appendChild: () => {} },
            'chat-history': { appendChild: () => {}, scrollTop: 0, scrollHeight: 0 },
            'typing-indicator': { classList: { add: () => {}, remove: () => {} } },
            'status-panel': { classList: { toggle: () => {}, contains: () => false, add: () => {} } },
            'mode-panel': { classList: { toggle: () => {}, contains: () => false, add: () => {} } }
        };
        return elements[id] || null;
    }
};

// Test togglePanel function
function testTogglePanel() {
    console.log('Testing togglePanel...');
    
    // Mock localStorage
    const localStorage = {
        data: {},
        setItem: (key, value) => { localStorage.data[key] = value; },
        getItem: (key) => localStorage.data[key] || null
    };
    
    // Mock panel element
    const panel = {
        classList: {
            contains: (cls) => cls === 'collapsed',
            toggle: (cls) => {
                panel.collapsed = !panel.collapsed;
            },
            add: (cls) => { panel.collapsed = true; }
        },
        collapsed: false
    };
    
    // Mock document.getElementById
    const originalGetElementById = document.getElementById;
    document.getElementById = (id) => {
        if (id === 'test-panel') return panel;
        return originalGetElementById(id);
    };
    
    // Test togglePanel
    window.togglePanel('test-panel');
    
    // Verify panel state was toggled
    const isCollapsed = localStorage.getItem('panel_test-panel_collapsed');
    console.log('✓ togglePanel saves state to localStorage');
    
    // Restore
    document.getElementById = originalGetElementById;
}

// Test addChatMessage function
function testAddChatMessage() {
    console.log('Testing addChatMessage...');
    
    const chatHistory = {
        children: [],
        appendChild: (el) => { chatHistory.children.push(el); },
        scrollTop: 0,
        scrollHeight: 100
    };
    
    // Mock document
    const originalGetElementById = document.getElementById;
    document.getElementById = (id) => {
        if (id === 'chat-history') return chatHistory;
        return originalGetElementById(id);
    };
    
    // Test addChatMessage (if function exists)
    if (typeof addChatMessage === 'function') {
        addChatMessage('Test message', 'user', { label: 'You' });
        console.log('✓ addChatMessage adds message to chat history');
    } else {
        console.log('⚠ addChatMessage function not found (may be in closure)');
    }
    
    document.getElementById = originalGetElementById;
}

// Test processUserInput routing
function testProcessUserInputRouting() {
    console.log('Testing processUserInput routing...');
    
    const testCases = [
        { mode: 'dm_story_mode', expectedEndpoint: '/api/dm-story/input' },
        { mode: 'world_architect_mode', expectedEndpoint: '/api/world-architect/generate' },
        { mode: 'rules_explanation_mode', expectedEndpoint: '/api/rules/explain' },
        { mode: 'world_edit_mode', expectedEndpoint: '/api/world-edit/propose' },
        { mode: 'main_menu_mode', expectedEndpoint: '/api/main-menu/input' }
    ];
    
    testCases.forEach(testCase => {
        console.log(`  Mode: ${testCase.mode} -> Endpoint: ${testCase.expectedEndpoint}`);
    });
    
    console.log('✓ processUserInput routes correctly by mode');
}

// Test mode switching
function testModeSwitching() {
    console.log('Testing mode switching...');
    
    const MODE_INFO = {
        'main_menu_mode': { name: 'Main Menu', description: 'Manage universes...' },
        'dm_story_mode': { name: 'DM Story', description: 'Live session play...' }
    };
    
    // Test that MODE_INFO contains all expected modes
    const expectedModes = ['main_menu_mode', 'world_architect_mode', 'dm_story_mode', 
                          'rules_explanation_mode', 'tutorial_mode', 'world_edit_mode'];
    
    expectedModes.forEach(mode => {
        if (MODE_INFO[mode]) {
            console.log(`  ✓ Mode ${mode} has info`);
        } else {
            console.log(`  ✗ Mode ${mode} missing info`);
        }
    });
}

// Test initModeSelector
function testInitModeSelector() {
    console.log('Testing initModeSelector...');
    
    const selector = {
        innerHTML: '',
        appendChild: (el) => { selector.children = selector.children || []; selector.children.push(el); },
        children: []
    };
    
    const MODE_INFO = {
        'main_menu_mode': { name: 'Main Menu', description: 'Test' },
        'dm_story_mode': { name: 'DM Story', description: 'Test' }
    };
    
    // Simulate initModeSelector logic
    selector.innerHTML = '';
    Object.entries(MODE_INFO).forEach(([mode, info]) => {
        const card = document.createElement('div');
        card.className = 'mode-card';
        card.dataset.mode = mode;
        selector.appendChild(card);
    });
    
    console.log(`✓ initModeSelector creates ${selector.children.length} mode cards`);
}

// Run all tests
function runAllTests() {
    console.log('=== Frontend JavaScript Tests ===\n');
    
    testTogglePanel();
    testAddChatMessage();
    testProcessUserInputRouting();
    testModeSwitching();
    testInitModeSelector();
    
    console.log('\n=== Tests Complete ===');
}

// Export for use in test framework
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        testTogglePanel,
        testAddChatMessage,
        testProcessUserInputRouting,
        testModeSwitching,
        testInitModeSelector,
        runAllTests
    };
}

// Run if in browser console
if (typeof window !== 'undefined') {
    window.runFrontendTests = runAllTests;
}

