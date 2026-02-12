from django.urls import path
from .views import get_orders, create_order, update_order, delete_order, get_order, upload_order_file, delete_order_file, list_order_files, update_process_timing#,delete_process#, get_workers, create_worker, delete_worker, update_process_timing

urlpatterns = [
    # Order
    path("order/get", get_orders, name="get_orders"),
    path("order/get/<int:order_id>", get_order, name="get_order"),
    path("order/post", create_order, name="create_order"),
    path("order/put/<int:order_id>", update_order, name="update_order"),
    path("order/delete/<int:order_id>", delete_order, name="delete_order"),
    # File endpoints
    path("order/file/post", upload_order_file, name="upload_order_file"),
    path("order/file/delete/<int:file_id>", delete_order_file, name="delete_order_file"),
    path("order/<int:order_id>/file/get", list_order_files, name="list_order_files"),

    # Process
    path("process/timing/<int:process_id>", update_process_timing, name="update_process_timing"),
#    path("process/delete/<int:process_id>", delete_process, name="delete_process"),

    # Worker
    #path("worker/get", get_workers, name="get_workers"),
    #path("worker/post", create_worker, name="create_worker"),
    #path("worker/delete/<int:order_id>", delete_worker, name="delete_worker"),
]
