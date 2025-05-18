from django.apps import AppConfig


class GameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'game'
    
    def ready(self):
        """Register any signals"""
        import game.signals  # Import signals module
