"""
Tests for API views
"""
import pytest
import json

@pytest.mark.django_db
class TestOrderViews:
    """Test order API endpoints"""

    def test_get_orders_empty(self, api_client):
        """Test getting orders when none exist"""
        response = api_client.get('/api/orders/get')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_orders_with_data(self, api_client, order):
        """Test getting orders with existing data"""
        response = api_client.get('/api/orders/get')

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == 'Test Order'
        assert data[0]['target_amount'] == 100

    def test_get_single_order(self, api_client, order):
        """Test getting a single order by ID"""
        response = api_client.get(f'/api/orders/get/{order.id}/')

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == order.id
        assert data['name'] == 'Test Order'

    def test_get_nonexistent_order(self, api_client):
        """Test getting an order that doesn't exist"""
        response = api_client.get('/api/orders/get/99999/')

        assert response.status_code == 404
        data = response.json()
        assert 'error' in data

    def test_create_order(self, api_client):
        """Test creating a new order"""
        order_data = {
            'name': 'New Order',
            'target': 200,
            'start': '2026-02-01',
            'end': '2026-02-28',
            'product': 'New Product',
            'status': 'Planned',
            'priority': 'High',
            'comments': 'New order comment'
        }

        response = api_client.post(
            '/api/orders/post',
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
            '/api/orders/post',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'error' in data

    def test_delete_order(self, api_client, order):
        """Test deleting an order"""
        order_id = order.id
        response = api_client.delete(f'/api/orders/delete/{order_id}/')

        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Order deleted successfully'

        # Verify order was deleted
        from app.models import Order
        assert not Order.objects.filter(id=order_id).exists()

    def test_delete_nonexistent_order(self, api_client):
        """Test deleting an order that doesn't exist"""
        response = api_client.delete('/api/orders/delete/99999/')

        assert response.status_code == 404


@pytest.mark.django_db
class TestProcessTimingViews:
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


class TestWorkerViews:
    """Test worker API endpoints"""
    def test_get_workers_empty(self, api_client, worker):
        """Test getting workers for an empty list"""
        response = api_client.get(f'/api/workers/')

    def test_get_workers_with_data(self, api_client, worker):
        """Test getting workers with data"""

    def test_get_worker_empty(self, api_client, worker):
        """Test getting workers for an empty list"""

    def test_get_worker_with_data(self, api_client, worker):
        """Test getting workers with data"""

    def test_create_worker(self, api_client, worker):
        """Test creating a worker"""

    def test_create_worker_wrong_input_type(self, api_client, worker):
        """Test creating workers with wrong input type"""

    def test_delete_worker(self, api_client, worker):
        """Test deleting a worker"""

    def test_delete_non_existent_worker(self, api_client, worker):
        """Test deleting a worker that doesn't exist"""


#class TestResourceViews:
#    """Test resource API endpoints"""


#class TestDisruptionViews:
#    """Test disruption API endpoints"""

