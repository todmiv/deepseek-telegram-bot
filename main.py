import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import APIError, OpenAI

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
MODEL_NAME = "deepseek-chat"  # Бесплатная модель

# Проверяем наличие обязательных переменных
if not TELEGRAM_TOKEN or not DEEPSEEK_API_KEY:
    logger.error("Необходимые переменные окружения не установлены!")
    exit(1)

# Инициализация клиента DeepSeek
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я бот с искусственным интеллектом DeepSeek. Просто напиши мне сообщение, и я постараюсь помочь!",
        reply_markup=None
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    try:
        user_message = update.message.text
        logger.info(f"Получено сообщение от {update.effective_user.id}: {user_message}")
        
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
        
    except APIError as e:
        if e.status_code == 402:
            logger.error("Ошибка баланса: Недостаточно средств на аккаунте DeepSeek")
            await update.message.reply_text(
                "⚠️ Недостаточно средств на API-аккаунте!\n\n"
                "Пожалуйста:\n"
                "1. Проверьте баланс на https://platform.deepseek.com/overview\n"
                "2. Пополните счет или перейдите на бесплатную модель"
            )
        else:
            logger.error(f"Ошибка API DeepSeek: {str(e)}")
            await update.message.reply_text("⚠️ Ошибка API DeepSeek. Попробуйте позже.")
            
    except Exception as e:
        logger.error(f"Общая ошибка: {str(e)}")
        await update.message.reply_text("⚠️ Произошла внутренняя ошибка. Пожалуйста, попробуйте позже.")

def main():
    """Запуск бота"""
    # Создаем приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
