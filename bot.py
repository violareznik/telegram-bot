import telebot
from telebot import types

TOKEN = "8831649954:AAGQg6ktHdf2LxmuJaNwAiwfUwauaN3BzPU"
ADMIN_ID = 8714268833

USDT_ADDRESS = "0x1604B0e202fB3b51d8bDe5250dea7Ff92FAD45a4"
SUPPORT = "@ust_agent"

bot = telebot.TeleBot(TOKEN)
users = {}


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Создать заявку")
    markup.add("Условия", "Статус")
    markup.add("Поддержка", "Помощь")
    return markup


def cancel_request(message):
    users.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "Заявка отменена.", reply_markup=main_menu())


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать!\n\nВыберите действие:", reply_markup=main_menu())


@bot.message_handler(commands=['exchange'])
@bot.message_handler(func=lambda message: message.text == "Создать заявку")
def start_exchange(message):
    users[message.chat.id] = {}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇪🇺 Европа", "🌏 СНГ")
    markup.add("🏔 Средняя Азия", "🇺🇸 США")
    markup.add("❌ Отмена")

    bot.send_message(message.chat.id, "Выберите регион:", reply_markup=markup)
    bot.register_next_step_handler(message, get_region)


def get_region(message):
    if message.text == "❌ Отмена":
        cancel_request(message)
        return

    users[message.chat.id]["region"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if message.text == "🇪🇺 Европа":
        markup.add("🇩🇪 Германия", "🇫🇷 Франция")
        markup.add("🇮🇹 Италия", "🇪🇸 Испания")
        markup.add("🇵🇱 Польша", "🇷🇴 Румыния")
        markup.add("🇲🇩 Молдова", "🇨🇿 Чехия")
        markup.add("🇬🇧 Великобритания", "🇵🇹 Португалия")
        markup.add("🇳🇱 Нидерланды", "🇧🇪 Бельгия")

    elif message.text == "🌏 СНГ":
        markup.add("🇷🇺 Россия", "🇧🇾 Беларусь")
        markup.add("🇦🇲 Армения", "🇦🇿 Азербайджан")
        markup.add("🇬🇪 Грузия")

    elif message.text == "🏔 Средняя Азия":
        markup.add("🇰🇿 Казахстан", "🇺🇿 Узбекистан")
        markup.add("🇰🇬 Кыргызстан", "🇹🇯 Таджикистан")

    elif message.text == "🇺🇸 США":
        users[message.chat.id]["country"] = "🇺🇸 США"
        bot.send_message(message.chat.id, "Введите банк:")
        bot.register_next_step_handler(message, get_bank)
        return

    else:
        bot.send_message(message.chat.id, "Выберите регион из списка.")
        start_exchange(message)
        return

    markup.add("❌ Отмена")
    bot.send_message(message.chat.id, "Выберите страну:", reply_markup=markup)
    bot.register_next_step_handler(message, get_country)


def get_country(message):
    if message.text == "❌ Отмена":
        cancel_request(message)
        return

    users[message.chat.id]["country"] = message.text
    bot.send_message(message.chat.id, "Введите банк:")
    bot.register_next_step_handler(message, get_bank)


def get_bank(message):
    if message.text == "❌ Отмена":
        cancel_request(message)
        return

    users[message.chat.id]["bank"] = message.text
    bot.send_message(message.chat.id, "Введите сумму USDT:")
    bot.register_next_step_handler(message, get_amount)


def get_amount(message):
    if message.text == "❌ Отмена":
        cancel_request(message)
        return

    try:
        amount = float(message.text.replace(",", "."))
    except:
        bot.send_message(message.chat.id, "Введите сумму цифрами. Например: 100")
        bot.register_next_step_handler(message, get_amount)
        return

    receive = round(amount * 0.98, 2)
    users[message.chat.id]["amount"] = amount
    users[message.chat.id]["receive"] = receive

    bot.send_message(
        message.chat.id,
        f"Вы отправляете: {amount} USDT\n"
        f"Комиссия сервиса: 2%\n"
        f"К получению: {receive} USD\n\n"
        f"Введите номер карты:"
    )
    bot.register_next_step_handler(message, get_card)


def get_card(message):
    if message.text == "❌ Отмена":
        cancel_request(message)
        return

    users[message.chat.id]["card"] = message.text
    bot.send_message(message.chat.id, "Введите имя и фамилию получателя:")
    bot.register_next_step_handler(message, get_name)


def get_name(message):
    if message.text == "❌ Отмена":
        cancel_request(message)
        return

    users[message.chat.id]["name"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ Я оплатил")
    markup.add("❌ Отмена")

    data = users[message.chat.id]

    bot.send_message(
        message.chat.id,
        f"Проверьте заявку:\n\n"
        f"Регион: {data.get('region')}\n"
        f"Страна: {data.get('country')}\n"
        f"Банк: {data.get('bank')}\n"
        f"Сумма: {data.get('amount')} USDT\n"
        f"К получению: {data.get('receive')} USD\n"
        f"Карта: {data.get('card')}\n"
        f"Получатель: {data.get('name')}\n\n"
        f"📌 Инструкция по оплате\n\n"
        f"• Отправьте {data.get('amount')} USDT\n"
        f"• Сеть: ERC20 (Ethereum)\n"
        f"• Отправляйте только USDT ERC20\n"
        f"• Не используйте TRC20, BEP20 или другие сети\n"
        f"• При отправке другой сети средства могут быть утеряны\n\n"
        f"💳 Адрес для перевода:\n"
        f"{USDT_ADDRESS}\n\n"
        f"После оплаты нажмите ✅ Я оплатил",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == "✅ Я оплатил")
def paid(message):
    data = users.get(message.chat.id)

    if not data:
        bot.send_message(message.chat.id, "Заявка не найдена.", reply_markup=main_menu())
        return

    bot.send_message(message.chat.id, "Заявка принята ✅\n\nОжидайте проверку оплаты.", reply_markup=main_menu())

    username = message.from_user.username or "без username"

    bot.send_message(
        ADMIN_ID,
        f"🔥 Новая заявка\n\n"
        f"User ID: {message.chat.id}\n"
        f"Username: @{username}\n\n"
        f"Регион: {data.get('region')}\n"
        f"Страна: {data.get('country')}\n"
        f"Банк: {data.get('bank')}\n"
        f"Сумма: {data.get('amount')} USDT\n"
        f"К получению: {data.get('receive')} USD\n"
        f"Карта: {data.get('card')}\n"
        f"Получатель: {data.get('name')}"
    )

    users.pop(message.chat.id, None)


@bot.message_handler(func=lambda message: message.text == "Условия")
def terms(message):
    bot.send_message(
        message.chat.id,
        "📌 Условия сервиса\n\n"
        "• Комиссия сервиса: 2%\n"
        "• Работаем только с USDT ERC20\n"
        "• Выплаты осуществляются на банковские карты\n"
        "• После оплаты заявка поступает в обработку\n"
        "• Среднее время обработки: 5–30 минут"
    )


@bot.message_handler(func=lambda message: message.text == "Статус")
def status(message):
    bot.send_message(message.chat.id, "Статус заявки уточните в поддержке.")


@bot.message_handler(func=lambda message: message.text == "Поддержка")
def support(message):
    bot.send_message(message.chat.id, f"Поддержка: {SUPPORT}")


@bot.message_handler(func=lambda message: message.text == "Помощь")
def help_message(message):
    bot.send_message(message.chat.id, "Нажмите «Создать заявку» и следуйте шагам.")


@bot.message_handler(func=lambda message: message.text == "❌ Отмена")
def cancel(message):
    cancel_request(message)


print("Bot started...")
bot.infinity_polling()
