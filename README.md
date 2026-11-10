# rest-api

Каталог open-source проєктів для новачків: знаходиш проєкт під свою мову і просту задачу, з якої можна почати.

На сайті: каталог проєктів з пошуком і фільтрами, сторінки проєктів, задач, мейнтейнерів і організацій, реєстрація, профіль, обране і "взяти задачу". Адмін може додавати, редагувати і видаляти дані.

Зараз зроблений CRUD для проєктів, задач, мейнтейнерів, організацій і мов, реєстрація, логін через JWT і права доступу. Фронтенд: https://github.com/zxkeee/rest-api-frontend

## Як запустити проєкт

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

У `.env` впиши свій `SECRET_KEY`. `ACCESS_TOKEN_MINUTES` задає, скільки живе access токен (за замовчуванням 5 хвилин). `migrate` одразу заповнює базу тестовими даними. `createsuperuser` створює адміна, без нього не вийде нічого додати чи видалити в каталозі.

Бекенд: http://127.0.0.1:8000, фронтенд має бути на порту 8001 (для нього налаштований CORS).

## API

Базовий шлях `/api/v1/`, формат JSON.

Колонка "Доступ": всі - можна без токена, user - будь-який залогінений користувач, admin - тільки адмін (`is_staff`).

| Метод | URL | Що робить | Параметри / body | Відповідь | Доступ |
|---|---|---|---|---|---|
| GET | `/projects/` | список проєктів | `search`, `language`, `difficulty`, `ordering` | `200` [проєкт] | всі |
| GET | `/projects/{id}/` | один проєкт | - | `200` проєкт, `404` | всі |
| POST | `/projects/` | додати проєкт | проєкт | `201` проєкт, `400`, `401`, `403` | admin |
| PATCH | `/projects/{id}/` | змінити проєкт | змінені поля | `200` проєкт, `400`, `404`, `401`, `403` | admin |
| DELETE | `/projects/{id}/` | видалити проєкт | - | `204`, `404`, `409`, `401`, `403` | admin |
| GET | `/issues/` | список задач | `difficulty`, `status`, `project` | `200` [задача] | всі |
| GET | `/issues/{id}/` | одна задача | - | `200` задача, `404` | всі |
| POST | `/issues/` | додати задачу | задача | `201` задача, `400`, `401` | user |
| PATCH | `/issues/{id}/` | змінити задачу | змінені поля | `200` задача, `400`, `404`, `401` | user |
| DELETE | `/issues/{id}/` | видалити задачу | - | `204`, `404`, `401`, `403` | admin |
| GET | `/maintainers/`, `/organizations/`, `/languages/` | список | `search` (крім мов) | `200` [обʼєкт] | всі |
| GET | `/maintainers/{id}/`, `/organizations/{id}/`, `/languages/{id}/` | один обʼєкт | - | `200` обʼєкт, `404` | всі |
| GET | `/maintainers/{id}/projects/`, `/organizations/{id}/projects/` | їх проєкти | - | `200` [проєкт], `404` | всі |
| POST | `/maintainers/`, `/organizations/`, `/languages/` | додати | обʼєкт | `201`, `400`, `401`, `403` | admin |
| PATCH | `/maintainers/{id}/`, `/organizations/{id}/`, `/languages/{id}/` | змінити | змінені поля | `200`, `400`, `404`, `401`, `403` | admin |
| DELETE | `/maintainers/{id}/`, `/organizations/{id}/`, `/languages/{id}/` | видалити | - | `204`, `404`, `409`, `401`, `403` | admin |

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

## Авторизація

