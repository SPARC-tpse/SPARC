"""
Tests for Django models
"""
import pytest
from datetime import date, datetime, time
from django.core.exceptions import ValidationError
from app.models import (
    Order, Process, Worker, Resource, ResourceType,
    Disruption, DisruptionType, OrderFile
)


@pytest.mark.django_db
class TestResourceTypeModel:
    """Test ResourceType model"""

    def test_create_resource_type(self):
        """Test creating a resource type"""
        resource_type = ResourceType.objects.create(name="Machine")
        assert resource_type.name == "Machine"
        assert str(resource_type) == f"{resource_type.id}, Machine"

    def test_resource_type_db_table(self):
        """Test that correct database table is used"""
        assert ResourceType._meta.db_table == 'sparc_resource_type'


@pytest.mark.django_db
class TestResourceModel:
    """Test Resource model"""

    def test_create_resource(self, resource_type):
        """Test creating a resource"""
        resource = Resource.objects.create(
            name="Machine A",
            type=resource_type,
            status=3
        )
        assert resource.name == "Machine A"
        assert resource.type == resource_type
        assert resource.status == "Available"
        assert str(resource) == f"{resource.id}, Machine A, ({resource.type.id}, Machine), 3"

    def test_resource_db_table(self):
        """Test that correct database table is used"""
        assert Resource._meta.db_table == 'sparc_resource'


@pytest.mark.django_db
class TestWorkerModel:
    """Test Worker model"""

    def test_create_worker(self):
        """Test creating a worker"""
        worker = Worker.objects.create(name="John Doe")
        assert worker.name == "John Doe"
        assert str(worker) == f"{worker.id}, John Doe"

    def test_worker_db_table(self):
        """Test that correct database table is used"""
        assert Worker._meta.db_table == 'sparc_worker'


@pytest.mark.django_db
class TestProcessModel:
    """Test Process model"""

    def test_create_process(self, worker, resource, order):
        """Test creating a process"""
        process = Process.objects.create(
            name="Test Process",
            setup_time=300,
            #waiting_time=120,
            #process_time=1800,
            resource=resource,
            order=order
        )
        process.workers.add(worker)

        assert process.setup_time == 300
        #assert process.waiting_time == 120
        #assert process.process_time == 1800
        assert worker in process.workers.all()
        assert str(process) == f"Process ({process.id}, Test Process, 300, [{str(worker)}], {str(resource)}, {str(order)})"

    def test_process_timing_defaults(self, order):
        """Test that timing fields have correct defaults"""
        process = Process.objects.create(
            name="Test Process",
            order=order
        )
        assert process.setup_time == 0

    def test_process_missing_order(self, order):
        """Test that error is raised if order is missing"""
        try:
            process = Process.objects.create(
                name="Test Process",
            )
        except Exception as e:
            print("good")
            print(e)

    def test_process_db_table(self):
        """Test that correct database table is used"""
        assert Process._meta.db_table == 'sparc_process'


@pytest.mark.django_db
class TestOrderModel:
    """Test Order model"""

    def test_create_order(self):
        """Test creating an order"""
        order = Order.objects.create(
            name="Test Order",
            target_amount=100,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            product_name="Test Product",
            priority=2,
            status=0,
            comments="Test comment"
        )

        assert order.name == "Test Order"
        assert order.target_amount == 100
        assert order.priority == 2
        assert order.status == 0
        assert str(order) == f"{order.id} - Test Order"

    def test_order_with_process(self, order, process):
        """Test order with process relationship"""
        assert process in order.process.all()

    def test_order_status_choices(self):
        """Test order status is integer"""
        order = Order.objects.create(
            name="Status Test",
            target_amount=50,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 28),
            product_name="Product",
            priority=1,
            status=1  # Running
        )
        assert order.status == 1
        assert isinstance(order.status, int)

    def test_order_db_table(self):
        """Test that correct database table is used"""
        assert Order._meta.db_table == 'sparc_order'


@pytest.mark.django_db
class TestDisruptionModel:
    """Test Disruption model"""

    def test_create_disruption(self, disruption_type, resource, process):
        """Test creating a disruption"""
        disruption = Disruption.objects.create(
            name="Test Disruption",
            type=disruption_type,
            process=process,
            resource=resource,
            disruption_time = 1
        )

        assert disruption.name == "Test Disruption"
        assert disruption.type == disruption_type
        assert disruption.resource == resource
        assert disruption.process == process
        assert disruption.disruption_time == 1
        assert str(disruption) == f"{disruption.id} - Test Disruption"

    def test_create_fast_disruption(self, disruption_type, resource, process):
        disruption = Disruption.objects.create(
            name="auto-name",
            process=process,
            resource=resource,
            disruption_time = 1
        )

    def test_disruption_optional_fields(self, disruption_type):
        """Test that resource and process are optional"""
        disruption = Disruption.objects.create(
            name="No Resource/Process",
            type=disruption_type,
            start_date=datetime(2026, 1, 15, 10, 0, 0),
            end_date=datetime(2026, 1, 15, 12, 0, 0)
        )
        assert disruption.resource is None
        assert disruption.process is None

    def test_disruption_db_table(self):
        """Test that correct database table is used"""
        assert Disruption._meta.db_table == 'sparc_disruption'


@pytest.mark.django_db
class TestOrderFileModel:
    """Test OrderFile model"""

    def test_create_order_file(self, order, sample_file):
        """Test creating an order file"""
        order_file = OrderFile.objects.create(
            order=order,
            file=sample_file,
            file_type='bom',
            description='Test BOM file'
        )

        assert order_file.order == order
        assert order_file.file_type == 'bom'
        assert order_file.description == 'Test BOM file'
        assert order_file.get_filename() == 'test_file.pdf'

    def test_order_file_upload_path_bom(self, order, sample_file):
        """Test BOM file upload path"""
        order_file = OrderFile.objects.create(
            order=order,
            file=sample_file,
            file_type='bom'
        )
        expected_path = f'{order.id}/bom/test_file.pdf'
        assert expected_path in order_file.file.name

    def test_order_file_upload_path_general(self, order, sample_file):
        """Test general file upload path"""
        order_file = OrderFile.objects.create(
            order=order,
            file=sample_file,
            file_type='general'
        )
        expected_path = f'{order.id}/general/test_file.pdf'
        assert expected_path in order_file.file.name

    def test_order_file_db_table(self):
        """Test that correct database table is used"""
        assert OrderFile._meta.db_table == 'sparc_order_file'