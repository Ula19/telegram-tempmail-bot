"""Хэндлер временной почты — создание ящика, проверка входящих, удаление."""
from __future__ import annotations

import html
import logging
import re
from datetime import datetime, timezone
from typing import Any

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.database import async_session
from bot.database.crud import (
    count_user_accounts,
    create_tempmail_account,
    delete_tempmail_account,
    get_account_by_id,
    get_user_accounts,
    get_user_language,
    get_or_create_user,
    update_last_checked,
    update_token,
)
from bot.database.models import TempMailAccount
from bot.i18n import t
from bot.keyboards.inline import (
    get_back_keyboard,
    get_start_keyboard,
    get_tempmail_account_menu_kb,
    get_tempmail_accounts_list_kb,
    get_tempmail_confirm_delete_kb,
    get_tempmail_empty_kb,
    get_tempmail_inbox_kb,
    get_tempmail_message_view_kb,
)
from bot.services.providers import (
    InboxProvider,
    ProviderAuthError,
    ProviderError,
    ProviderRateLimitError,
    ProviderRouter,
    ProviderServiceError,
)
from bot.services.providers.mailtm import MailTmProvider

logger = logging.getLogger(__name__)
router = Router()

MAX_ACCOUNTS_PER_USER = 5
CHECK_COOLDOWN_SECONDS = 5


async def _safe_edit(message: Message, text: str, **kwargs: Any) -> None:
    """edit_text, проглатывающий 'message is not modified'."""
    try:
        await message.edit_text(text, **kwargs)
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc):
            raise
# Безопасный порог: Telegram считает по UTF-16 code units (лимит 4096).
# Берём 3900 UTF-16 code units с запасом.
TELEGRAM_UTF16_LIMIT = 3900

# Блокировка одновременного создания ящика одним юзером (защита от TOCTOU)
_creating: set[int] = set()


class TempMailStates(StatesGroup):
    waiting_delete_confirm = State()


# === Утилиты ===

def _get_router() -> ProviderRouter | None:
    """Достаёт ProviderRouter из глобала main.py."""
    from bot import main as _main
    return getattr(_main, "provider_router", None)


def _strip_html(text: str) -> str:
    """Грубо вырезает HTML-теги и декодирует entities."""
    if not text:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return text.strip()


def _extract_text(message: dict) -> str:
    """Берёт text, иначе конвертит html в текст."""
    text = message.get("text") or ""
    if not text.strip():
        html_body = message.get("html")
        if isinstance(html_body, list):
            html_body = "\n".join(html_body)
        text = _strip_html(html_body or "")
    return text


def _format_from(from_obj: Any) -> str:
    """mail.tm отдаёт from как {address, name}"""
    if isinstance(from_obj, dict):
        addr = from_obj.get("address", "")
        name = from_obj.get("name", "")
        if name and addr:
            return f"{name} <{addr}>"
        return addr or name or "?"
    return str(from_obj or "?")


def _service_error_i18n(exc: Exception) -> str:
    """Маппинг исключения на i18n ключ"""
    if isinstance(exc, ProviderRateLimitError):
        return "tempmail.rate_limited"
    return "tempmail.service_unavailable"


def _utf16_len(s: str) -> int:
    """Длина строки в UTF-16 code units (как считает Telegram)."""
    return len(s.encode("utf-16-le")) // 2


