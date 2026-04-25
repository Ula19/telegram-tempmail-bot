"""Inline-клавиатуры — меню, подписка, выбор языка, tempmail"""
from typing import Any

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import settings
from bot.emojis import E_ID
from bot.i18n import t


def get_start_keyboard(
    user_id: int, lang: str = "ru", accounts_count: int = 0,
) -> InlineKeyboardMarkup:
    """Главное меню бота"""
    buttons = []
    if accounts_count == 0:
        buttons.append([InlineKeyboardButton(
            text=t("btn.create_email", lang),
            callback_data="tempmail:new",
            style="primary",
            icon_custom_emoji_id=E_ID["plus"],
        )])
    else:
        buttons.append([InlineKeyboardButton(
            text=t("btn.my_accounts", lang, count=accounts_count),
            callback_data="tempmail:list",
            style="primary",
            icon_custom_emoji_id=E_ID["folder"],
        )])
        buttons.append([InlineKeyboardButton(
            text=t("btn.new_email", lang),
            callback_data="tempmail:new",
            style="primary",
            icon_custom_emoji_id=E_ID["plus"],
        )])
    buttons.append([
        InlineKeyboardButton(
            text=t("btn.profile", lang),
            callback_data="my_profile",
            style="success",
            icon_custom_emoji_id=E_ID["profile"],
        ),
        InlineKeyboardButton(
            text=t("btn.help", lang),
            callback_data="help",
            style="success",
            icon_custom_emoji_id=E_ID["info"],
        ),
    ])
    buttons.append([InlineKeyboardButton(
        text=t("btn.language", lang),
        callback_data="change_language",
        style="success",
        icon_custom_emoji_id=E_ID["gear"],
    )])

    # кнопка админки для админов
    if user_id in settings.admin_id_list:
        buttons.append([InlineKeyboardButton(
            text=t("btn.admin_panel", lang),
            callback_data="admin_panel",
            style="danger",
            icon_custom_emoji_id=E_ID["lock"],
        )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка 'Назад' в главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_menu",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])


def get_subscription_keyboard(
    channels: list[dict], lang: str = "ru"
) -> InlineKeyboardMarkup:
    """Клавиатура подписки на каналы"""
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(
            text=f"{ch['title']}",
            url=ch["invite_link"],
            style="primary",
            icon_custom_emoji_id=E_ID["megaphone"],
        )])
    buttons.append([InlineKeyboardButton(
        text=t("btn.check_sub", lang),
        callback_data="check_subscription",
        style="success",
        icon_custom_emoji_id=E_ID["check"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора языка"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Русский",
                callback_data="set_lang_ru",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_ru"],
            ),
            InlineKeyboardButton(
                text="O'zbek",
                callback_data="set_lang_uz",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_uz"],
            ),
            InlineKeyboardButton(
                text="English",
                callback_data="set_lang_en",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_gb"],
            ),
        ],
    ])


# === TempMail-клавиатуры ===

def get_tempmail_account_menu_kb(acc_pk: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Меню конкретного ящика: проверить, новый, удалить, назад"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.check_mail", lang),
            callback_data=f"tempmail:check:{acc_pk}",
            style="primary",
            icon_custom_emoji_id=E_ID["refresh"],
        )],
        [
            InlineKeyboardButton(
                text=t("btn.new_email", lang),
                callback_data="tempmail:new",
                style="primary",
                icon_custom_emoji_id=E_ID["plus"],
            ),
            InlineKeyboardButton(
                text=t("btn.delete_account", lang),
                callback_data=f"tempmail:delete:{acc_pk}",
                style="danger",
                icon_custom_emoji_id=E_ID["trash"],
            ),
        ],
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_menu",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])


def get_tempmail_inbox_kb(
    acc_pk: int, messages: list[dict], lang: str = "ru",
) -> InlineKeyboardMarkup:
    """Список писем со ссылкой на каждое + кнопка обновить + назад к ящику"""
    rows: list[list[InlineKeyboardButton]] = []
    for m in messages:
        frm_obj = m.get("from") or {}
        if isinstance(frm_obj, dict):
            addr = frm_obj.get("address", "")
            name = frm_obj.get("name", "")
            frm = f"{name} <{addr}>" if name and addr else (addr or name or "?")
        else:
            frm = str(frm_obj or "?")
        subj = (m.get("subject") or "").strip() or t("tempmail.no_subject", lang)
        label = f"{frm} - {subj[:40]}"
        if len(label) > 60:
            label = label[:57] + "..."
        # seen → primary, unseen → danger (выделено как новое)
        msg_style = "primary" if m.get("seen") else "danger"
        rows.append([InlineKeyboardButton(
            text=label,
            callback_data=f"tempmail:msg:{acc_pk}:{m['id']}",
            style=msg_style,
            icon_custom_emoji_id=E_ID["plane"],
        )])
    rows.append([InlineKeyboardButton(
        text=t("btn.check_mail", lang),
        callback_data=f"tempmail:check:{acc_pk}",
        style="primary",
        icon_custom_emoji_id=E_ID["refresh"],
    )])
    rows.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data=f"tempmail:account:{acc_pk}",
        style="success",
        icon_custom_emoji_id=E_ID["back"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_tempmail_confirm_delete_kb(
    acc_pk: int, lang: str = "ru",
) -> InlineKeyboardMarkup:
    """Подтверждение удаления ящика: Да/Нет"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=t("btn.yes", lang),
                callback_data=f"tempmail:delete_confirm:{acc_pk}",
                style="danger",
                icon_custom_emoji_id=E_ID["check"],
            ),
            InlineKeyboardButton(
                text=t("btn.no", lang),
                callback_data=f"tempmail:account:{acc_pk}",
                style="success",
                icon_custom_emoji_id=E_ID["cross"],
            ),
        ],
    ])


def get_tempmail_accounts_list_kb(
    accounts: list[Any], lang: str = "ru",
) -> InlineKeyboardMarkup:
    """Список ящиков + кнопка создать + назад"""
    rows: list[list[InlineKeyboardButton]] = []
    for a in accounts:
        rows.append([InlineKeyboardButton(
            text=a.email,
            callback_data=f"tempmail:account:{a.id}",
            style="primary",
            icon_custom_emoji_id=E_ID["folder"],
        )])
    rows.append([InlineKeyboardButton(
        text=t("btn.new_email", lang),
        callback_data="tempmail:new",
        style="primary",
        icon_custom_emoji_id=E_ID["plus"],
    )])
    rows.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data="back_to_menu",
        style="success",
        icon_custom_emoji_id=E_ID["back"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_tempmail_empty_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    """Когда нет ящиков — кнопка создать + назад"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.create_email", lang),
            callback_data="tempmail:new",
            style="primary",
            icon_custom_emoji_id=E_ID["plus"],
        )],
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_menu",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])


def get_tempmail_message_view_kb(
    acc_pk: int, lang: str = "ru",
) -> InlineKeyboardMarkup:
    """Клавиатура под открытым письмом: назад к списку"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.back_to_list", lang),
            callback_data=f"tempmail:check:{acc_pk}",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])
