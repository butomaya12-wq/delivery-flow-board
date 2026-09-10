# Delivery Flow Board

Delivery Flow Board — минимальная Kanban-доска для оператора или менеджера доставки. Она позволяет создавать заказы, видеть их на доске и перемещать между этапами доставки.

## Current status

Completed Homework 2 MVP.

## MVP features

- Создание заказа с именем клиента, адресом доставки и краткой информацией о заказе.
- Автоматическая генерация `order_id` и начальный статус `New`.
- Kanban-доска с четырьмя статусами: `New`, `Preparing`, `Out for delivery`, `Delivered`.
- Перемещение заказа между любыми статусами.
- Карточка заказа с ID, клиентом, адресом, описанием и текущим статусом.
- Сохранение заказов и статусов между перезапусками backend.

## Architecture

```text
React
→ frontend API module
→ HTTP
→ FastAPI
→ SQLAlchemy
→ SQLite
```

## Technology stack

- React + Vite
- FastAPI
- uv
- SQLAlchemy
- SQLite
- pytest

## API

Backend URL: http://localhost:8000

- `GET /api/orders` — получить все заказы.
- `POST /api/orders` — создать заказ.
- `PATCH /api/orders/{order_id}/status` — изменить статус заказа.

Контракт запросов и ответов описан в [openapi.yaml](openapi.yaml).

## Run locally

Запустите backend:

```sh
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

В отдельном терминале запустите frontend:

```sh
cd frontend
npm install
npm run dev
```

Frontend URL: http://localhost:5173

Backend URL: http://localhost:8000

## Verification

Выполните команды из корня репозитория:

```sh
(cd backend && uv run pytest)
(cd frontend && npm run build)
(cd frontend && npm run lint)
npx @redocly/cli lint openapi.yaml
```

## Persistence

Development data хранится в SQLite. По умолчанию используется файл `backend/delivery_flow_board.db`; он игнорируется Git через правило `*.db`.

Для другого расположения или имени БД задайте `DELIVERY_FLOW_BOARD_DATABASE_URL` как SQLAlchemy database URL перед запуском backend.

## Out of scope

Аутентификация, управление курьерами, GPS-tracking, платежи и остальные Non-Goals из [_docs/specs.md](_docs/specs.md) не входят в этот MVP.
