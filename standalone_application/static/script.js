/**
 * AI Game Bot Dashboard JavaScript
 * Handles real-time updates and user interactions
 */

class GameBotDashboard {
    constructor() {
        this.updateInterval = 2000; // 2 seconds
        this.isRecording = false;
        this.commandHistory = [];
        this.trainingMode = false;
        this.currentTrainingMode = 'idle';
        this.zoneCorners = [];
        this.spacebarListener = null;
        
        this.initializeEventListeners();
        this.startStatusUpdates();
        this.loadMacros();
    }
    
    initializeEventListeners() {
        // Command execution
        document.getElementById('executeBtn').addEventListener('click', () => {
            this.executeCommand();
        });
        
        document.getElementById('commandInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.executeCommand();
            }
        });
        
        // Quick command buttons
        document.querySelectorAll('.quick-cmd').forEach(btn => {
            btn.addEventListener('click', () => {
                const command = btn.getAttribute('data-cmd');
                document.getElementById('commandInput').value = command;
                this.executeCommand();
            });
        });
        
        // Learning functionality
        document.getElementById('learnBtn').addEventListener('click', () => {
            this.learnFromSource();
        });
        
        document.getElementById('learnInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.learnFromSource();
            }
        });
        
        // Interactive Training controls
        document.getElementById('processCommandBtn').addEventListener('click', () => {
            this.processNaturalCommand();
        });
        
        document.getElementById('trainingCommand').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.processNaturalCommand();
            }
        });
        
        document.querySelectorAll('.training-mode').forEach(btn => {
            btn.addEventListener('click', () => {
                const mode = btn.getAttribute('data-mode');
                this.startTrainingMode(mode);
            });
        });
        
        document.getElementById('stopTrainingBtn').addEventListener('click', () => {
            this.stopTraining();
        });
        
        document.getElementById('analyzeSimilarBtn').addEventListener('click', () => {
            this.analyzeSimilarities();
        });
        
        document.getElementById('findItemsBtn').addEventListener('click', () => {
            this.findSimilarItems();
        });
        
        // Spacebar listener for item learning
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && this.trainingMode && this.currentTrainingMode === 'item_learning') {
                e.preventDefault();
                this.processSpacebarInput();
            }
        });
        
        // Screen click listener for zone mapping
        document.addEventListener('click', (e) => {
            if (this.trainingMode && this.currentTrainingMode === 'zone_mapping') {
                // Only process clicks on the screen capture area
                const screenImg = document.getElementById('screenCapture');
                if (screenImg && screenImg.contains(e.target)) {
                    this.processZoneClick(e);
                }
            }
        });
        
        // Macro controls
        document.getElementById('recordBtn').addEventListener('click', () => {
            this.toggleRecording();
        });
        
        document.getElementById('stopBtn').addEventListener('click', () => {
            this.stopRecording();
        });
        
        document.getElementById('playMacroBtn').addEventListener('click', () => {
            this.playMacro();
        });
    }
    
    async executeCommand() {
        const commandInput = document.getElementById('commandInput');
        const command = commandInput.value.trim();
        
        if (!command) return;
        
        // Add to history
        this.commandHistory.push({
            command: command,
            timestamp: new Date().toISOString()
        });
        
        // Show loading state
        const executeBtn = document.getElementById('executeBtn');
        const originalHTML = executeBtn.innerHTML;
        executeBtn.innerHTML = '<div class="loading-spinner"></div>';
        executeBtn.disabled = true;
        
        try {
            const response = await fetch('/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ command: command })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.displayCommandResult(result);
                commandInput.value = ''; // Clear input on success
            } else {
                this.displayError(`Command failed: ${result.error}`);
            }
        } catch (error) {
            this.displayError(`Network error: ${error.message}`);
        } finally {
            executeBtn.innerHTML = originalHTML;
            executeBtn.disabled = false;
        }
    }
    
    async learnFromSource() {
        const learnInput = document.getElementById('learnInput');
        const source = learnInput.value.trim();
        
        if (!source) return;
        
        const learnBtn = document.getElementById('learnBtn');
        const originalHTML = learnBtn.innerHTML;
        learnBtn.innerHTML = '<div class="loading-spinner"></div>';
        learnBtn.disabled = true;
        
        try {
            const response = await fetch('/api/learn', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    source: source,
                    type: 'auto'
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.displayCommandResult({
                    command: `learn from ${source}`,
                    result: result.result,
                    timestamp: result.timestamp
                });
                learnInput.value = ''; // Clear input on success
            } else {
                this.displayError(`Learning failed: ${result.error}`);
            }
        } catch (error) {
            this.displayError(`Network error: ${error.message}`);
        } finally {
            learnBtn.innerHTML = originalHTML;
            learnBtn.disabled = false;
        }
    }
    
    displayCommandResult(result) {
        const resultsDiv = document.getElementById('commandResults');
        const timestamp = new Date(result.timestamp).toLocaleTimeString();
        
        const resultHTML = `
            <div class="mb-2">
                <span class="command-timestamp">[${timestamp}]</span>
                <strong>Command:</strong> ${this.escapeHtml(result.command)}
            </div>
            <div class="mb-3 result-success">
                <strong>Result:</strong> ${this.escapeHtml(result.result)}
            </div>
        `;
        
        resultsDiv.innerHTML = resultHTML + resultsDiv.innerHTML;
        
        // Keep only last 20 results
        const results = resultsDiv.children;
        while (results.length > 40) { // 40 because each result creates 2 divs
            resultsDiv.removeChild(results[results.length - 1]);
        }
    }
    
    displayError(message) {
        const resultsDiv = document.getElementById('commandResults');
        const timestamp = new Date().toLocaleTimeString();
        
        const errorHTML = `
            <div class="mb-3 result-error">
                <span class="command-timestamp">[${timestamp}]</span>
                <strong>Error:</strong> ${this.escapeHtml(message)}
            </div>
        `;
        
        resultsDiv.innerHTML = errorHTML + resultsDiv.innerHTML;
    }
    
    async updateStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            if (response.ok) {
                this.updateStatusDisplay(status);
                this.updateScreenCapture(status.screen_capture);
            } else {
                console.error('Failed to fetch status:', status.error);
                this.updateConnectionStatus(false);
            }
        } catch (error) {
            console.error('Status update failed:', error);
            this.updateConnectionStatus(false);
        }
    }
    
    updateStatusDisplay(status) {
        // Update timestamp
        const timestamp = new Date(status.timestamp).toLocaleTimeString();
        document.getElementById('timestamp').textContent = timestamp;
        
        // Update system status badges
        const visionStatus = document.getElementById('visionStatus');
        const automationStatus = document.getElementById('automationStatus');
        
        visionStatus.textContent = status.vision_active ? 'Active' : 'Inactive';
        visionStatus.className = `badge ${status.vision_active ? 'bg-success' : 'bg-secondary'}`;
        
        automationStatus.textContent = status.automation_active ? 'Active' : 'Inactive';
        automationStatus.className = `badge ${status.automation_active ? 'bg-success' : 'bg-secondary'}`;
        
        // Update counts
        document.getElementById('macroCount').textContent = status.macro_count;
        document.getElementById('knowledgeCount').textContent = status.knowledge_count;
        document.getElementById('knowledgeCount2').textContent = status.knowledge_count;
        
        // Update learning stats
        const learningStats = document.getElementById('learningStats');
        if (status.learning_stats && typeof status.learning_stats === 'object') {
            learningStats.textContent = `Learned: ${status.learning_stats.items_learned || 0}`;
        } else {
            learningStats.textContent = 'No data';
        }
        
        // Update connection status
        this.updateConnectionStatus(true);
    }
    
    updateScreenCapture(screenB64) {
        const screenImg = document.getElementById('screenCapture');
        const noCapture = document.getElementById('noCapture');
        
        if (screenB64) {
            screenImg.src = `data:image/jpeg;base64,${screenB64}`;
            screenImg.style.display = 'block';
            noCapture.style.display = 'none';
        } else {
            screenImg.style.display = 'none';
            noCapture.style.display = 'flex';
        }
    }
    
    updateConnectionStatus(connected) {
        const statusBadge = document.getElementById('status-badge');
        
        if (connected) {
            statusBadge.textContent = 'Connected';
            statusBadge.className = 'badge bg-success me-2';
        } else {
            statusBadge.textContent = 'Disconnected';
            statusBadge.className = 'badge bg-danger me-2';
        }
    }
    
    async loadMacros() {
        try {
            const response = await fetch('/api/macros');
            const data = await response.json();
            
            const macroSelect = document.getElementById('macroSelect');
            
            if (response.ok && data.macros && data.macros.length > 0) {
                macroSelect.innerHTML = data.macros.map(macro => 
                    `<option value="${macro}">${macro}</option>`
                ).join('');
            } else {
                macroSelect.innerHTML = '<option>No macros available</option>';
            }
        } catch (error) {
            console.error('Failed to load macros:', error);
            document.getElementById('macroSelect').innerHTML = '<option>Failed to load macros</option>';
        }
    }
    
    toggleRecording() {
        const recordBtn = document.getElementById('recordBtn');
        
        if (this.isRecording) {
            this.stopRecording();
        } else {
            // Start recording
            this.isRecording = true;
            recordBtn.innerHTML = '<i class="fas fa-stop me-1"></i>Recording...';
            recordBtn.className = 'btn btn-danger btn-sm';
            
            // Execute record command
            this.executeRecordCommand('record macro new_macro');
        }
    }
    
    stopRecording() {
        if (this.isRecording) {
            this.isRecording = false;
            
            const recordBtn = document.getElementById('recordBtn');
            recordBtn.innerHTML = '<i class="fas fa-record-vinyl me-1"></i>Record';
            recordBtn.className = 'btn btn-outline-danger btn-sm';
            
            // Execute stop command
            this.executeRecordCommand('stop recording');
            
            // Refresh macros list
            setTimeout(() => this.loadMacros(), 1000);
        }
    }
    
    async executeRecordCommand(command) {
        try {
            await fetch('/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ command: command })
            });
        } catch (error) {
            console.error('Failed to execute record command:', error);
        }
    }
    
    async playMacro() {
        const macroSelect = document.getElementById('macroSelect');
        const selectedMacro = macroSelect.value;
        
        if (selectedMacro && selectedMacro !== 'No macros available' && selectedMacro !== 'Failed to load macros') {
            const command = `play macro ${selectedMacro}`;
            document.getElementById('commandInput').value = command;
            await this.executeCommand();
        }
    }
    
    startStatusUpdates() {
        // Initial update
        this.updateStatus();
        
        // Set up periodic updates
        setInterval(() => {
            this.updateStatus();
        }, this.updateInterval);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Interactive Training Methods
    async processNaturalCommand() {
        const command = document.getElementById('trainingCommand').value.trim();
        if (!command) return;
        
        try {
            const response = await fetch('/api/training/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ command: command })
            });
            
            const data = await response.json();
            this.showAlert(data.result || data.error, data.success ? 'success' : 'danger');
            
            // Clear input and update status
            document.getElementById('trainingCommand').value = '';
            this.updateTrainingStatus();
            
        } catch (error) {
            this.showAlert('Failed to process command', 'danger');
        }
    }
    
    async startTrainingMode(mode) {
        try {
            const response = await fetch('/api/training/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ mode: mode })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.trainingMode = true;
                this.currentTrainingMode = mode;
                this.zoneCorners = [];
                
                // Update UI
                this.updateTrainingModeButtons(mode);
                this.showAlert(data.result, 'success');
                
                // Show specific instructions
                this.showTrainingInstructions(mode);
            } else {
                this.showAlert(data.error || 'Failed to start training', 'danger');
            }
            
            this.updateTrainingStatus();
            
        } catch (error) {
            this.showAlert('Failed to start training mode', 'danger');
        }
    }
    
    async stopTraining() {
        try {
            const response = await fetch('/api/training/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            this.trainingMode = false;
            this.currentTrainingMode = 'idle';
            this.zoneCorners = [];
            
            // Reset UI
            this.resetTrainingModeButtons();
            this.showAlert(data.result || 'Training stopped', 'info');
            this.updateTrainingStatus();
            
        } catch (error) {
            this.showAlert('Failed to stop training', 'danger');
        }
    }
    
    async processSpacebarInput() {
        try {
            const itemType = prompt('What type of item is this? (chest, egg, breakable, resource, etc.)');
            if (!itemType) return;
            
            const response = await fetch('/api/training/spacebar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ item_type: itemType })
            });
            
            const data = await response.json();
            this.showAlert(data.result || data.error, data.success ? 'success' : 'danger');
            this.updateTrainingStatus();
            
        } catch (error) {
            this.showAlert('Failed to process spacebar input', 'danger');
        }
    }
    
    async processZoneClick(event) {
        // Get click coordinates relative to the screen capture
        const rect = event.target.getBoundingClientRect();
        const x = Math.round(event.clientX - rect.left);
        const y = Math.round(event.clientY - rect.top);
        
        try {
            const response = await fetch('/api/training/corner', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ x: x, y: y })
            });
            
            const data = await response.json();
            this.showAlert(data.result || data.error, data.success ? 'success' : 'danger');
            
            // Update zone progress
            this.zoneCorners.push({ x, y });
            document.getElementById('zoneProgress').textContent = `${this.zoneCorners.length}/4 corners`;
            
            // If zone is complete, reset
            if (this.zoneCorners.length >= 4) {
                setTimeout(() => {
                    this.zoneCorners = [];
                    document.getElementById('zoneProgress').textContent = '0/4 corners';
                }, 2000);
            }
            
            this.updateTrainingStatus();
            
        } catch (error) {
            this.showAlert('Failed to process zone click', 'danger');
        }
    }
    
    async analyzeSimilarities() {
        try {
            const response = await fetch('/api/training/similarities');
            const data = await response.json();
            this.showAlert(data.result || data.error, data.success ? 'success' : 'danger');
            
        } catch (error) {
            this.showAlert('Failed to analyze similarities', 'danger');
        }
    }
    
    async findSimilarItems() {
        try {
            const threshold = parseFloat(prompt('Similarity threshold (0.0 - 1.0):') || '0.8');
            const response = await fetch(`/api/training/find-items?threshold=${threshold}`);
            const data = await response.json();
            
            if (data.success && data.matches) {
                this.showAlert(`Found ${data.matches.length} similar items on screen`, 'success');
                this.highlightFoundItems(data.matches);
            } else {
                this.showAlert(data.error || 'No similar items found', 'warning');
            }
            
        } catch (error) {
            this.showAlert('Failed to find similar items', 'danger');
        }
    }
    
    highlightFoundItems(matches) {
        // Clear previous highlights
        const existingHighlights = document.querySelectorAll('.item-highlight');
        existingHighlights.forEach(h => h.remove());
        
        // Add new highlights
        const screenImg = document.getElementById('screenCapture');
        if (!screenImg) return;
        
        matches.forEach(match => {
            const highlight = document.createElement('div');
            highlight.className = 'item-highlight';
            highlight.style.position = 'absolute';
            highlight.style.left = `${match.position[0]}px`;
            highlight.style.top = `${match.position[1]}px`;
            highlight.style.width = '50px';
            highlight.style.height = '50px';
            highlight.style.border = '2px solid #ff0000';
            highlight.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';
            highlight.style.pointerEvents = 'none';
            highlight.style.zIndex = '1000';
            highlight.title = `${match.item_type} (${Math.round(match.confidence * 100)}%)`;
            
            screenImg.parentElement.style.position = 'relative';
            screenImg.parentElement.appendChild(highlight);
        });
        
        // Remove highlights after 5 seconds
        setTimeout(() => {
            const highlights = document.querySelectorAll('.item-highlight');
            highlights.forEach(h => h.remove());
        }, 5000);
    }
    
    updateTrainingModeButtons(activeMode) {
        document.querySelectorAll('.training-mode').forEach(btn => {
            const mode = btn.getAttribute('data-mode');
            if (mode === activeMode) {
                btn.classList.remove('btn-outline-success', 'btn-outline-info', 'btn-outline-warning');
                btn.classList.add('btn-success');
            } else {
                btn.classList.add('btn-outline-success', 'btn-outline-info', 'btn-outline-warning');
                btn.classList.remove('btn-success');
            }
        });
    }
    
    resetTrainingModeButtons() {
        document.querySelectorAll('.training-mode').forEach(btn => {
            btn.classList.add('btn-outline-success', 'btn-outline-info', 'btn-outline-warning');
            btn.classList.remove('btn-success');
        });
    }
    
    showTrainingInstructions(mode) {
        let instructions = '';
        switch (mode) {
            case 'item_learning':
                instructions = 'Hover your mouse over items and press SPACE to learn them. You\'ll be prompted for the item type.';
                break;
            case 'zone_mapping':
                instructions = 'Click 4 corners on the screen to define a game zone boundary.';
                break;
            case 'gameplay_recording':
                instructions = 'The bot will now watch and learn from your gameplay actions.';
                break;
        }
        
        if (instructions) {
            this.showAlert(instructions, 'info');
        }
    }
    
    async updateTrainingStatus() {
        try {
            const response = await fetch('/api/training/status');
            const status = await response.json();
            
            // Update status display
            const statusElement = document.getElementById('trainingStatus');
            if (status.training_mode) {
                statusElement.textContent = `Active: ${status.current_mode}`;
                statusElement.className = 'text-success';
            } else {
                statusElement.textContent = 'Not active';
                statusElement.className = 'text-muted';
            }
            
            // Update counters
            document.getElementById('learnedItemsCount').textContent = status.learned_items_count || 0;
            document.getElementById('gameZonesCount').textContent = status.game_zones_count || 0;
            document.getElementById('zoneProgress').textContent = `${status.zone_corners_collected || 0}/4 corners`;
            
        } catch (error) {
            console.error('Failed to update training status:', error);
        }
    }
    
    showAlert(message, type = 'info') {
        // Create alert element
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.style.position = 'fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.style.maxWidth = '400px';
        alert.innerHTML = `
            ${this.escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new GameBotDashboard();
});
