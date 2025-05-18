from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User  # Temporarily use Django's User model
import random

class Player(models.Model):
    """
    Player model representing a user's in-game character
    """
    # Relationship with User model
    # user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='player')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player')
    
    # Basic player attributes
    nickname = models.CharField(max_length=50, unique=True)
    level = models.PositiveIntegerField(default=1)
    experience = models.PositiveIntegerField(default=0)
    cash = models.BigIntegerField(default=1000)
    bank_balance = models.BigIntegerField(default=0)
    
    # Stats
    strength = models.PositiveIntegerField(default=10)
    defense = models.PositiveIntegerField(default=10)
    speed = models.PositiveIntegerField(default=10)
    dexterity = models.PositiveIntegerField(default=10)
    intelligence = models.PositiveIntegerField(default=10)
    
    # Resources
    energy = models.PositiveIntegerField(default=100)
    max_energy = models.PositiveIntegerField(default=100)
    health = models.PositiveIntegerField(default=100)
    max_health = models.PositiveIntegerField(default=100)
    
    # Location
    current_location = models.ForeignKey(
        'Location', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='players_present'
    )
    
    # Status fields
    is_in_hospital = models.BooleanField(default=False)
    hospital_release_time = models.DateTimeField(null=True, blank=True)
    is_in_jail = models.BooleanField(default=False)
    jail_release_time = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    last_energy_refill = models.DateTimeField(default=timezone.now)
    last_health_refill = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.nickname
    
    def level_up(self):
        """Increase player level and update stats"""
        self.level += 1
        self.max_energy += 5
        self.max_health += 10
        self.energy = self.max_energy
        self.health = self.max_health
        self.save()
    
    def gain_experience(self, amount):
        """Add experience and check for level up"""
        self.experience += amount
        
        # Check if player should level up (simple formula)
        exp_needed = self.level * 100
        if self.experience >= exp_needed:
            self.experience -= exp_needed
            self.level_up()
            return True
        self.save()
        return False
    
    def regenerate_energy(self):
        """Regenerate energy based on time passed since last refill"""
        now = timezone.now()
        time_diff = now - self.last_energy_refill
        
        # Energy regenerates at a rate of 1 per 5 minutes
        energy_to_add = min(
            self.max_energy - self.energy,
            time_diff.total_seconds() // 300
        )
        
        if energy_to_add > 0:
            self.energy += int(energy_to_add)
            self.last_energy_refill = now - timezone.timedelta(
                seconds=(time_diff.total_seconds() % 300)
            )
            self.save()
    
    def regenerate_health(self):
        """Regenerate health based on time passed since last refill"""
        now = timezone.now()
        time_diff = now - self.last_health_refill
        
        # Health regenerates at a rate of 1 per 10 minutes
        health_to_add = min(
            self.max_health - self.health,
            time_diff.total_seconds() // 600
        )
        
        if health_to_add > 0:
            self.health += int(health_to_add)
            self.last_health_refill = now - timezone.timedelta(
                seconds=(time_diff.total_seconds() % 600)
            )
            self.save()
            
    def check_status(self):
        """Check and update player status (hospital, jail)"""
        now = timezone.now()
        
        if self.is_in_hospital and now >= self.hospital_release_time:
            self.is_in_hospital = False
            self.health = self.max_health
            self.hospital_release_time = None
        
        if self.is_in_jail and now >= self.jail_release_time:
            self.is_in_jail = False
            self.jail_release_time = None
            
        if self.is_in_hospital or self.is_in_jail:
            self.save()
    
    def train_stat(self, stat_name, energy_cost=5):
        """Train a specific stat"""
        if self.energy < energy_cost:
            return False, "Not enough energy"
            
        if stat_name not in ['strength', 'defense', 'speed', 'dexterity', 'intelligence']:
            return False, "Invalid stat name"
            
        # Deduct energy
        self.energy -= energy_cost
        
        # Increase the stat
        current_value = getattr(self, stat_name)
        setattr(self, stat_name, current_value + 1)
        
        # Give some experience
        self.gain_experience(energy_cost * 2)
        
        self.save()
        return True, f"Successfully trained {stat_name}"
    
    class Meta:
        db_table = 'game_player'
