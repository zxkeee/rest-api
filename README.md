# rest-api

Каталог open-source проєктів для новачків: знаходиш проєкт під свою мову і просту задачу, з якої можна почати.

На сайті: каталог проєктів з пошуком і фільтрами, сторінки проєктів, задач, мейнтейнерів і організацій, реєстрація, профіль, обране і "взяти задачу". Адмін може додавати, редагувати і видаляти дані.

Зараз зроблений CRUD для проєктів, задач, мейнтейнерів, організацій і мов. Фронтенд: https://github.com/zxkeee/rest-api-frontend

## Як запустити проєкт

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

У `.env` впиши свій `SECRET_KEY`. `migrate` одразу заповнює базу тестовими даними.

Бекенд: http://127.0.0.1:8000, фронтенд має бути на порту 8001 (для нього налаштований CORS).

## API

Базовий шлях `/api/v1/`, формат JSON.

| Метод | URL | Що робить | Параметри / body | Відповідь |
|---|---|---|---|---|
| GET | `/projects/` | список проєктів | `search`, `language`, `difficulty`, `ordering` | `200` [проєкт] |
| GET | `/projects/{id}/` | один проєкт | - | `200` проєкт, `404` |
| POST | `/projects/` | додати проєкт | проєкт | `201` проєкт, `400` |
| PATCH | `/projects/{id}/` | змінити проєкт | змінені поля | `200` проєкт, `400`, `404` |
| DELETE | `/projects/{id}/` | видалити проєкт | - | `204`, `404`, `409` |
| GET | `/issues/` | список задач | `difficulty`, `status`, `project` | `200` [задача] |
| GET | `/issues/{id}/` | одна задача | - | `200` задача, `404` |
| POST | `/issues/` | додати задачу | задача | `201` задача, `400` |
| PATCH | `/issues/{id}/` | змінити задачу | змінені поля | `200` задача, `400`, `404` |
| DELETE | `/issues/{id}/` | видалити задачу | - | `204`, `404` |
| GET | `/maintainers/`, `/organizations/`, `/languages/` | список | `search` (крім мов) | `200` [обʼєкт] |
| GET | `/maintainers/{id}/`, `/organizations/{id}/`, `/languages/{id}/` | один обʼєкт | - | `200` обʼєкт, `404` |
| GET | `/maintainers/{id}/projects/`, `/organizations/{id}/projects/` | їх проєкти | - | `200` [проєкт], `404` |
| POST | `/maintainers/`, `/organizations/`, `/languages/` | додати | обʼєкт | `201`, `400` |
| PATCH | `/maintainers/{id}/`, `/organizations/{id}/`, `/languages/{id}/` | змінити | змінені поля | `200`, `400`, `404` |
| DELETE | `/maintainers/{id}/`, `/organizations/{id}/`, `/languages/{id}/` | видалити | - | `204`, `404`, `409` |

`difficulty`: `beginner`, `intermediate`, `advanced`. `status`: `open`, `in_progress`, `closed`. `ordering`: `name`, `-name`, `stars`, `-stars`.

Проєкт:

```json
{ "id": 1, "name": "Django", "description": "...", "repo_url": "https://github.com/django/django", "stars": 81000, "difficulty": "intermediate", "languages": [1, 2], "maintainer": 2, "organization": 1 }
```

Задача:

```json
{ "id": 1, "project": 1, "title": "Fix typo in tutorial part 2", "difficulty": "beginner", "status": "open" }
```

Мейнтейнер, організація, мова:

```json
{ "id": 2, "full_name": "Sarah Boyce", "github_username": "sarahboyce" }
{ "id": 1, "name": "Django Software Foundation", "github_url": "https://github.com/django" }
{ "id": 1, "name": "Python" }
```

## Помилки

Всі помилки в одному форматі:

```json
{ "status": 409, "detail": "Неможливо видалити організацію «Microsoft», оскільки за нею закріплено 2 проєкти. ...", "errors": null }
```

В `errors` помилки по полях, якщо дані не пройшли валідацію.

- `400` - невалідні дані або фільтр
- `404` - обʼєкта з таким id немає
- `409` - дія конфліктує з даними, які вже є: не можна видалити організацію, мейнтейнера чи мову, поки до них привʼязані проєкти, і проєкт, поки в нього є відкриті задачі. Запит сам по собі правильний, тому не 400. Коли прибрати причину, він пройде.

## Postman

Колекція в `postman/rest-api.postman_collection.json`, адреса сервера в змінній `base_url`. Краще запускати на свіжій базі.

## Схема бази даних

- `organizations` (name, github_url) - один до багатьох з `projects`
- `maintainers` (full_name, github_username) - один до багатьох з `projects`
- `languages` (name) - багато до багатьох з `projects`
- `projects` (name, description, repo_url, stars, difficulty, maintainer_id, organization_id)
- `issues` (project_id, title, difficulty, status)

## TODO

- [ ] авторизація, профіль, обране і "взяти задачу"
- [ ] пошук і фільтри для задач по мові програмування
- [ ] підтягувати зірки і задачі з GitHub API автоматично
- [ ] сторінка "Про нас"
