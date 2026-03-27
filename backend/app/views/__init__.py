from typing import Any, Dict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_db_change(model: str, action: str, order_data: Dict[str, Any] | None = None) -> None:
    """Helper to broadcast database changes via WebSocket"""
    channel_layer = get_channel_layer()
    s = model + '_' + model
    model_type = model + '_message'
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            s,
            {
                'type': model_type,
                'action': action,
                'data': order_data
            }
        )
