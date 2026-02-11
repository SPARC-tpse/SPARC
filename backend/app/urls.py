from django.urls import path
from .views import get_orders, create_order, update_order, delete_order, get_order, upload_order_file, delete_order_file, list_order_files

urlpatterns = [
    path("orders/get", get_orders, name="get_orders"),
    path("orders/get/<int:order_id>", get_order, name="get_order"),
    path("orders/post", create_order, name="create_order"),
    path("orders/put/<int:order_id>", update_order, name="update_order"),
    path("orders/delete/<int:order_id>", delete_order, name="delete_order"),

    # File endpoints
    path("files/upload", upload_order_file, name="upload_order_file"),
    path("files/delete", delete_order_file, name="delete_order_file"),
    path("files/list", list_order_files, name="list_order_files"),
]
