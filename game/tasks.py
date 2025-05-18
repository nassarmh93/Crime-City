from celery import shared_task
from django.utils import timezone
from datetime import timedelta

@shared_task
def regenerate_all_player_resources():
    """
    Task to regenerate energy and health for all players
    This is a backup to the middleware regeneration
    """
    from game.models import Player
    
    players = Player.objects.all()
    updated_count = 0
    
    for player in players:
        player.regenerate_energy()
        player.regenerate_health()
        player.check_status()  # Check if player should be released from hospital/jail
        updated_count += 1
    
    return f"Updated resources for {updated_count} players"

@shared_task
def expire_old_market_listings():
    """
    Task to expire old market listings
    """
    from game.models import MarketListing
    
    # Find active listings that have expired
    expired_listings = MarketListing.objects.filter(
        status='active',
        expires_at__lte=timezone.now()
    )
    
    expired_count = 0
    for listing in expired_listings:
        if listing.check_expiry():
            expired_count += 1
    
    return f"Expired {expired_count} market listings"
