"""Script to generate test data for load testing"""
import os
import django
import sys
import random
from pathlib import Path
from app.models import Order, Process, Worker, Resource, ResourceType
from datetime import date, datetime, time, timedelta


# Add the parent directory to the path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def generate_test_orders(count=1000):
    """Generate test orders with associated data"""

    print(f"Generating {count} test orders...")

    # Create base data
    print("Creating base resources and workers...")

    # Resource types
    resource_types = []
    for rt_name in ["Machine", "Conveyor", "Assembly Station", "Quality Check"]:
        rt, _ = ResourceType.objects.get_or_create(name=rt_name)
        resource_types.append(rt)

    # Resources
    resources = []
    for i in range(20):
        resource, _ = Resource.objects.get_or_create(
            name=f"Resource-{i:03d}",
            defaults={
                'type': random.choice(resource_types),
                'status': random.choice(['Available', 'In Use', 'Maintenance'])
            }
        )
        resources.append(resource)

    # Workers
    workers = []
    worker_names = [
        "John", "Jane", "Mike", "Sarah", "Tom", "Lisa", "David", "Emma",
        "Chris", "Anna", "Paul", "Maria", "Steve", "Laura", "Kevin", "Sophie"
    ]
    for name in worker_names:
        worker, _ = Worker.objects.get_or_create(name=name)
        workers.append(worker)

    print(f"Created {len(resource_types)} resource types")
    print(f"Created {len(resources)} resources")
    print(f"Created {len(workers)} workers")

    # Product names
    products = [
        "Valve Assembly", "Motor Component", "Circuit Board", "Sensor Unit",
        "Control Panel", "Hydraulic Pump", "Gear Box", "Bearing Assembly",
        "Filter Housing", "Connector Module", "Switch Panel", "Power Supply",
        "Display Unit", "Actuator", "Encoder", "Transformer"
    ]

    # Status choices
    statuses = [0, 1, 2, 3]  # Planned, Running, Paused, Done
    priorities = [1, 2, 3]  # Low, Medium, High

    # Generate orders
    print(f"\nGenerating {count} orders...")
    orders_created = 0
    batch_size = 100

    start_date = date(2026, 1, 1)

    for i in range(count):
        # Random date range
        order_start = start_date + timedelta(days=random.randint(0, 365))
        order_end = order_start + timedelta(days=random.randint(1, 30))

        # Create order
        order = Order.objects.create(
            name=f"Order-{i:04d}",
            target_amount=random.randint(10, 1000),
            start_date=order_start,
            end_date=order_end,
            product_name=random.choice(products),
            priority=random.choice(priorities),
            status=random.choice(statuses),
            comments=f"Test order {i} - Generated for load testing"
        )

        # Create 1-3 processes for this order
        num_processes = random.randint(1, 3)
        for j in range(num_processes):
            process_start = datetime.combine(order_start, time(8, 0, 0)) + timedelta(days=j)
            process_end = process_start + timedelta(hours=random.randint(4, 12))

            process = Process.objects.create(
                start_time=process_start,
                end_time=process_end,
                work_time=time(random.randint(4, 8), 0, 0),
                setup_time=time(0, random.randint(15, 60), 0),
                setup_time_seconds=random.randint(900, 3600),
                waiting_time_seconds=random.randint(0, 1800),
                process_time_seconds=random.randint(3600, 14400)
            )

            # Add random workers
            num_workers = random.randint(1, 3)
            process.workers.add(*random.sample(workers, num_workers))

            # Link to order
            order.process.add(process)

        orders_created += 1

        # Progress indicator
        if (i + 1) % batch_size == 0:
            print(f"Created {i + 1}/{count} orders...")

    print(f"\n Successfully created {orders_created} orders with processes!")
    print(f"Total Orders in DB: {Order.objects.count()}")

def delete_test_orders():
    """Delete all test orders"""
    print("Deleting test orders...")

    # Count before deletion
    order_count = Order.objects.count()
    process_count = Process.objects.count()

    print(f"Found {order_count} orders and {process_count} processes")

    # Delete orders (cascades to ManyToMany relationships)
    deleted_orders, _ = Order.objects.all().delete()

    # Delete orphaned processes
    deleted_processes, _ = Process.objects.all().delete()

    print(f"Deleted {deleted_orders} orders")
    print(f"Deleted {deleted_processes} processes")
    print(f"Remaining orders: {Order.objects.count()}")

def show_stats():
    """Show database statistics"""
    print("\n" + "="*50)
    print("DATABASE STATISTICS")
    print("="*50)
    print(f"Orders:         {Order.objects.count():,}")
    print(f"Processes:      {Process.objects.count():,}")
    print(f"Workers:        {Worker.objects.count():,}")
    print(f"Resources:      {Resource.objects.count():,}")
    print(f"Resource Types: {ResourceType.objects.count():,}")
    print("="*50 + "\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generate or delete test data')
    parser.add_argument(
        'action',
        choices=['generate', 'delete', 'stats'],
        help='Action to perform'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=1000,
        help='Number of orders to generate (default: 1000)'
    )

    args = parser.parse_args()

    if args.action == 'generate':
        generate_test_orders(args.count)
        show_stats()
    elif args.action == 'delete':
        confirm = input("Are you sure you want to delete ALL orders? (yes/no): ")
        if confirm.lower() == 'yes':
            delete_test_orders()
            show_stats()
        else:
            print("Deletion cancelled.")
    elif args.action == 'stats':
        show_stats()