# Foodgram
![workflow badge](https://github.com/botanikboy/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Foodram is a website for posting recipes with photos. User authentification and personal favirities, one can add recipies and download a list of grosseries from basket as a txt.

## Installation and launch

### env file template [.env.example](infra-dev/.env.example)

```python
DB_ENGINE=django.db.backends.postgresql # database type
DB_NAME=postgres # database name
POSTGRES_USER=postgres # database login
POSTGRES_PASSWORD=postgres # database password
DB_HOST=db # docker container name wuth databaase
DB_PORT=5432 # database port
SECRET_KEY = 'XXX' # Secret Key for Django
```
To launch the project in Docker containers locally do the following:
1. change working directory to location of docker-compose.yaml file
```bash
cd .\infra\
```
2. launch build for docker images
```
docker compose up -d --build
```
3. enshure that all containers are up and running
```
docker container ls
```
4. mage database migrations
```bash
docker compose exec web python manage.py migrate
```
5. for database test data load fixtures
```bash
docker compose exec web python manage.py loaddata fixtures.json
```
6. createsuperuser for control
```bash
docker compose exec web python manage.py createsuperuser
```
7. collect static files in one folder
```bash
docker compose exec web python manage.py collectstatic --no-input
```
If everything is ok the web site is availible:
http://localhost/

## Tech stack
- [Python](https://www.python.org/)
- [Docker](https://www.docker.com/)
- [Django](https://www.djangoproject.com/)
- [Django REST framework](https://www.django-rest-framework.org/)
- [Djoser](https://djoser.readthedocs.io/en/latest/)

## Author
Developed by:
[Ilya Savinkin](https://www.linkedin.com/in/ilya-savinkin-6002a711/)
