"""Маршрутизатор провайдеров: mail.tm → guerrillamail.

Логика простая, без health-state:
- Для НОВЫХ ящиков: пробуем mail.tm; при ProviderServiceError/таймауте
  идём по цепочке дальше (guerrillamail).
- Для СУЩЕСТВУЮЩИХ ящиков — провайдер берётся по имени из acc.provider.
"""
from __future__ import annotations

import logging

from bot.services.providers.base import InboxProvider
from bot.services.providers.guerrillamail import GuerrillaMailProvider
from bot.services.providers.mailtm import MailTmProvider

logger = logging.getLogger(__name__)


class ProviderRouter:
    def __init__(
        self,
        mailtm: MailTmProvider,
        guerrillamail: GuerrillaMailProvider,
    ):
        self._mailtm = mailtm
        self._guerrillamail = guerrillamail

    @property
    def chain(self) -> list[InboxProvider]:
        """Цепочка провайдеров для нового ящика."""
        return [self._mailtm, self._guerrillamail]

    def get_provider_by_name(self, name: str) -> InboxProvider:
        if name == self._mailtm.name:
            return self._mailtm
        if name == self._guerrillamail.name:
            return self._guerrillamail
        logger.warning("Unknown provider name=%r, fallback to mailtm", name)
        return self._mailtm

    @property
    def mailtm(self) -> MailTmProvider:
        return self._mailtm

    @property
    def guerrillamail(self) -> GuerrillaMailProvider:
        return self._guerrillamail
