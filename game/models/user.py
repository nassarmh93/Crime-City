from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Temporarily comment out custom User model to resolve migration issue
"""
class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser
    """
    created_at = models.DateTimeField(default=timezone.now)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Additional user preferences
    display_mode = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light'
    )
    
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'game_user'
"""
