import os
import re
import logging
from telegram import Update, MessageEntity
from telegram.ext import Application, MessageHandler, filters, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменной окружения
TOKEN = os.getenv('TOKEN')
# Укажите ваш URL на Render
WEBHOOK_URL = 'https://your-render-url.com/webhook'

# Функция для отправки сообщения "Размут @user_id"
async def unmute_user(context: CallbackContext):
    job = context.job
    chat_id = job.chat_id
    user_id = job.data['user_id']

    await context.bot.send_message(chat_id=chat_id, text=f"Размут @{user_id}")
    logger.info(f"Пользователь @{user_id} размучен.")

# Обработчик сообщений
async def handle_message(update: Update, context: CallbackContext):
    message = update.message

    # Проверяем, что сообщение содержит указанный текст
    if "Модератор: Iris | Чат-менеджер" in message.text:
        # Ищем часть сообщения с ником пользователя
        match = re.search(r'🔇 (.*?) лишается права слова', message.text)
        if match:
            display_name = match.group(1)  # Отображаемое имя пользователя
            user_id = None

            # Проверяем сущности для гиперссылки на пользователя
            if message.entities:
                for entity in message.entities:
                    # Если сущность - это TEXT_LINK (скрытая гиперссылка)
                    if entity.type == MessageEntity.TEXT_LINK:
                        user_id = entity.url.split('/')[-1]  # Извлекаем user_id из ссылки
                        break
                    # Если сущность - это MENTION (упоминание @username)
                    elif entity.type == MessageEntity.MENTION:
                        user_id = message.text[entity.offset + 1:entity.offset + entity.length]  # Извлекаем username
                        break

            # Если user_id не найден через сущности, пробуем извлечь его из текста
            if not user_id:
                # Пытаемся извлечь user_id или username из текста
                user_id_match = re.search(r'https://t.me/(\w+)', message.text)
                if user_id_match:
                    user_id = user_id_match.group(1)

            if user_id:
                chat_id = message.chat_id

                # Отправляем сообщение "Мут @user_id"
                await context.bot.send_message(chat_id=chat_id, text=f"Мут @{user_id}")
                logger.info(f"Пользователь @{user_id} замьючен.")

                # Планируем сообщение "Размут @user_id"
                context.job_queue.run_once(
                    callback=unmute_user,
                    when=0,  # Через 0 секунд (без задержки)
                    data={'user_id': user_id},
                    chat_id=chat_id
                )
            else:
                # Если user_id не найден, выдаем сообщение об ошибке
                await context.bot.send_message(
                    chat_id=message.chat_id,
                    text=f"Не удалось извлечь user_id для пользователя {display_name}. "
                         f"Проверьте формат сообщения."
                )
                logger.warning(f"Не удалось извлечь user_id для пользователя {display_name}.")

# Обработчик ошибок
async def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Ошибка: {context.error}")

def main():
    # Создаем Application с включенным job_queue
    application = Application.builder().token(TOKEN).job_queue(None).build()

    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)

    # Устанавливаем вебхук
    application.run_webhook(
        listen="0.0.0.0",
        port=5000,
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL
    )

    logger.info("Бот запущен с использованием вебхуков.")

if __name__ == '__main__':
    main()