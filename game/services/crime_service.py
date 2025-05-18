"""
Crime service module for handling crime-related functionalities.
"""
import random
import math
from datetime import timedelta
from django.utils import timezone
from django.db.models import F, Q, Sum
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models.crime import CrimeType, CrimeResult
from ..models.item import Item, PlayerInventory

def get_available_crimes(player):
    """
    Get crimes available for a player based on level.
    
    Args:
        player: Player object
        
    Returns:
        Queryset of CrimeType objects
    """
    return CrimeType.objects.filter(min_level__lte=player.level).order_by('min_level')

def calculate_success_chance(player, crime_type):
    """
    Calculate a player's chance of successfully committing a crime.
    
    Args:
        player: Player object
        crime_type: CrimeType object
        
    Returns:
        Float between 0.0 and 1.0 representing success chance
    """
    # Base chance
    chance = crime_type.base_success_chance
    
    # Add stat contributions
    chance += (player.strength / 100) * crime_type.strength_factor
    chance += (player.defense / 100) * crime_type.defense_factor
    chance += (player.speed / 100) * crime_type.speed_factor
    chance += (player.dexterity / 100) * crime_type.dexterity_factor
    chance += (player.intelligence / 100) * crime_type.intelligence_factor
    
    # Adjust for level difference
    level_diff = player.level - crime_type.min_level
    if level_diff > 0:
        chance += min(0.2, level_diff * 0.02)  # Max bonus: 20%
    
    # Clamp between 10% and 95%
    return max(0.10, min(0.95, chance))

def commit_crime(player, crime_type_id, location):
    """
    Have a player attempt to commit a crime.
    
    Args:
        player: Player object
        crime_type_id: ID of the crime type
        location: Location object
        
    Returns:
        CrimeResult object
        
    Raises:
        ValueError: If validation fails
    """
    try:
        crime_type = CrimeType.objects.get(id=crime_type_id)
    except CrimeType.DoesNotExist:
        raise ValueError("Invalid crime type.")
    
    # Check if player meets level requirement
    if player.level < crime_type.min_level:
        raise ValueError(f"You need to be level {crime_type.min_level} to commit this crime.")
    
    # Check if player has enough energy
    if player.energy < crime_type.energy_cost:
        raise ValueError(f"Not enough energy. You need {crime_type.energy_cost} but have {player.energy}.")
    
    # Deduct energy first
    player.energy -= crime_type.energy_cost
    player.save(update_fields=['energy'])
    
    # Calculate success chance
    success_chance = calculate_success_chance(player, crime_type)
    
    # Determine outcome
    roll = random.random()
    
    # Create result object
    result = CrimeResult(
        player=player,
        crime_type=crime_type,
        location=location
    )
    
    # Success - player gets rewards
    if roll <= success_chance:
        # Determine if player gets caught despite success
        caught_roll = random.random()
        if caught_roll <= crime_type.jail_risk:
            # Player succeeded but got caught
            handle_jail_sentence(player, crime_type, result)
            message = f"You committed the crime but got caught by law enforcement!"
            notify_player(player, "Busted!", message, "danger")
        else:
            # Complete success
            cash_reward = random.randint(crime_type.min_cash_reward, crime_type.max_cash_reward)
            exp_reward = random.randint(crime_type.min_exp_reward, crime_type.max_exp_reward)
            
            # Apply rewards
            player.cash += cash_reward
            player.gain_experience(exp_reward)
            
            # Possible item reward
            item_reward = None
            if crime_type.possible_rewards.exists() and random.random() <= crime_type.item_reward_chance:
                item_reward = award_random_item(player, crime_type)
            
            # Update result
            result.result = 'success'
            result.cash_reward = cash_reward
            result.exp_reward = exp_reward
            result.item_reward = item_reward
            
            # Save player changes
            player.save(update_fields=['cash', 'experience', 'level'])
            
            # Prepare notification message
            message = f"Crime successful! You earned ${cash_reward} and {exp_reward} XP."
            if item_reward:
                message += f" You also found: {item_reward.name}!"
            
            notify_player(player, "Success!", message, "success")
    else:
        # Failure - determine if player gets caught
        caught_roll = random.random()
        if caught_roll <= crime_type.jail_risk * 1.5:  # Higher chance of jail when failing
            # Player failed and got caught
            handle_jail_sentence(player, crime_type, result)
            message = f"You failed the crime and got caught by law enforcement!"
            notify_player(player, "Busted!", message, "danger")
        else:
            # Simple failure
            result.result = 'failed'
            message = "You failed to commit the crime but managed to escape without being noticed."
            notify_player(player, "Failed", message, "warning")
    
    # Save the result
    result.save()
    
    return result

