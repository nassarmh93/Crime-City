from django.db import models
from django.utils import timezone

class MarketListing(models.Model):
    """
    Represents an item listing on the marketplace
    """
    LISTING_STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Relationships
    seller = models.ForeignKey(
        'Player', 
        on_delete=models.CASCADE, 
        related_name='market_listings'
    )
    buyer = models.ForeignKey(
        'Player', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='purchases'
    )
    item = models.ForeignKey(
        'Item', 
        on_delete=models.CASCADE, 
        related_name='market_listings'
    )
    
    # Listing details
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    
    # Status
    status = models.CharField(
        max_length=10,
        choices=LISTING_STATUS_CHOICES,
        default='active'
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    sold_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.quantity}x {self.item.name} for ${self.price}"
    
    def purchase(self, buyer):
        """
        Process a purchase of this listing
        Returns: (success, message)
        """
        if self.status != 'active':
            return False, "This listing is no longer active"
            
        if buyer.id == self.seller.id:
            return False, "You cannot buy your own listing"
            
        if buyer.cash < self.price:
            return False, "You don't have enough cash"
            
        # Process the transaction
        buyer.cash -= self.price
        self.seller.cash += self.price
        
        # Update the listing
        self.status = 'sold'
        self.buyer = buyer
        self.sold_at = timezone.now()
        
        # Add the item to buyer's inventory
        from game.models.item import PlayerInventory
        
        # Check if buyer already has this item
        inventory, created = PlayerInventory.objects.get_or_create(
            player=buyer,
            item=self.item,
            defaults={'quantity': 0}
        )
        
        # Add the quantity
        inventory.quantity += self.quantity
        
        # Save all changes
        buyer.save()
        self.seller.save()
        self.save()
        inventory.save()
        
        return True, f"Successfully purchased {self.quantity}x {self.item.name}"
    
    def cancel(self):
        """
        Cancel a listing and return the item to seller's inventory
        Returns: (success, message)
        """
        if self.status != 'active':
            return False, "This listing is not active"
            
        # Update the listing
        self.status = 'cancelled'
        self.save()
        
        # Return the item to seller's inventory
        from game.models.item import PlayerInventory
        
        inventory, created = PlayerInventory.objects.get_or_create(
            player=self.seller,
            item=self.item,
            defaults={'quantity': 0}
        )
        
        inventory.quantity += self.quantity
        inventory.save()
        
        return True, "Listing cancelled successfully"
    
    def check_expiry(self):
        """
        Check if the listing has expired and process accordingly
        Returns: True if expired and processed, False otherwise
        """
        if self.status != 'active':
            return False
            
        if timezone.now() >= self.expires_at:
            # Mark as expired
            self.status = 'expired'
            self.save()
            
            # Return the item to seller's inventory
            from game.models.item import PlayerInventory
            
            inventory, created = PlayerInventory.objects.get_or_create(
                player=self.seller,
                item=self.item,
                defaults={'quantity': 0}
            )
            
            inventory.quantity += self.quantity
            inventory.save()
            
            return True
            
        return False
    
    class Meta:
        db_table = 'game_market_listing'
