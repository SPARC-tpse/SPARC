from django.contrib import admin
from .models import Order, Process, ResourceType, Resource, DisruptionType, Disruption, Worker

admin.site.register(Order)
admin.site.register(Process)
admin.site.register(ResourceType)
admin.site.register(Resource)
admin.site.register(DisruptionType)
admin.site.register(Disruption)
admin.site.register(Worker)