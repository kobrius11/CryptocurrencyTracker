
from django.urls import re_path
from website import consumers

websocket_urlpatterns = [
    re_path(r'ws/price/(?P<room_name>\w+)/$', consumers.PriceConsumer.as_asgi()),
]

