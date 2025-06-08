from django.urls import re_path
from .consumers import CanvasConsumer

websocket_urlpatterns = [
    re_path(r"^ws/canvas/(?P<canvas_id>\d+)/$", CanvasConsumer.as_asgi()),
]
