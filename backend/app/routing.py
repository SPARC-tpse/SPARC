from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/order/$', consumers.OrderConsumer.as_asgi()),
    re_path(r'ws/worker/$', consumers.WorkerConsumer.as_asgi()),
    re_path(r'ws/resource/$', consumers.ResourceConsumer.as_asgi()),
    re_path(r'ws/disruption/$', consumers.DisruptionConsumer.as_asgi())
]
