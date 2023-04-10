# Foodgram
![workflow badge](https://github.com/botanikboy/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Foodram is a website for posting recipes.

## Установка

### Шаблон наполенеия env-файла

```python
DB_ENGINE=django.db.backends.postgresql # тип используемой базы данных(в примере postgresql)
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
SECRET_KEY = 'XXX' # Secret Key для проекта Django
```
Для разворачивания проекта в контейнерах с помощью Docker перейдите в директорию с проектом и выполните следующие команды:
1. перейти в директорию с файлом docker-compose.yaml
```bash
cd .\infra\
```
2. запустить процесс создания docker image (образов)
```
docker compose up -d --build
```
3. после окончания процесса убедиться, что успешно запущены все контейнеры
```
docker container ls
```
4. выполнить миграции
```bash
docker compose exec web python manage.py migrate
```
5. для заполнения базы данных тестовыми данными из фикстур выполнить команду
```bash
docker compose exec web python manage.py loaddata fixtures.json
```
6. создать суперпользователя
```bash
docker compose exec web python manage.py createsuperuser
```
7. собрать файлы статики
```bash
docker compose exec web python manage.py collectstatic --no-input
```
Если всё прошло успешно проект доступен по адресу:
http://localhost/
