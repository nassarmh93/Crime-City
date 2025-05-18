from django.db import models

class Location(models.Model):
    """
    Represents locations/areas in the game world
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.CharField(max_length=200, null=True, blank=True)  # Path to image
    
    # Location attributes
    is_safe_zone = models.BooleanField(default=False)  # No PvP combat allowed
    energy_cost = models.PositiveIntegerField(default=1)  # Energy cost to perform actions here
    min_level = models.PositiveIntegerField(default=1)  # Minimum player level to access
    
    # For neighborhood organization
    district = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'game_location'

class LocationConnection(models.Model):
    """
    Represents connections between locations (for travel)
    """
    from_location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        related_name='connections_from'
    )
    to_location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        related_name='connections_to'
    )
    travel_time = models.PositiveIntegerField(default=0)  # Travel time in seconds
    travel_cost = models.PositiveIntegerField(default=0)  # Cost to travel
    
    class Meta:
        unique_together = ('from_location', 'to_location')
        db_table = 'game_location_connection'
        
    def __str__(self):
        return f"{self.from_location.name} → {self.to_location.name}"
