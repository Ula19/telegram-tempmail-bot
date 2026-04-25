"""Провайдеры временной почты — единый интерфейс над mail.tm и guerrillamail.

Используется для прозрачного fallback: при недоступности mail.tm
ProviderRouter переключает создание новых ящиков на guerrillamail.
"""
from bot.services.providers.base import (
    InboxAccount,
    InboxMessage,
    InboxProvider,
    ProviderAuthError,
    ProviderError,
    ProviderRateLimitError,
    ProviderServiceError,
)
from bot.services.providers.guerrillamail import GuerrillaMailProvider
from bot.services.providers.mailtm import MailTmProvider
from bot.services.providers.router import ProviderRouter

__all__ = [
    "InboxAccount",
    "InboxMessage",
    "InboxProvider",
    "ProviderAuthError",
    "ProviderError",
    "ProviderRateLimitError",
    "ProviderServiceError",
    "MailTmProvider",
    "GuerrillaMailProvider",
    "ProviderRouter",
]
