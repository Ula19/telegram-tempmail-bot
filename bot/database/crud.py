"""CRUD операции с базой данных"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func as sa_func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Channel, TempMailAccount, User


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    full_name: str,
    language: str | None = None,
) -> User:
    """Получить юзера или создать нового"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            language=language or "ru",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


async def get_user_language(session: AsyncSession, telegram_id: int) -> str:
    """Получить язык юзера (по умолчанию ru)"""
    result = await session.execute(
        select(User.language).where(User.telegram_id == telegram_id)
    )
    lang = result.scalar_one_or_none()
    return lang or "ru"


async def update_user_language(
    session: AsyncSession, telegram_id: int, language: str
) -> None:
    """Обновить язык юзера"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.language = language
        await session.commit()


async def get_active_channels(session: AsyncSession) -> list[Channel]:
    """Получить все каналы для обязательной подписки"""
    result = await session.execute(select(Channel))
    return list(result.scalars().all())


async def add_channel(
    session: AsyncSession,
    channel_id: int,
    title: str,
    invite_link: str,
) -> Channel:
    """Добавить канал для обязательной подписки"""
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError(f"Канал {channel_id} уже добавлен")

    channel = Channel(
        channel_id=channel_id,
        title=title,
        invite_link=invite_link,
    )
    session.add(channel)
    await session.commit()
    await session.refresh(channel)
    return channel


async def remove_channel(session: AsyncSession, channel_id: int) -> bool:
    """Удалить канал. Возвращает True если удалён"""
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    channel = result.scalar_one_or_none()
    if not channel:
        return False

    await session.delete(channel)
    await session.commit()
    return True


async def get_user_stats(session: AsyncSession) -> dict:
    """Статистика: всего юзеров, за сегодня, действий"""
    from sqlalchemy import func as sa_func

    total = await session.execute(select(sa_func.count(User.id)))
    total_users = total.scalar() or 0

    today = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0,
    )
    today_result = await session.execute(
        select(sa_func.count(User.id)).where(User.created_at >= today)
    )
    today_users = today_result.scalar() or 0

    downloads = await session.execute(
        select(sa_func.sum(User.download_count))
    )
    total_downloads = downloads.scalar() or 0

    channels = await session.execute(select(sa_func.count(Channel.id)))
    total_channels = channels.scalar() or 0

    return {
        "total_users": total_users,
        "today_users": today_users,
        "total_downloads": total_downloads,
        "total_channels": total_channels,
    }


async def get_all_user_ids(session: AsyncSession) -> list[int]:
    """Получить все telegram_id юзеров для рассылки"""
    result = await session.execute(select(User.telegram_id))
    return [row[0] for row in result.all()]


# === TempMail CRUD ===

async def create_tempmail_account(
    session: AsyncSession,
    user_id: int,
    email: str,
    password: str,
    token: str,
    account_id: str,
    provider: str = "mailtm",
) -> TempMailAccount:
    """Создать запись о временном ящике"""
    acc = TempMailAccount(
        user_id=user_id,
        email=email,
        password=password,
        token=token,
        account_id=account_id,
        provider=provider,
    )
    session.add(acc)
    await session.commit()
    await session.refresh(acc)
    return acc


async def get_user_accounts(
    session: AsyncSession, user_id: int,
) -> list[TempMailAccount]:
    """Все ящики юзера, сортировка по дате создания (новые первые)"""
    result = await session.execute(
        select(TempMailAccount)
        .where(TempMailAccount.user_id == user_id)
        .order_by(TempMailAccount.created_at.desc())
    )
    return list(result.scalars().all())


async def count_user_accounts(session: AsyncSession, user_id: int) -> int:
    """Количество ящиков юзера"""
    result = await session.execute(
        select(sa_func.count(TempMailAccount.id))
        .where(TempMailAccount.user_id == user_id)
    )
    return result.scalar() or 0


async def get_account_by_id(
    session: AsyncSession, account_pk: int,
) -> TempMailAccount | None:
    """Получить ящик по PK (id из БД, не account_id из mail.tm)"""
    result = await session.execute(
        select(TempMailAccount).where(TempMailAccount.id == account_pk)
    )
    return result.scalar_one_or_none()


async def update_token(
    session: AsyncSession, account_pk: int, new_token: str,
) -> None:
    """Обновить JWT-токен после перевыпуска"""
    acc = await get_account_by_id(session, account_pk)
    if acc:
        acc.token = new_token
        await session.commit()


async def update_last_checked(
    session: AsyncSession, account_pk: int,
) -> None:
    """Отметить время последней проверки входящих"""
    acc = await get_account_by_id(session, account_pk)
    if acc:
        acc.last_checked_at = datetime.now(timezone.utc)
        await session.commit()


async def delete_tempmail_account(
    session: AsyncSession, account_pk: int,
) -> bool:
    """Удалить запись о ящике из БД. True если был удалён."""
    acc = await get_account_by_id(session, account_pk)
    if not acc:
        return False
    await session.delete(acc)
    await session.commit()
    return True


async def delete_accounts_older_than(
    session: AsyncSession, days: int,
) -> list[TempMailAccount]:
    """Вернуть список неактивных ящиков и удалить их из БД.

    Критерий "просроченности" — неактивность (а не возраст):
      - если `last_checked_at` заполнен → сравниваем его с cutoff;
      - если `last_checked_at IS NULL` → используем `created_at` (ящик ни
        разу не проверяли, значит юзер им не пользуется).

    Возвращаем объекты до удаления, чтобы вызвавший код смог параллельно
    удалить их и на стороне mail.tm.
    """
    from sqlalchemy import or_

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await session.execute(
        select(TempMailAccount).where(
            or_(
                TempMailAccount.last_checked_at < cutoff,
                (TempMailAccount.last_checked_at.is_(None))
                & (TempMailAccount.created_at < cutoff),
            )
        )
    )
    stale = list(result.scalars().all())
    if stale:
        await session.execute(
            delete(TempMailAccount).where(
                TempMailAccount.id.in_([a.id for a in stale])
            )
        )
        await session.commit()
    return stale
