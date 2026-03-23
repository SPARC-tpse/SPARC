from typing import Any, cast

from django.http import JsonResponse, QueryDict
from rest_framework.decorators import api_view
from rest_framework.request import Request

from ..models import Process, Resource, ResourceType
from ..serializers.resource_serializer import ResourceSerializer
from . import broadcast_db_change


def _get_request_data(request: Request) -> tuple[dict[str, Any] | None, JsonResponse | None]:
    """Narrows request.data to a plain dict, or returns a 400 response."""
    if not isinstance(request.data, (dict, QueryDict)):
        return None, JsonResponse({'error': 'Invalid request body'}, status=400)
    data: dict[str, Any] = dict(request.data) if isinstance(request.data, QueryDict) else request.data
    return data, None


@api_view(['GET'])
def get_resources(request: Request) -> JsonResponse:
    """Get all resources"""
    try:
        resources = Resource.objects.all()
        serializer = ResourceSerializer(resources, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
def get_resource(request: Request, resource_id: int) -> JsonResponse:
    """Get a single resource by ID"""
    try:
        resource = Resource.objects.get(id=resource_id)
        serializer = ResourceSerializer(resource)
        return JsonResponse(serializer.data, safe=True)
    except Resource.DoesNotExist:
        return JsonResponse({'error': 'Resource not found'}, status=404)
    except Exception as e:
        print(e, flush=True)
        return JsonResponse({'error': 'Resource not found'}, status=500)


@api_view(['POST'])
def create_resource(request: Request) -> JsonResponse:
    """Create a new resource"""
    data, err_response = _get_request_data(request)
    if err_response:
        return err_response
    assert data is not None

    # Validate required fields up front before any DB work
    name = data.get('name')
    type_name = data.get('type')
    status = data.get('status')

    if not name:
        return JsonResponse({'error': 'name is required'}, status=400)
    if not type_name:
        return JsonResponse({'error': 'type is required'}, status=400)
    if status is None:
        return JsonResponse({'error': 'status is required'}, status=400)

    try:
        status_int = int(status)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'status must be an integer'}, status=400)

    r_type_obj, _ = ResourceType.objects.get_or_create(
        name__iexact=type_name,
        defaults={'name': type_name}
    )

    new_resource = Resource.objects.create(
        name=name,
        type=r_type_obj,
        status=status_int,
    )
    serializer = ResourceSerializer(new_resource)
    broadcast_db_change('resource', 'created', cast(dict[str, Any], serializer.data))
    return JsonResponse({'message': 'Resource created'}, status=201)


@api_view(['PUT'])
def update_resource(request: Request, resource_id: int) -> JsonResponse:
    """Update an existing resource"""
    data, err_response = _get_request_data(request)
    if err_response:
        return err_response
    assert data is not None

    try:
        r = Resource.objects.get(id=resource_id)
        r.name = data.get('name', r.name)
        r.status = int(data.get('status', r.status))

        if 'type' in data:
            type_name = data['type']
            r_type_obj, _ = ResourceType.objects.get_or_create(
                name__iexact=type_name,
                defaults={'name': type_name}
            )
            r.type = r_type_obj

        r.save()
        return JsonResponse({'message': 'Resource updated'})
    except Resource.DoesNotExist:
        return JsonResponse({'error': 'Resource not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['DELETE'])
def delete_resource(request: Request, resource_id: int) -> JsonResponse:
    """Delete an existing resource"""
    try:
        Resource.objects.get(id=resource_id).delete()
        return JsonResponse({'message': 'Resource deleted'})
    except Resource.DoesNotExist:
        return JsonResponse({'error': 'Resource not found'}, status=404)


@api_view(['GET'])
def get_resource_approximated_time(request: Request, resource_id:int) -> JsonResponse:
    """Get all processes a resource is used in"""
    try:
        processes = Process.objects.filter(resource__id=resource_id)
        res = []
        for processes in processes:
            res.append(processes.approximated_time)
        return JsonResponse({'approximated_times': res}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
