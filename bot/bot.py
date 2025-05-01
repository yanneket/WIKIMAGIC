from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = '7953140297:AAGwWVx3zwmo-9MbQ-UUU1764nljCxuncQU'
BASE_SITE_URL = 'https://wikimagic.onrender.com'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ref_link = f"{BASE_SITE_URL}/?ref={user_id}"
    keyboard = [
        [InlineKeyboardButton("🔗 Перейти на сайт", url=ref_link)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}!\n"
        f"Вот твоя уникальная ссылка:\n{ref_link}\n\n"
        "🔎 Поделись ею, чтобы видеть, что ищут другие!",
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Бот запущен...")
    app.run_polling()
