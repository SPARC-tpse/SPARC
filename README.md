# test_django

try CI, tesing and release with django, vue, docker, PostgreSQL and uvcorn, pylint, github

> [!IMPORTANT]
> 1. This repo is under active development till 15.02.2026
> 2. All instructions provided where tested on Fedora 43

> [!IMPORTANT]
> Before you commit!
> Run the tests before you commit and check that pylint does not complain about the formating of your code.

> [!TIP]
> we assume for every command that we start in the root directory

## project structure

``` txt
SPARC/
├── backend/
│   ├── Dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   └── sparc/
│       ├── __init__.py
│       ├── asgi.py
│       ├── models.py
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py
├── frontend/
│   ├── .nuxt/
│   ├── app/
│   ├── node_module/
│   ├── public/
│   ├── Dockerfile
│   ├── nuxt.config.ts
│   ├── package-lock.json
│   ├── package.json
│   └── tsconfig.json
├── .gitignore
├── README.md
└── docker-compose.yml
```

## inital setup
`mkdir SPARC`\
`touch docker-compose.yml`

setup backend:\
`mkdir backend`\
`cd backend`\
`touch Dockerfile`\
`python3.14 -m venv venv`\
`source venv/bin/activate`\
`pip install django uvicorn djangorestframework`\
`python -m django --version`\
`django-admin startproject sparc .`\
`python manage.py runserver`

setup frontend:\
`mkdir frontend`\
`cd frontend`\
`touch Dockerfile`\
`npm create nuxt@latest .`\
`npm run dev -- -o`

setup docker:\
```
sudo dnf remove docker
                docker-client
                docker-client-latest
                docker-common
                docker-latest
                docker-latest-logrotate
                docker-logrotate
                docker-selinux
                docker-engine-selinux
                docker-engine
```
```
sudo dnf install docker-ce
                 docker-ce-cli
                 containerd.io
                 docker-buildx-plugin
                 docker-compose-plugin
```
`sudo systemctl enable --now docker`

setup tests:\
`mkdir tests`

setup django admin(for manageing backend)
`docker compose exec web python manage.py createsuperuser`

## run app

### build and run from source

`docker compose up --build`

### run release on linux

## run tests

## package manager

- pip (v25.3)
- npm (v10.9.3)

## depenencies

- nuxt          (v4.2.1)
- vue           (v3.5.24)
- vue-router  (v4.6.3)
- uvcorn        (v0.38.0) (gunicorn instead?)
- django        (v5.2.8)
- djangorestframework (v3.16.1)
- PostgreSQL    (v18.0)
- nginx         (? we probably don't need a reverse proxy because we are not connected to the internet)

## update branch
