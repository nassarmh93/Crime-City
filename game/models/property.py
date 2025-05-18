from django.db import models
from django.utils import timezone

class PropertyType(models.Model):
    """
    Represents different types of properties players can own
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.CharField(max_length=200, null=True, blank=True)
    
    # Base attributes
    base_price = models.PositiveIntegerField(default=1000)
    base_income = models.PositiveIntegerField(default=100)  # Daily income
    
    # Requirements
    min_level = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'game_property_type'
        verbose_name_plural = 'property types'

class Property(models.Model):
    """
    Represents a specific instance of a property owned by a player
    """
    player = models.ForeignKey(
        'Player', 
        on_delete=models.CASCADE, 
        related_name='properties'
    )
    property_type = models.ForeignKey(
        PropertyType, 
        on_delete=models.CASCADE, 
        related_name='instances'
    )
    
    # Instance attributes
    name = models.CharField(max_length=100)
    purchase_price = models.PositiveIntegerField()
    current_value = models.PositiveIntegerField()
    
    # Location of the property
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        related_name='properties'
    )
    
    # Business metrics
    income_rate = models.PositiveIntegerField()  # Daily income
    level = models.PositiveIntegerField(default=1)  # Property level (can be upgraded)
    
    # Status
    last_income_collection = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    purchased_on = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name} ({self.property_type.name})"
    
    def collect_income(self):
        """
        Collect accumulated income from the property
        Returns: (amount_collected, message)
        """
        if not self.is_active:
            return 0, "This property is not active"
            
        now = timezone.now()
        time_diff = now - self.last_income_collection
        
        # Calculate income based on time passed (max 7 days)
        days_passed = min(time_diff.days + (time_diff.seconds / 86400), 7)
        income = int(self.income_rate * days_passed)
        
        if income <= 0:
            return 0, "No income to collect yet"
            
        # Update the player's balance
        self.player.cash += income
        self.player.save()
        
        # Update the last income collection time
        self.last_income_collection = now
        self.save()
        
        return income, f"Collected ${income} from {self.name}"
        
    def upgrade(self, cost):
        """
        Upgrade the property to increase income
        Returns: (success, message)
        """
        if self.player.cash < cost:
            return False, "Not enough cash"
            
        # Deduct cash
        self.player.cash -= cost
        self.player.save()
        
        # Upgrade property
        self.level += 1
        self.income_rate = int(self.income_rate * 1.2)  # 20% increase per level
        self.current_value = int(self.current_value * 1.15)  # 15% increase in value
        self.save()
        
        return True, f"Successfully upgraded {self.name} to level {self.level}"
    
    class Meta:
        db_table = 'game_property'
        verbose_name_plural = 'properties'
