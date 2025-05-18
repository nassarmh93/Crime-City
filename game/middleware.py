from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

class PlayerMiddleware(MiddlewareMixin):
    """
    Middleware to check and update player status on each request
    """
    def process_request(self, request):
        if not hasattr(request, 'user') or isinstance(request.user, AnonymousUser):
            return
            
        # Only continue if the user is authenticated
        if request.user.is_authenticated:
            try:
                # Get the player instance
                player = request.user.player
                
                # Assign player to request
                request.player = player
                
                # Check if player is in hospital or jail
                player.check_status()
                
                # Regenerate energy and health
                player.regenerate_energy()
                player.regenerate_health()
                
            except (AttributeError, Exception):
                # User might not have a player profile yet
                pass
