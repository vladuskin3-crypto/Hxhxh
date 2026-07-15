import telebot
from telebot import types
from datetime import datetime

# ВСТАВЬ СЮДА СВОЙ ТОКЕН ОТ @BotFather
TOKEN = '8653998611:AAHkEOKsLKmq3SunTMbB-bE-7_uDw4pQjHc'
bot = telebot.TeleBot(TOKEN)

# --- Имитация базы данных (в реальном проекте тут будет SQL) ---
# Храним данные в словаре: {user_id: {username, balance, joined_at}}
user_data = {}

def get_user_info(user):
    """Получает или создает профиль пользователя"""
    uid = user.id
    if uid not in user_data:
        user_data[uid] = {
            'username': user.username or "Без юзернейма",
            'balance': 0.0,
            'joined_at': datetime.now().strftime("%d.%m.%Y %H:%M")
        }
    return user_data[uid]

# --- ГЛАВНОЕ МЕНЮ ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    info = get_user_info(user)
    
    # Клавиатура
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn_buy = types.KeyboardButton("🛍 Купить")
    btn_profile = types.KeyboardButton("👤 Профиль")
    btn_support = types.KeyboardButton("💬 Поддержка")
    markup.add(btn_buy, btn_profile)
    markup.add(btn_support)

    text = (
        f"👋 Привет, {user.first_name}! Добро пожаловать в наш магазин!\n\n"
        f"Здесь ты можешь приобрести доступ к услугам на разный срок.\n"
        f"Выбирай раздел в меню ниже."
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

# --- ОБРАБОТЧИК КНОПОК ГЛАВНОГО МЕНЮ ---
@bot.message_handler(func=lambda message: message.text == "🛍 Купить")
def show_products(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    # Кнопки товаров (callback_data передает код товара)
    btn_1w = types.InlineKeyboardButton("📅 1 неделя — 500 ₽", callback_data="prod_1week")
    btn_2w = types.InlineKeyboardButton("🗓 2 недели — 900 ₽", callback_data="prod_2week")
    btn_3w = types.InlineKeyboardButton("📆 3 недели — 1300 ₽", callback_data="prod_3week")
    markup.add(btn_1w, btn_2w, btn_3w)
    
    bot.send_message(
        message.chat.id, 
        "🛒 Выбери срок доступа:", 
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "👤 Профиль")
def show_profile(message):
    user = message.from_user
    info = get_user_info(user)
    
    # Клавиатура для профиля
    markup = types.InlineKeyboardMarkup()
    btn_topup = types.InlineKeyboardButton("➕ Пополнить баланс", callback_data="act_topup")
    btn_withdraw = types.InlineKeyboardButton("💸 Вывести средства", callback_data="act_withdraw")
    markup.add(btn_topup)
    markup.add(btn_withdraw)

    text = (
        f"👤 **Твой профиль**\n\n"
        f"🆔 ID: `{user.id}`\n"
        f"🧑‍💻 Юзернейм: @{info['username']}\n"
        f"💰 Баланс: **{info['balance']} ₽**\n"
        f"📅 Дата регистрации: {info['joined_at']}"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "💬 Поддержка")
def contact_support(message):
    text = (
        "👨‍💻 Служба поддержки уже на связи!\n"
        "Опиши свою проблему, и мы поможем в ближайшее время."
    )
    bot.send_message(message.chat.id, text)

# --- ИНЛАЙН-КНОПКИ (Товары и Действия) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    user_id = call.from_user.id
    info = get_user_info(call.from_user)

    # Логика товаров
    if call.data.startswith("prod_"):
        product_map = {
            "prod_1week": "1 неделя",
            "prod_2week": "2 недели",
            "prod_3week": "3 недели"
        }
        product_name = product_map.get(call.data, "Товар")
        
        bot.answer_callback_query(call.id, f"Вы выбрали: {product_name}")
        bot.send_message(
            call.message.chat.id,
            f"✅ Отлично! Ты выбрал доступ на **{product_name}**.\n\n"
            f"Скоро менеджер подтвердит оплату. Спасибо за выбор!",
            parse_mode="Markdown"
        )

    # Логика действий в профиле (Пополнение)
    elif call.data == "act_topup":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "💳 **Пополнение баланса**\n\n"
            "Для пополнения напиши сумму, которую хочешь внести, или перейди по ссылке ниже:\n"
            "[Ссылка на платежную систему](https://example.com)", # Замени на реальную ссылку
            parse_mode="Markdown"
        )

    # Логика действий в профиле (Вывод)
    elif call.data == "act_withdraw":
        if info['balance'] <= 0:
            bot.answer_callback_query(call.id, "На балансе недостаточно средств!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Заявка на вывод отправлена!")
            bot.send_message(
                call.message.chat.id,
                f"💸 Заявка на вывод {info['balance']} ₽ создана.\n"
                f"Ожидай подтверждения администратора."
            )

if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)
