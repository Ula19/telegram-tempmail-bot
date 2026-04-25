# bot_4_tempmail

Telegram-бот для создания временной одноразовой почты через [mail.tm](https://mail.tm) API.

## Стек

- Python 3.12, aiogram 3.26
- PostgreSQL + SQLAlchemy (asyncpg)
- aiohttp (HTTP-клиент для mail.tm)
- Docker + docker-compose

## Быстрый старт

```bash
cp .env.example .env
# заполнить BOT_TOKEN, ADMIN_IDS, DB_PASSWORD
docker compose up -d
```

## Структура

```
bot/
├── main.py          — entrypoint
├── config.py        — настройки из .env
├── i18n.py          — переводы ru/uz/en
├── emojis.py        — премиум-эмодзи
├── database/        — модели и CRUD
├── handlers/        — хэндлеры команд
├── middlewares/     — подписка, rate limit
├── keyboards/       — inline-клавиатуры
├── services/        — бизнес-логика (mailtm.py)
└── utils/           — вспомогательные утилиты
```

## Команды

| Команда    | Описание          |
|------------|-------------------|
| /start     | Запустить бота    |
| /menu      | Главное меню      |
| /profile   | Мой профиль       |
| /help      | Помощь            |
| /language  | Сменить язык      |
| /admin     | Панель управления |
