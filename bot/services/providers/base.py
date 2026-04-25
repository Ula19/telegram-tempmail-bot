"""Базовые типы и интерфейс провайдеров временной почты."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


# === Исключения (общие для всех провайдеров) ===

class ProviderError(Exception):
    """Базовая ошибка провайдера временной почты."""


class ProviderAuthError(ProviderError):
    """401 / истёкшая сессия → нужно перевыпустить токен или ящик протух."""


class ProviderRateLimitError(ProviderError):
    """429 Too Many Requests."""


class ProviderServiceError(ProviderError):
    """5xx, таймаут, сеть. Сигнал для router'а пометить провайдер unhealthy."""


# === Dataclasses (нейтральные DTO) ===

@dataclass
class InboxAccount:
    """Унифицированное представление аккаунта почты.

    provider     — имя провайдера ("mailtm" или "guerrillamail")
    email        — адрес ящика
    password     — пароль (для mail.tm; у guerrillamail пустой)
    token        — JWT (mail.tm) или sid_token (guerrillamail)
    account_id   — id для DELETE (mail.tm) или sid_token дубликат (guerrillamail)
    raw_data     — провайдер-специфичные поля (alias, seq и пр.)
    """
    provider: str
    email: str
    password: str
    token: str
    account_id: str
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class InboxMessage:
    """Унифицированное письмо."""
    id: str
    from_addr: str
    subject: str
    text: str
    html: str
    date: str
    has_attachments: bool = False


# === Интерфейс провайдера ===

@runtime_checkable
class InboxProvider(Protocol):
    """Интерфейс провайдера временной почты."""

    name: str

    async def create_inbox(self) -> InboxAccount:
        ...

    async def list_messages(self, account: InboxAccount) -> list[InboxMessage]:
        ...

    async def get_message(
        self, account: InboxAccount, message_id: str,
    ) -> InboxMessage:
        ...

    async def delete_inbox(self, account: InboxAccount) -> bool:
        ...

    async def health_check(self) -> bool:
        ...
