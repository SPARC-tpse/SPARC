from django.urls import path
from .views import get_orders, create_order, update_order, delete_order, get_disruptions, create_disruption, update_disruption, delete_disruption, get_disruptionTypes, get_resources, create_resource, get_resourceTypes, update_resource, delete_resource

urlpatterns = [

    #Order
    path("orders/get_orders/", get_orders, name="get_orders"),
    path("orders/create_order/", create_order, name="create_order"),
    path("orders/update_order/<int:order_id>/", update_order, name="update_order"),
    path("orders/delete_order/<int:order_id>/", delete_order, name="delete_order"),
    
    #Disruption
    path("disruptions/get_disruptions/", get_disruptions, name="get_disruptions"),
    path("disruptions/create_disruption/", create_disruption, name="create_disruption"),
    path("disruptions/update_disruption/<int:disruption_id>/", update_disruption, name="update_disruption"),
    path("disruptions/delete_disruption/<int:disruption_id>/", delete_disruption, name="delete_disruption"),
    
    #DisruptionTypes
    path("disruptionTypes/get_disruptionTypes/", get_disruptionTypes, name="get_disruptionTypes"),
    
    #Resources
    path("resources/get_resources/", get_resources, name="get_resources"),
    path("resources/create_resource/", create_resource, name="create_resource"),
    path("resources/update_resource/<int:resource_id>/", update_resource, name="update_resource"),
    path("resources/delete_resource/<int:resources_id>/", delete_resource, name="delete_resource"),
    
    #ResourceTypes
     path("resourceTypes/get_resourceTypes", get_resourceTypes, name="get_resourceTypes"),
]
