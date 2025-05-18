from django.db import models
from django.utils import timezone
import random

class Combat(models.Model):
    """
    Represents a combat encounter between players
    """
    # Combat participants
    attacker = models.ForeignKey(
        'Player', 
        on_delete=models.CASCADE, 
        related_name='attacks'
    )
    defender = models.ForeignKey(
        'Player', 
        on_delete=models.CASCADE, 
        related_name='defenses'
    )
    
    # Combat outcome
    winner = models.ForeignKey(
        'Player', 
        on_delete=models.CASCADE, 
        related_name='combat_wins',
        null=True, 
        blank=True
    )
    
    # Combat details
    location = models.ForeignKey(
        'Location', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='combats'
    )
    
    # Resources
    cash_stolen = models.PositiveIntegerField(default=0)
    experience_gained = models.PositiveIntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.attacker.nickname} vs {self.defender.nickname}"
    
    def start_combat(self):
        """
        Start the combat and process results
        Returns: (log, result_message)
        """
        attacker = self.attacker
        defender = self.defender
        
        # Check if either player is in hospital or jail
        if attacker.is_in_hospital or attacker.is_in_jail:
            return [], "You cannot attack while in hospital or jail"
            
        if defender.is_in_hospital or defender.is_in_jail:
            return [], "You cannot attack a player who is in hospital or jail"
            
        # Check if in a safe zone
        if self.location and self.location.is_safe_zone:
            return [], "You cannot attack in a safe zone"
            
        # Check if attacker has enough energy
        if attacker.energy < 5:
            return [], "Not enough energy to attack"
            
        # Reduce attacker's energy
        attacker.energy -= 5
        attacker.save()
        
        # Combat log to track actions
        combat_log = []
        combat_log.append(f"{attacker.nickname} attacks {defender.nickname}!")
        
        # Calculate base attack and defense values
        attack_value = attacker.strength * 2 + attacker.dexterity + attacker.speed
        defense_value = defender.defense * 2 + defender.dexterity + defender.speed
        
        # Add equipment bonuses
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
            self.winner = attacker
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
                self.cash_stolen = int(defender.cash * steal_percentage)
                
                if self.cash_stolen > 0:
                    defender.cash -= self.cash_stolen
                    attacker.cash += self.cash_stolen
                    combat_log.append(f"{attacker.nickname} stole ${self.cash_stolen}!")
            
            # Calculate experience gained
            self.experience_gained = 10 + defender.level * 2
            attacker.gain_experience(self.experience_gained)
            combat_log.append(f"{attacker.nickname} gained {self.experience_gained} experience!")
            
            result_message = f"You won the fight against {defender.nickname}!"
        else:
            self.winner = defender
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
        self.ended_at = timezone.now()
        self.save()
        attacker.save()
        defender.save()
        
        # Create combat log entries
        for entry in combat_log:
            CombatLog.objects.create(
                combat=self,
                message=entry,
                timestamp=timezone.now()
            )
        
        return combat_log, result_message
    
    class Meta:
        db_table = 'game_combat'

class CombatLog(models.Model):
    """
    Represents individual events during combat
    """
    combat = models.ForeignKey(
        Combat, 
        on_delete=models.CASCADE, 
        related_name='logs'
    )
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'game_combat_log'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.combat}: {self.message[:50]}..."
