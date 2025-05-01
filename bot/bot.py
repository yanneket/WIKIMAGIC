import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import requests

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = '7953140297:AAGwWVx3zwmo-9MbQ-UUU1764nljCxuncQU'
BASE_SITE_URL = 'https://wikimagic.onrender.com'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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
    except Exception as e:
        logger.error(f"Error in start: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        
        if query.data == "reset":
            user_id = query.from_user.id
            try:
                response = requests.get(f"{BASE_SITE_URL}/reset_referrals?ref={user_id}")
                if response.status_code == 200:
                    await query.edit_message_text(text="✅ Все рефералы сброшены и перенаправлены на Википедию!")
                else:
                    await query.edit_message_text(text="⚠️ Ошибка при сбросе рефералов")
            except Exception as e:
                logger.error(f"API error: {e}")
                await query.edit_message_text(text=f"⚠️ Ошибка соединения: {str(e)}")
    except Exception as e:
        logger.error(f"Error in button_handler: {e}")

def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        logger.info("Бот запущен...")
        application.run_polling()
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")

if __name__ == '__main__':
    main()