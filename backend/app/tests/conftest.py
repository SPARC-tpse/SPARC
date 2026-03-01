"""
Pytest fixtures and configuration for tests
"""
import pytest
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from app.models import (
    Order, Process, Worker, Resource, ResourceType,
    Disruption, DisruptionType, OrderFile
)
from datetime import date, datetime, time
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture
def api_client():
    """Provide an API client for making requests"""
    return APIClient()

@pytest.fixture
def resource_type(db):
    """Create a test resource type"""
    return ResourceType.objects.create(name="Machine")


@pytest.fixture
def resource(db, resource_type):
    """Create a test resource"""
    return Resource.objects.create(
        name="Machine A",
        type=resource_type,
        status=3
    )


@pytest.fixture
def disruption_type(db):
    """Create a test disruption type"""
    return DisruptionType.objects.create(name="Machine Error")


@pytest.fixture
def worker(db):
    """Create a test worker"""
    return Worker.objects.create(name="John Doe")

@pytest.fixture
def order(db):
    """Create a test order"""
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
    return order


@pytest.fixture
def process(db, worker, resource, order):
    """Create a test process"""
    process = Process.objects.create(
        name="Test Process",
        approximated_time=800,
        setup_time=300,
        waiting_time=120,
        resource=resource,
        order=order
    )
    process.workers.add(worker)
    return process


@pytest.fixture
def disruption(db, disruption_type, resource, process):
    """Create a test disruption"""
    return Disruption.objects.create(
        name="Test Disruption",
        type=disruption_type,
        process=process,
        resource=resource,
        disruption_time=100
    )


@pytest.fixture
def sample_file():
    """Create a sample file for upload tests"""
    return SimpleUploadedFile(
        "test_file.pdf",
        b"file_content",
        content_type="application/pdf"
    )
