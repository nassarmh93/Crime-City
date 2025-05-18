"""
WebSocket consumers for real-time functionality.
This is a placeholder file for now.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models.player import Player

class GameConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for game-related real-time updates.
    """
    async def connect(self):
        self.user = self.scope["user"]
        self.player = None
        
        # Only authenticated users can connect
        if self.user and not isinstance(self.user, AnonymousUser):
            self.player = await self.get_player()
            self.player_group_name = f'player_{self.player.id}'
            
            # Join player-specific group
            await self.channel_layer.group_add(
                self.player_group_name,
                self.channel_name
            )
            
            # Join global game updates group
            await self.channel_layer.group_add(
                'game_updates',
                self.channel_name
            )
            
            # Accept the connection
            await self.accept()
            
            # Send initial status update
            await self.send_player_status()
        else:
            # Reject the connection if not authenticated
            await self.close()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'player_group_name'):
            # Leave player-specific group
            await self.channel_layer.group_discard(
                self.player_group_name,
                self.channel_name
            )
            
            # Leave global game updates group
            await self.channel_layer.group_discard(
                'game_updates',
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Handle messages from WebSocket.
        """
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'get_status':
                await self.send_player_status()
            elif action == 'refresh_combat':
                await self.send_combat_status(data.get('combat_id'))
        except Exception as e:
            await self.send_error(str(e))
    
    async def player_update(self, event):
        """
        Handler for player update events.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'player_update',
            'data': event['data']
        }))
    
    async def combat_update(self, event):
        """
        Handler for combat update events.
        """
        await self.send(text_data=json.dumps({
            'type': 'combat_update',
            'data': event['data']
        }))
    
    async def game_notification(self, event):
        """
        Handler for game-wide notifications.
        """
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message']
        }))
    
    @database_sync_to_async
    def get_player(self):
        """
        Get the player object for the current user.
        """
        return Player.objects.get(user=self.user)
    
    @database_sync_to_async
    def get_player_data(self):
        """
        Get serialized player data.
        """
        player = Player.objects.get(user=self.user)
        player.check_status()  # Update player status
        player.regenerate_energy()  # Update energy
        player.regenerate_health()  # Update health
        
        return {
            'id': player.id,
            'nickname': player.nickname,
            'level': player.level,
            'experience': player.experience,
            'cash': player.cash,
            'energy': player.energy,
            'max_energy': player.max_energy,
            'health': player.health,
            'max_health': player.max_health,
            'location': player.current_location.name if player.current_location else None,
            'is_in_hospital': player.is_in_hospital,
            'is_in_jail': player.is_in_jail,
        }
    
    async def send_player_status(self):
        """
        Send current player status.
        """
        player_data = await self.get_player_data()
        await self.send(text_data=json.dumps({
            'type': 'player_status',
            'data': player_data
        }))
    
    async def send_error(self, message):
        """
        Send error message.
        """
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    @database_sync_to_async
    def get_combat_data(self, combat_id):
        """
        Get serialized combat data.
        """
        from .models.combat import Combat, CombatLog
        from django.shortcuts import get_object_or_404
        
        combat = get_object_or_404(Combat, id=combat_id)
        logs = CombatLog.objects.filter(combat=combat)
        
        return {
            'id': combat.id,
            'attacker': combat.attacker.nickname,
            'defender': combat.defender.nickname,
            'winner': combat.winner.nickname if combat.winner else None,
            'cash_stolen': combat.cash_stolen,
            'experience_gained': combat.experience_gained,
            'started_at': combat.started_at.isoformat(),
            'ended_at': combat.ended_at.isoformat() if combat.ended_at else None,
            'logs': [{'message': log.message, 'timestamp': log.timestamp.isoformat()} for log in logs]
        }
    
    async def send_combat_status(self, combat_id):
        """
        Send combat status.
        """
        if not combat_id:
            await self.send_error("Combat ID is required")
            return
            
        try:
            combat_data = await self.get_combat_data(combat_id)
            await self.send(text_data=json.dumps({
                'type': 'combat_status',
                'data': combat_data
            }))
        except Exception as e:
            await self.send_error(str(e))
