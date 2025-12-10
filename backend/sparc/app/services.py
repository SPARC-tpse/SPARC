from .models import Resource, Disruption, DisruptionType


##class to provide a database-frotend interface. Any methods needed by the frontend may be added here
class Database:

    @staticmethod
    def get_resource_name_by_id(resource_id: int) -> str:
        if not resource_id:
            return "N/A"
        try:
            resource = Resource.objects.only('name').get(id=resource_id)
            return resource.name
        except Resource.DoesNotExist:
            return "Resource Not Found"

    @staticmethod
    def get_disruption_name_by_id(disruption_id: int) -> str:
        if not disruption_id:
            return "N/A"
        try:
            disruption = Disruption.objects.only('name').get(id=disruption_id)
            return disruption.name
        except Disruption.DoesNotExist:
            return "Disruption Not Found"

    @staticmethod
    def get_disruption_type_name_by_id(disruption_type_id: int) -> str:
        if not disruption_type_id:
            return "N/A"
        try:
            disruption_type = DisruptionType.objects.only('name').get(id=disruption_type_id)
            return disruption_type.name
        except DisruptionType.DoesNotExist:
            return "Disruption Type Not Found"
