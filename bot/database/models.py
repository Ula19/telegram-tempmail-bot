"""Модели базы данных — User, Channel"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    """Пользователь бота"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    # когда первый раз зашёл в бота
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # сколько ящиков создал (используется как счётчик действий)
    download_count: Mapped[int] = mapped_column(default=0)
    # язык интерфейса: ru / uz / en
    language: Mapped[str] = mapped_column(String(5), default="ru")

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} ({self.username})>"


class Channel(Base):
    """Канал/группа для обязательной подписки"""
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # id канала в Telegram (например -1001234567890)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    # название для отображения юзеру
    title: Mapped[str] = mapped_column(String(255))
    # ссылка на канал (для кнопки "Подписаться")
    invite_link: Mapped[str] = mapped_column(String(255))
    # когда добавлен
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Channel {self.channel_id} ({self.title})>"


class TempMailAccount(Base):
    """Временный почтовый ящик пользователя (mail.tm)"""
    __tablename__ = "tempmail_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), index=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    # пароль, сгенерированный нами; юзеру не показываем (для guerrillamail — пусто)
    password: Mapped[str] = mapped_column(String(64))
    # JWT-токен mail.tm или sid_token guerrillamail
    token: Mapped[str] = mapped_column(Text)
    # ID аккаунта в mail.tm (для DELETE /accounts/{id}) или sid_token для guerrillamail
    account_id: Mapped[str] = mapped_column(String(256))
    # имя провайдера: "mailtm" | "guerrillamail"
    provider: Mapped[str] = mapped_column(
        String(32), default="mailtm", server_default="mailtm",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<TempMailAccount {self.email}>"
