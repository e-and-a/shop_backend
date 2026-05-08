# Интернет-магазин техники: backend API

Серверная часть веб-приложения «Интернет-магазин техники и электроники». Проект реализован как API-first backend на Django и Django REST Framework с JWT-аутентификацией, ролевой моделью доступа, PostgreSQL и Swagger/OpenAPI-документацией.

## Стек

- Python 3.10+
- Django
- Django REST Framework
- PostgreSQL
- djangorestframework-simplejwt
- drf-spectacular
- django-filter
- django-cors-headers
- python-dotenv
- Pillow

## Архитектура

Проект следует MVT-подходу:

- Model: Django ORM модели в приложениях `users`, `catalog`, `cart`, `orders`, `reviews`.
- View: DRF ViewSet/APIView классы.
- Template/Representation: serializers и JSON-представления API.

Основные приложения:

- `users` - кастомная модель пользователя, роли, регистрация, профиль.
- `catalog` - категории, бренды, товары, характеристики, избранное.
- `cart` - корзина покупателя.
- `orders` - оформление, история и обработка заказов.
- `reviews` - отзывы и рейтинги товаров.
- `common` - permissions, pagination, filters, seed command.

## Быстрый запуск

```bash
cd shop_backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

## PostgreSQL

Пример создания базы:

```sql
CREATE DATABASE shop_db;
CREATE USER shop_user WITH PASSWORD 'shop_password';
GRANT ALL PRIVILEGES ON DATABASE shop_db TO shop_user;
```

На macOS с Homebrew PostgreSQL это можно выполнить так:

```bash
brew services start postgresql@16
psql postgres -c "CREATE ROLE shop_user WITH LOGIN PASSWORD 'shop_password';"
createdb -O shop_user shop_db
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE shop_db TO shop_user;"
```

Если роль уже существует, команда `CREATE ROLE` вернёт ошибку. В этом случае достаточно проверить, что база создана и строка `DATABASE_URL` в `.env` совпадает с именем пользователя, паролем и базой.

В `.env` укажите строку подключения:

```env
DATABASE_URL=postgresql://shop_user:shop_password@localhost:5432/shop_db
```

## Переменные окружения

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://shop_user:shop_password@localhost:5432/shop_db
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

## Команды

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
python manage.py runserver
```

## Документация API

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`

В Swagger UI доступна JWT Bearer авторизация. Получите access token через `/api/v1/auth/login/`, затем нажмите `Authorize` и вставьте токен в формате `Bearer <access_token>`.

## Тестовые пользователи

Создаются командой `python manage.py seed_data`:

- `admin@example.com / admin12345`
- `manager@example.com / manager12345`
- `customer@example.com / customer12345`

## Роли

- `ADMIN`: полный доступ ко всем сущностям и административной статистике.
- `MANAGER`: управление каталогом, товарами, остатками, заказами и модерацией отзывов.
- `CUSTOMER`: просмотр каталога, корзина, избранное, оформление заказов, отзывы.
- Анонимный пользователь: просмотр активного публичного каталога и модерированных отзывов.

## Основные endpoints

Auth:

- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/token/refresh/`
- `POST /api/v1/auth/logout/`
- `GET /api/v1/auth/me/`
- `PATCH /api/v1/auth/me/`

Catalog:

- `GET /api/v1/categories/`
- `POST /api/v1/categories/`
- `GET /api/v1/brands/`
- `POST /api/v1/brands/`
- `GET /api/v1/products/`
- `POST /api/v1/products/`
- `PATCH /api/v1/products/{id}/`
- `DELETE /api/v1/products/{id}/`

Product filters:

- `category`, `category_slug`
- `brand`, `brand_slug`
- `min_price`, `max_price`
- `in_stock`
- `search`
- `ordering=price,-created_at,rating,stock`
- `page`, `page_size`

Favorites:

- `GET /api/v1/favorites/`
- `POST /api/v1/favorites/`
- `DELETE /api/v1/favorites/{id}/`

Cart:

- `GET /api/v1/cart/`
- `POST /api/v1/cart/items/`
- `PATCH /api/v1/cart/items/{id}/`
- `DELETE /api/v1/cart/items/{id}/`
- `DELETE /api/v1/cart/clear/`

Orders:

- `GET /api/v1/orders/`
- `GET /api/v1/orders/{id}/`
- `POST /api/v1/orders/create-from-cart/`
- `PATCH /api/v1/orders/{id}/status/`
- `POST /api/v1/orders/{id}/cancel/`

Reviews:

- `GET /api/v1/products/{product_id}/reviews/`
- `POST /api/v1/products/{product_id}/reviews/`
- `PATCH /api/v1/reviews/{id}/`
- `DELETE /api/v1/reviews/{id}/`

Admin:

- `GET /api/v1/admin/stats/`

## Бизнес-правила

- Корзина привязана к пользователю и доступна только `CUSTOMER`.
- Повторное добавление товара в корзину увеличивает количество.
- Нельзя добавить неактивный товар, товар без остатка или количество больше `stock`.
- Сумма корзины считается сервером и не хранится в БД.
- Заказ создаётся из корзины в транзакции, сохраняет snapshot названия, SKU и цены.
- При создании заказа остатки товаров уменьшаются.
- При отмене заказа в статусе `CREATED` или `PROCESSING` остатки восстанавливаются.
- `CUSTOMER` видит только свои заказы и не может менять статус напрямую.
- `MANAGER` и `ADMIN` видят все заказы и могут менять статусы.
- Удаление товара через API выполняется как soft delete: `is_active=false`.
- Отзыв может оставить только `CUSTOMER`, который покупал товар в завершённом заказе.
- Публично отображаются только модерированные отзывы.
