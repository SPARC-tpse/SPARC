"""
Tests for Django models
"""
import pytest
from datetime import date, datetime, time
from django.utils import timezone
from django.core.exceptions import ValidationError
from app.models import (
    Order, Process, Worker, Resource, ResourceType,
    Disruption, DisruptionType, OrderFile, Part
)


@pytest.mark.django_db
class TestResourceTypeModel:
    """Test ResourceType model"""

    def test_create_resource_type(self):
        """Test creating a resource type"""
        resource_type = ResourceType.objects.create(name="Machine")
        assert resource_type.name == "Machine"
        assert str(resource_type) == f"ResourceType (id: {resource_type.id}, name: Machine)"

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
        assert resource.status == 3
        assert str(resource) == f"Resource (id: {resource.id}, name: Machine A, type: ResourceType (id: {resource.type.id}, name: Machine), status: 3)"

    def test_resource_db_table(self):
        """Test that correct database table is used"""
        assert Resource._meta.db_table == 'sparc_resource'


@pytest.mark.django_db
class TestDisruptionTypeModel:
    """Test DisruptionType model"""

    def test_create_disruption_type(self):
        """Test creating a disruption type"""
        disruption_type = DisruptionType.objects.create(name="Machine Error")
        assert disruption_type.name == "Machine Error"
        assert str(disruption_type) == f"DisruptionType (id: {disruption_type.id}, name: Machine Error)"

    def test_disruption_type_db_table(self):
        """Test that correct database table is used"""
        assert DisruptionType._meta.db_table == 'sparc_disruption_type'


@pytest.mark.django_db
class TestWorkerModel:
    """Test Worker model"""

    def test_create_worker(self):
        """Test creating a worker"""
        worker = Worker.objects.create(name="John Doe")
        assert worker.name == "John Doe"
        assert str(worker) == f"Worker (id: {worker.id}, name: John Doe)"

    def test_worker_db_table(self):
        """Test that correct database table is used"""
        assert Worker._meta.db_table == 'sparc_worker'


@pytest.mark.django_db
class TestOrderModel:
    """Test Order model"""

    def test_create_order(self):
        """Test creating an order"""
        order = Order.objects.create(
            name="Test Order",
            order_number="28022026001",
            target_amount=100,
            start_date=timezone.make_aware(datetime(2026, 1, 1, 8, 0, 0)),
            end_date=date(2026, 1, 31),
            product_name="Test Product",
            priority=1,
            status=0,
            comments="Test comment"
        )

        assert order.name == "Test Order"
        assert order.order_number == "28022026001"
        assert order.target_amount == 100
        assert order.priority == 1
        assert order.status == 0
        assert str(order) == f"Order (id: {order.id}, name: Test Order, order_number: 28022026001, target_amount: 100, start_date: 2026-01-01 08:00:00+01:00, end_date: 2026-01-31, product_name: Test Product, priority: 1, status: 0)"

    def test_order_db_table(self):
        """Test that correct database table is used"""
        assert Order._meta.db_table == 'sparc_order'


@pytest.mark.django_db
class TestProcessModel:
    """Test Process model"""

    def test_create_process(self, worker, resource, order):
        """Test creating a process"""
        process = Process.objects.create(
            name="Test Process",
            approximated_time=800,
            setup_time=300,
            waiting_time=120,
            resource=resource,
            order=order
        )
        process.workers.add(worker)

        assert process.setup_time == 300
        assert process.waiting_time == 120
        assert worker in process.workers.all()
        assert str(process) == f"Process (id: {process.id}, name: Test Process, setup_time: 300, waiting_time: 120, approximated_time: 800, workers: [{str(worker)}], resource: {str(resource)}, order: {str(order)})"

    def test_process_timing_defaults(self, order):
        """Test that timing fields have correct defaults"""
        process = Process.objects.create(
            name="Test Process",
            order=order
        )
        assert process.approximated_time == 0
        assert process.setup_time == 0
        assert process.waiting_time == 0

    def test_process_missing_order(self, order):
        """Test that error is raised if order is missing"""
        with pytest.raises(Exception):
            Process.objects.create(
                name="Test Process",
            )

    def test_process_db_table(self):
        """Test that correct database table is used"""
        assert Process._meta.db_table == 'sparc_process'


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
            disruption_time = 100
        )

        assert disruption.name == "Test Disruption"
        assert disruption.type == disruption_type
        assert disruption.process == process
        assert disruption.resource == resource
        assert disruption.disruption_time == 100
        assert str(disruption) == f"Disruption (id: {disruption.id}, name: Test Disruption, type: {disruption.type}, process: {disruption.process}, resource: {disruption.resource}, disruption_time: 100)"

    def test_disruption_optional_fields(self, disruption_type):
        """Test that resource and process are optional"""
        disruption = Disruption.objects.create(
            name="No Resource/Process",
            type=disruption_type,
        )
        assert disruption.resource is None
        assert disruption.process is None
        assert disruption.disruption_time == 0

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
            file_type='bom'
        )

        assert order_file.order == order
        assert order_file.file_type == 'bom'
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


@pytest.mark.django_db
class TestPartModel:
    """Test Part model"""
    def test_create_part(self, process):
        """Test creating a part"""
        part = Part.objects.create(
            process=process,
            process_time=100
        )
        assert part.process_time == 100

    def test_part_missing_process(self):
        """Test that error is raised if order is missing"""
        with pytest.raises(Exception):
            Part.objects.create()

    def test_part_db_table(self):
        """Test that correct database table is used"""
        assert Part._meta.db_table == 'sparc_part'