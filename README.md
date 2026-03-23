# SPARC

SPARC (Smart Planning and Resource Control) is a web application that allows the users to enter production steps and manage resources, such as personnel and machinery.

> [!IMPORTANT]
> This project is only planed for use in a private network!

## Developer setup

### IDE

if you use zed as IDE there is a ./.zed/settings.json conofig file

dev setup for PyCharm (You will  need PyCharm Pro if you want nuxt support):
```bash
sudo docker compose up -d frontend
```
```bash
sudo docker exec -it nuxt-frontend npm install
```
```bash
sudo docker exec -it nuxt-frontend npx nuxi prepare
```
```bash
sudo chown -R $USER:$USER ~/Documents/GitHub/SPARC/frontend/node_modules
```
```bash
sudo chown -R $USER:$USER ~/Documents/GitHub/SPARC/frontend/.nuxt
```

### envirment

create a file ./.env with following fileds (replace the default user and password!)
```.env
# --- DJANGO SETTINGS ---
# Generate a new one with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
DJANGO_SECRET_KEY=your-super-secret-random-string-here
DEBUG=False
# Space-separated list of IPs/domains (e.g., 192.168.1.50 localhost)
ALLOWED_HOSTS=192.168.178.59 localhost 127.0.0.1
CSRF_TRUSTED_ORIGINS=http://192.168.178.59 http://localhost:3000

# --- DATABASE SETTINGS (Postgres) ---
POSTGRES_DB=django_db
POSTGRES_USER=db_admin
POSTGRES_PASSWORD=choose_a_strong_password
DB_HOST=db
DB_PORT=5432

# --- FRONTEND SETTINGS (Nuxt) ---
# This is what the USER'S browser will use to call the API
NUXT_PUBLIC_API_BASE=http://192.168.178.59/api

# --- REDIS SETTINGS (For Channels) ---
REDIS_URL=redis://redis:6379/0
```

### backend

follow the [README](./backend/README.md) in ./backend

### frontend

follow the [README](./frontend/README.md) in ./frontend


## Run

### Development

```bash
sudo docker compose up --build
```

migrations:

```bash
sudo docker compose exec backend python manage.py makemigrations
```
```bash
sudo docker compose exec backend python manage.py migrate
```

create super user:
```bash
sudo docker compose exec backend python manage.py collectstatic --noinput
```
```bash
sudo docker compose exec backend python manage.py createsuperuser
```

### Production

open your firewall at port 3000 and 8000:\
`u allow 3000`

install docker on server:
https://docs.docker.com/engine/install/ubuntu/


## run tests

### backend

look in the backend [README](./backend/README.md#run)

### frontend


## reset all data

`sudo docker volume rm sparc_pgdata`\
`sudo docker compose up -d`\
`sudo docker compose exec backend python manage.py createsuperuser`

## Package manager

- pip (v25.3)
- npm (v10.9.3)

## Dependencies

- nuxt                (v4.2.1)
- vue                 (v3.5.24)
- vue-router          (v4.6.3)
- uvcorn              (v0.38.0)
- django              (v5.2.8)
- djangorestframework (v3.16.1)
- PostgreSQL          (v18.0)
- nginx               (v)

## Project Structure

`tree -I 'node_modules*|staticfiles*|htmlcov*|media*|__pycache__*|migrations*' --dirsfirst`
```
SPARC
├── backend                             |
│   ├── app                             |
│   │   ├── tests                       |
│   │   │   ├── __init__.py             |
│   │   │   ├── test_config.py          |
│   │   │   ├── test_models.py          |
│   │   │   └── test_views.py           |
│   │   ├── admin.py                    | what is visible in admin view
│   │   ├── apps.py                     |
│   │   ├── consumers.py                |
│   │   ├── __init__.py                 |
│   │   ├── models.py                   | definition of all Entety of the ER diagram
│   │   ├── routing.py                  |
│   │   ├── serializers.py              | serilizer definitions of the models
│   │   ├── urls.py                     | urls for the api
│   │   └── views.py                    | definitions of api functions
│   ├── config                          |
│   │   ├── asgi.py                     |
│   │   ├── __init__.py                 |
│   │   ├── settings.py                 |
│   │   ├── urls.py                     |
│   │   └── wsgi.py                     |
│   ├── scripts                         |
│   │   └── generate_test_data.py       |
│   ├── Dockerfile                      |
│   ├── manage.py                       |
│   ├── pytest.ini                      |
│   └── requirements.txt                |
├── frontend                            |
│   ├── app                             |
│   │   ├── assets                      |
│   │   │   └── css                     |
│   │   │       └── tailwind.css        |
│   │   ├── components                  |
│   │   │   ├── FileUpload.vue          |
│   │   │   ├── Navbar.vue              | navbar with the diffrent views as buttons
│   │   │   ├── ProcessTimer.vue        | topbar with title and submit button
│   │   │   ├── Topbar.vue              |
│   │   │   └── WorkerMultiSelect.vue   |
│   │   ├── composables                 |
│   │   │   ├── useAppTheme.js          |
│   │   │   ├── useDisruptionDraft.ts   |
│   │   │   ├── useDisruptionTimer.ts   |
│   │   │   ├── useTheme.js             |
│   │   │   └── useWebSocket.js         | handels connection to the websocket and passes msgs on to page
│   │   ├── layouts                     |
│   │   │   └── custom.vue              |
│   │   ├── pages                       |
│   │   │   ├── disruption              |
│   │   │   │   ├── edit                |
│   │   │   │   │   └── [id].vue        |
│   │   │   │   ├── index.vue           |
│   │   │   │   ├── new.vue             |
│   │   │   │   └── overview.vue        |
│   │   │   ├── order                   |
│   │   │   │   ├── edit                |
│   │   │   │   │   └── [id].vue        |
│   │   │   │   ├── process-steps       |
│   │   │   │   │   └── [id].vue        |
│   │   │   │   ├── index.vue           |
│   │   │   │   ├── new.vue             |
│   │   │   │   └── overview.vue        |
│   │   │   ├── resource                |
│   │   │   │   ├── edit                |
│   │   │   │   │   └── [id].vue        |
│   │   │   │   ├── index.vue           |
│   │   │   │   ├── new.vue             |
│   │   │   │   └── overview.vue        |
│   │   │   ├── worker                  |
│   │   │   │   ├── edit                |
│   │   │   │   │   └── [id].vue        |
│   │   │   │   ├── index.vue           |
│   │   │   │   ├── new.vue             |
│   │   │   │   └── overview.vue        |
│   │   │   ├── dashboard.vue           | 
│   │   │   └── index.vue               | redirects to dashboard
│   │   └── app.vue                     |
│   ├── public                          |
│   │   ├── favicon.ico                 |
│   │   └── robots.txt                  |
│   ├── Dockerfile                      |
│   ├── nuxt.config.ts                  | config file for nuxt
│   ├── package.json                    | used packages
│   ├── package-lock.json               |
│   ├── postcss.config.cjs              |
│   ├── tailwind.config.cjs             | tailwind config
│   └── tsconfig.json                   |
├── CHANGELOG                           |
├── docker-compose-server.yml           |
├── docker-compose.yml                  |
├── download_sparc.sh                   |
├── LICENSE                             |
├── manuel_tests.md                     |
├── package-lock.json                   |
├── README.md                           |
└── run_server.sh                       |
```
