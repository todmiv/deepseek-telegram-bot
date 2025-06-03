import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Конфигурация
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Получить у @BotFather
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # Получить на platform.deepseek.com
MODEL_NAME = "deepseek-chat"  # Бесплатная модель

# Инициализация клиента DeepSeek
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет {user.mention_html()}! Я бот с искусственным интеллектом DeepSeek.\n"
        "Просто напиши мне сообщение, и я отвечу!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_message = update.message.text
    
    # Запрос к DeepSeek API
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Ты полезный AI-ассистент DeepSeek-R1. Отвечай на русском."},
            {"role": "user", "content": user_message}
        ],
        max_tokens=2000,
        stream=False
    )
    
    # Отправка ответа пользователю
    ai_response = response.choices[0].message.content
    await update.message.reply_text(ai_response)

def main():
    """Запуск бота"""
    # Создаем приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
