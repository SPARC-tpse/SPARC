from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Disruption, Resource, DisruptionType
from datetime import datetime
from .services import Database


def get_resources(request):
    data = list(Resource.objects.values("id", "name"))
    return JsonResponse(data, safe=False)

def get_disruption_types(request):
    data = list(DisruptionType.objects.values("id", "name"))
    return JsonResponse(data, safe=False)

def get_disruptions(request):
    disruptions = Disruption.objects.all().values()

    response_data = []
    for d in disruptions:
        response_data.append({
            "id": d["id"],
            "name": d["name"],
            "type": d["type_id"],
            "resource": d["resource_id"],
            "start_date": d["start_date"],
            "end_date": d["end_date"],
            "disruption_type_name": Database.get_disruption_type_name_by_id(d["type_id"]),
            "resource_name": Database.get_resource_name_by_id(d["resource_id"]),
            "comment":d["comment"],
        })

    return JsonResponse(response_data, safe=False)


@csrf_exempt
def create_disruption(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    try:
        data = json.loads(request.body)

        name = data.get("name")
        type_id = data.get("type")
        resource_id = data.get("resource")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        comment = data.get("comment")

        d_type = DisruptionType.objects.get(id=type_id)
        resource = Resource.objects.get(id=resource_id)

        disruption = Disruption.objects.create(
            name=name,
            type=d_type,
            resource=resource,
            start_date=start_date,
            end_date=end_date,
            comment = comment,
        )

        return JsonResponse({"id": disruption.id, "status": "created"}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