Ендпоінти в `/api/v1/auth/`. Логін працює через JWT ([djangorestframework-simplejwt](https://github.com/jazzband/djangorestframework-simplejwt)).

| Метод | URL | Що робить | Body | Відповідь | Доступ |
|---|---|---|---|---|---|
| POST | `/auth/register/` | реєстрація | `username`, `first_name`, `last_name`, `email`, `password`, `password_confirm` | `201` користувач, `400` | всі |
| POST | `/auth/login/` | логін | `username`, `password` | `200` `access` і `refresh`, `400`, `401` | всі |
| POST | `/auth/token/refresh/` | новий access токен | `refresh` | `200` `access` і `refresh`, `401` | всі |
| POST | `/auth/logout/` | вихід | `refresh` | `205`, `400`, `401` | всі |
| GET | `/auth/me/` | хто я | - | `200` користувач, `401` | user |

Токен передається в заголовку:

```
Authorization: Bearer <access>
```

Реєстрація:

```json
{ "username": "olena", "first_name": "Олена", "last_name": "", "email": "olena@example.com", "password": "Kv1tka-na-vikni", "password_confirm": "Kv1tka-na-vikni" }
```

`first_name` і `last_name` можна не передавати або залишити порожніми, решта полів обовʼязкові. Що перевіряється:

- `username` до 150 символів, тільки літери, цифри і `@ . + - _`, має бути унікальним
- `first_name`, `last_name` до 150 символів
- `email` до 254 символів, формат `name@example.com`, унікальний (без урахування регістру)
- `password` від 8 до 128 символів, не схожий на username чи email, не зі списку популярних паролів і не з самих цифр (стандартні валідатори Django)
- `password_confirm` має збігатися з `password`

Відповідь `201` (пароль не повертається, в базі він лежить тільки як хеш PBKDF2):

```json
{ "id": 2, "username": "olena", "first_name": "Олена", "last_name": "", "email": "olena@example.com", "role": "user" }
```

`role` буде `admin` для користувачів з `is_staff`, інакше `user`. Такий самий обʼєкт повертає `GET /auth/me/`.

Помилка `400` з повідомленням для кожного поля:

```json
{ "status": 400, "detail": "Невалідні дані. Деталі в полі errors.", "errors": { "email": ["Введіть коректну адресу електронної пошти."], "password_confirm": ["Паролі не збігаються."] } }
```

Логін повертає пару токенів:

```json
{ "refresh": "eyJhbGciOi...", "access": "eyJhbGciOi..." }
```

Access токен живе 5 хвилин, refresh 1 день. Коли access протух, API на будь-який запит з ним відповідає `401` з `"Токен недійсний або прострочений."`. Тоді клієнт шле refresh на `/auth/token/refresh/` і отримує новий access і новий refresh. Старий refresh після цього потрапляє в чорний список і вдруге не спрацює (ротація). Якщо і refresh вже недійсний, теж `401`, і треба логінитись заново.

Вихід: клієнт видаляє в себе обидва токени. Додатково можна відправити refresh на `/auth/logout/`, він потрапить у чорний список, і оновити ним access вже не вийде. Сам access токен до кінця своїх 5 хвилин ще працює, бо сервер його ніде не зберігає.

## Права доступу

- переглядати каталог і задачі може будь-хто, токен не потрібен
- додавати і змінювати задачі може будь-який залогінений користувач
- видаляти задачі і змінювати проєкти, мейнтейнерів, організації й мови може тільки адмін

Без токена (або з недійсним) на закритий ендпоінт буде `401`:

```json
{ "status": 401, "detail": "Потрібна авторизація. Передайте access токен у заголовку Authorization: Bearer <token>.", "errors": null }
```

Якщо токен нормальний, але прав не вистачає, буде `403`:

```json
{ "status": 403, "detail": "Змінювати ці дані може лише адміністратор.", "errors": null }
```

## Помилки

Всі помилки в одному форматі:

```json
{ "status": 409, "detail": "Неможливо видалити організацію «Microsoft», оскільки за нею закріплено 2 проєкти. ...", "errors": null }
```

В `errors` помилки по полях, якщо дані не пройшли валідацію.

- `400` - невалідні дані або фільтр
- `401` - немає токена, токен недійсний чи прострочений, або неправильний логін/пароль
- `403` - користувач залогінений, але на цю дію немає прав
- `404` - обʼєкта з таким id немає
- `409` - дія конфліктує з даними, які вже є: не можна видалити організацію, мейнтейнера чи мову, поки до них привʼязані проєкти, і проєкт, поки в нього є відкриті задачі. Запит сам по собі правильний, тому не 400. Коли прибрати причину, він пройде.

## Postman

Колекція в `postman/rest-api.postman_collection.json`, адреса сервера в змінній `base_url`. Краще запускати на свіжій базі.

Перед запуском впиши логін і пароль адміна в змінні `admin_username` і `admin_password`. Папка "Авторизація" реєструє нового користувача, перевіряє логін, refresh, права і вихід, а в кінці логінить адміна. Решта запитів бере токен зі змінної `access_token`. Якщо через 5 хвилин посипались `401`, повтори "Логін адміна".

## Схема бази даних

- `organizations` (name, github_url) - один до багатьох з `projects`
- `maintainers` (full_name, github_username) - один до багатьох з `projects`
- `languages` (name) - багато до багатьох з `projects`
- `projects` (name, description, repo_url, stars, difficulty, maintainer_id, organization_id)
- `issues` (project_id, title, difficulty, status)

## TODO

- [x] реєстрація, логін, права доступу
- [ ] профіль, обране і "взяти задачу"
- [ ] пошук і фільтри для задач по мові програмування
- [ ] підтягувати зірки і задачі з GitHub API автоматично
- [ ] сторінка "Про нас"
