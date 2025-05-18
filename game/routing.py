from django.urls import re_path
from . import consumers

# Empty for now, will be filled with WebSocket routes later
websocket_urlpatterns = [
    re_path(r'ws/game/$', consumers.GameConsumer.as_asgi()),
]
