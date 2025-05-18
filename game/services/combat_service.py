from django.utils import timezone
import random
from game.models import Combat, CombatLog
from game.services.energy_service import use_energy

def get_available_opponents(player, location, limit=10):
    """
    Get available opponents for the player at the current location
    
    Args:
        player: Player model instance
        location: Location model instance
        limit: Maximum number of opponents to return
    
    Returns:
        queryset: QuerySet of Player objects
    """
    from game.models import Player
    
    # Get players at the same location who are not in hospital/jail
    opponents = Player.objects.filter(
        current_location=location,
        is_in_hospital=False,
        is_in_jail=False,
    ).exclude(
        id=player.id
    )
    
    # Filter by level range (within ±3 of player's level)
    min_level = max(1, player.level - 3)
    max_level = player.level + 3
    
    opponents = opponents.filter(level__gte=min_level, level__lte=max_level)
    
    # Return a limited number of opponents
    return opponents[:limit]

def initiate_combat(attacker, defender, location):
    """
    Start a combat encounter between two players
    
    Args:
        attacker: Attacking Player model instance
        defender: Defending Player model instance
        location: Location model instance
    
    Returns:
        tuple: (Combat, log_messages, result_message)
    """
    # Check if attacker has enough energy
    energy_success, energy_message = use_energy(attacker, 5)
    if not energy_success:
        return None, [], energy_message
        
    # Check if either player is in hospital or jail
    if attacker.is_in_hospital or attacker.is_in_jail:
        return None, [], "You cannot attack while in hospital or jail"
        
    if defender.is_in_hospital or defender.is_in_jail:
        return None, [], "You cannot attack a player who is in hospital or jail"
        
    # Check if in a safe zone
    if location.is_safe_zone:
        # Refund energy
        attacker.energy += 5
        attacker.save(update_fields=['energy'])
        return None, [], "You cannot attack in a safe zone"
    
    # Create new combat record
    combat = Combat.objects.create(
        attacker=attacker,
        defender=defender,
        location=location,
        started_at=timezone.now()
    )
    
    # Process the combat
    log_messages, result_message = process_combat(combat)
    
    return combat, log_messages, result_message

def process_combat(combat):
    """
    Process the outcome of a combat
    
    Args:
        combat: Combat model instance
    
    Returns:
        tuple: (log_messages, result_message)
    """
    attacker = combat.attacker
    defender = combat.defender
    
    # Combat log to track actions
    combat_log = []
    combat_log.append(f"{attacker.nickname} attacks {defender.nickname}!")
    
    # Calculate base attack and defense values
    attack_value = attacker.strength * 2 + attacker.dexterity + attacker.speed
    defense_value = defender.defense * 2 + defender.dexterity + defender.speed
    
    # Add equipment bonuses from items
    attack_items = attacker.inventory.filter(is_equipped=True)
    for item in attack_items:
        attack_value += item.item.attack_power
        
    defense_items = defender.inventory.filter(is_equipped=True)
    for item in defense_items:
        defense_value += item.item.defense_power
        
    # Add randomness
    attack_roll = random.randint(1, 20)
    defense_roll = random.randint(1, 20)
    
    attack_value += attack_roll
    defense_value += defense_roll
    
    combat_log.append(f"{attacker.nickname} attack value: {attack_value}")
    combat_log.append(f"{defender.nickname} defense value: {defense_value}")
    
    # Determine winner
    if attack_value > defense_value:
        combat.winner = attacker
        damage = int((attack_value - defense_value) / 2)
        
        # Ensure minimum damage
        damage = max(5, damage)
        
        # Apply damage to defender
        defender.health -= damage
        combat_log.append(f"{attacker.nickname} hits for {damage} damage!")
        
        # If defender health drops to zero or below, send them to hospital
        if defender.health <= 0:
            defender.health = 0
            defender.is_in_hospital = True
            defender.hospital_release_time = timezone.now() + timezone.timedelta(minutes=30)
            combat_log.append(f"{defender.nickname} has been hospitalized!")
            
            # Calculate stolen cash (10-20% of on-hand cash)
            steal_percentage = random.uniform(0.1, 0.2)
            combat.cash_stolen = int(defender.cash * steal_percentage)
            
            if combat.cash_stolen > 0:
                defender.cash -= combat.cash_stolen
                attacker.cash += combat.cash_stolen
                combat_log.append(f"{attacker.nickname} stole ${combat.cash_stolen}!")
        
        # Calculate experience gained
        combat.experience_gained = 10 + defender.level * 2
        attacker.gain_experience(combat.experience_gained)
        combat_log.append(f"{attacker.nickname} gained {combat.experience_gained} experience!")
        
        result_message = f"You won the fight against {defender.nickname}!"
    else:
        combat.winner = defender
        damage = int((defense_value - attack_value) / 3)
        damage = max(3, damage)  # Ensure minimum counter-damage
        
        # Apply counter-damage to attacker
        attacker.health -= damage
        combat_log.append(f"{defender.nickname} counters for {damage} damage!")
        
        # If attacker health drops to zero or below, send them to hospital
        if attacker.health <= 0:
            attacker.health = 0
            attacker.is_in_hospital = True
            attacker.hospital_release_time = timezone.now() + timezone.timedelta(minutes=20)
            combat_log.append(f"{attacker.nickname} has been hospitalized!")
        
        # Defender still gains some experience for successful defense
        defender_exp = 5 + attacker.level
        defender.gain_experience(defender_exp)
        combat_log.append(f"{defender.nickname} gained {defender_exp} experience from defending!")
        
        result_message = f"You lost the fight against {defender.nickname}!"
    
    # Save changes
    combat.ended_at = timezone.now()
    combat.save()
    attacker.save()
    defender.save()
    
    # Create combat log entries
    for entry in combat_log:
        CombatLog.objects.create(
            combat=combat,
            message=entry,
            timestamp=timezone.now()
        )
    
    return combat_log, result_message

def get_recent_combat_logs(player, limit=5):
    """
    Get recent combat logs for a player
    
    Args:
        player: Player model instance
        limit: Maximum number of logs to return
    
    Returns:
        queryset: QuerySet of Combat objects
    """
    combat_logs = Combat.objects.filter(
        attacker=player
    ).order_by('-started_at')[:limit]
    
    return combat_logs
