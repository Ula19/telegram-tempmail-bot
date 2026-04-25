"""Резервный провайдер — guerrillamail.com (публичный API без ключей).

API: https://api.guerrillamail.com/ajax.php
- f=get_email_address      → создать ящик, получить sid_token и адрес
- f=check_email&seq=N      → список новых писем (с excerpt)
- f=fetch_email&email_id=I → полное письмо (mail_body)
- f=forget_me              → удалить (отвязать) адрес
"""
from __future__ import annotations

import asyncio
import logging
import re
from html import unescape
from typing import Any

import aiohttp

from bot.services.providers.base import (
    InboxAccount,
    InboxMessage,
    ProviderAuthError,
    ProviderError,
    ProviderRateLimitError,
    ProviderServiceError,
)

logger = logging.getLogger(__name__)

GUERRILLA_BASE_URL = "https://api.guerrillamail.com/ajax.php"
REQUEST_TIMEOUT = 15  # секунд


def _strip_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    return text.strip()


class GuerrillaMailProvider:
    """Адаптер guerrillamail.com под единый интерфейс InboxProvider."""

    name = "guerrillamail"

    def __init__(self, session: aiohttp.ClientSession):
        self._session = session
        self._semaphore = asyncio.Semaphore(5)

    async def _request(self, params: dict[str, Any]) -> dict:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with self._semaphore:
            try:
                async with self._session.get(
                    GUERRILLA_BASE_URL,
                    params=params,
                    timeout=timeout,
                ) as resp:
                    status = resp.status
                    if status == 429:
                        raise ProviderRateLimitError(
                            f"guerrillamail 429: {params.get('f')}"
                        )
                    if status >= 500:
                        body = await resp.text()
                        raise ProviderServiceError(
                            f"guerrillamail {status}: {body[:200]}"
                        )
                    if status >= 400:
                        body = await resp.text()
                        raise ProviderError(
                            f"guerrillamail {status}: {body[:200]}"
                        )
                    return await resp.json(content_type=None) or {}
            except asyncio.TimeoutError as exc:
                raise ProviderServiceError(
                    f"guerrillamail timeout: {params.get('f')}"
                ) from exc
            except aiohttp.ClientError as exc:
                raise ProviderServiceError(
                    f"guerrillamail client error: {exc}"
                ) from exc

    # === API ===

    async def create_inbox(self) -> InboxAccount:
        data = await self._request({
            "f": "get_email_address",
            "lang": "en",
        })
        email = data.get("email_addr") or ""
        sid_token = data.get("sid_token") or ""
        if not email or not sid_token:
            raise ProviderServiceError(
                "guerrillamail: пустой email_addr или sid_token"
            )
        return InboxAccount(
            provider=self.name,
            email=email,
            password="",  # session-based
            token=sid_token,
            account_id=sid_token,  # для unified DELETE — используем sid_token
            raw_data={
                "alias": data.get("alias") or "",
                "email_timestamp": data.get("email_timestamp") or 0,
            },
        )

    async def list_messages(self, account: InboxAccount) -> list[InboxMessage]:
        data = await self._request({
            "f": "check_email",
            "seq": "0",
            "sid_token": account.token,
        })
        # guerrillamail возвращает {list: [...]} либо {auth: {success: false}}
        auth = data.get("auth") or {}
        if isinstance(auth, dict) and auth.get("success") is False:
            raise ProviderAuthError("guerrillamail: sid_token expired")
        items = data.get("list") or []
        result: list[InboxMessage] = []
        for m in items:
            result.append(InboxMessage(
                id=str(m.get("mail_id", "")),
                from_addr=str(m.get("mail_from") or "?"),
                subject=(m.get("mail_subject") or "").strip(),
                text=m.get("mail_excerpt") or "",
                html="",
                date=str(m.get("mail_timestamp") or m.get("mail_date") or ""),
                has_attachments=False,
            ))
        return result

    async def get_message(
        self, account: InboxAccount, message_id: str,
    ) -> InboxMessage:
        data = await self._request({
            "f": "fetch_email",
            "email_id": message_id,
            "sid_token": account.token,
        })
        if not data or "mail_id" not in data:
            # API возвращает пустоту/ошибку при истёкшей сессии
            raise ProviderAuthError(
                "guerrillamail: fetch_email empty (session expired?)"
            )
        body = data.get("mail_body") or ""
        # mail.body может быть HTML — извлечём text
        text = _strip_html(body) if "<" in body else body
        return InboxMessage(
            id=str(data.get("mail_id", message_id)),
            from_addr=str(data.get("mail_from") or "?"),
            subject=(data.get("mail_subject") or "").strip(),
            text=text,
            html=body,
            date=str(data.get("mail_timestamp") or data.get("mail_date") or ""),
            has_attachments=False,
        )

    async def delete_inbox(self, account: InboxAccount) -> bool:
        try:
            await self._request({
                "f": "forget_me",
                "email_addr": account.email,
                "sid_token": account.token,
            })
            return True
        except ProviderError as exc:
            logger.warning("guerrillamail delete_inbox failed: %s", exc)
            return False

    async def health_check(self) -> bool:
        """Дёргаем легковесный get_email_address — но это создаёт ящик.
        Проще: дёрнуть check_email с пустым sid_token — API вернёт ошибку
        авторизации, но сам сервис будет жив (status 200). Если 5xx/timeout —
        провайдер мёртв."""
        try:
            await self._request({
                "f": "check_email",
                "seq": "0",
                "sid_token": "healthcheck_dummy",
            })
            return True
        except ProviderAuthError:
            # сервис ответил, просто sid_token невалидный — это норма
            return True
        except ProviderServiceError:
            return False
        except ProviderError:
            # 4xx — сервис жив
            return True
