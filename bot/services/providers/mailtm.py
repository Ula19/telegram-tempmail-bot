"""Адаптер MailTmClient → InboxProvider (единый интерфейс)."""
from __future__ import annotations

import logging
import secrets
from typing import Any

from bot.services.mailtm import (
    MailTmAuthError,
    MailTmClient,
    MailTmError,
    MailTmRateLimitError,
    MailTmServiceError,
)
from bot.services.providers.base import (
    InboxAccount,
    InboxMessage,
    ProviderAuthError,
    ProviderError,
    ProviderRateLimitError,
    ProviderServiceError,
)

logger = logging.getLogger(__name__)


def _wrap(exc: MailTmError) -> ProviderError:
    """Маппинг исключений mail.tm на провайдер-нейтральные."""
    if isinstance(exc, MailTmAuthError):
        return ProviderAuthError(str(exc))
    if isinstance(exc, MailTmRateLimitError):
        return ProviderRateLimitError(str(exc))
    if isinstance(exc, MailTmServiceError):
        return ProviderServiceError(str(exc))
    return ProviderError(str(exc))


def _format_from(from_obj: Any) -> str:
    if isinstance(from_obj, dict):
        addr = from_obj.get("address", "")
        name = from_obj.get("name", "")
        if name and addr:
            return f"{name} <{addr}>"
        return addr or name or "?"
    return str(from_obj or "?")


def _msg_from_dict(data: dict) -> InboxMessage:
    html_body = data.get("html") or ""
    if isinstance(html_body, list):
        html_body = "\n".join(html_body)
    return InboxMessage(
        id=str(data.get("id", "")),
        from_addr=_format_from(data.get("from")),
        subject=(data.get("subject") or "").strip(),
        text=data.get("intro") or data.get("text") or "",
        html=html_body or "",
        date=str(data.get("createdAt") or ""),
        has_attachments=bool(
            data.get("hasAttachments") or data.get("attachments")
        ),
    )


class MailTmProvider:
    """Адаптер mail.tm под единый интерфейс InboxProvider."""

    name = "mailtm"

    def __init__(self, client: MailTmClient):
        self._client = client

    async def create_inbox(self) -> InboxAccount:
        try:
            domain = await self._client.get_active_domain()
            local = secrets.token_hex(8)
            password = secrets.token_urlsafe(12)
            address = f"{local}@{domain}"
            acc_data = await self._client.create_account(address, password)
            account_id = acc_data.get("id", "")
            token = await self._client.get_token(address, password)
        except MailTmError as exc:
            raise _wrap(exc) from exc

        return InboxAccount(
            provider=self.name,
            email=address,
            password=password,
            token=token,
            account_id=account_id,
            raw_data={},
        )

    async def list_messages(self, account: InboxAccount) -> list[InboxMessage]:
        try:
            raw = await self._client.get_messages(account.token)
        except MailTmError as exc:
            raise _wrap(exc) from exc
        # mail.tm в /messages не отдаёт html/text, только intro/subject
        return [_msg_from_dict(m) for m in raw]

    async def get_message(
        self, account: InboxAccount, message_id: str,
    ) -> InboxMessage:
        try:
            raw = await self._client.get_message(account.token, message_id)
        except MailTmError as exc:
            raise _wrap(exc) from exc
        msg = _msg_from_dict(raw)
        # подменяем text на полный (а не intro)
        full_text = raw.get("text") or ""
        if full_text:
            msg.text = full_text
        return msg

    async def refresh_token(self, account: InboxAccount) -> str:
        """Перевыпустить JWT по паролю. Возвращает новый токен."""
        try:
            new_token = await self._client.get_token(
                account.email, account.password,
            )
        except MailTmError as exc:
            raise _wrap(exc) from exc
        account.token = new_token
        return new_token

    async def delete_inbox(self, account: InboxAccount) -> bool:
        try:
            return await self._client.delete_account(
                account.token, account.account_id,
            )
        except MailTmError as exc:
            logger.warning("mailtm delete_inbox failed: %s", exc)
            return False

    async def health_check(self) -> bool:
        """Быстрый GET /domains. True если 2xx."""
        try:
            await self._client.get_domains()
            return True
        except MailTmError as exc:
            logger.debug("mailtm health_check failed: %s", exc)
            return False
