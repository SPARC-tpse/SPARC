from django.contrib import admin

from .models import (
    Disruption,
    DisruptionType,
    Order,
    OrderFile,
    Part,
    Process,
    Resource,
    ResourceType,
    Worker,
)

admin.site.register(Order)
admin.site.register(Process)
admin.site.register(ResourceType)
admin.site.register(Resource)
admin.site.register(DisruptionType)
admin.site.register(Disruption)
admin.site.register(Worker)
admin.site.register(Part)
admin.site.register(OrderFile)
