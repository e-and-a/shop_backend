# Tech Store Frontend

React/Vite/TypeScript клиент для backend интернет-магазина техники.

## Стек

- React
- Vite
- TypeScript
- React Router
- Axios
- CSS

## Запуск

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend будет доступен на `http://127.0.0.1:5173`.

## Env

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Backend должен быть запущен на `http://127.0.0.1:8000`.

## Основные страницы

- `/` - главная
- `/products` - каталог с фильтрами, поиском, сортировкой и пагинацией
- `/products/:id` - карточка товара, отзывы, добавление в корзину и избранное
- `/login` - вход
- `/register` - регистрация
- `/profile` - профиль
- `/favorites` - избранное CUSTOMER
- `/cart` - корзина CUSTOMER
- `/checkout` - оформление заказа
- `/orders` и `/orders/:id` - заказы CUSTOMER
- `/manager` - панель MANAGER/ADMIN
- `/manager/products` - управление товарами
- `/manager/categories` - управление категориями
- `/manager/brands` - управление брендами
- `/manager/orders` - управление заказами
- `/manager/reviews` - модерация отзывов
- `/admin` - статистика ADMIN

## Тестовые пользователи

После `python manage.py seed_data`:

- `admin@example.com / admin12345`
- `manager@example.com / manager12345`
- `customer@example.com / customer12345`
