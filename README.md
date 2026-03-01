# SPARC

SPARC (Smart Planning and Resource Control) is a web application that runs on mobile devices. It allows users to enter production steps and manage resources, such as personnel and machinery

> [!IMPORTANT]
> 1. This repo is under active development till 08.03.2026
> 2. Instructions are planted to be performed on an ubuntu system
> 3. This project is only planed for use in a private network

> [!IMPORTANT]
> Before you commit!
> Run the tests before you commit and check that pylint does not complain about the formating of your code.

## run app

### from source

`docker compose up --build`

> [!Warning]
> if you get this error:
>
> Error response from daemon: Conflict. The container name "/django-backend" is already in use by container
>
> just do this:
>
> `sudo docker rm -f <container-name>`


### on ubuntu server
open your firewall at port 3000 and 8000:\
\
In this repo (if manually else just take from repo release):
1. `sudo docker compose build`
2. `sudo docker save sparc-backend sparc-frontend postgres:18 -o sparc-images.tar`

install docker on server:
https://docs.docker.com/engine/install/ubuntu/

on server: (make sure that the docker-compose.yml does not use build instead of image or uses volumes)
1. `sudo docker load -i sparc-images.tar`
2. `sudo docker compose down` (when updating)
3. `sudo docker compose up -d`
4. `sudo docker stop django-backend nuxt-frontend postgres-db`

## make migrations
`sudo docker compose exec backend python manage.py makemigrations`\
`1`\
`None`\
`sudo docker compose exec backend python manage.py migrate`

## run tests
`sudo docker compose exec backend pytest`\
or if you want to run a specific test (e.g.: test_models):\
`sudo docker compose exec backend pytest app/tests/test_models.py`\
if you want to add a test:\
1. go to backend\app\tests\
2. if you want to 

## create super user
`sudo docker compose exec backend python manage.py collectstatic --noinput`\
`sudo docker compose exec backend python manage.py createsuperuser`

## reset all data
`sudo docker volume rm sparc_pgdata`\
`sudo docker compose up -d`\
`sudo docker compose exec backend python manage.py createsuperuser`

## project structure

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

## Package manager

- pip (v25.3)
- npm (v10.9.3)

## Dependencies

- nuxt          (v4.2.1)
- vue           (v3.5.24)
- vue-router  (v4.6.3)
- uvcorn        (v0.38.0) (gunicorn instead?)
- django        (v5.2.8)
- djangorestframework (v3.16.1)
- PostgreSQL    (v18.0)
- nginx         (? we probably don't need a reverse proxy because we are not connected to the internet)