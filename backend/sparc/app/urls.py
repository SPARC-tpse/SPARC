from django.urls import path
from .views import get_resources, get_disruption_types, get_resource_types

urlpatterns = [
    path("api/resources/", get_resources, name="get_resources"),
    path("api/disruption-types/", get_disruption_types,
         name="get_disruption_types"),
    path("api/resource_types/", get_)

]
