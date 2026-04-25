# bot_4_tempmail

Telegram-бот для создания временной одноразовой почты.
Основной провайдер — [mail.tm](https://mail.tm), fallback —
[guerrillamail](https://www.guerrillamail.com). Каждый запрос проходит цепочку
с нуля: если mail.tm работает — используется он, иначе guerrillamail.

## Стек

- Python 3.12, aiogram 3.26
- PostgreSQL + SQLAlchemy (asyncpg)
- aiohttp (HTTP-клиент для провайдеров)
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
├── services/
│   ├── mailtm.py    — низкоуровневый клиент mail.tm
│   └── providers/   — единый интерфейс + цепочка mail.tm → guerrillamail
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
