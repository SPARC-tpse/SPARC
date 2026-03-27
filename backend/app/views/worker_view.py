from typing import Any, cast

from django.http import JsonResponse, QueryDict
from rest_framework.decorators import api_view
from rest_framework.request import Request

from ..models import Worker
from ..serializers.worker_serializer import WorkerSerializer
from . import broadcast_db_change


def _get_request_data(request: Request) -> tuple[dict[str, Any] | None, JsonResponse | None]:
    """Narrows request.data to a plain dict, or returns a 400 response."""
    if not isinstance(request.data, (dict, QueryDict)):
        return None, JsonResponse({'error': 'Invalid request body'}, status=400)
    data: dict[str, Any] = dict(request.data) if isinstance(request.data, QueryDict) else request.data
    return data, None


@api_view(['GET'])
def get_workers(request: Request) -> JsonResponse:
    """Get all workers"""
    try:
        workers = Worker.objects.all()
        serializer = WorkerSerializer(workers, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['DELETE'])
def delete_worker(request: Request, worker_id: int) -> JsonResponse:
    """Delete a worker by ID"""
    try:
        Worker.objects.get(id=worker_id).delete()
        return JsonResponse({'success': True, 'message': 'Worker deleted'})
    except Worker.DoesNotExist:
        return JsonResponse({'error': 'Worker not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
def create_worker(request: Request) -> JsonResponse:
    """Create a new worker"""
    try:
        serializer = WorkerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        broadcast_db_change('worker', 'created', cast(dict[str, Any], serializer.data))
        return JsonResponse(serializer.errors, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
def get_worker(request: Request, worker_id: int) -> JsonResponse:
    """Get a single worker by ID"""
    try:
        worker = Worker.objects.get(id=worker_id)
        serializer = WorkerSerializer(worker, many=False)
        return JsonResponse(serializer.data, safe=False)
    except Worker.DoesNotExist:
        return JsonResponse({'error': 'Worker not found'}, status=404)


@api_view(['PUT'])
def update_worker(request: Request, worker_id: int) -> JsonResponse:
    """Update an existing worker"""
    data, err_response = _get_request_data(request)
    if err_response:
        return err_response
    assert data is not None

    try:
        worker = Worker.objects.get(id=worker_id)
        worker.name = data.get('name', worker.name)
        worker.save()
        return JsonResponse({'message': 'Worker updated successfully', 'id': worker.id, 'name': worker.name})
    except Worker.DoesNotExist:
        return JsonResponse({'error': 'Worker not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
