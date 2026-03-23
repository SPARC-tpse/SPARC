from typing import Any, cast

from django.urls import re_path

from .consumers import (
    disruption_consumer,
    order_consumer,
    resource_consumer,
    worker_consumer,
)

websocket_urlpatterns = [
    # Cast as_asgi() result to Any to satisfy the Django view requirement
    re_path(r"ws/order/$", cast(Any, order_consumer.OrderConsumer.as_asgi())),
    re_path(r"ws/worker/$", cast(Any, worker_consumer.WorkerConsumer.as_asgi())),
    re_path(r"ws/resource/$", cast(Any, resource_consumer.ResourceConsumer.as_asgi())),
    re_path(r"ws/disruption/$", cast(Any, disruption_consumer.DisruptionConsumer.as_asgi())),
]
