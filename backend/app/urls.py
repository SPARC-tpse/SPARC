from django.urls import path

from .views.disruption_view import (
    create_disruption,
    delete_disruption,
    get_disruption,
    get_disruption_chart,
    get_disruption_types,
    get_disruptions,
    update_disruption,
)
from .views.order_file_view import (
    delete_order_file,
    get_order_files,
    upload_order_file,
)
from .views.order_view import (
    create_order,
    delete_order,
    get_order,
    get_order_approximated_time,
    get_order_processes,
    get_orders,
    update_order,
)
from .views.process_view import (
    add_part,
    delete_process,
    get_parts,
    get_processes,
    update_process_timing,
)
from .views.resource_view import (
    create_resource,
    delete_resource,
    get_resource,
    get_resource_approximated_time,
    get_resources,
    update_resource,
)
from .views.worker_view import (
    create_worker,
    delete_worker,
    get_worker,
    get_workers,
    update_worker,
)

urlpatterns = [
    # Order
    path("order/get/", get_orders, name="get_orders"),
    path("order/get/<int:order_id>/", get_order, name="get_order"),
    path("order/get_processes/<int:order_id>/", get_order_processes, name="get_order_processes"),
    path("order/post/", create_order, name="create_order"),
    path("order/put/<int:order_id>/", update_order, name="update_order"),
    path("order/delete/<int:order_id>/", delete_order, name="delete_order"),
    path("order/approximated_time/<int:order_id>/", get_order_approximated_time, name="get_order_approximated_time"),

    # File endpoints
    path("order/file/post/", upload_order_file, name="upload_order_file"),
    path("order/file/delete/<int:file_id>/", delete_order_file, name="delete_order_file"),
    path("order/file/get/<int:order_id>/", get_order_files, name="get_order_files"),

    # Process
    path("process/timing/<int:process_id>/", update_process_timing, name="update_process_timing"),
    path("process/delete/<int:process_id>/", delete_process, name="delete_process"),
    path("process/get/", get_processes, name="get_processes"),
    path("process/part/post/<int:process_id>/", add_part, name="add_part"),
    path("process/part/get/<int:process_id>/", get_parts, name="get_parts"),

    # Worker
    path("worker/get/", get_workers, name="get_workers"),
    path("worker/post/", create_worker, name="create_worker"),
    path("worker/delete/<int:worker_id>/", delete_worker, name="delete_worker"),
    path("worker/get/<int:worker_id>/", get_worker, name="get_worker"),
    path("worker/put/<int:worker_id>/", update_worker, name="update_worker"),

    # Resources
    path("resource/get/", get_resources, name="get_resources"),
    path("resource/get/<int:resource_id>/", get_resource, name="get_resource"),
    path("resource/post/", create_resource, name="create_resource"),
    path("resource/put/<int:resource_id>/", update_resource, name="update_resource"),
    path("resource/delete/<int:resource_id>/", delete_resource, name="delete_resource"),
    path("resource/approximated_time/<int:resource_id>/", get_resource_approximated_time, name="get_resource_approximated_time"),

    # DISRUPTIONS
    path("disruption/get/", get_disruptions, name="get_disruptions"),
    path("disruption/get/<int:disruption_id>/", get_disruption, name="get_disruption"),
    path("disruption/put/<int:disruption_id>/", update_disruption, name="update_disruption"),
    path("disruption/post/", create_disruption, name="create_disruption"),
    path("disruption/delete/<int:disruption_id>/", delete_disruption, name="delete_disruption"),
    path("disruption-type/get/", get_disruption_types, name="get_disruption_types"),
    path("disruption/chart/get/", get_disruption_chart, name="get_disruption_chart"),
]
