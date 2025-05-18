from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User  # Use Django's default User model
from game.models import Player, Location

# User = get_user_model()  # Comment out custom user model reference

@receiver(post_save, sender=User)
def create_player_for_new_user(sender, instance, created, **kwargs):
    """
    Create a Player instance for newly created User instances
    """
    if created:
        # Get the first location or create a default one if none exists
        default_location, _ = Location.objects.get_or_create(
            name="Downtown",
            defaults={
                'description': 'The downtown area of Crime City. A good place to start your journey.',
                'is_safe_zone': True,
                'energy_cost': 1,
                'min_level': 1,
                'district': 'Central'
            }
        )
        
        # Create a new player for this user
        Player.objects.create(
            user=instance,
            nickname=instance.username,  # Default nickname is username
            current_location=default_location
        ) 