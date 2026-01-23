from django.urls import path
from .views import get_orders, create_order, update_order, delete_order

urlpatterns = [
    path("orders/", get_orders, name="get_orders"),                    # GET
    path("orders/", create_order, name="create_order"),                # POST
    path("orders/<int:order_id>/", update_order, name="update_order"), # PUT
    path("orders/<int:order_id>/", delete_order, name="delete_order"), # DELETE
]
