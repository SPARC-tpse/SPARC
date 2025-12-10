from django.urls import path
from .views import (
    get_resources,
    get_disruption_types,
    get_disruptions,
    create_disruption
)

urlpatterns = [
    path("api/resources/", get_resources, name="get_resources"),
    path("api/disruption-types/", get_disruption_types, name="get_disruption_types"),
    path("api/disruptions/", get_disruptions, name="get_disruptions"),
    path("api/disruptions/create/", create_disruption, name="create_disruption"),
]
