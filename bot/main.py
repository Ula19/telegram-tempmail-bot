"""Точка входа — запуск tempmail-бота"""
import asyncio
import logging
import os
import sys

# uvloop ускоряет asyncio в 2-4 раза (не работает на Windows!)
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass  # на Windows — работаем без uvloop

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings

# настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# флаг-файл для crash recovery
CRASH_FLAG = ".crash_flag"

# глобальные объекты (инициализируются в on_startup, используются в handlers)
http_session: aiohttp.ClientSession | None = None
mailtm_client = None  # type: ignore[assignment]
provider_router = None  # type: ignore[assignment]  # ProviderRouter

# храним ссылки на фоновые таски, чтобы GC их не убил
_bg_tasks: set[asyncio.Task] = set()


async def main() -> None:
    """Инициализация и запуск бота"""
    global http_session, mailtm_client, provider_router

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # подключаем хэндлеры (порядок важен!)
    from bot.handlers import start, admin, tempmail
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(tempmail.router)

    # подключаем мидлвари
    from bot.middlewares.rate_limit import RateLimitMiddleware
    from bot.middlewares.subscription import SubscriptionMiddleware

    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    # фоновая задача: очистка rate limit памяти
    async def _background_cleanup() -> None:
        """Очистка rate-limit памяти каждые 5 минут"""
        from bot.middlewares.rate_limit import cleanup_stale_entries
        while True:
            await asyncio.sleep(300)  # 5 минут
            removed = cleanup_stale_entries()
            if removed:
                logger.info("Фоновая очистка: удалено %d записей rate limit", removed)

    async def _tempmail_gc() -> None:
        """Раз в сутки — удалить ящики старше 7 дней из БД и с провайдера."""
        from bot.database import async_session
        from bot.database.crud import delete_accounts_older_than
        from bot.services.providers import InboxAccount
        while True:
            try:
                async with async_session() as session:
                    stale = await delete_accounts_older_than(session, days=7)
                if stale and provider_router is not None:
                    logger.info("tempmail GC: удаляем %d просроченных ящиков", len(stale))
                    for acc in stale:
                        try:
                            prov = provider_router.get_provider_by_name(
                                acc.provider or "mailtm"
                            )
                            dto = InboxAccount(
                                provider=acc.provider or "mailtm",
                                email=acc.email,
                                password=acc.password or "",
                                token=acc.token,
                                account_id=acc.account_id,
                            )
                            await prov.delete_inbox(dto)
                        except Exception as exc:  # noqa: BLE001
                            logger.warning("tempmail GC: provider delete failed: %s", exc)
            except Exception as exc:  # noqa: BLE001
                logger.error("tempmail GC error: %s", exc)
            await asyncio.sleep(86400)  # 24 часа

    @dp.startup()
    async def on_startup() -> None:
        global http_session, mailtm_client, provider_router

        # создаём таблицы в БД
        from bot.database import engine
        from bot.database.models import Base
        from sqlalchemy import text as sa_text
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            # Ручная миграция для существующих БД: добавляем provider, если
            # колонки ещё нет (create_all не модифицирует уже созданные таблицы).
            await conn.execute(sa_text(
                "ALTER TABLE tempmail_accounts "
                "ADD COLUMN IF NOT EXISTS provider VARCHAR(32) "
                "NOT NULL DEFAULT 'mailtm'"
            ))
            # account_id мог быть VARCHAR(64), для guerrillamail sid_token длиннее
            await conn.execute(sa_text(
                "ALTER TABLE tempmail_accounts "
                "ALTER COLUMN account_id TYPE VARCHAR(256)"
            ))
        logger.info("Таблицы БД созданы / мигрированы")

        # crash recovery
        if os.path.exists(CRASH_FLAG):
            logger.warning("Обнаружен crash-flag — предыдущий запуск завершился аварийно")
            os.remove(CRASH_FLAG)
        with open(CRASH_FLAG, "w") as f:
            f.write("running")

        # общий aiohttp session, провайдеры и роутер
        from bot.services.mailtm import MailTmClient
        from bot.services.providers import (
            GuerrillaMailProvider,
            MailTmProvider,
            ProviderRouter,
        )
        timeout = aiohttp.ClientTimeout(total=15)
        http_session = aiohttp.ClientSession(timeout=timeout)
        mailtm_client = MailTmClient(http_session)
        mailtm_provider = MailTmProvider(mailtm_client)
        guerrilla_provider = GuerrillaMailProvider(http_session)
        provider_router = ProviderRouter(mailtm_provider, guerrilla_provider)
        # экспорт в модуль (handlers читают через bot.main.*)
        import bot.main as _self
        _self.http_session = http_session
        _self.mailtm_client = mailtm_client
        _self.provider_router = provider_router
        logger.info(
            "Провайдеры инициализированы: основной=mailtm, fallback=guerrillamail"
        )

        for coro in (
            _background_cleanup(),
            _tempmail_gc(),
        ):
            task = asyncio.create_task(coro)
            _bg_tasks.add(task)
            task.add_done_callback(_bg_tasks.discard)
        logger.info("Фоновые задачи запущены")

        bot_info = await bot.get_me()
        logger.info("Бот @%s запущен!", bot_info.username)

        from bot.utils.commands import set_default_commands
        await set_default_commands(bot)
        logger.info("Дефолтное меню команд установлено")

    @dp.shutdown()
    async def on_shutdown() -> None:
        global http_session
        if os.path.exists(CRASH_FLAG):
            os.remove(CRASH_FLAG)
        if http_session and not http_session.closed:
            await http_session.close()
            logger.info("aiohttp session закрыт")
        logger.info("Бот остановлен")

    try:
        logger.info("Запуск polling...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