def handle_jail_sentence(player, crime_type, result):
    """
    Handle sending a player to jail.
    
    Args:
        player: Player object
        crime_type: CrimeType object
        result: CrimeResult object to update
    """
    # Calculate jail time
    jail_time = random.randint(crime_type.min_jail_time, crime_type.max_jail_time)
    
    # Set player in jail
    player.is_in_jail = True
    player.jail_release_time = timezone.now() + timedelta(seconds=jail_time)
    player.save(update_fields=['is_in_jail', 'jail_release_time'])
    
    # Update result
    result.result = 'jailed'
    result.jail_time = jail_time

def award_random_item(player, crime_type):
    """
    Award a random item from the possible rewards for a crime.
    
    Args:
        player: Player object
        crime_type: CrimeType object
        
    Returns:
        Item object or None
    """
    # Get possible rewards
    possible_items = crime_type.possible_rewards.all()
    
    if not possible_items:
        return None
    
    # Pick a random item
    item = random.choice(possible_items)
    
    # Add to player inventory
    inventory, created = PlayerInventory.objects.get_or_create(
        player=player,
        item=item,
        defaults={'quantity': 1}
    )
    
    # If player already has the item, increase quantity
    if not created:
        inventory.quantity += 1
        inventory.save()
    
    return item

def get_recent_crimes(player, limit=10):
    """
    Get recent crime results for a player.
    
    Args:
        player: Player object
        limit: Maximum number of results
        
    Returns:
        Queryset of CrimeResult objects
    """
    return CrimeResult.objects.filter(player=player).order_by('-created_at')[:limit]

def notify_player(player, title, message, level="info"):
    """
    Send a notification to the player through WebSocket.
    
    Args:
        player: Player object
        title: Notification title
        message: Notification message
        level: Notification level (info, success, warning, danger)
    """
    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(
            f'player_{player.id}',
            {
                'type': 'game_notification',
                'message': message,
                'title': title,
                'level': level
            }
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")

def get_crime_stats(player):
    """
    Get crime statistics for a player.
    
    Args:
        player: Player object
        
    Returns:
        Dictionary with crime statistics
    """
    total_crimes = CrimeResult.objects.filter(player=player).count()
    successful_crimes = CrimeResult.objects.filter(player=player, result='success').count()
    failed_crimes = CrimeResult.objects.filter(player=player, result='failed').count()
    jailed_count = CrimeResult.objects.filter(player=player, result='jailed').count()
    
    success_rate = (successful_crimes / total_crimes * 100) if total_crimes > 0 else 0
    
    total_earnings = CrimeResult.objects.filter(
        player=player, 
        result='success'
    ).values('cash_reward').aggregate(
        total=Sum('cash_reward')
    )['total'] or 0
    
    total_exp = CrimeResult.objects.filter(
        player=player, 
        result='success'
    ).values('exp_reward').aggregate(
        total=Sum('exp_reward')
    )['total'] or 0
    
    return {
        'total_crimes': total_crimes,
        'successful_crimes': successful_crimes,
        'failed_crimes': failed_crimes,
        'jailed_count': jailed_count,
        'success_rate': round(success_rate, 1),
        'total_earnings': total_earnings,
        'total_exp': total_exp
    } 