def _truncate_utf16(s: str, limit: int) -> str:
    """Обрезает строку до `limit` UTF-16 code units, добавляет суффикс."""
    if _utf16_len(s) <= limit:
        return s
    suffix = "\n\n..."
    suffix_len = _utf16_len(suffix)
    # Отрезаем хвост, пока не влезаем
    result = s
    while _utf16_len(result) + suffix_len > limit and result:
        # обрезаем по ~5% каждый шаг для скорости
        cut = max(1, len(result) // 20)
        result = result[:-cut]
    return result + suffix


def _account_to_dto(acc: TempMailAccount):
    """Конвертит ORM TempMailAccount → InboxAccount (DTO для провайдеров)."""
    from bot.services.providers import InboxAccount
    return InboxAccount(
        provider=acc.provider or "mailtm",
        email=acc.email,
        password=acc.password or "",
        token=acc.token,
        account_id=acc.account_id,
        raw_data={},
    )


async def _maybe_refresh_token(
    session, provider: InboxProvider, account: TempMailAccount,
) -> str | None:
    """Перевыпуск JWT. Доступно только для mail.tm (у guerrillamail
    sid_token не перевыпустить — нужно создавать новый ящик)."""
    if not isinstance(provider, MailTmProvider):
        return None
    if not account.password:
        return None
    try:
        dto = _account_to_dto(account)
        new_token = await provider.refresh_token(dto)
    except ProviderError as exc:
        logger.warning("Token refresh failed for %s: %s", account.email, exc)
        return None
    await update_token(session, account.id, new_token)
    account.token = new_token
    return new_token


# === Handlers ===

@router.callback_query(F.data == "new_tempmail")
@router.callback_query(F.data == "tempmail:new")
async def create_new_account(callback: CallbackQuery, state: FSMContext) -> None:
    """Создание нового ящика"""
    await state.clear()
    user_id = callback.from_user.id
    logger.info(
        "create_new_account triggered: user_id=%s callback_data=%r message_id=%s",
        user_id, callback.data, callback.message.message_id if callback.message else None,
    )
    router = _get_router()

    # Защита от двойного клика / параллельного создания
    if user_id in _creating:
        async with async_session() as session:
            lang = await get_user_language(session, user_id)
        await callback.answer(t("tempmail.rate_limited", lang), show_alert=False)
        return

    async with async_session() as session:
        lang = await get_user_language(session, user_id)
        await get_or_create_user(
            session=session,
            telegram_id=user_id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name,
            language=lang,
        )
        cnt = await count_user_accounts(session, user_id)

    if cnt >= MAX_ACCOUNTS_PER_USER:
        await callback.answer(t("tempmail.limit_reached", lang), show_alert=True)
        return

    if router is None:
        await callback.answer(t("tempmail.service_unavailable", lang), show_alert=True)
        return

    await callback.answer()
    _creating.add(user_id)
    try:
        # Идём по цепочке провайдеров: mail.tm → guerrillamail.
        # Каждый запрос проходит цепочку с нуля — если mail.tm заработал,
        # fallback не нужен.
        dto = None
        provider = None
        last_exc: ProviderError | None = None
        for prv in router.chain:
            try:
                dto = await prv.create_inbox()
                provider = prv
                break
            except ProviderServiceError as exc:
                logger.warning("create_inbox via %s failed: %s", prv.name, exc)
                last_exc = exc
                continue
            except ProviderError as exc:
                logger.warning("create_inbox via %s error: %s", prv.name, exc)
                last_exc = exc
                break

        if dto is None or provider is None:
            await _safe_edit(callback.message,
                t(_service_error_i18n(last_exc) if last_exc else "tempmail.service_unavailable", lang),
                reply_markup=get_back_keyboard(lang),
                parse_mode="HTML",
            )
            return

        # Повторная проверка лимита ПОСЛЕ создания (race с параллельными сессиями)
        async with async_session() as session:
            cnt_after = await count_user_accounts(session, user_id)
            if cnt_after >= MAX_ACCOUNTS_PER_USER:
                # откатываем — удаляем на стороне провайдера
                try:
                    await provider.delete_inbox(dto)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Rollback delete_inbox failed: %s", exc)
                await _safe_edit(callback.message,
                    t("tempmail.limit_reached", lang),
                    reply_markup=get_back_keyboard(lang),
                    parse_mode="HTML",
                )
                return

            acc = await create_tempmail_account(
                session=session,
                user_id=user_id,
                email=dto.email,
                password=dto.password,
                token=dto.token,
                account_id=dto.account_id,
                provider=provider.name,
            )
            # инкрементим счётчик
            user = await get_or_create_user(
                session=session,
                telegram_id=user_id,
                username=callback.from_user.username,
                full_name=callback.from_user.full_name,
            )
            user.download_count = (user.download_count or 0) + 1
            await session.commit()

        await _safe_edit(callback.message,
            t("tempmail.created", lang, email=dto.email),
            reply_markup=get_tempmail_account_menu_kb(acc.id, lang),
            parse_mode="HTML",
        )
    finally:
        _creating.discard(user_id)


@router.callback_query(F.data.startswith("tempmail:list"))
async def show_accounts_list(callback: CallbackQuery, state: FSMContext) -> None:
    """Список моих ящиков"""
    await state.clear()
    user_id = callback.from_user.id
    async with async_session() as session:
        lang = await get_user_language(session, user_id)
        accounts = await get_user_accounts(session, user_id)

    if not accounts:
        await callback.answer()
        await _safe_edit(callback.message, 
            t("tempmail.welcome_hint", lang),
            reply_markup=get_tempmail_empty_kb(lang),
            parse_mode="HTML",
        )
        return

    await callback.answer()
    await _safe_edit(callback.message, 
        t("tempmail.my_accounts_header", lang),
        reply_markup=get_tempmail_accounts_list_kb(accounts, lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("tempmail:account:"))
async def show_account_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Меню конкретного ящика"""
    await state.clear()
    try:
        acc_pk = int(callback.data.rsplit(":", 1)[-1])
    except ValueError:
        await callback.answer()
        return

    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)
        acc = await get_account_by_id(session, acc_pk)

    if not acc or acc.user_id != callback.from_user.id:
        await callback.answer(t("tempmail.not_found", lang), show_alert=True)
        return

    await callback.answer()
    await _safe_edit(callback.message, 
        t("tempmail.account_menu", lang, email=acc.email),
        reply_markup=get_tempmail_account_menu_kb(acc.id, lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("tempmail:check:"))
@router.callback_query(F.data.startswith("tempmail:inbox:"))
async def check_inbox(callback: CallbackQuery) -> None:
    """Проверить входящие для ящика.

    `tempmail:check:N` — нажатие «Проверить почту», с cooldown 10 сек.
    `tempmail:inbox:N` — возврат «Назад к списку» из письма, без cooldown.
    """
    user_id = callback.from_user.id
    skip_cooldown = callback.data.startswith("tempmail:inbox:")
    try:
        acc_pk = int(callback.data.rsplit(":", 1)[-1])
    except ValueError:
        await callback.answer()
        return

    router = _get_router()

    async with async_session() as session:
        lang = await get_user_language(session, user_id)
        acc = await get_account_by_id(session, acc_pk)

        if not acc or acc.user_id != user_id:
            await callback.answer(t("tempmail.not_found", lang), show_alert=True)
            return

        # Анти-спам: per-account cooldown на основе last_checked_at в БД
        if not skip_cooldown and acc.last_checked_at is not None:
            last = acc.last_checked_at
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            delta = (datetime.now(timezone.utc) - last).total_seconds()
            if delta < CHECK_COOLDOWN_SECONDS:
                await callback.answer(
                    t("tempmail.check_too_fast", lang), show_alert=True,
                )
                return

        if router is None:
            await callback.answer(t("tempmail.service_unavailable", lang), show_alert=True)
            return

        provider = router.get_provider_by_name(acc.provider or "mailtm")
        dto = _account_to_dto(acc)

        # Попытка получить письма; при auth-fail — один раз пробуем перевыпустить токен (только mailtm)
        messages_dto = None
        try:
            messages_dto = await provider.list_messages(dto)
        except ProviderAuthError:
            new_token = await _maybe_refresh_token(session, provider, acc)
            if new_token is None:
                await delete_tempmail_account(session, acc.id)
                await _safe_edit(callback.message,
                    t("tempmail.account_expired", lang),
                    reply_markup=get_back_keyboard(lang),
                    parse_mode="HTML",
                )
                await callback.answer()
                return
            dto.token = new_token
            try:
                messages_dto = await provider.list_messages(dto)
            except ProviderError as exc:
                await callback.answer(t(_service_error_i18n(exc), lang), show_alert=True)
                return
        except ProviderServiceError as exc:
            logger.warning("check_inbox service-fail: %s", exc)
            await callback.answer(t(_service_error_i18n(exc), lang), show_alert=True)
            return
        except ProviderError as exc:
            logger.warning("check_inbox failed: %s", exc)
            await callback.answer(t(_service_error_i18n(exc), lang), show_alert=True)
            return

        await update_last_checked(session, acc.id)
        # совместимость со старым кодом: messages должен быть list[dict]
        messages = [
            {
                "id": m.id,
                "from": {"address": m.from_addr},
                "subject": m.subject,
                "intro": m.text,
                "createdAt": m.date,
            }
            for m in messages_dto
        ]

    await callback.answer()

    if not messages:
        await _safe_edit(callback.message, 
            t("tempmail.no_messages", lang) + f"\n\n<code>{acc.email}</code>",
            reply_markup=get_tempmail_account_menu_kb(acc.id, lang),
            parse_mode="HTML",
        )
        return

    header = t("tempmail.messages_header", lang, count=len(messages))
    await _safe_edit(callback.message, 
        f"{header}\n\n<code>{acc.email}</code>",
        reply_markup=get_tempmail_inbox_kb(acc.id, messages, lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("tempmail:msg:"))
async def view_message(callback: CallbackQuery) -> None:
    """Просмотр конкретного письма"""
    parts = callback.data.split(":", 3)
    # format: tempmail:msg:<acc_pk>:<message_id>
    if len(parts) < 4:
        await callback.answer()
        return
    try:
        acc_pk = int(parts[2])
    except ValueError:
        await callback.answer()
        return
    message_id = parts[3]

    user_id = callback.from_user.id
    router = _get_router()

    async with async_session() as session:
        lang = await get_user_language(session, user_id)
        acc = await get_account_by_id(session, acc_pk)

        if not acc or acc.user_id != user_id:
            await callback.answer(t("tempmail.not_found", lang), show_alert=True)
            return

        if router is None:
            await callback.answer(t("tempmail.service_unavailable", lang), show_alert=True)
            return

        provider = router.get_provider_by_name(acc.provider or "mailtm")
        dto = _account_to_dto(acc)

        try:
            message_dto = await provider.get_message(dto, message_id)
        except ProviderAuthError:
            new_token = await _maybe_refresh_token(session, provider, acc)
            if new_token is None:
                await delete_tempmail_account(session, acc.id)
                await _safe_edit(callback.message,
                    t("tempmail.account_expired", lang),
                    reply_markup=get_back_keyboard(lang),
                    parse_mode="HTML",
                )
                await callback.answer()
                return
            dto.token = new_token
            try:
                message_dto = await provider.get_message(dto, message_id)
            except ProviderError as exc:
                await _safe_edit(callback.message,
                    t(_service_error_i18n(exc), lang),
                    reply_markup=get_back_keyboard(lang),
                    parse_mode="HTML",
                )
                await callback.answer()
                return
        except ProviderServiceError as exc:
            logger.warning("view_message service-fail: %s", exc)
            await callback.answer(t(_service_error_i18n(exc), lang), show_alert=True)
            return
        except ProviderError as exc:
            logger.warning("view_message failed: %s", exc)
            await callback.answer(t(_service_error_i18n(exc), lang), show_alert=True)
            return

    frm = message_dto.from_addr
    subject = (message_dto.subject or t("tempmail.no_subject", lang)).strip()
    date = message_dto.date
    text_body = message_dto.text or _strip_html(message_dto.html)
    # для совместимости с дальнейшим кодом (hasAttachments)
    message = {"hasAttachments": message_dto.has_attachments}

    body_html = html.escape(text_body)
    rendered = t(
        "tempmail.message_view", lang,
        from_=html.escape(frm),
        subject=html.escape(subject),
        date=html.escape(str(date)),
        text=body_html,
    )

    if message.get("hasAttachments") or message.get("attachments"):
        rendered += t("tempmail.has_attachments", lang)

    # Безопасная обрезка по UTF-16 code units (Telegram лимит 4096)
    rendered = _truncate_utf16(rendered, TELEGRAM_UTF16_LIMIT)

    await callback.answer()
    await _safe_edit(callback.message, 
        rendered,
        reply_markup=get_tempmail_message_view_kb(acc_pk, lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("tempmail:delete:"))
async def ask_delete(callback: CallbackQuery, state: FSMContext) -> None:
    """Спросить подтверждение удаления"""
    try:
        acc_pk = int(callback.data.rsplit(":", 1)[-1])
    except ValueError:
        await callback.answer()
        return

    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)
        acc = await get_account_by_id(session, acc_pk)

    if not acc or acc.user_id != callback.from_user.id:
        await callback.answer(t("tempmail.not_found", lang), show_alert=True)
        return

    await state.set_state(TempMailStates.waiting_delete_confirm)
    await callback.answer()
    await _safe_edit(callback.message, 
        t("tempmail.confirm_delete", lang, email=acc.email),
        reply_markup=get_tempmail_confirm_delete_kb(acc.id, lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("tempmail:delete_confirm:"))
async def do_delete(callback: CallbackQuery, state: FSMContext) -> None:
    """Подтверждённое удаление"""
    await state.clear()
    logger.info(
        "do_delete triggered: user_id=%s callback_data=%r",
        callback.from_user.id, callback.data,
    )
    try:
        acc_pk = int(callback.data.rsplit(":", 1)[-1])
    except ValueError:
        await callback.answer()
        return

    user_id = callback.from_user.id
    router = _get_router()

    async with async_session() as session:
        lang = await get_user_language(session, user_id)
        acc = await get_account_by_id(session, acc_pk)
        if not acc or acc.user_id != user_id:
            await callback.answer(t("tempmail.not_found", lang), show_alert=True)
            return
        dto_to_delete = _account_to_dto(acc)
        provider_name = acc.provider or "mailtm"

    # Сначала удаляем на стороне провайдера (игнорируем 404/сеть — логируем),
    # затем локально — чтобы юзер всегда мог избавиться из записи.
    if router is not None and dto_to_delete.account_id:
        try:
            provider = router.get_provider_by_name(provider_name)
            await provider.delete_inbox(dto_to_delete)
        except Exception as exc:  # noqa: BLE001
            logger.warning("provider delete_inbox failed: %s", exc)

    async with async_session() as session:
        await delete_tempmail_account(session, acc_pk)
        lang = await get_user_language(session, user_id)
        cnt = await count_user_accounts(session, user_id)

    await callback.answer(t("tempmail.deleted", lang), show_alert=False)
    welcome = t("start.welcome", lang, name=callback.from_user.first_name)
    await _safe_edit(callback.message,
        welcome,
        reply_markup=get_start_keyboard(
            user_id=user_id, lang=lang, accounts_count=cnt,
        ),
        parse_mode="HTML",
    )
