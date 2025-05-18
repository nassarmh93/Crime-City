"""
Models for crime-related game features.
"""
from django.db import models
from django.utils import timezone
import random

class CrimeType(models.Model):
    """
    Represents different types of crimes players can commit
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Requirements
    min_level = models.PositiveIntegerField(default=1)
    energy_cost = models.PositiveIntegerField(default=10)
    
    # Rewards
    min_cash_reward = models.PositiveIntegerField(default=100)
    max_cash_reward = models.PositiveIntegerField(default=500)
    min_exp_reward = models.PositiveIntegerField(default=10)
    max_exp_reward = models.PositiveIntegerField(default=50)
    
    # Risks
    jail_risk = models.FloatField(default=0.2)  # 0.0 to 1.0
    min_jail_time = models.PositiveIntegerField(default=300)  # in seconds
    max_jail_time = models.PositiveIntegerField(default=1800)  # in seconds
    
    # Item reward (optional)
    possible_rewards = models.ManyToManyField(
        'game.Item', 
        related_name='crime_rewards',
        blank=True
    )
    item_reward_chance = models.FloatField(default=0.1)  # 0.0 to 1.0
    
    # Success factors - which stats affect success chance
    strength_factor = models.FloatField(default=0.0)
    defense_factor = models.FloatField(default=0.0)
    speed_factor = models.FloatField(default=0.0)
    dexterity_factor = models.FloatField(default=0.0)
    intelligence_factor = models.FloatField(default=0.0)
    
    # Base success chance
    base_success_chance = models.FloatField(default=0.5)  # 0.0 to 1.0
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'game_crime_type'
        verbose_name = 'Crime Type'
        verbose_name_plural = 'Crime Types'


class CrimeResult(models.Model):
    """
    Records results of crimes committed by players
    """
    RESULT_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('jailed', 'Player Jailed'),
        ('interrupted', 'Interrupted'),
    ]
    
    player = models.ForeignKey(
        'game.Player', 
        on_delete=models.CASCADE, 
        related_name='crime_results'
    )
    crime_type = models.ForeignKey(
        CrimeType, 
        on_delete=models.CASCADE, 
        related_name='results'
    )
    
    # Result details
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    cash_reward = models.PositiveIntegerField(default=0)
    exp_reward = models.PositiveIntegerField(default=0)
    
    # If jail result
    jail_time = models.PositiveIntegerField(default=0)  # in seconds
    
    # Item reward, if any
    item_reward = models.ForeignKey(
        'game.Item', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='crime_results'
    )
    
    # Location where crime was committed
    location = models.ForeignKey(
        'game.Location', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='crimes'
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.player.nickname} - {self.crime_type.name} - {self.result}"
    
    class Meta:
        db_table = 'game_crime_result'
        ordering = ['-created_at'] 