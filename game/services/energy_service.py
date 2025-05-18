from django.utils import timezone
from django.db.models import F

def calculate_energy_regeneration(player, current_time=None):
    """
    Calculate how much energy should be regenerated based on time passed
    
    Args:
        player: Player model instance
        current_time: Optional timezone-aware datetime (defaults to now)
    
    Returns:
        int: Amount of energy to add
    """
    if current_time is None:
        current_time = timezone.now()
        
    time_diff = current_time - player.last_energy_refill
    
    # Energy regenerates at 1 point per 5 minutes
    energy_to_add = min(
        player.max_energy - player.energy,
        time_diff.total_seconds() // 300  # 300 seconds = 5 minutes
    )
    
    return int(energy_to_add)

def regenerate_player_energy(player):
    """
    Regenerate a player's energy based on time elapsed
    
    Args:
        player: Player model instance
    
    Returns:
        bool: True if energy was regenerated, False otherwise
    """
    current_time = timezone.now()
    energy_to_add = calculate_energy_regeneration(player, current_time)
    
    if energy_to_add <= 0:
        return False
        
    # Update player's energy
    player.energy += energy_to_add
    
    # Update the last refill time, but keep partial progress toward next point
    seconds_used = energy_to_add * 300  # 300 seconds = 5 minutes
    player.last_energy_refill = current_time - timezone.timedelta(
        seconds=(current_time - player.last_energy_refill).total_seconds() % 300
    )
    
    player.save(update_fields=['energy', 'last_energy_refill'])
    return True

def use_energy(player, amount):
    """
    Use energy for an action
    
    Args:
        player: Player model instance
        amount: Amount of energy to use
    
    Returns:
        tuple: (success, message)
    """
    # Make sure player has enough energy
    if player.energy < amount:
        return False, "Not enough energy"
        
    # Deduct energy
    player.energy -= amount
    player.save(update_fields=['energy'])
    
    return True, f"Used {amount} energy"

def refill_energy(player, amount=None):
    """
    Immediately refill player's energy (e.g., from using an item)
    
    Args:
        player: Player model instance
        amount: Amount to refill (defaults to max)
    
    Returns:
        int: Actual amount refilled
    """
    if amount is None:
        # Full refill
        amount = player.max_energy - player.energy
    else:
        # Partial refill, capped at max
        amount = min(amount, player.max_energy - player.energy)
        
    if amount <= 0:
        return 0
        
    player.energy += amount
    player.save(update_fields=['energy'])
    
    return amount
