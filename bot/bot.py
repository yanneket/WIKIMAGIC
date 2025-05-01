from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import requests
import os

BOT_TOKEN = '7953140297:AAGwWVx3zwmo-9MbQ-UUU1764nljCxuncQU'
BASE_SITE_URL = 'https://wikimagic.onrender.com'
API_URL = BASE_SITE_URL  # или ваш API URL, если он отличается

# Храним активные сессии {user_id: [list_of_referred_user_ids]}
active_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ref_link = f"{BASE_SITE_URL}/?ref={user_id}"
    keyboard = [
        [InlineKeyboardButton("🔗 Перейти на сайт", url=ref_link)],
        [InlineKeyboardButton("🔄 Сбросить всех", callback_data="reset")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}!\n"
        f"Вот твоя уникальная ссылка:\n{ref_link}\n\n"
        "🔎 Поделись ею, чтобы видеть, что ищут другие!\n"
        "🔄 Нажми 'Сбросить всех', чтобы перенаправить всех на Википедию",
        reply_markup=reply_markup
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Здесь можно добавить вызов API для сброса всех рефералов
    await update.message.reply_text("Все пользователи, перешедшие по вашей ссылке, будут перенаправлены на Википедию.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "reset":
        user_id = query.from_user.id
        # Отправляем запрос на сервер для сброса рефералов
        try:
            response = requests.get(f"{API_URL}/reset_referrals?ref={user_id}")
            if response.status_code == 200:
                await query.edit_message_text(text="✅ Все рефералы сброшены и перенаправлены на Википедию!")
            else:
                await query.edit_message_text(text="⚠️ Ошибка при сбросе рефералов")
        except Exception as e:
            await query.edit_message_text(text=f"⚠️ Ошибка соединения: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.CallbackQuery(), button))
    print("Бот запущен...")
    app.run_polling()