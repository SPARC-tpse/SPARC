from django.urls import path
from .views import get_orders, create_order, update_order, delete_order

urlpatterns = [
    path("orders/get_orders", get_orders, name="get_orders"),
    path("orders/create_order", create_order, name="create_order"),
    path("orders/update_order", update_order, name="update_order"),
    path("orders/delete_order", delete_order, name="delete_order"),
]
