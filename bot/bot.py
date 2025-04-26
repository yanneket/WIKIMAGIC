from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Токен твоего бота
TOKEN = '7953140297:AAGwWVx3zwmo-9MbQ-UUU1764nljCxuncQU'

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет!')

def main():
    # Создаем объект Application
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчик для команды /start
    application.add_handler(CommandHandler('start', start))

    # Запуск бота с использованием polling
    application.run_polling()

if __name__ == '__main__':
    main()
