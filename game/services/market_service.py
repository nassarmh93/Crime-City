"""
Market service module for handling marketplace functionalities.
"""
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

from ..models.market import MarketListing
from ..models.item import Item, PlayerInventory

def get_active_listings(player=None, item_type=None, min_level=None, max_price=None, limit=20):
    """
    Get active market listings with optional filtering.
    
    Args:
        player: Optional player to exclude their own listings
        item_type: Optional item type filter
        min_level: Optional minimum level filter
        max_price: Optional maximum price filter
        limit: Maximum number of listings to return
        
    Returns:
        Queryset of MarketListing objects
    """
    listings = MarketListing.objects.filter(
        status='active',
        expires_at__gt=timezone.now()
    )
    
    # Filter by item type if provided
    if item_type:
        listings = listings.filter(item__item_type=item_type)
    
    # Filter by player level requirements
    if min_level is not None:
        listings = listings.filter(item__min_level__lte=min_level)
    
    # Filter by maximum price
    if max_price is not None:
        listings = listings.filter(price__lte=max_price)
    
    # Exclude player's own listings
    if player:
        listings = listings.exclude(seller=player)
    
    return listings.order_by('price')[:limit]

def get_player_listings(player, include_sold=False, limit=20):
    """
    Get listings created by a player.
    
    Args:
        player: Player whose listings to retrieve
        include_sold: Whether to include sold listings
        limit: Maximum number of listings to return
        
    Returns:
        Queryset of MarketListing objects
    """
    if include_sold:
        listings = MarketListing.objects.filter(seller=player)
    else:
        listings = MarketListing.objects.filter(seller=player, status='active')
    
    return listings.order_by('-created_at')[:limit]

def create_listing(player, item_id, quantity, price, duration_days=3):
    """
    Create a new market listing.
    
    Args:
        player: Player creating the listing
        item_id: ID of the item to sell
        quantity: Quantity to sell
        price: Listing price
        duration_days: Number of days the listing should be active
        
    Returns:
        New MarketListing object or None if failed
        
    Raises:
        ValueError: If validation fails
    """
    # Check if player has enough of the item
    try:
        item = Item.objects.get(id=item_id)
        inventory = PlayerInventory.objects.get(player=player, item=item)
    except (Item.DoesNotExist, PlayerInventory.DoesNotExist):
        raise ValueError("You don't have this item in your inventory.")
    
    if inventory.quantity < quantity:
        raise ValueError(f"You only have {inventory.quantity} of this item.")
    
    if inventory.is_equipped:
        raise ValueError("You cannot sell equipped items. Please unequip first.")
    
    if not item.is_tradable:
        raise ValueError("This item cannot be traded on the market.")
    
    # Create the listing
    expires_at = timezone.now() + timedelta(days=duration_days)
    
    listing = MarketListing.objects.create(
        seller=player,
        item=item,
        quantity=quantity,
        price=price,
        expires_at=expires_at
    )
    
    # Remove item from player's inventory
    if inventory.quantity == quantity:
        inventory.delete()
    else:
        inventory.quantity -= quantity
        inventory.save()
    
    return listing

def cancel_listing(listing_id, player):
    """
    Cancel a market listing and return items to inventory.
    
    Args:
        listing_id: ID of the listing to cancel
        player: Player who owns the listing
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        ValueError: If validation fails
    """
    try:
        listing = MarketListing.objects.get(id=listing_id, seller=player, status='active')
    except MarketListing.DoesNotExist:
        raise ValueError("Listing not found or cannot be canceled.")
    
    return listing.cancel()

def purchase_listing(listing_id, player):
    """
    Purchase an item from the marketplace.
    
    Args:
        listing_id: ID of the listing to purchase
        player: Player making the purchase
        
    Returns:
        Purchased MarketListing object
        
    Raises:
        ValueError: If purchase validation fails
    """
    try:
        listing = MarketListing.objects.get(id=listing_id, status='active')
    except MarketListing.DoesNotExist:
        raise ValueError("Listing not found or no longer available.")
    
    # Check if player has enough money
    if player.cash < listing.price:
        raise ValueError(f"Not enough cash. You need {listing.price} but have {player.cash}.")
    
    # Check if player is trying to buy their own listing
    if listing.seller == player:
        raise ValueError("You cannot buy your own listing.")
    
    # Process the purchase
    return listing.purchase(player)

def get_expired_listings():
    """
    Get all expired but still active listings.
    
    Returns:
        Queryset of MarketListing objects
    """
    return MarketListing.objects.filter(
        status='active',
        expires_at__lte=timezone.now()
    )

def process_expired_listings():
    """
    Process all expired listings by canceling them.
    
    Returns:
        Number of processed listings
    """
    expired_listings = get_expired_listings()
    count = 0
    
    for listing in expired_listings:
        try:
            listing.check_expiry()
            count += 1
        except Exception:
            continue
    
    return count
