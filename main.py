"""
DeepSeek Telegram Bot

Телеграм бот для общения с ИИ DeepSeek через Telegram.
Бот принимает текстовые сообщения и отвечает через DeepSeek API.

Автор: todmiv
Лицензия: MIT
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import APIError, OpenAI

# Настройка логирования для отслеживания работы бота
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токены из переменных окружения для безопасности
# Эти переменные должны быть установлены в .env файле или в системе
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')  # Токен бота от @BotFather
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')  # API ключ от DeepSeek
MODEL_NAME = "deepseek-chat"  # Используемая модель DeepSeek

# Проверяем наличие обязательных переменных окружения
# Без этих токенов бот не сможет работать
if not TELEGRAM_TOKEN or not DEEPSEEK_API_KEY:
    logger.error("Необходимые переменные окружения TELEGRAM_TOKEN и DEEPSEEK_API_KEY не установлены!")
    logger.error("Создайте файл .env на основе .env.example и заполните токены")
    exit(1)

# Инициализация клиента DeepSeek через OpenAI совместимый API
# Используем кастомный base_url для доступа к DeepSeek API
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start

    Приветствует пользователя и объясняет функционал бота.
    Вызывается автоматически при первом запуске бота пользователем.
    """
    user = update.effective_user
    # Отправляем персонализированное приветствие с упоминанием пользователя
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я бот с искусственным интеллектом DeepSeek. Просто напиши мне сообщение, и я постараюсь помочь!",
        reply_markup=None
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Основной обработчик текстовых сообщений

    Получает сообщение от пользователя, отправляет его в DeepSeek API
    и возвращает ответ бота пользователю.

    Обрабатывает различные типы ошибок и предоставляет информативные сообщения.
    """
    try:
        # Получаем текст сообщения от пользователя
        user_message = update.message.text
        logger.info(f"Получено сообщение от пользователя {update.effective_user.id}: {user_message}")

        # Формируем запрос к DeepSeek API
        # Используем системный промпт для указания поведения ИИ
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Ты полезный AI-ассистент DeepSeek-R1. Отвечай на русском."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=2000,  # Ограничение на длину ответа
            stream=False  # Синхронный режим (без стриминга)
        )

        # Извлекаем ответ ИИ из ответа API
        ai_response = response.choices[0].message.content
        # Отправляем ответ пользователю в Telegram
        await update.message.reply_text(ai_response)

    except APIError as e:
        # Обработка специфических ошибок DeepSeek API
        if e.status_code == 402:
            # Ошибка недостатка средств на аккаунте
            logger.error("Ошибка баланса: Недостаточно средств на аккаунте DeepSeek")
            await update.message.reply_text(
                "⚠️ Недостаточно средств на API-аккаунте!\n\n"
                "Пожалуйста:\n"
                "1. Проверьте баланс на https://platform.deepseek.com/overview\n"
                "2. Пополните счет или перейдите на бесплатную модель"
            )
        else:
            # Другие ошибки API (сетевые проблемы, неверные параметры и т.д.)
            logger.error(f"Ошибка API DeepSeek: {str(e)}")
            await update.message.reply_text("⚠️ Ошибка API DeepSeek. Попробуйте позже.")

    except Exception as e:
        # Обработка непредвиденных ошибок (программные ошибки, исключения)
        logger.error(f"Общая ошибка в обработке сообщения: {str(e)}")
        await update.message.reply_text("⚠️ Произошла внутренняя ошибка. Пожалуйста, попробуйте позже.")

def main():
    """
    Главная функция запуска бота

    Создает приложение Telegram бота, регистрирует все обработчики команд
    и запускает бота в режиме опроса (polling).
    """
    # Создаем экземпляр приложения Telegram бота с токеном
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрируем обработчики команд и сообщений
    # Обработчик команды /start - приветствие пользователя
    app.add_handler(CommandHandler("start", start))
    # Обработчик текстовых сообщений (исключая команды, начинающиеся с /)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота в режиме постоянного опроса Telegram API
    # Бот будет работать до принудительного завершения
    logger.info("Бот запущен и готов к работе...")
    app.run_polling()

# Точка входа в программу
# Запускаем main() только если файл запущен напрямую, а не импортирован
if __name__ == "__main__":
    main()
