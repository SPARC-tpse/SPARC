# SPARC Backend

## Developer setup

Prerequisites:
- uv
- python >= 3.12

steps:
1. create the virtual envirment:
```bash
uv venv
```

2. download the dependencies in pyproject.toml:
```bash
uv sync
```

## Run

### without Docker

```bash
uv run daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

### Docker

development:\
```bash
sudo docker build --target development -t sparc:dev .
sudo docker run -it -p 8000:8000 -v $(pwd):/app sparc:dev
```

production:\
```bash
sudo docker build --target production -t sparc:prod .
sudo docker run -it -p 8000:8000 --env-file .env sparc:prod
```

## Tests

### Run

#### Dev

```bash
uv run pytest
```
or if you want to run a specific test (e.g.: test_models):\
```bash
uv run pytest app/tests/test_models.py
```

#### Docker

```bash
sudo docker compose exec backend pytest
```
or if you want to run a specific test (e.g.: test_models):\
```bash
sudo docker compose exec backend pytest app/tests/test_models.py
```

### add test

1. Go into the ./app/tests/ folder.
2. if you want to add a view test open test_views.py or if you want to test for a model open test_models.py

## Project Structure

`tree -I "staticfiles|.venv|media|__pycache__" --dirsfirst`
```
.
├── app
│   ├── admin.py
│   ├── apps.py
│   ├── consumers
│   │   ├── disruption_consumer.py
│   │   ├── __init__.py
│   │   ├── order_consumer.py
│   │   ├── resource_consumer.py
│   │   └── worker_consumer.py
│   ├── __init__.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_process_name_process_resource_and_more.py
│   │   ├── 0003_disruption_process.py
│   │   ├── 0004_remove_disruption_end_date_and_more.py
│   │   ├── 0005_rename_process_order_processes_and_more.py
│   │   ├── 0006_remove_order_bill_of_materials_remove_order_files_and_more.py
│   │   ├── 0007_remove_disruption_duration_remove_order_processes_and_more.py
│   │   ├── 0008_alter_order_order_number.py
│   │   └── __init__.py
│   ├── models.py
│   ├── routing.py
│   ├── serializers
│   │   ├── disruption_serializer.py
│   │   ├── disruption_type_serializer.py
│   │   ├── __init__.py
│   │   ├── order_file_serializer.py
│   │   ├── order_serializer.py
│   │   ├── part_serializer.py
│   │   ├── process_serializer.py
│   │   ├── resource_serializer.py
│   │   ├── resource_type_serializer.py
│   │   └── worker_serializer.py
│   ├── tests
│   │   ├── conftest.py
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   └── test_views.py
│   ├── urls.py
│   └── views
│       ├── disruption_view.py
│       ├── __init__.py
│       ├── order_file_view.py
│       ├── order_view.py
│       ├── process_view.py
│       ├── resource_view.py
│       └── worker_view.py
├── config
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   └── urls.py
├── Dockerfile
├── main.py
├── manage.py
├── pyproject.toml
├── pytest.ini
├── README.md
├── scripts
│   └── generate_test_data.py
└── uv.lock
```
