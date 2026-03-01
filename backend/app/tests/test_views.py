"""
Tests for API views
"""
import pytest
import json
from app.models import (
    Resource, ResourceType, Disruption, Worker
)

@pytest.mark.django_db
class TestOrderViews:
    """Test order API endpoints"""

    def test_get_orders_empty(self, api_client):
        """Test getting orders when none exist"""
        response = api_client.get('/api/order/get/')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_orders_with_data(self, api_client, order):
        """Test getting orders with existing data"""
        response = api_client.get('/api/order/get/')

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == 'Test Order'
        assert data[0]['target_amount'] == 100

    def test_get_single_order(self, api_client, order):
        """Test getting a single order by ID"""
        response = api_client.get(f'/api/order/get/{order.id}/')

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == order.id
        assert data['name'] == 'Test Order'

    def test_get_nonexistent_order(self, api_client):
        """Test getting an order that doesn't exist"""
        response = api_client.get('/api/order/get/99999/')

        assert response.status_code == 404
        data = response.json()
        assert 'error' in data

    def test_create_order(self, api_client):
        """Test creating a new order"""
        order_data = {
            'name': 'New Order',
            'target_amount': 200,
            'start_date': '2026-02-01 08:00:00',
            'end_date': '2026-02-28',
            'product_name': 'New Product',
            'status': 0,
            'priority': 1,
            'comments': 'New order comment',
            'process': []
        }

        response = api_client.post(
            '/api/order/post/',
            data=json.dumps(order_data),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = response.json()
        assert 'id' in data
        assert data['message'] == 'Order created successfully'

    def test_create_order_missing_fields(self, api_client):
        """Test creating order with missing required fields"""
        incomplete_data = {
            'name': 'Incomplete Order'
        }

        response = api_client.post(
            '/api/order/post/',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'error' in data

    def test_delete_order(self, api_client, order):
        """Test deleting an order"""
        order_id = order.id
        response = api_client.delete(f'/api/order/delete/{order_id}/')

        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Order deleted successfully'

        # Verify order was deleted
        from app.models import Order
        assert not Order.objects.filter(id=order_id).exists()

    def test_delete_nonexistent_order(self, api_client):
        """Test deleting an order that doesn't exist"""
        response = api_client.delete('/api/order/delete/99999/')

        assert response.status_code == 404


@pytest.mark.django_db
class TestProcessViews:
    """Test process timing API endpoints"""

    def test_update_process_timing(self, api_client, process):
        """Test updating process timing"""
        timing_data = {
            'setup_time_seconds': 600,
            'waiting_time_seconds': 240,
            'process_time_seconds': 3600
        }

        response = api_client.put(
            f'/api/process/timing/{process.id}/',
            data=json.dumps(timing_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.json()
        assert data['setup_time_seconds'] == 600
        assert data['waiting_time_seconds'] == 240
        assert data['process_time_seconds'] == 3600

    def test_update_nonexistent_process(self, api_client):
        """Test updating timing for non-existent process"""
        timing_data = {'setup_time_seconds': 600}

        response = api_client.put(
            '/api/process/timing/99999/',
            data=json.dumps(timing_data),
            content_type='application/json'
        )

        assert response.status_code == 404

    def test(self, api_client):
        pass


@pytest.mark.django_db
class TestFileUploadViews:
    """Test file upload API endpoints"""

    def test_upload_file(self, api_client, order, sample_file):
        """Test uploading a file"""
        response = api_client.post(
            '/api/files/upload',
            {
                'file': sample_file,
                'type': 'bom',
                'order_id': order.id
            },
            format='multipart'
        )

        assert response.status_code == 201
        data = response.json()
        assert data['file_name'] == 'test_file.pdf'
        assert data['file_type'] == 'bom'

    def test_upload_file_missing_order_id(self, api_client, sample_file):
        """Test uploading file without order_id"""
        response = api_client.post(
            '/api/files/upload',
            {
                'file': sample_file,
                'type': 'bom'
            },
            format='multipart'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'error' in data

    def test_delete_file(self, api_client, order, sample_file):
        """Test deleting a file"""
        from app.models import OrderFile
        order_file = OrderFile.objects.create(
            order=order,
            file=sample_file,
            file_type='bom'
        )

        response = api_client.delete(f'/api/files/{order_file.id}/delete')

        assert response.status_code == 200
        assert not OrderFile.objects.filter(id=order_file.id).exists()

    def test_list_order_files(self, api_client, order, sample_file):
        """Test listing files for an order"""
        from app.models import OrderFile
        OrderFile.objects.create(
            order=order,
            file=sample_file,
            file_type='bom'
        )

        response = api_client.get(f'/api/orders/{order.id}/files')

        assert response.status_code == 200
        data = response.json()
        assert 'files' in data
        assert len(data['files']) == 1


@pytest.mark.django_db
class TestWorkerViews:
    """Test worker API endpoints"""

    def test_get_workers_empty(self, api_client):
        response = api_client.get('/api/worker/get/')
        assert response.status_code == 200
        assert response.json() == []

    def test_get_workers_with_data(self, api_client, worker):
        response = api_client.get('/api/worker/get/')
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == "John Doe"

    def test_get_worker(self, api_client, worker):
        response = api_client.get(f'/api/worker/get/{worker.id}/')
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == worker.id
        assert data['name'] == "John Doe"

    def test_get_worker_not_found(self, api_client):
        response = api_client.get('/api/worker/get/9999/')
        assert response.status_code == 404
        assert 'error' in response.json()

    def test_create_worker(self, api_client):
        response = api_client.post('/api/worker/post/', {'name': 'Jane Doe'}, format='json')
        assert response.status_code == 201
        assert Worker.objects.filter(name='Jane Doe').exists()

    def test_create_worker_missing_name(self, api_client):
        response = api_client.post('/api/worker/post/', {}, format='json')
        assert response.status_code == 400

    def test_update_worker(self, api_client, worker):
        response = api_client.put(f'/api/worker/put/{worker.id}/', {'name': 'John Updated'}, format='json')
        assert response.status_code == 200
        worker.refresh_from_db()
        assert worker.name == 'John Updated'

    def test_update_worker_not_found(self, api_client):
        response = api_client.put('/api/worker/put/9999/', {'name': 'X'}, format='json')
        assert response.status_code == 404
        assert 'error' in response.json()

    def test_delete_worker(self, api_client, worker):
        response = api_client.delete(f'/api/worker/delete/{worker.id}/')
        assert response.status_code == 200
        assert not Worker.objects.filter(id=worker.id).exists()

    def test_delete_worker_not_found(self, api_client):
        response = api_client.delete('/api/worker/delete/9999/')
        assert response.status_code == 404


@pytest.mark.django_db
class TestResourceViews:
    """Test resource API endpoints"""

    def test_get_resources(self, api_client, resource):
        response = api_client.get('/api/resource/get/')
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == "Machine A"
        assert data[0]['status'] == 3

    def test_get_resources_empty(self, api_client):
        response = api_client.get('/api/resource/get/')
        assert response.status_code == 200
        assert response.json() == []

    def test_get_resource(self, api_client, resource):
        response = api_client.get(f'/api/resource/get/{resource.id}/')
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == resource.id
        assert data['name'] == "Machine A"
        assert data['status'] == 3

    def test_get_resource_not_found(self, api_client):
        response = api_client.get('/api/resource/get/9999/')
        assert response.status_code == 404
        assert 'error' in response.json()

    def test_create_resource(self, api_client, resource_type):
        payload = {'name': 'Machine B', 'type': 'Machine', 'status': 1}
        response = api_client.post('/api/resource/post/', payload, format='json')
        assert response.status_code == 201
        assert Resource.objects.filter(name='Machine B').exists()

    def test_create_resource_creates_new_type(self, api_client):
        payload = {'name': 'Robot A', 'type': 'Robot', 'status': 0}
        response = api_client.post('/api/resource/post/', payload, format='json')
        assert response.status_code == 201
        assert ResourceType.objects.filter(name='Robot').exists()

    def test_update_resource(self, api_client, resource):
        payload = {'name': 'Machine A Updated', 'status': 2}
        response = api_client.put(f'/api/resource/put/{resource.id}/', payload, format='json')
        assert response.status_code == 200
        resource.refresh_from_db()
        assert resource.name == 'Machine A Updated'
        assert resource.status == 2

    def test_update_resource_not_found(self, api_client):
        response = api_client.put('/api/resource/put/9999/', {'name': 'X'}, format='json')
        assert response.status_code == 404

    def test_delete_resource(self, api_client, resource):
        response = api_client.delete(f'/api/resource/delete/{resource.id}/')
        assert response.status_code == 200
        assert not Resource.objects.filter(id=resource.id).exists()

    def test_delete_resource_not_found(self, api_client):
        response = api_client.delete('/api/resource/delete/9999/')
        assert response.status_code == 404


@pytest.mark.django_db
class TestDisruptionViews:
    """Test disruption API endpoints"""

    def test_get_disruptions(self, api_client, disruption):
        response = api_client.get('/api/disruption/get/')
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == "Test Disruption"

    def test_get_disruptions_empty(self, api_client):
        response = api_client.get('/api/disruption/get/')
        assert response.status_code == 200
        assert response.json() == []

    def test_get_disruption(self, api_client, disruption):
        response = api_client.get(f'/api/disruption/get/{disruption.id}/')
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == disruption.id
        assert data['name'] == "Test Disruption"

    def test_get_disruption_not_found(self, api_client):
        response = api_client.get('/api/disruption/get/9999/')
        assert response.status_code == 404

    def test_get_disruption_types(self, api_client, disruption_type):
        response = api_client.get('/api/disruption-type/get/')
        assert response.status_code == 200
        data = response.json()
        names = [t['name'] for t in data]
        # should always include defaults
        assert 'Error' in names
        assert 'Maintenance' in names

    def test_create_disruption(self, api_client, disruption_type, resource):
        payload = {
            'name': 'New Disruption',
            'type': disruption_type.id,
            'resource': resource.id,
            'disruption_time': 3600,
        }
        response = api_client.post('/api/disruption/post/', payload, format='json')
        assert response.status_code == 201
        assert Disruption.objects.filter(name='New Disruption').exists()

    def test_create_disruption_calculates_duration(self, api_client, disruption_type, resource):
        payload = {
            'name': 'Timed Disruption',
            'type': disruption_type.id,
            'resource': resource.id,
            'disruption_time': 3600,
        }
        api_client.post('/api/disruption/post/', payload, format='json')
        d = Disruption.objects.get(name='Timed Disruption')
        assert d.disruption_time == 3600

    def test_update_disruption(self, api_client, disruption):
        payload = {'name': 'Updated Disruption'}
        response = api_client.put(f'/api/disruption/put/{disruption.id}/', payload, format='json')
        assert response.status_code == 200
        disruption.refresh_from_db()
        assert disruption.name == 'Updated Disruption'

    def test_update_disruption_not_found(self, api_client):
        response = api_client.put('/api/disruption/put/9999/', {'name': 'X'}, format='json')
        assert response.status_code == 404

    def test_delete_disruption(self, api_client, disruption):
        response = api_client.delete(f'/api/disruption/delete/{disruption.id}/')
        assert response.status_code == 200
        assert not Disruption.objects.filter(id=disruption.id).exists()

    def test_delete_disruption_not_found(self, api_client):
        response = api_client.delete('/api/disruption/delete/9999/')
        assert response.status_code == 404
