import re
from telegram import Update, MessageEntity
from telegram.ext import Application, MessageHandler, filters, CallbackContext

TOKEN = '8084478893:AAFM_VQOn7lwTZZpmorl44Sf5NFT6NxC7Ak'

# Функция для отправки сообщения "Размут @user_id"
async def unmute_user(context: CallbackContext):
    job = context.job
    chat_id = job.chat_id
    user_id = job.data['user_id']

    await context.bot.send_message(chat_id=chat_id, text=f"Размут @{user_id}")

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
                # Для отладки выведем все сущности сообщения
                await context.bot.send_message(
                    chat_id=message.chat_id,
                    text=f"Сущности сообщения: {message.entities}"
                )

def main():
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()