# SPARC

> [!IMPORTANT]
> 1. This repo is under active development till 15.02.2026
> 2. Instructions are planted to be performed on an ubuntu system
> 3. This project was only planed for use in a private network

> [!IMPORTANT]
> Before you commit!
> Run the tests before you commit and check that pylint does not complain about the formating of your code.

> [!TIP]
> we assume for every command that we start in the root directory

## project structure

```txt
SPARC/
├── backend
│   ├── app                                         | 
│   │   ├── admin.py                                | what is visible in admin view
│   │   ├── apps.py                                 | app config
│   │   ├── __init__.py                             |
│   │   ├── migrations                              |
│   │   │   └── __init__.py
│   │   ├── models.py                               | definition of all Entety of the ER diagram
│   │   ├── serializers.py                          | serilizer definitions of the models
│   │   ├── test.py                                 | test cases
│   │   ├── urls.py                                 | urls for the api
│   │   └── views.py                                | definitions of api functions
│   ├── config                                      | 
│   │   ├── asgi.py                                 |
│   │   ├── __init__.py                             |
│   │   ├── settings.py                             |
│   │   ├── urls.py                                 |
│   │   └── wsgi.py                                 | 
│   ├── Dockerfile                                  |
│   ├── manage.py                                   |
│   ├── requirements.txt                            |
│   └── staticfiles
│       ├── admin
│       └── rest_framework
├── frontend                                        |
│   ├── app                                         |
│   │   ├── app.vue                                 |
│   │   ├── assets                                  |
│   │   │   └── css                                 |
│   │   │       └── tailwind.css                    |
│   │   ├── components                              |
│   │   │   ├── Navbar.vue                          | navbar with the diffrent views as buttons
│   │   │   └── Topbar.vue                          | topbar with title and submit button
│   │   ├── composables                             |
│   │   │   └── useTheme.js
│   │   ├── layouts
│   │   │   └── custom.vue
│   │   └── pages
│   │       ├── disruption
│   │       │   ├── edit
│   │       │   │   └── [id].vue
│   │       │   ├── index.vue
│   │       │   ├── new.vue
│   │       │   └── overview.vue
│   │       ├── index.vue
│   │       └── order
│   │           ├── edit
│   │           │   └── [id].vue
│   │           ├── index.vue
│   │           ├── new.vue
│   │           └── overview.vue
│   ├── Dockerfile
│   ├── node_modules
│   ├── nuxt.config.ts
│   ├── package.json
│   ├── package-lock.json
│   ├── postcss.config.cjs
│   ├── public
│   │   ├── favicon.ico
│   │   └── robots.txt
│   ├── tailwind.config.cjs
│   └── tsconfig.json
├── .gitattributes
├── .gitignore
├── CHANGELOG
├── docker-compose.yml
├── LICENSE
├── package-lock.json
└── README.md
```

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
In this repo (if manually else just take from repo release):
1. `docker compose build`
2. `docker save sparc-backend sparc-frontend postgres:18 -o sparc-images.tar`

install docker on server:
https://docs.docker.com/engine/install/ubuntu/

on server: (make sure that the docker-compose.yml does not use build instead of image or uses volumes)
1. `docker load -i sparc-images.tar`
2. `docker compose down` (when updating)
3. `docker compose up -d`
4. `docker stop django-backend nuxt-frontend postgres-db`

## run tests

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