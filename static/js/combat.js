/**
 * Combat functionality for Crime City
 */
document.addEventListener('DOMContentLoaded', function() {
    // Combat WebSocket setup
    const combatLogContainer = document.getElementById('combat-logs');
    const playerHealthBar = document.getElementById('player-health');
    const opponentHealthBar = document.getElementById('opponent-health');
    const combatResultContainer = document.getElementById('combat-result');
    const combatStatusContainer = document.getElementById('combat-status');
    const attackButton = document.getElementById('attack-button');
    
    // Get combat ID if on combat detail page
    const combatId = document.getElementById('combat-id')?.value;
    
    // WebSocket connection
    let socket = null;
    
    // Check if on a combat page
    if (combatLogContainer || combatId) {
        // Initialize WebSocket connection
        connectWebSocket();
    }
    
    function connectWebSocket() {
        // Create WebSocket connection
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsPath = `${wsProtocol}//${window.location.host}/ws/game/`;
        
        socket = new WebSocket(wsPath);
        
        // Connection opened
        socket.addEventListener('open', function(event) {
            console.log('WebSocket connected');
            
            // If on combat detail page, request combat status
            if (combatId) {
                socket.send(JSON.stringify({
                    'action': 'refresh_combat',
                    'combat_id': combatId
                }));
            }
        });
        
        // Listen for messages
        socket.addEventListener('message', function(event) {
            const data = JSON.parse(event.data);
            
            switch (data.type) {
                case 'combat_update':
                    handleCombatUpdate(data.data);
                    break;
                case 'combat_status':
                    handleCombatStatus(data.data);
                    break;
                case 'player_status':
                    handlePlayerStatus(data.data);
                    break;
                case 'notification':
                    showNotification(data.message);
                    break;
                case 'error':
                    showError(data.message);
                    break;
            }
        });
        
        // Connection closed
        socket.addEventListener('close', function(event) {
            console.log('WebSocket disconnected');
            
            // Try to reconnect after 5 seconds
            setTimeout(function() {
                connectWebSocket();
            }, 5000);
        });
        
        // Connection error
        socket.addEventListener('error', function(event) {
            console.error('WebSocket error:', event);
        });
    }
    
    function handleCombatUpdate(data) {
        // Update the combat logs if container exists
        if (combatLogContainer) {
            // Create new log entry
            const logEntry = document.createElement('div');
            logEntry.className = 'alert alert-info mb-2';
            logEntry.textContent = data.message;
            
            // Add to container
            combatLogContainer.appendChild(logEntry);
            
            // Scroll to bottom
            combatLogContainer.scrollTop = combatLogContainer.scrollHeight;
        }
        
        // Update health bars if they exist
        if (data.attacker_health && playerHealthBar) {
            updateHealthBar(playerHealthBar, data.attacker_health, data.attacker_max_health);
        }
        
        if (data.defender_health && opponentHealthBar) {
            updateHealthBar(opponentHealthBar, data.defender_health, data.defender_max_health);
        }
        
        // Update combat status
        if (data.status && combatStatusContainer) {
            combatStatusContainer.textContent = data.status;
        }
        
        // Display result if combat is over
        if (data.is_complete && combatResultContainer) {
            displayCombatResult(data);
            
            // Disable attack button
            if (attackButton) {
                attackButton.disabled = true;
            }
        }
    }
    
    function handleCombatStatus(data) {
        // Update all combat logs
        if (combatLogContainer) {
            // Clear existing logs
            combatLogContainer.innerHTML = '';
            
            // Add all logs
            data.logs.forEach(log => {
                const logEntry = document.createElement('div');
                logEntry.className = 'alert alert-info mb-2';
                logEntry.textContent = log.message;
                combatLogContainer.appendChild(logEntry);
            });
            
            // Scroll to bottom
            combatLogContainer.scrollTop = combatLogContainer.scrollHeight;
        }
        
        // Display result if combat is over
        if (data.ended_at && combatResultContainer) {
            const resultHTML = `
                <div class="alert ${data.winner ? 'alert-success' : 'alert-danger'}">
                    <h4 class="alert-heading">${data.winner ? 'Victory!' : 'Defeat!'}</h4>
                    <p>
                        ${data.winner === data.attacker ? 'You won the fight!' : 'You lost the fight!'}
                    </p>
                    <hr>
                    <p class="mb-0">
                        ${data.cash_stolen > 0 ? `Cash stolen: $${data.cash_stolen}` : ''}
                        ${data.experience_gained > 0 ? `Experience gained: ${data.experience_gained}` : ''}
                    </p>
                </div>
            `;
            
            combatResultContainer.innerHTML = resultHTML;
            
            // Disable attack button
            if (attackButton) {
                attackButton.disabled = true;
            }
        }
    }
    
    function handlePlayerStatus(data) {
        // Update player stats on the page
        const playerCash = document.getElementById('player-cash');
        const playerEnergy = document.getElementById('player-energy');
        const playerHealth = document.getElementById('player-health-stat');
        
        if (playerCash) {
            playerCash.textContent = data.cash;
        }
        
        if (playerEnergy) {
            playerEnergy.textContent = `${data.energy}/${data.max_energy}`;
        }
        
        if (playerHealth) {
            playerHealth.textContent = `${data.health}/${data.max_health}`;
        }
    }
    
    function updateHealthBar(bar, current, max) {
        const percentage = Math.round((current / max) * 100);
        bar.style.width = `${percentage}%`;
        bar.textContent = `${current}/${max}`;
        
        // Change color based on health percentage
        if (percentage <= 25) {
            bar.classList.remove('bg-success', 'bg-warning');
            bar.classList.add('bg-danger');
        } else if (percentage <= 50) {
            bar.classList.remove('bg-success', 'bg-danger');
            bar.classList.add('bg-warning');
        } else {
            bar.classList.remove('bg-danger', 'bg-warning');
            bar.classList.add('bg-success');
        }
    }
    
    function displayCombatResult(data) {
        if (!combatResultContainer) return;
        
        const resultHTML = `
            <div class="alert ${data.is_winner ? 'alert-success' : 'alert-danger'}">
                <h4 class="alert-heading">${data.is_winner ? 'Victory!' : 'Defeat!'}</h4>
                <p>
                    ${data.result_message}
                </p>
                <hr>
                <p class="mb-0">
                    ${data.reward_message || ''}
                </p>
            </div>
        `;
        
        combatResultContainer.innerHTML = resultHTML;
    }
    
    function showNotification(message) {
        // Create a toast or notification
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    function showError(message) {
        // Create error toast
        const error = document.createElement('div');
        error.className = 'alert alert-danger alert-dismissible fade show';
        error.innerHTML = `
            Error: ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add to page
        document.body.appendChild(error);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            error.remove();
        }, 5000);
    }
    
    // Attack button handler
    if (attackButton) {
        attackButton.addEventListener('click', function() {
            // Disable button during attack
            attackButton.disabled = true;
            
            // Re-enable after 2 seconds
            setTimeout(() => {
                attackButton.disabled = false;
            }, 2000);
        });
    }
    
    // Cleanup when page unloads
    window.addEventListener('beforeunload', function() {
        if (socket) {
            socket.close();
        }
    });
});
