# SPARC

SPARC (Smart Planning and Resource Control) is a web application that allows the users to enter production steps and manage resources, such as personnel and machinery.

> [!IMPORTANT]
> This project is only planed for use in a private network!

## Developer setup

### Envirment

create a file ./.env with following fileds (replace the default user and password!)
```.env
# DJANGO SETTINGS
DJANGO_SECRET_KEY=replace-with-random-string
DEBUG=False
# Space-separated list of IPs/domains (e.g., 192.168.1.50 localhost)
ALLOWED_HOSTS=192.168.178.59 localhost 127.0.0.1
CSRF_TRUSTED_ORIGINS=http://192.168.178.59 http://localhost:3000

# DATABASE SETTINGS (Postgres)
POSTGRES_DB=django_db
POSTGRES_USER=db_admin
POSTGRES_PASSWORD=choose_a_strong_password
DB_HOST=db
DB_PORT=5432

# FRONTEND SETTINGS (Nuxt)
NUXT_PUBLIC_API_BASE=http://192.168.178.59/api

# REDIS SETTINGS (For Channels)
REDIS_URL=redis://redis:6379/0
```

### Backend

Follow the Developer setup in the backend [README](./backend/README.md).

### Frontend

Follow the Developer setup in the frontend [README](./frontend/README.md).


## Run

### Development

1. build and run the docker container
```bash
sudo docker compose up --build
```

2. run migrations (Do not forget!!!)
```bash
sudo docker compose exec backend .venv/bin/python manage.py makemigrations

sudo docker compose exec backend .venv/bin/python manage.py migrate
```

3. create super user
```bash
sudo docker compose exec backend .venv/bin/python manage.py collectstatic --noinput

sudo docker compose exec backend .venv/bin/python manage.py createsuperuser
```

### Production

1. open your firewall at port 3000 and 8000
```bash
sudo ufw allow 3000
sudo ufw allow 8000
sudo ufw allow enable
```

2. install docker on server\
https://docs.docker.com/engine/install/ubuntu/

3. download sparc
```bash
chmod +x download_sparc.sh
./download_sparc.sh
```

4. run the init script (run_server.sh will be downloaded by download_sparc)
```bash
./run_server.sh
```

## Tests

### Backend

Follow the Tests section in the backend [README](./backend/README.md).

### Frontend

Follow the Tests section in the frontend [README](./frontend/README.md).

## Reset all data

```bash
sudo docker volume rm sparc_pgdata
sudo docker compose up -d
sudo docker compose exec backend python manage.py createsuperuser
```

## Project Structure

