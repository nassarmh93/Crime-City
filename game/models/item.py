from django.db import models
from django.conf import settings

class ItemType(models.Model):
    """
    Represents different types of items in the game
    """
    name = models.CharField(max_length=50)
    description = models.TextField()
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'game_item_type'

class Item(models.Model):
    """
    Represents item definitions (templates)
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.CharField(max_length=200, null=True, blank=True)
    item_type = models.ForeignKey(ItemType, on_delete=models.CASCADE, related_name='items')
    
    # Item attributes
    buy_price = models.PositiveIntegerField(default=0)  # Base shop price
    sell_price = models.PositiveIntegerField(default=0)  # Base selling price
    min_level = models.PositiveIntegerField(default=1)  # Minimum level to use
    
    # Item stats (for weapons, armor, etc)
    attack_power = models.PositiveIntegerField(default=0)
    defense_power = models.PositiveIntegerField(default=0)
    speed_bonus = models.IntegerField(default=0)
    
    # For consumables
    energy_restore = models.PositiveIntegerField(default=0)
    health_restore = models.PositiveIntegerField(default=0)
    
    is_tradable = models.BooleanField(default=True)
    is_equippable = models.BooleanField(default=False)
    is_consumable = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'game_item'

class PlayerInventory(models.Model):
    """
    Represents items owned by players
    """
    player = models.ForeignKey(
        'Player', 
        on_delete=models.CASCADE, 
        related_name='inventory'
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_equipped = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('player', 'item')
        db_table = 'game_player_inventory'
    
    def __str__(self):
        return f"{self.player.nickname}'s {self.item.name} (x{self.quantity})"
        
    def use_item(self):
        """
        Use a consumable item
        Returns: (success, message)
        """
        if not self.item.is_consumable:
            return False, "This item cannot be consumed"
            
        if self.quantity <= 0:
            return False, "You don't have any of this item"
            
        player = self.player
        
        # Apply item effects
        if self.item.energy_restore > 0:
            player.energy = min(player.energy + self.item.energy_restore, player.max_energy)
            
        if self.item.health_restore > 0:
            player.health = min(player.health + self.item.health_restore, player.max_health)
            
        player.save()
        
        # Reduce quantity
        self.quantity -= 1
        if self.quantity <= 0:
            self.delete()
        else:
            self.save()
            
        return True, f"You used {self.item.name}"
    
    def equip(self):
        """
        Equip an item
        Returns: (success, message)
        """
        if not self.item.is_equippable:
            return False, "This item cannot be equipped"
            
        if self.is_equipped:
            return False, "This item is already equipped"
            
        # Unequip any items of the same type
        PlayerInventory.objects.filter(
            player=self.player,
            item__item_type=self.item.item_type,
            is_equipped=True
        ).update(is_equipped=False)
        
        # Equip this item
        self.is_equipped = True
        self.save()
        
        return True, f"You equipped {self.item.name}"
    
    def unequip(self):
        """
        Unequip an item
        Returns: (success, message)
        """
        if not self.is_equipped:
            return False, "This item is not equipped"
            
        self.is_equipped = False
        self.save()
        
        return True, f"You unequipped {self.item.name}"
