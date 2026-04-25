"""Мультиязычность — русский, узбекский, английский
Использование: from bot.i18n import t
  t("start.welcome", lang="en", name="John")
"""

from bot.emojis import E

TRANSLATIONS = {
    # === /start ===
    "start.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет, {{name}}!</b>\n\n"
            f"{E['folder']} Я помогу тебе создать временную одноразовую почту.\n\n"
            f"{E['pin']} <b>Как пользоваться:</b>\n"
            "Создай временный email-адрес и получай письма "
            f"прямо в Telegram! {E['plane']}\n\n"
            "Выбери действие ниже:"
        ),
        "uz": (
            f"{E['bot']} <b>Salom, {{name}}!</b>\n\n"
            f"{E['folder']} Vaqtinchalik bir martalik pochta yaratishga yordam beraman.\n\n"
            f"{E['pin']} <b>Qanday foydalanish:</b>\n"
            "Vaqtinchalik email manzil yarating va xatlarni "
            f"to'g'ridan-to'g'ri Telegramda oling! {E['plane']}\n\n"
            "Quyidagi tugmalardan birini tanlang:"
        ),
        "en": (
            f"{E['bot']} <b>Hello, {{name}}!</b>\n\n"
            f"{E['folder']} I'll help you create a temporary disposable email.\n\n"
            f"{E['pin']} <b>How to use:</b>\n"
            "Create a temporary email address and receive messages "
            f"right in Telegram! {E['plane']}\n\n"
            "Choose an action below:"
        ),
    },

    # === Кнопки главного меню ===
    "btn.new_mail": {
        "ru": "Создать почту",
        "uz": "Pochta yaratish",
        "en": "Create email",
    },
    "btn.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "btn.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "btn.back": {
        "ru": "Назад",
        "uz": "Orqaga",
        "en": "Back",
    },
    "btn.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },

    # === Профиль ===
    "profile.title": {
        "ru": (
            f"{E['profile']} <b>Твой профиль</b>\n\n"
            f"{E['edit']} Имя: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['folder']} Создано ящиков: {{downloads}}\n"
        ),
        "uz": (
            f"{E['profile']} <b>Profilingiz</b>\n\n"
            f"{E['edit']} Ism: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['folder']} Yaratilgan qutichalar: {{downloads}}\n"
        ),
        "en": (
            f"{E['profile']} <b>Your profile</b>\n\n"
            f"{E['edit']} Name: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['folder']} Mailboxes created: {{downloads}}\n"
        ),
    },

    # === Помощь ===
    "help.text": {
        "ru": (
            f"{E['book']} <b>Помощь</b>\n\n"
            f"{E['star']} Создай временный email одной кнопкой\n"
            f"{E['star']} Получай письма прямо в Telegram\n"
            f"{E['star']} Ящик живёт 10 минут, затем удаляется\n"
            f"{E['lock']} Используй для регистраций на сайтах\n\n"
            f"{E['plane']} По вопросам: @{{admin_username}}"
        ),
        "uz": (
            f"{E['book']} <b>Yordam</b>\n\n"
            f"{E['star']} Bir tugma bilan vaqtinchalik email yarating\n"
            f"{E['star']} Xatlarni to'g'ridan-to'g'ri Telegramda oling\n"
            f"{E['star']} Quti 10 daqiqa yashaydi, keyin o'chadi\n"
            f"{E['lock']} Saytlarda ro'yxatdan o'tish uchun foydalaning\n\n"
            f"{E['plane']} Savollar uchun: @{{admin_username}}"
        ),
        "en": (
            f"{E['book']} <b>Help</b>\n\n"
            f"{E['star']} Create a temporary email with one button\n"
            f"{E['star']} Receive messages right in Telegram\n"
            f"{E['star']} Mailbox lives 10 minutes, then deleted\n"
            f"{E['lock']} Use for website registrations\n\n"
            f"{E['plane']} Contact: @{{admin_username}}"
        ),
    },

    # === Подписка ===
    "sub.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет!</b>\n\n"
            f"{E['folder']} Этот бот создаёт временные email-адреса — "
            "быстро и бесплатно!\n\n"
            f"{E['lock']} <b>Для начала подпишись на каналы ниже:</b>\n\n"
            f"После подписки нажми «{E['check']} Проверить подписку»"
        ),
        "uz": (
            f"{E['bot']} <b>Salom!</b>\n\n"
            f"{E['folder']} Bu bot vaqtinchalik email manzillar yaratadi — "
            "tez va bepul!\n\n"
            f"{E['lock']} <b>Boshlash uchun quyidagi kanallarga obuna bo'l:</b>\n\n"
            f"Obuna bo'lgach «{E['check']} Obunani tekshirish» tugmasini bos"
        ),
        "en": (
            f"{E['bot']} <b>Hello!</b>\n\n"
            f"{E['folder']} This bot creates temporary email addresses — "
            "fast and free!\n\n"
            f"{E['lock']} <b>To start, subscribe to the channels below:</b>\n\n"
            f"After subscribing, tap «{E['check']} Check subscription»"
        ),
    },
    "sub.not_subscribed": {
        "ru": (
            f"{E['cross']} <b>Ты ещё не подписался на все каналы:</b>\n\n"
            f"Подпишись и нажми «{E['check']} Проверить подписку» ещё раз."
        ),
        "uz": (
            f"{E['cross']} <b>Hali barcha kanallarga obuna bo'lmading:</b>\n\n"
            f"Obuna bo'lib, «{E['check']} Obunani tekshirish» tugmasini qayta bos."
        ),
        "en": (
            f"{E['cross']} <b>You haven't subscribed to all channels yet:</b>\n\n"
            f"Subscribe and tap «{E['check']} Check subscription» again."
        ),
    },
    "sub.success": {
        "ru": (
            f"{E['check']} <b>Отлично, {{name}}!</b>\n\n"
            f"Теперь ты можешь пользоваться ботом! {E['plane']}\n\n"
            "Создай временный email-адрес."
        ),
        "uz": (
            f"{E['check']} <b>Zo'r, {{name}}!</b>\n\n"
            f"Endi botdan foydalanishing mumkin! {E['plane']}\n\n"
            "Vaqtinchalik email yaratib ko'r."
        ),
        "en": (
            f"{E['check']} <b>Great, {{name}}!</b>\n\n"
            f"You can now use the bot! {E['plane']}\n\n"
            "Create a temporary email address."
        ),
    },
    "btn.check_sub": {
        "ru": "Проверить подписку",
        "uz": "Obunani tekshirish",
        "en": "Check subscription",
    },
    "sub.check_alert_fail": {
        "ru": f"{E['cross']} Подпишись на все каналы!",
        "uz": f"{E['cross']} Barcha kanallarga obuna bo'l!",
        "en": f"{E['cross']} Subscribe to all channels!",
    },
    "sub.check_alert_ok": {
        "ru": f"{E['check']} Подписка подтверждена!",
        "uz": f"{E['check']} Obuna tasdiqlandi!",
        "en": f"{E['check']} Subscription confirmed!",
    },
    "sub.not_required": {
        "ru": f"{E['check']} Подписка не требуется!",
        "uz": f"{E['check']} Obuna talab qilinmaydi!",
        "en": f"{E['check']} No subscription required!",
    },

    # === Ошибки ===
    "error.generic": {
        "ru": f"{E['cross']} <b>Что-то пошло не так</b>\n\nПопробуй позже.",
        "uz": f"{E['cross']} <b>Nimadir noto'g'ri ketdi</b>\n\nKeyinroq urinib ko'ring.",
        "en": f"{E['cross']} <b>Something went wrong</b>\n\nPlease try again later.",
    },
    "error.rate_limit": {
        "ru": f"{E['clock']} <b>Слишком много запросов!</b>\n\nПодожди {{seconds}} секунд и попробуй снова.",
        "uz": f"{E['clock']} <b>Juda ko'p so'rovlar!</b>\n\n{{seconds}} soniya kuting va qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Too many requests!</b>\n\nWait {{seconds}} seconds and try again.",
    },

    # === Выбор языка ===
    "lang.choose": {
        "ru": f"{E['gear']} <b>Выберите язык:</b>",
        "uz": f"{E['gear']} <b>Tilni tanlang:</b>",
        "en": f"{E['gear']} <b>Choose language:</b>",
    },
    "lang.changed": {
        "ru": f"{E['check']} Язык изменён на русский",
        "uz": f"{E['check']} Til o'zbek tiliga o'zgartirildi",
        "en": f"{E['check']} Language changed to English",
    },

    # === Админ-панель ===
    "admin.title": {
        "ru": f"{E['gear']} <b>Админ-панель</b>\n\nВыбери действие:",
        "uz": f"{E['gear']} <b>Admin panel</b>\n\nAmalni tanlang:",
        "en": f"{E['gear']} <b>Admin panel</b>\n\nChoose an action:",
    },
    "admin.no_access": {
        "ru": "🔒 У тебя нет доступа к админке.",
        "uz": "🔒 Sizda admin panelga kirish huquqi yo'q.",
        "en": "🔒 You don't have access to admin panel.",
    },
    "admin.stats": {
        "ru": (
            f"{E['chart']} <b>Статистика бота</b>\n\n"
            f"{E['users']} Всего юзеров: <b>{{total_users}}</b>\n"
            f"{E['star']} Новых юзеров сегодня: <b>{{today_users}}</b>\n"
            f"{E['folder']} Всего ящиков создано: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Каналов: <b>{{total_channels}}</b>"
        ),
        "uz": (
            f"{E['chart']} <b>Bot statistikasi</b>\n\n"
            f"{E['users']} Jami foydalanuvchilar: <b>{{total_users}}</b>\n"
            f"{E['star']} Bugungi yangi foydalanuvchilar: <b>{{today_users}}</b>\n"
            f"{E['folder']} Jami yaratilgan qutichalar: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Kanallar: <b>{{total_channels}}</b>"
        ),
        "en": (
            f"{E['chart']} <b>Bot statistics</b>\n\n"
            f"{E['users']} Total users: <b>{{total_users}}</b>\n"
            f"{E['star']} New users today: <b>{{today_users}}</b>\n"
            f"{E['folder']} Total mailboxes created: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Channels: <b>{{total_channels}}</b>"
        ),
    },
    "admin.channels_empty": {
        "ru": f"{E['megaphone']} <b>Каналы</b>\n\nСписок пуст. Добавь канал кнопкой ниже.",
        "uz": f"{E['megaphone']} <b>Kanallar</b>\n\nRo'yxat bo'sh. Quyidagi tugma orqali kanal qo'shing.",
        "en": f"{E['megaphone']} <b>Channels</b>\n\nList is empty. Add a channel using the button below.",
    },
    "admin.channels_title": {
        "ru": f"{E['megaphone']} <b>Каналы для подписки:</b>\n",
        "uz": f"{E['megaphone']} <b>Obuna kanallari:</b>\n",
        "en": f"{E['megaphone']} <b>Subscription channels:</b>\n",
    },
    "admin.add_channel_id": {
        "ru": (
            f"{E['megaphone']} <b>Добавление канала</b>\n\n"
            "Отправь <b>ID канала</b> (например <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Узнать ID: добавь бота @getmyid_bot в канал"
        ),
        "uz": (
            f"{E['megaphone']} <b>Kanal qo'shish</b>\n\n"
            "<b>Kanal ID</b> raqamini yuboring (masalan <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} ID bilish: @getmyid_bot ni kanalga qo'shing"
        ),
        "en": (
            f"{E['megaphone']} <b>Add channel</b>\n\n"
            "Send the <b>channel ID</b> (e.g. <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Get ID: add @getmyid_bot to the channel"
        ),
    },
    "admin.add_channel_title": {
        "ru": f"{E['edit']} Теперь отправь <b>название канала</b>:",
        "uz": f"{E['edit']} Endi <b>kanal nomini</b> yuboring:",
        "en": f"{E['edit']} Now send the <b>channel name</b>:",
    },
    "admin.add_channel_link": {
        "ru": (
            f"{E['link']} Теперь отправь <b>ссылку или юзернейм канала</b>\n\n"
            "Принимаю любой формат:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "uz": (
            f"{E['link']} Endi <b>kanal havolasi yoki username</b> yuboring\n\n"
            "Istalgan formatda:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "en": (
            f"{E['link']} Now send the <b>channel link or username</b>\n\n"
            "Any format accepted:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
    },
    "admin.channel_added": {
        "ru": f"{E['check']} <b>Канал добавлен!</b>",
        "uz": f"{E['check']} <b>Kanal qo'shildi!</b>",
        "en": f"{E['check']} <b>Channel added!</b>",
    },
    "admin.confirm_delete": {
        "ru": f"{E['warning']} <b>Удалить канал?</b>\n\nID: <code>{{channel_id}}</code>\n\nЭто действие нельзя отменить.",
        "uz": f"{E['warning']} <b>Kanalni o'chirishni xohlaysizmi?</b>\n\nID: <code>{{channel_id}}</code>\n\nBu amalni qaytarib bo'lmaydi.",
        "en": f"{E['warning']} <b>Delete channel?</b>\n\nID: <code>{{channel_id}}</code>\n\nThis action cannot be undone.",
    },
    "admin.id_not_number": {
        "ru": f"{E['cross']} ID должен быть числом. Попробуй ещё раз:",
        "uz": f"{E['cross']} ID raqam bo'lishi kerak. Qayta urinib ko'ring:",
        "en": f"{E['cross']} ID must be a number. Try again:",
    },
    "admin.title_too_long": {
        "ru": f"{E['cross']} Название слишком длинное (макс 200 символов)",
        "uz": f"{E['cross']} Nom juda uzun (maks 200 belgi)",
        "en": f"{E['cross']} Name is too long (max 200 characters)",
    },
    "admin.link_invalid": {
        "ru": f"{E['cross']} Не удалось распознать ссылку.\nПопробуй ещё:",
        "uz": f"{E['cross']} Havolani aniqlab bo'lmadi.\nQayta urinib ko'ring:",
        "en": f"{E['cross']} Could not parse the link.\nTry again:",
    },

    # === Кнопки админки ===
    "btn.admin_stats": {"ru": "Статистика", "uz": "Statistika", "en": "Statistics"},
    "btn.admin_channels": {"ru": "Каналы", "uz": "Kanallar", "en": "Channels"},
    "btn.admin_home": {"ru": "Главное меню", "uz": "Bosh menyu", "en": "Main menu"},
    "btn.admin_add": {"ru": "Добавить канал", "uz": "Kanal qo'shish", "en": "Add channel"},
    "btn.admin_back": {"ru": "Назад", "uz": "Orqaga", "en": "Back"},
    "btn.admin_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_confirm_del": {"ru": "Да, удалить", "uz": "Ha, o'chirish", "en": "Yes, delete"},
    "btn.admin_cancel_del": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_panel": {"ru": "Админ-панель", "uz": "Admin panel", "en": "Admin panel"},
    "btn.admin_broadcast": {"ru": "Рассылка", "uz": "Xabar yuborish", "en": "Broadcast"},

    # === Рассылка ===
    "admin.broadcast_prompt": {
        "ru": f"{E['plane']} <b>Массовая рассылка</b>\n\nОтправь текст/фото/видео для рассылки.\nПоддерживается HTML.",
        "uz": f"{E['plane']} <b>Ommaviy xabar</b>\n\nYuborish uchun matn/rasm/video yuboring.\nHTML qo'llab-quvvatlanadi.",
        "en": f"{E['plane']} <b>Mass broadcast</b>\n\nSend text/photo/video to broadcast.\nHTML supported.",
    },
    "admin.broadcast_preview": {
        "ru": f"{E['eye']} <b>Предпросмотр</b>\n\nОтправить это сообщение всем юзерам?",
        "uz": f"{E['eye']} <b>Oldindan ko'rish</b>\n\nBu xabarni barcha foydalanuvchilarga yuborishni xohlaysizmi?",
        "en": f"{E['eye']} <b>Preview</b>\n\nSend this message to all users?",
    },
    "admin.broadcast_confirm": {"ru": "Да, отправить", "uz": "Ha, yuborish", "en": "Yes, send"},
    "admin.broadcast_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "admin.broadcast_started": {
        "ru": f"{E['plane']} Рассылка запущена... Ожидай отчёт.",
        "uz": f"{E['plane']} Xabar yuborilmoqda... Hisobotni kuting.",
        "en": f"{E['plane']} Broadcast started... Wait for report.",
    },
    "admin.broadcast_done": {
        "ru": f"{E['chart']} <b>Рассылка завершена!</b>\n\n{E['check']} Доставлено: <b>{{success}}</b>\n{E['cross']} Ошибок: <b>{{failed}}</b>\n{E['users']} Всего: <b>{{total}}</b>",
        "uz": f"{E['chart']} <b>Xabar yuborish tugadi!</b>\n\n{E['check']} Yetkazildi: <b>{{success}}</b>\n{E['cross']} Xatolar: <b>{{failed}}</b>\n{E['users']} Jami: <b>{{total}}</b>",
        "en": f"{E['chart']} <b>Broadcast complete!</b>\n\n{E['check']} Delivered: <b>{{success}}</b>\n{E['cross']} Failed: <b>{{failed}}</b>\n{E['users']} Total: <b>{{total}}</b>",
    },

    # === Описания команд бота (для меню Telegram) ===
    "cmd.start": {
        "ru": "Запустить бота",
        "uz": "Botni boshlash",
        "en": "Start the bot",
    },
    "cmd.menu": {
        "ru": "Главное меню",
        "uz": "Asosiy menyu",
        "en": "Main menu",
    },
    "cmd.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "cmd.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "cmd.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },

    # === TempMail — доменные тексты ===
    "tempmail.welcome_hint": {
        "ru": (
            f"{E['folder']} <b>Временная почта</b>\n\n"
            "Создай одноразовый email для регистрации на сайтах — "
            "письма придут прямо в Telegram."
        ),
        "uz": (
            f"{E['folder']} <b>Vaqtinchalik pochta</b>\n\n"
            "Saytlarda ro'yxatdan o'tish uchun bir martalik email yarat — "
            "xatlar to'g'ridan-to'g'ri Telegramga keladi."
        ),
        "en": (
            f"{E['folder']} <b>Temporary mail</b>\n\n"
            "Create a disposable email for website registrations — "
            "messages will arrive right in Telegram."
        ),
    },
    "tempmail.created": {
        "ru": (
            f"{E['check']} <b>Твой временный адрес:</b>\n\n"
            "<code>{email}</code>\n\n"
            "Скопируй и используй для регистрации. "
            "Проверь входящие через кнопку ниже."
        ),
        "uz": (
            f"{E['check']} <b>Vaqtinchalik manziling:</b>\n\n"
            "<code>{email}</code>\n\n"
            "Nusxalab, ro'yxatdan o'tishda ishlatgin. "
            "Kelgan xatlarni quyidagi tugma orqali tekshir."
        ),
        "en": (
            f"{E['check']} <b>Your temporary address:</b>\n\n"
            "<code>{email}</code>\n\n"
            "Copy it and use it to sign up. "
            "Check your inbox with the button below."
        ),
    },
    "tempmail.limit_reached": {
        "ru": "⚠️ Максимум 5 ящиков. Удали старый, чтобы создать новый.",
        "uz": "⚠️ Maksimal 5 ta quti. Yangi yaratish uchun eskisini o'chir.",
        "en": "⚠️ You've reached the limit of 5 mailboxes. Delete one to create a new.",
    },
    "tempmail.no_messages": {
        "ru": f"{E['folder']} Входящих нет. Попробуй обновить через минуту.",
        "uz": f"{E['folder']} Xatlar yo'q. Bir daqiqadan so'ng yangilab ko'r.",
        "en": f"{E['folder']} No messages yet. Try again in a minute.",
    },
    "tempmail.messages_header": {
        "ru": f"{E['folder']} <b>Входящие ({{count}}):</b>",
        "uz": f"{E['folder']} <b>Kiruvchi xatlar ({{count}}):</b>",
        "en": f"{E['folder']} <b>Inbox ({{count}}):</b>",
    },
    "tempmail.check_too_fast": {
        "ru": "⏰ Полегче — раз в 10 секунд, не чаще.",
        "uz": "⏰ Sekinroq — har 10 soniyada bir marta.",
        "en": "⏰ Slow down — once every 10 seconds.",
    },
    "tempmail.account_expired": {
        "ru": (
            f"{E['warning']} Ящик удалён на стороне mail.tm "
            "(неактивность > 7 дней). Нажми «Новый email», чтобы создать другой."
        ),
        "uz": (
            f"{E['warning']} Quti mail.tm tomonidan o'chirildi "
            "(7 kundan ortiq faolsizlik). Yangi email yaratish uchun tugmani bos."
        ),
        "en": (
            f"{E['warning']} This mailbox was removed by mail.tm "
            "(no activity for 7+ days). Tap «New email» to create another one."
        ),
    },
    "tempmail.service_unavailable": {
        "ru": "❌ Сервис временной почты сейчас недоступен. Попробуй позже.",
        "uz": "❌ Vaqtinchalik pochta xizmati hozir mavjud emas. Keyinroq urinib ko'ring.",
        "en": "❌ Temporary mail service is unavailable. Please try again later.",
    },
    "tempmail.rate_limited": {
        "ru": "⏰ Слишком много запросов. Подожди минуту.",
        "uz": "⏰ Juda ko'p so'rovlar. Bir daqiqa kuting.",
        "en": "⏰ Too many requests. Wait a minute.",
    },
    "tempmail.confirm_delete": {
        "ru": (
            f"{E['warning']} Удалить <code>{{email}}</code>?\n\n"
            "Все письма пропадут."
        ),
        "uz": (
            f"{E['warning']} <code>{{email}}</code> o'chirilsinmi?\n\n"
            "Barcha xatlar yo'qoladi."
        ),
        "en": (
            f"{E['warning']} Delete <code>{{email}}</code>?\n\n"
            "All messages will be lost."
        ),
    },
    "tempmail.not_found": {
        "ru": "❌ Ящик не найден.",
        "uz": "❌ Quti topilmadi.",
        "en": "❌ Mailbox not found.",
    },
    "tempmail.no_subject": {
        "ru": "(без темы)",
        "uz": "(mavzusiz)",
        "en": "(no subject)",
    },
    "tempmail.deleted": {
        "ru": f"{E['check']} Ящик удалён.",
        "uz": f"{E['check']} Quti o'chirildi.",
        "en": f"{E['check']} Mailbox deleted.",
    },
    "tempmail.my_accounts_header": {
        "ru": f"{E['folder']} <b>Твои ящики:</b>",
        "uz": f"{E['folder']} <b>Qutilaring:</b>",
        "en": f"{E['folder']} <b>Your mailboxes:</b>",
    },
    "tempmail.account_menu": {
        "ru": (
            f"{E['folder']} <b>Ящик:</b>\n\n"
            "<code>{email}</code>\n\n"
            "Выбери действие:"
        ),
        "uz": (
            f"{E['folder']} <b>Quti:</b>\n\n"
            "<code>{email}</code>\n\n"
            "Nima qilmoqchisan?"
        ),
        "en": (
            f"{E['folder']} <b>Mailbox:</b>\n\n"
            "<code>{email}</code>\n\n"
            "What do you want to do?"
        ),
    },
    "tempmail.message_view": {
        "ru": (
            f"{E['plane']} <b>От:</b> <code>{{from_}}</code>\n"
            "<b>Тема:</b> {subject}\n"
            f"{E['clock']} {{date}}\n\n"
            "{text}"
        ),
        "uz": (
            f"{E['plane']} <b>Kimdan:</b> <code>{{from_}}</code>\n"
            "<b>Mavzu:</b> {subject}\n"
            f"{E['clock']} {{date}}\n\n"
            "{text}"
        ),
        "en": (
            f"{E['plane']} <b>From:</b> <code>{{from_}}</code>\n"
            "<b>Subject:</b> {subject}\n"
            f"{E['clock']} {{date}}\n\n"
            "{text}"
        ),
    },
    "tempmail.has_attachments": {
        "ru": f"\n\n{E['package']} В этом письме есть вложения (пока не поддерживаются).",
        "uz": f"\n\n{E['package']} Bu xatda biriktirilgan fayllar bor (hozircha qo'llab-quvvatlanmaydi).",
        "en": f"\n\n{E['package']} This message has attachments (not supported yet).",
    },

    # === Кнопки tempmail ===
    "btn.create_email": {
        "ru": "Создать email",
        "uz": "Email yaratish",
        "en": "Create email",
    },
    "btn.check_mail": {
        "ru": "Проверить почту",
        "uz": "Pochtani tekshirish",
        "en": "Check mail",
    },
    "btn.new_email": {
        "ru": "Новый email",
        "uz": "Yangi email",
        "en": "New email",
    },
    "btn.delete_account": {
        "ru": "Удалить",
        "uz": "O'chirish",
        "en": "Delete",
    },
    "btn.my_accounts": {
        "ru": "Мои ящики ({count})",
        "uz": "Qutilarim ({count})",
        "en": "My mailboxes ({count})",
    },
    "btn.back_to_list": {
        "ru": "Назад к списку",
        "uz": "Ro'yxatga qaytish",
        "en": "Back to list",
    },
    "btn.yes": {
        "ru": "Да",
        "uz": "Ha",
        "en": "Yes",
    },
    "btn.no": {
        "ru": "Нет",
        "uz": "Yo'q",
        "en": "No",
    },
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить перевод по ключу и языку"""
    translations = TRANSLATIONS.get(key, {})
    text = translations.get(lang, translations.get("ru", f"[{key}]"))
    if kwargs:
        text = text.format(**kwargs)
    return text


def detect_language(language_code: str | None) -> str:
    """Определяет язык по Telegram: ru → русский, uz → узбекский, остальное → английский"""
    if not language_code:
        return "en"
    if language_code.startswith("ru"):
        return "ru"
    if language_code.startswith("uz"):
        return "uz"
    return "en"