`tree -I 'node_modules*|staticfiles*|htmlcov*|media*|__pycache__*|migrations*' --dirsfirst`
```
SPARC
├── backend
│   ├── app
│   │   ├── consumers
│   │   │   ├── disruption_consumer.py
│   │   │   ├── __init__.py
│   │   │   ├── order_consumer.py
│   │   │   ├── resource_consumer.py
│   │   │   └── worker_consumer.py
│   │   ├── serializers
│   │   │   ├── disruption_serializer.py
│   │   │   ├── disruption_type_serializer.py
│   │   │   ├── __init__.py
│   │   │   ├── order_file_serializer.py
│   │   │   ├── order_serializer.py
│   │   │   ├── part_serializer.py
│   │   │   ├── process_serializer.py
│   │   │   ├── resource_serializer.py
│   │   │   ├── resource_type_serializer.py
│   │   │   └── worker_serializer.py
│   │   ├── tests
│   │   │   ├── conftest.py
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py
│   │   │   └── test_views.py
│   │   ├── views
│   │   │   ├── disruption_view.py
│   │   │   ├── __init__.py
│   │   │   ├── order_file_view.py
│   │   │   ├── order_view.py
│   │   │   ├── process_view.py
│   │   │   ├── resource_view.py
│   │   │   └── worker_view.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routing.py
│   │   └── urls.py
│   ├── config
│   │   ├── asgi.py
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── urls.py
│   ├── scripts
│   │   └── generate_test_data.py
│   ├── Dockerfile
│   ├── main.py
│   ├── manage.py
│   ├── pyproject.toml
│   ├── pytest.ini
│   ├── README.md
│   └── uv.lock
├── frontend
│   ├── app
│   │   ├── assets
│   │   │   └── css
│   │   │       └── tailwind.css
│   │   ├── components
│   │   │   ├── widgets
│   │   │   │   ├── DashboardWidget.vue
│   │   │   │   ├── DisruptionsWidget.vue
│   │   │   │   ├── GanttWidget.vue
│   │   │   │   ├── KPIWidget.vue
│   │   │   │   ├── OrderGanttWidget.vue
│   │   │   │   ├── OrdersWidget.vue
│   │   │   │   ├── ProcessGanttWidget.vue
│   │   │   │   ├── ResourceGanttWidget.vue
│   │   │   │   └── ResourcesWidget.vue
│   │   │   ├── DashboardAddPanel.vue
│   │   │   ├── DashboardGrid.vue
│   │   │   ├── DisruptionTimerPopout.vue
│   │   │   ├── FileUpload.vue
│   │   │   ├── MultiSelect.vue
│   │   │   ├── Navbar.vue
│   │   │   ├── ProcessTimer.vue
│   │   │   ├── Topbar.vue
│   │   │   └── WorkerMultiSelect.vue
│   │   ├── composables
│   │   │   ├── useAppTheme.js
│   │   │   ├── useDashboardData.ts
│   │   │   ├── useDashboardLayout.ts
│   │   │   ├── useDisruptionDraft.ts
│   │   │   ├── useDisruptionTimer.ts
│   │   │   ├── useOrderDraft.ts
│   │   │   ├── useOrderWebSocket.js
│   │   │   ├── useResourceDraft.ts
│   │   │   ├── useTheme.js
│   │   │   ├── useWorkerDraft.ts
│   │   │   └── useZoom.ts
│   │   ├── layouts
│   │   │   └── custom.vue
│   │   ├── pages
│   │   │   ├── dashboard
│   │   │   │   ├── gantt
│   │   │   │   │   └── [id].vue
│   │   │   │   ├── index.vue
│   │   │   │   └── old.vue
│   │   │   ├── disruption
│   │   │   │   ├── edit
│   │   │   │   │   └── [id].vue
│   │   │   │   ├── index.vue
│   │   │   │   ├── new.vue
│   │   │   │   └── overview.vue
│   │   │   ├── order
│   │   │   │   ├── edit
│   │   │   │   │   └── [id].vue
│   │   │   │   ├── index.vue
│   │   │   │   ├── new.vue
│   │   │   │   └── overview.vue
│   │   │   ├── resource
│   │   │   │   ├── edit
│   │   │   │   │   └── [id].vue
│   │   │   │   ├── index.vue
│   │   │   │   ├── new.vue
│   │   │   │   └── overview.vue
│   │   │   ├── worker
│   │   │   │   ├── edit
│   │   │   │   │   └── [id].vue
│   │   │   │   ├── index.vue
│   │   │   │   ├── new.vue
│   │   │   │   └── overview.vue
│   │   │   └── index.vue
│   │   └── app.vue
│   ├── public
│   │   ├── favicon.ico
│   │   └── robots.txt
│   ├── Dockerfile
│   ├── nuxt.config.ts
│   ├── package.json
│   ├── package-lock.json
│   ├── postcss.config.cjs
│   ├── README.md
│   ├── tailwind.config.cjs
│   └── tsconfig.json
├── nginx
│   └── default.conf
├── CHANGELOG
├── docker-compose.prod.yml
├── docker-compose.yml
├── download_sparc.sh
├── LICENSE
├── manuel_tests.md
├── package-lock.json
├── README.md
└── run_server.sh
```
