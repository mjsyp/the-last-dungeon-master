        // Make togglePanel globally accessible (must be in window scope for onclick handlers)
        window.togglePanel = function(panelId) {
            const panel = document.getElementById(panelId);
            if (!panel) {
                console.error(`Panel ${panelId} not found`);
                return;
            }
            panel.classList.toggle('collapsed');
            
            // Save state to localStorage
            const isCollapsed = panel.classList.contains('collapsed');
            localStorage.setItem(`panel_${panelId}_collapsed`, isCollapsed);
        };
        
        // Restore panel states from localStorage
        function restorePanelStates() {
            const panels = ['status-panel', 'mode-panel'];
            panels.forEach(panelId => {
                const isCollapsed = localStorage.getItem(`panel_${panelId}_collapsed`) === 'true';
                const panel = document.getElementById(panelId);
                if (panel && isCollapsed) {
                    panel.classList.add('collapsed');
                }
            });
        }
        
        // Make handleChatSubmit globally accessible
        window.handleChatSubmit = async function() {
            const input = document.getElementById('chat-input');
            if (!input) {
                console.error('Chat input not found');
                return;
            }
            const inputText = input.value.trim();
            if (!inputText) return;
            
            // Clear input
            input.value = '';
            input.style.height = 'auto';
            
            // Add user message to chat
            addChatMessage(inputText, 'user', { label: 'You' });
            
            // Process the input
            await processUserInput(inputText);
        };
        
        const API_BASE = '';
        let currentMode = null;
        let chatHistory = [];
        let isListening = false;
        let mediaRecorder = null;
        let audioChunks = [];
        let audioContext = null;
        
        const MODE_INFO = {
            'main_menu_mode': {
                name: 'Main Menu',
                description: 'Manage universes, campaigns, and parties. Select your active world context.'
            },
            'world_architect_mode': {
                name: 'World Architect',
                description: 'Generate or import new universes and campaigns. Create rich, interconnected worlds.'
            },
            'dm_story_mode': {
                name: 'DM Story',
                description: 'Live session play. The DM narrates the world and responds to player actions.'
            },
            'rules_explanation_mode': {
                name: 'Rules Explanation',
                description: 'Ask questions about game rules and mechanics. Get clear explanations with examples.'
            },
            'tutorial_mode': {
                name: 'Tutorial',
                description: 'Guided walkthroughs to learn the system and game mechanics step-by-step.'
            },
            'world_edit_mode': {
                name: 'World Edit',
                description: 'Propose changes to the world. The system checks for conflicts and helps resolve them.'
            }
        };
        
        // Initialize mode selector
        function initModeSelector() {
            const selector = document.getElementById('mode-selector');
            if (!selector) {
                console.error('Mode selector element not found');
                return;
            }
            selector.innerHTML = '';
            
            Object.entries(MODE_INFO).forEach(([mode, info]) => {
                const card = document.createElement('div');
                card.className = 'mode-card';
                card.dataset.mode = mode;
                card.innerHTML = `
                    <div class="mode-name">${info.name}</div>
                    <div class="mode-description">${info.description}</div>
                `;
                card.addEventListener('click', () => switchMode(mode));
                selector.appendChild(card);
            });
            
            console.log(`Initialized ${Object.keys(MODE_INFO).length} mode cards`);
        }
        
        // Load initial state
        async function loadState() {
            try {
                const response = await fetch(`${API_BASE}/api/state`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const state = await response.json();
                currentMode = state.current_mode;
                updateUI(state);
                loadEntities();
            } catch (error) {
                console.error('Error loading state:', error);
                // Set default values if state fails to load
                document.getElementById('current-mode').textContent = 'main_menu_mode';
                document.getElementById('universe-id').textContent = 'None';
                document.getElementById('campaign-id').textContent = 'None';
                document.getElementById('party-id').textContent = 'None';
                document.getElementById('turn-index').textContent = '0';
                showError('Failed to load session state');
            }
        }
        
        function updateUI(state) {
            document.getElementById('current-mode').textContent = state.current_mode || 'None';
            document.getElementById('universe-id').textContent = state.active_universe_id || 'None';
            document.getElementById('campaign-id').textContent = state.active_campaign_id || 'None';
            document.getElementById('party-id').textContent = state.active_party_id || 'None';
            document.getElementById('turn-index').textContent = state.turn_index || 0;
            
            // Update active mode card using the helper function
            updateModeIndicator(state.current_mode);
        }
        
        // Load entities (universes, campaigns, characters)
        async function loadEntities() {
            try {
                // Load universes
                const universesRes = await fetch(`${API_BASE}/api/universes`);
                const universes = await universesRes.json();
                displayEntities('universes-list', universes, 'name', 'description');
                
                // Load campaigns
                const campaignsRes = await fetch(`${API_BASE}/api/campaigns`);
                const campaigns = await campaignsRes.json();
                displayEntities('campaigns-list', campaigns, 'name', 'genre');
                
                // Load characters
                const charactersRes = await fetch(`${API_BASE}/api/characters`);
                const characters = await charactersRes.json();
                displayEntities('characters-list', characters, 'name', 'role');
                
                // Show entity panel if we have entities or in relevant modes
                const relevantModes = ['main_menu_mode', 'world_architect_mode', 'dm_story_mode', 'world_edit_mode'];
                if (relevantModes.includes(currentMode) && (universes.length > 0 || campaigns.length > 0 || characters.length > 0)) {
                    document.getElementById('entity-panel').style.display = 'block';
                } else {
                    document.getElementById('entity-panel').style.display = 'none';
                }
            } catch (error) {
                console.error('Error loading entities:', error);
            }
        }
        
        function displayEntities(containerId, entities, nameField, metaField) {
            const container = document.getElementById(containerId);
            if (entities.length === 0) {
                container.innerHTML = '<div class="entity-item empty">No items yet</div>';
                return;
            }
            
            container.innerHTML = entities.map(entity => `
                <div class="entity-item">
                    <div class="entity-name">${entity[nameField] || 'Unnamed'}</div>
                    <div class="entity-meta">${entity[metaField] || ''}</div>
                </div>
            `).join('');
        }
        
        // Mode switching
        async function switchMode(mode) {
            try {
                const response = await fetch(`${API_BASE}/api/mode/switch`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mode })
                });
                const result = await response.json();
                if (result.status === 'success') {
                    currentMode = result.mode;
                    // Update UI immediately
                    updateModeIndicator(result.mode);
                    // Then refresh full state
                    await loadState();
                    showSuccess(`Switched to ${MODE_INFO[mode].name}`);
                }
            } catch (error) {
                console.error('Error switching mode:', error);
                showError('Failed to switch mode');
            }
        }
        
        // Update mode indicator immediately
        function updateModeIndicator(mode) {
            document.querySelectorAll('.mode-card').forEach(card => {
                card.classList.remove('active');
                if (card.dataset.mode === mode) {
                    card.classList.add('active');
                }
            });
            // Also update the status display
            if (document.getElementById('current-mode')) {
                document.getElementById('current-mode').textContent = mode || 'None';
            }
        }
        
        // Add message to chat history
        function addChatMessage(text, sender, metadata = {}) {
            const chatHistoryEl = document.getElementById('chat-history');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${sender}`;
            
            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            bubble.textContent = text;
            messageDiv.appendChild(bubble);
            
            const meta = document.createElement('div');
            meta.className = 'message-meta';
            meta.textContent = metadata.label || sender;
            messageDiv.appendChild(meta);
            
            chatHistoryEl.appendChild(messageDiv);
            scrollChatToBottom();
            
            // Store in history
            chatHistory.push({ text, sender, timestamp: new Date(), metadata });
        }
        
        // Scroll chat to bottom
        function scrollChatToBottom() {
            const chatHistoryEl = document.getElementById('chat-history');
            chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
        }
        
        // Show/hide typing indicator
        function showTypingIndicator(show = true) {
            const indicator = document.getElementById('typing-indicator');
            if (show) {
                indicator.classList.add('active');
            } else {
                indicator.classList.remove('active');
            }
            scrollChatToBottom();
        }
        
        // Handle chat submission is now defined in window scope above
        
        // Process user input (from text or STT)
        async function processUserInput(inputText) {
            const sendBtn = document.getElementById('chat-send-btn');
            const inputEl = document.getElementById('chat-input');
            
            if (sendBtn) {
                sendBtn.disabled = true;
            }
            showTypingIndicator(true);
            
            try {
                let endpoint = '';
                let body = {};
                
                // Route to appropriate endpoint based on mode
                // Default to main menu mode if currentMode is null
                const mode = currentMode || 'main_menu_mode';
                
                switch (mode) {
                    case 'dm_story_mode':
                        endpoint = '/api/dm-story/input';
                        body = { player_utterance: inputText };
                        break;
                    case 'world_architect_mode':
                        endpoint = '/api/world-architect/generate';
                        body = { requirements: inputText };
                        break;
                    case 'rules_explanation_mode':
                        endpoint = '/api/rules/explain';
                        body = { question: inputText };
                        break;
                    case 'world_edit_mode':
                        endpoint = '/api/world-edit/propose';
                        body = { proposed_change: inputText, player_id: 'user1' };
                        break;
                    case 'main_menu_mode':
                    default:
                        endpoint = '/api/main-menu/input';
                        body = { input: inputText };
                        break;
                }
                
                console.log(`Sending to ${endpoint} with mode: ${mode}`);
                const response = await fetch(`${API_BASE}${endpoint}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                
                // Hide typing indicator
                showTypingIndicator(false);
                
                // Re-enable send button
                if (sendBtn) {
                    sendBtn.disabled = false;
                }
                
                // Format and add response
                let responseText = '';
                if (result.narration) {
                    responseText = result.narration;
                } else if (result.explanation) {
                    responseText = result.explanation;
                } else if (result.message) {
                    responseText = result.message;
                } else if (result.response) {
                    responseText = result.response;
                } else if (typeof result === 'string') {
                    responseText = result;
                } else {
                    responseText = JSON.stringify(result, null, 2);
                }
                
                if (responseText) {
                    addChatMessage(responseText, 'system', { label: 'DM' });
                    
                    // Play TTS if enabled
                    const speakCheckbox = document.getElementById('speak-checkbox');
                    if (speakCheckbox && speakCheckbox.checked) {
                        await playTTS(responseText);
                    }
                }
                
                // Focus input again
                if (inputEl) {
                    inputEl.focus();
                }
            } catch (error) {
                console.error('Error processing input:', error);
                showTypingIndicator(false);
                if (sendBtn) {
                    sendBtn.disabled = false;
                }
                addChatMessage(`Error: ${error.message}`, 'system', { label: 'Error' });
            }
        }
        
        // Start listening with microphone
        async function startListening() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                
                // Create MediaRecorder
                mediaRecorder = new MediaRecorder(stream, {
                    mimeType: 'audio/webm;codecs=opus'
                });
                
                audioChunks = [];
                
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                    }
                };
                
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    await processAudioInput(audioBlob);
                    stream.getTracks().forEach(track => track.stop());
                };
                
                // Start recording
                mediaRecorder.start();
                isListening = true;
                listenIndicator.classList.add('active');
                updateCheckboxLabels();
                
                // Auto-stop after 5 seconds of silence or manual stop
                setTimeout(() => {
                    if (isListening && mediaRecorder.state === 'recording') {
                        stopListening();
                    }
                }, 5000);
                
            } catch (error) {
                console.error('Error accessing microphone:', error);
                showError('Failed to access microphone. Please check permissions.');
                listenCheckbox.checked = false;
                updateCheckboxLabels();
            }
        }
        
        // Stop listening
        function stopListening() {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
            }
            isListening = false;
            listenIndicator.classList.remove('active');
            updateCheckboxLabels();
        }
        
        // Process audio input through STT
        async function processAudioInput(audioBlob) {
            try {
                // Show processing message
                addChatMessage('Processing audio...', 'system', { label: 'System' });
                
                // Convert to format Deepgram can use
                const formData = new FormData();
                formData.append('audio', audioBlob, 'audio.webm');
                
                // Send to STT endpoint
                const response = await fetch(`${API_BASE}/api/stt/transcribe`, {
                    method: 'POST',
                    body: formData
                    // Note: Don't set Content-Type header, browser will set it with boundary
                });
                
                const result = await response.json();
                
                if (result.transcript) {
                    // Add transcript to chat
                    addChatMessage(result.transcript, 'user', { label: 'You (Voice)' });
                    
                    // Process as if it was typed
                    await processUserInput(result.transcript);
                } else {
                    addChatMessage('Could not transcribe audio. Please try again.', 'system', { label: 'Error' });
                }
                
            } catch (error) {
                console.error('Error processing audio:', error);
                addChatMessage(`Error processing audio: ${error.message}`, 'system', { label: 'Error' });
            }
        }
        
        // Play TTS audio
        async function playTTS(text) {
            try {
                // Request TTS from server
                const response = await fetch(`${API_BASE}/api/tts/synthesize`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                
                // Play audio
                const audio = new Audio(audioUrl);
                await audio.play();
                
                // Clean up
                audio.onended = () => {
                    URL.revokeObjectURL(audioUrl);
                };
                
            } catch (error) {
                console.error('Error playing TTS:', error);
                // Don't show error to user, just log it
            }
        }
        
        // Listen/Speak checkbox handlers
        const listenCheckbox = document.getElementById('listen-checkbox');
        const speakCheckbox = document.getElementById('speak-checkbox');
        const listenIndicator = document.getElementById('listen-indicator');
        
        listenCheckbox.addEventListener('change', async (e) => {
            if (e.target.checked) {
                await startListening();
            } else {
                stopListening();
            }
        });
        
        speakCheckbox.addEventListener('change', (e) => {
            // Just update the state, TTS will be used when processing responses
            updateCheckboxLabels();
        });
        
        function updateCheckboxLabels() {
            const listenLabel = listenCheckbox.closest('.toggle-switch');
            const speakLabel = speakCheckbox.closest('.toggle-switch');
            
            if (listenCheckbox.checked) {
                listenLabel.classList.add('active');
            } else {
                listenLabel.classList.remove('active');
            }
            
            if (speakCheckbox.checked) {
                speakLabel.classList.add('active');
            } else {
                speakLabel.classList.remove('active');
            }
        }
        
        // Chat input event listeners are now set up in initializeApp()
        
        function showError(message) {
            addChatMessage(message, 'system', { label: 'Error' });
        }
        
        function showSuccess(message) {
            addChatMessage(message, 'system', { label: 'Success' });
        }
        
        // Initialize when DOM is ready
        function initializeApp() {
            // Initialize mode selector
            const selector = document.getElementById('mode-selector');
            if (selector) {
                initModeSelector();
            } else {
                console.error('Mode selector element not found');
            }
            
            // Load state immediately and set up intervals
            loadState().catch(err => {
                console.error('Initial state load failed:', err);
                // Set defaults
                const modeEl = document.getElementById('current-mode');
                if (modeEl) {
                    modeEl.textContent = 'main_menu_mode';
                }
            });
            setInterval(loadState, 5000); // Refresh state every 5 seconds
            setInterval(loadEntities, 10000); // Refresh entities every 10 seconds
            
            // Restore panel states
            restorePanelStates();
            
            // Initialize checkbox labels
            updateCheckboxLabels();
            
            // Set up chat input event listeners
            const chatInput = document.getElementById('chat-input');
            if (chatInput) {
                // Auto-resize textarea
                chatInput.addEventListener('input', function() {
                    this.style.height = 'auto';
                    this.style.height = Math.min(this.scrollHeight, 150) + 'px';
                });
                
                // Enter key to submit (Ctrl+Enter or just Enter)
                chatInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                        e.preventDefault();
                        handleChatSubmit();
                    } else if (e.key === 'Enter' && !e.shiftKey) {
                        // Allow Enter to submit, Shift+Enter for new line
                        e.preventDefault();
                        handleChatSubmit();
                    }
                });
                chatInput.focus();
            }
        }
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initializeApp);
        } else {
            // DOM is already loaded, initialize now
            initializeApp();
        }

