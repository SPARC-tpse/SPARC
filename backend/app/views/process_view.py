from typing import Any

from django.http import JsonResponse, QueryDict
from rest_framework.decorators import api_view
from rest_framework.request import Request

from ..models import Part, Process
from ..serializers.part_serializer import PartSerializer
from ..serializers.process_serializer import ProcessSerializer


def _get_request_data(request: Request) -> tuple[dict[str, Any] | None, JsonResponse | None]:
    """Narrows request.data to a plain dict, or returns a 400 response."""
    if not isinstance(request.data, (dict, QueryDict)):
        return None, JsonResponse({'error': 'Invalid request body'}, status=400)
    data: dict[str, Any] = dict(request.data) if isinstance(request.data, QueryDict) else request.data
    return data, None


@api_view(['GET'])
def get_processes(request: Request) -> JsonResponse:
    """Get all processes"""
    try:
        processes = Process.objects.all()
        serializer = ProcessSerializer(processes, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False)
    except Process.DoesNotExist:
        return JsonResponse({'error': 'Process not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['PUT'])
@api_view(['PUT'])
def update_process_timing(request: Request, process_id: int) -> JsonResponse:
    """Update the timing of a process by ID"""
    data, err_response = _get_request_data(request)
    if err_response:
        return err_response

    assert data is not None

    updates: dict[str, int] = {}
    for field in ('setup_time', 'waiting_time'):
        if field in data:
            value = int(data[field])
            if value < 0:
                return JsonResponse({'error': f'{field} must not be negative'}, status=400)
            updates[field] = value

    if not updates:
        return JsonResponse({'error': 'No valid fields provided'}, status=400)

    updated = Process.objects.filter(id=process_id).update(**updates)
    if not updated:
        return JsonResponse({'error': 'Process not found'}, status=404)

    return JsonResponse({'message': 'Process timing updated successfully', **updates})


@api_view(['DELETE'])
def delete_process(request: Request, process_id: int) -> JsonResponse:
    """Delete a process by ID"""
    try:
        process = Process.objects.get(id=process_id)
        process.delete()
        return JsonResponse({'success': True, 'message': 'Process deleted'})
    except Process.DoesNotExist:
        return JsonResponse({'error': 'Process not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
def add_part(request: Request, process_id: int) -> JsonResponse:
    """Add a part to a process with the current process time"""
    data, err_response = _get_request_data(request)
    if err_response:
        return err_response
    assert data is not None

    try:
        process = Process.objects.get(id=process_id)
        process_time = data.get('process_time', 0)
        part = Part.objects.create(
            process=process,
            process_time=process_time
        )
        part.save()
        serializer = PartSerializer(part, many=False)
        return JsonResponse(serializer.data, status=201)
    except Process.DoesNotExist:
        return JsonResponse({'error': 'Process not found'}, status=404)
    except Exception as e:
        print(f"Add part error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
def get_parts(request: Request, process_id: int) -> JsonResponse:
    """Get all parts for a process"""
    try:
        parts = Part.objects.filter(process=process_id)
        serializer = PartSerializer(parts, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Part.DoesNotExist:
        return JsonResponse({'error': 'Part not found'}, status=404)
    except Exception as e:
        print(e, flush=True)
        return JsonResponse({'error': 'Failed to retrieve orders'}, status=500)
