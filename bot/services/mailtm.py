"""Клиент для mail.tm API — одноразовая почта.

TODO fallback: при недоступности mail.tm рассмотреть tempmail.lol или guerrillamail
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)

MAILTM_BASE_URL = "https://api.mail.tm"
REQUEST_TIMEOUT = 15  # секунд


class MailTmError(Exception):
    """Базовая ошибка mail.tm"""


class MailTmAuthError(MailTmError):
    """401 Unauthorized — токен протух или аккаунт удалён"""


class MailTmRateLimitError(MailTmError):
    """429 Too Many Requests"""


class MailTmServiceError(MailTmError):
    """5xx или сеть/таймаут"""


class MailTmClient:
    """Асинхронный клиент mail.tm. Использует общий aiohttp.ClientSession,
    создаваемый в main.py при старте бота и закрываемый при shutdown.
    """

    def __init__(self, session: aiohttp.ClientSession):
        self._session = session
        # mail.tm заявляет ~8 req/sec, держим 5 параллельных запросов
        self._semaphore = asyncio.Semaphore(5)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        token: str | None = None,
    ) -> Any:
        headers = {"Accept": "application/ld+json"}
        if json is not None:
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = f"Bearer {token}"

        url = f"{MAILTM_BASE_URL}{path}"
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

        async with self._semaphore:
            try:
                async with self._session.request(
                    method, url, json=json, headers=headers, timeout=timeout
                ) as resp:
                    status = resp.status
                    if status == 401:
                        raise MailTmAuthError(f"401 Unauthorized: {path}")
                    if status == 429:
                        raise MailTmRateLimitError(f"429 Rate Limited: {path}")
                    if status >= 500:
                        text = await resp.text()
                        raise MailTmServiceError(f"{status} {path}: {text[:200]}")
                    if status >= 400:
                        text = await resp.text()
                        raise MailTmError(f"{status} {path}: {text[:200]}")
                    # 204 No Content (DELETE)
                    if status == 204 or resp.content_length == 0:
                        return None
                    return await resp.json(content_type=None)
            except asyncio.TimeoutError as exc:
                raise MailTmServiceError(f"timeout on {path}") from exc
            except aiohttp.ClientError as exc:
                raise MailTmServiceError(f"client error on {path}: {exc}") from exc

    # --- публичные методы ---

    async def get_domains(self) -> list[dict]:
        """Список доступных доменов. Возвращает список dict с полями
        domain/id/isActive/isPrivate."""
        data = await self._request("GET", "/domains")
        # hydra (JSON-LD) формат: {"hydra:member": [...]} или список напрямую
        if isinstance(data, dict):
            return data.get("hydra:member", [])
        return data or []

    async def get_active_domain(self) -> str:
        """Возвращает первый активный домен (строка)."""
        domains = await self.get_domains()
        for d in domains:
            if d.get("isActive") and not d.get("isPrivate"):
                return d["domain"]
        if domains:
            return domains[0]["domain"]
        raise MailTmServiceError("нет доступных доменов mail.tm")

    async def create_account(self, address: str, password: str) -> dict:
        """POST /accounts → {id, address, ...}"""
        return await self._request(
            "POST", "/accounts",
            json={"address": address, "password": password},
        )

    async def get_token(self, address: str, password: str) -> str:
        """POST /token → JWT"""
        data = await self._request(
            "POST", "/token",
            json={"address": address, "password": password},
        )
        token = data.get("token") if isinstance(data, dict) else None
        if not token:
            raise MailTmServiceError("mail.tm /token: нет поля token")
        return token

    async def get_messages(self, token: str, page: int = 1) -> list[dict]:
        """GET /messages?page=N → список {id, from, subject, intro, seen, createdAt}"""
        data = await self._request("GET", f"/messages?page={page}", token=token)
        if isinstance(data, dict):
            return data.get("hydra:member", [])
        return data or []

    async def get_message(self, token: str, message_id: str) -> dict:
        """GET /messages/{id} → полное письмо с text/html/attachments"""
        return await self._request("GET", f"/messages/{message_id}", token=token)

    async def delete_account(self, token: str, account_id: str) -> bool:
        """DELETE /accounts/{id}. Возвращает True если удалён (или уже не существовал)."""
        try:
            await self._request("DELETE", f"/accounts/{account_id}", token=token)
            return True
        except MailTmAuthError:
            # аккаунта уже нет — считаем успехом
            return True
        except MailTmError as exc:
            logger.warning("delete_account failed for %s: %s", account_id, exc)
            return False
