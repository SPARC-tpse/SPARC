from django.urls import path
from .views import (
    get_resources,
    get_resource_types,
    get_disruption_types,
    get_disruptions,
    create_disruption,
    create_resource
)

urlpatterns = [
    #resources
    path("api/resources/", get_resources, name="get_resources"),
    path("api/resource-types/", get_resource_types, name="get_resource_types"),
    path("api/resources/create/", create_resource, name="create_resource"),

    #disruptions
    path("api/disruptions/", get_disruptions, name="get_disruptions"),
    path("api/disruption-types/", get_disruption_types, name="get_disruption_types"),
    path("api/disruptions/create/", create_disruption, name="create_disruption"),


]
