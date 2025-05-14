from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import logging
from datetime import datetime, timedelta
from threading import Lock
import asyncio
import aiohttp

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


BOT_TOKEN = '7953140297:AAGwWVx3zwmo-9MbQ-UUU1764nljCxuncQU'
BASE_SITE_URL = 'https://wikimagic.onrender.com'  # URL вашего Flask-приложения

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ref_link = f"{BASE_SITE_URL}?ref={user_id}"
    
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

# reset_callback
async def reset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.callback_query.answer()

    async with aiohttp.ClientSession() as session:
        await session.get(f"{BASE_SITE_URL}/trigger_reset?ref={user_id}")

    await update.callback_query.edit_message_text(
        "🔄 Сброс выполнен! Пользователи скоро будут перенаправлены на Википедию.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Перейти на сайт", url=f"{BASE_SITE_URL}?ref={user_id}")]
        ])
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(reset_callback, pattern="^reset$"))
    
    
    application.run_polling(drop_pending_updates=True)



if __name__ == '__main__':
    main()  # Важно! Без этого код не запустится.