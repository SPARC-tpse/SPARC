"""
Pytest fixtures and configuration for tests
"""
import pytest
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
        status="Available"
    )


@pytest.fixture
def worker(db):
    """Create a test worker"""
    return Worker.objects.create(name="John Doe")


@pytest.fixture
def process(db, worker):
    """Create a test process"""
    process = Process.objects.create(
        start_time=datetime(2026, 1, 1, 8, 0, 0),
        end_time=datetime(2026, 1, 1, 16, 0, 0),
        setup_time_seconds=300,
        waiting_time_seconds=120,
        process_time_seconds=1800
    )
    process.workers.add(worker)
    return process


@pytest.fixture
def order(db, process):
    """Create a test order"""
    order = Order.objects.create(
        name="Test Order",
        target_amount=100,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        product_name="Test Product",
        priority=2,
        status=0,  # Planned
        comments="Test comment"
    )
    order.process.add(process)
    return order


@pytest.fixture
def disruption_type(db):
    """Create a test disruption type"""
    return DisruptionType.objects.create(name="Machine Error")


@pytest.fixture
def disruption(db, disruption_type, resource, process):
    """Create a test disruption"""
    return Disruption.objects.create(
        name="Test Disruption",
        type=disruption_type,
        resource=resource,
        process=process,
        start_date=datetime(2026, 1, 15, 10, 0, 0),
        end_date=datetime(2026, 1, 15, 12, 0, 0)
    )


@pytest.fixture
def sample_file():
    """Create a sample file for upload tests"""
    return SimpleUploadedFile(
        "test_file.pdf",
        b"file_content",
        content_type="application/pdf"
    )
