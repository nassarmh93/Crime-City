/**
 * Game Notification System for Crime City
 * Handles real-time notifications and updates
 */

class NotificationManager {
    constructor() {
        this.container = null;
        this.socket = null;
        this.notifications = [];
        this.maxNotifications = 5;
        this.sound = new Audio('/static/sounds/notification.mp3');
        this.initialize();
    }

    initialize() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            this.container = document.createElement('div');
            this.container.id = 'notification-container';
            this.container.className = 'notification-container';
            document.body.appendChild(this.container);

            // Add styles if they don't exist
            if (!document.getElementById('notification-styles')) {
                const style = document.createElement('style');
                style.id = 'notification-styles';
                style.textContent = `
                    .notification-container {
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        width: 300px;
                        z-index: 9999;
                    }
                    .game-notification {
                        background-color: rgba(33, 37, 41, 0.85);
                        color: white;
                        border-left: 4px solid #007bff;
                        border-radius: 4px;
                        padding: 12px 15px;
                        margin-bottom: 10px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                        transition: all 0.3s ease;
                        opacity: 0;
                        transform: translateX(50px);
                    }
                    .game-notification.show {
                        opacity: 1;
                        transform: translateX(0);
                    }
                    .game-notification.info { border-left-color: #007bff; }
                    .game-notification.success { border-left-color: #28a745; }
                    .game-notification.warning { border-left-color: #ffc107; }
                    .game-notification.danger { border-left-color: #dc3545; }
                    .game-notification .notification-title {
                        font-weight: bold;
                        margin-bottom: 5px;
                        display: flex;
                        justify-content: space-between;
                    }
                    .game-notification .notification-close {
                        cursor: pointer;
                        font-size: 16px;
                    }
                    .game-notification .notification-body {
                        font-size: 14px;
                    }
                `;
                document.head.appendChild(style);
            }
        } else {
            this.container = document.getElementById('notification-container');
        }

        // Connect to WebSocket if available
        this.connectWebSocket();
    }

    connectWebSocket() {
        // Create WebSocket connection if not already connected
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsPath = `${wsProtocol}//${window.location.host}/ws/game/`;
            
            this.socket = new WebSocket(wsPath);
            
            // Connection opened
            this.socket.addEventListener('open', () => {
                console.log('NotificationManager: WebSocket connected');
                this.notify('System', 'Connected to game server', 'info');
            });
            
            // Listen for messages
            this.socket.addEventListener('message', (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'notification') {
                    this.notify('Game', data.message, data.level || 'info');
                } else if (data.type === 'player_update') {
                    this.handlePlayerUpdate(data.data);
                }
            });
            
            // Connection closed
            this.socket.addEventListener('close', () => {
                console.log('NotificationManager: WebSocket disconnected');
                
                // Try to reconnect after 5 seconds
                setTimeout(() => this.connectWebSocket(), 5000);
            });
        }
    }

    handlePlayerUpdate(playerData) {
        // Handle player stat updates
        if (playerData.level_up) {
            this.notify('Level Up!', `You've reached level ${playerData.level}!`, 'success');
        }
        
        // Update UI elements with player data
        document.querySelectorAll('[data-player-stat]').forEach(el => {
            const stat = el.getAttribute('data-player-stat');
            if (playerData[stat] !== undefined) {
                el.textContent = playerData[stat];
            }
        });
    }

    notify(title, message, type = 'info', autoClose = true, duration = 5000) {
        // Create notification element
        const notificationId = 'notification-' + Date.now();
        const notification = document.createElement('div');
        notification.id = notificationId;
        notification.className = `game-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-title">
                ${title}
                <span class="notification-close">&times;</span>
            </div>
            <div class="notification-body">${message}</div>
        `;

        // Add to container
        this.container.appendChild(notification);
        this.notifications.push(notificationId);

        // Show with animation
        setTimeout(() => notification.classList.add('show'), 10);

        // Play sound if allowed
        this.playSound();

        // Set up close button
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.closeNotification(notificationId);
        });

        // Auto close if specified
        if (autoClose) {
            setTimeout(() => {
                this.closeNotification(notificationId);
            }, duration);
        }

        // Remove oldest notification if we exceed max
        if (this.notifications.length > this.maxNotifications) {
            this.closeNotification(this.notifications[0]);
        }

        return notificationId;
    }

    closeNotification(id) {
        const notification = document.getElementById(id);
        if (notification) {
            notification.classList.remove('show');
            
            // Remove after animation
            setTimeout(() => {
                notification.remove();
                this.notifications = this.notifications.filter(n => n !== id);
            }, 300);
        }
    }

    playSound() {
        // Check if sound is enabled in user preferences
        const soundEnabled = localStorage.getItem('soundEnabled') !== 'false';
        if (soundEnabled && this.sound) {
            this.sound.play().catch(e => {
                // Ignore autoplay errors - browsers require user interaction
            });
        }
    }
}

// Initialize notification manager when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.notificationManager = new NotificationManager();
    
    // Export for global use
    window.notify = (title, message, type) => {
        window.notificationManager.notify(title, message, type);
    };
}); 