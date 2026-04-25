# bot_4_tempmail

Telegram-бот, который выдаёт одноразовые email-адреса и показывает входящие
письма прямо в чате. Подходит для регистраций на сомнительных сервисах,
тестов рассылок и быстрой проверки писем без своей основной почты.

## Особенности

- Создание ящиков в один клик, до 5 активных на пользователя
- Чтение входящих внутри Telegram, без переходов на сайт
- Цепочка провайдеров `mail.tm → guerrillamail`: при сбое основного
  автоматически создаём ящик в резервном
- Анти-спам: rate-limit `5 запросов/мин` + cooldown `10 сек` на ручную
  проверку входящих
- Защита от двойного клика при создании ящика (TOCTOU)
- Обязательная подписка на каналы (опционально)
- Админ-панель: статистика, управление каналами, рассылки
- Три языка: русский, узбекский (латиница), английский
- Фоновая очистка неактивных ящиков (>7 дней без проверок)

## Стек

- Python 3.12, [aiogram 3.26](https://docs.aiogram.dev/)
- PostgreSQL 16, SQLAlchemy (async), asyncpg
- aiohttp — общий HTTP-клиент для всех провайдеров
- Docker, docker-compose

## Архитектура

```
TG → handlers/tempmail.py
        │
        ▼
   ProviderRouter ──► [ MailTmProvider, GuerrillaMailProvider ]
        │                       │                 │
        │              services/mailtm.py    services/providers/guerrillamail.py
        │
        ▼
   PostgreSQL (TempMailAccount: provider, email, token, account_id)
```

- Существующие ящики всегда обслуживаются провайдером, на котором были созданы
  (поле `acc.provider`)
- Создание нового ящика идёт по цепочке: пробуем mail.tm, при `5xx/timeout`
  переходим к guerrillamail. Health-state не храним — каждый запрос проверяет
  цепочку с нуля
- Один общий `aiohttp.ClientSession` на весь бот, закрывается в `on_shutdown`
- Семафор `asyncio.Semaphore(5)` на каждый провайдер ограничивает rps

## Быстрый старт

```bash
git clone <repo>
cd bot_4_tempmail
cp .env.example .env
# заполните BOT_TOKEN, ADMIN_IDS, DB_PASSWORD
docker compose up -d --build
```

После запуска проверьте логи:

```bash
docker compose logs -f bot
```

## Переменные окружения

| Переменная     | Назначение                                | Обязательно |
|----------------|-------------------------------------------|:-----------:|
| `BOT_TOKEN`    | Токен от [@BotFather](https://t.me/BotFather) |     ✓     |
| `ADMIN_IDS`    | Telegram ID админов через запятую         |             |
| `DB_NAME`      | Имя БД (default: `bot_4_tempmail`)        |             |
| `DB_USER`      | Пользователь PostgreSQL                   |             |
| `DB_PASSWORD`  | Пароль PostgreSQL                         |     ✓     |
| `DB_HOST`      | Хост БД (default: `postgres`)             |             |
| `DB_PORT`      | Порт БД (default: `5432`)                 |             |

## Команды бота

| Команда     | Описание                       | Доступ |
|-------------|--------------------------------|:------:|
| `/start`    | Запуск, главное меню           |  все   |
| `/menu`     | Главное меню                   |  все   |
| `/profile`  | Мой профиль и статистика       |  все   |
| `/help`     | Справка                        |  все   |
| `/language` | Сменить язык интерфейса        |  все   |
| `/admin`    | Админ-панель                   | админы |

## Лимиты

- **5 ящиков на пользователя** — для шестого приходит ошибка
- **10 секунд cooldown** между нажатиями «Проверить почту» на одном ящике
- **5 запросов/минуту** общий rate-limit (для нечислового ввода)
- **Письмо до 4096 UTF-16 code units** — обрезаем по `_truncate_utf16(3900)`
- **Время жизни ящика mail.tm** — фактически 7 дней неактивности (mail.tm
  чистит сам); локальный GC синхронизируется
- **guerrillamail sid_token** протухает через ~1 час бездействия → бот
  показывает «ящик удалён» и предлагает создать новый

## Структура

```
bot/
├── main.py              entrypoint, инициализация провайдеров и фоновых тасков
├── config.py            pydantic-settings из .env
├── i18n.py              переводы ru/uz/en + t() + detect_language()
├── emojis.py            премиум-эмодзи (E_ID для кнопок, E для HTML)
├── database/
│   ├── models.py        User, Channel, TempMailAccount
│   └── crud.py          асинхронный CRUD
├── handlers/
│   ├── start.py         /start, меню, профиль, язык, подписка
│   ├── admin.py         /admin: stats, channels, broadcast
│   └── tempmail.py      создание/проверка/просмотр/удаление ящиков
├── middlewares/
│   ├── subscription.py  обязательная подписка на каналы
│   └── rate_limit.py    5 запросов/мин
├── keyboards/
│   ├── inline.py        главное меню, ящики, входящие, подтверждения
│   └── admin.py         клавиатуры админки
├── services/
│   ├── mailtm.py        низкоуровневый клиент mail.tm API
│   └── providers/
│       ├── base.py      InboxProvider Protocol + DTO
│       ├── mailtm.py    адаптер mail.tm под единый интерфейс
│       ├── guerrillamail.py  клиент guerrillamail API
│       └── router.py    цепочка mail.tm → guerrillamail
└── utils/
    └── commands.py      персональное меню команд Telegram (BotCommandScopeChat)
```

## Обработка ошибок провайдеров

| Ситуация                          | Что видит юзер                              |
|-----------------------------------|---------------------------------------------|
| mail.tm 5xx → guerrillamail OK    | Получает ящик `@sharklasers.com` молча      |
| Оба провайдера 5xx                | «Сервис временной почты сейчас недоступен»  |
| 429 rate limit                    | «Слишком много запросов, подожди минуту»    |
| 401 (mail.tm)                     | Один раз перевыпуск JWT; при повторе — ящик помечается expired |
| Ящик удалён со стороны провайдера | «Ящик удалён, создай новый»                 |
| Telegram «message not modified»   | Игнорируется через `_safe_edit()`           |

## Разработка

Локально без Docker:

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# поднять postgres вручную или через docker compose up postgres
python -m bot.main
```

## Лицензия

MIT
