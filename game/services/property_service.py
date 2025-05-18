"""
Property service module for handling property management.
"""
from django.utils import timezone
from django.db.models import F

from ..models.property import Property, PropertyType
from ..models.location import Location

def get_available_properties(player, location=None, limit=20):
    """
    Get property types available for purchase.
    
    Args:
        player: Player who wants to buy a property
        location: Optional location filter
        limit: Maximum number of results
        
    Returns:
        List of PropertyType objects
    """
    # Get property types that match player's level
    property_types = PropertyType.objects.filter(min_level__lte=player.level)
    
    # You might apply other filters here based on game rules
    return property_types.order_by('base_price')[:limit]

def get_player_properties(player, location=None, include_inactive=False):
    """
    Get properties owned by a player.
    
    Args:
        player: The player whose properties to retrieve
        location: Optional location filter
        include_inactive: Whether to include inactive properties
        
    Returns:
        Queryset of Property objects
    """
    properties = Property.objects.filter(player=player)
    
    if not include_inactive:
        properties = properties.filter(is_active=True)
    
    if location:
        properties = properties.filter(location=location)
    
    return properties.order_by('-income_rate')

def purchase_property(player, property_type_id, location_id, name):
    """
    Purchase a new property.
    
    Args:
        player: Player making the purchase
        property_type_id: ID of the property type to purchase
        location_id: Location ID where the property will be
        name: Name for the new property
        
    Returns:
        New Property object
        
    Raises:
        ValueError: If purchase validation fails
    """
    try:
        property_type = PropertyType.objects.get(id=property_type_id)
        location = Location.objects.get(id=location_id)
    except (PropertyType.DoesNotExist, Location.DoesNotExist):
        raise ValueError("Invalid property type or location.")
    
    # Check if player meets level requirement
    if player.level < property_type.min_level:
        raise ValueError(f"You need to be level {property_type.min_level} to purchase this property.")
    
    # Check if player has enough money
    if player.cash < property_type.base_price:
        raise ValueError(f"Not enough cash. You need {property_type.base_price} but have {player.cash}.")
    
    # Create the property
    new_property = Property.objects.create(
        player=player,
        property_type=property_type,
        name=name,
        purchase_price=property_type.base_price,
        current_value=property_type.base_price,
        location=location,
        income_rate=property_type.base_income
    )
    
    # Deduct money from player
    player.cash -= property_type.base_price
    player.save()
    
    return new_property

def collect_property_income(player, property_id=None):
    """
    Collect income from a player's property or all properties.
    
    Args:
        player: Player collecting income
        property_id: Optional specific property ID to collect from
        
    Returns:
        Total income collected
        
    Raises:
        ValueError: If property doesn't belong to player
    """
    total_income = 0
    
    # Collect from specific property
    if property_id:
        try:
            player_property = Property.objects.get(id=property_id, player=player, is_active=True)
            income = player_property.collect_income()
            total_income += income
        except Property.DoesNotExist:
            raise ValueError("Property not found or doesn't belong to you.")
    
    # Collect from all properties
    else:
        properties = get_player_properties(player)
        for player_property in properties:
            try:
                income = player_property.collect_income()
                total_income += income
            except Exception:
                continue
    
    return total_income

def upgrade_property(player, property_id):
    """
    Upgrade a property to increase its income.
    
    Args:
        player: Player upgrading the property
        property_id: ID of the property to upgrade
        
    Returns:
        Upgraded Property object
        
    Raises:
        ValueError: If upgrade validation fails
    """
    try:
        player_property = Property.objects.get(id=property_id, player=player, is_active=True)
    except Property.DoesNotExist:
        raise ValueError("Property not found or doesn't belong to you.")
    
    # Calculate upgrade cost based on current level
    upgrade_cost = player_property.current_value * 0.5
    
    # Check if player can afford upgrade
    if player.cash < upgrade_cost:
        raise ValueError(f"Not enough cash. You need {upgrade_cost} but have {player.cash}.")
    
    # Process the upgrade
    player_property.upgrade(upgrade_cost)
    
    # Deduct money from player
    player.cash -= upgrade_cost
    player.save()
    
    return player_property

def sell_property(player, property_id):
    """
    Sell a property back to the game.
    
    Args:
        player: Player selling the property
        property_id: ID of the property to sell
        
    Returns:
        Amount of cash received from sale
        
    Raises:
        ValueError: If property doesn't belong to player
    """
    try:
        player_property = Property.objects.get(id=property_id, player=player, is_active=True)
    except Property.DoesNotExist:
        raise ValueError("Property not found or doesn't belong to you.")
    
    # Calculate sell price (usually a percentage of current value)
    sell_price = int(player_property.current_value * 0.7)  # 70% of current value
    
    # Add money to player
    player.cash += sell_price
    player.save()
    
    # Mark property as inactive
    player_property.is_active = False
    player_property.save()
    
    return sell_price
