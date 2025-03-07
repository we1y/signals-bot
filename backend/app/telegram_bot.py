import os
import secrets
from dotenv import load_dotenv
from fastapi import HTTPException
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackContext
from app.services.balances import create_or_update_balance
from app.database import get_db
from app.services.users import register_user, create_referral_data
import logging
from app.routers.general_routes import get_user_by_telegram_id
import httpx
from app.services.telegram_service import generate_auth_token

# Загружаем .env файл
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'app', '.env')
load_dotenv(dotenv_path)

# Получаем токен из переменных окружения
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_API_TOKEN:
    print("Ошибка: не найден токен для Telegram бота в .env файле!")
    exit(1)

# URL вашего сайта
WEBSITE_URL = "https://your-website.com"  # Замените на ваш URL

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    chat_id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    language_code = user.language_code
    photo_url = user.photo_url if hasattr(user, 'photo_url') and user.photo_url else ""

    try:
        logger.info(f"Обрабатываем /start для {chat_id}")
        logger.info(f"Полученный photo_url: {photo_url}")

        async with get_db() as db:
            db_user = None

            try:
                db_user = await get_user_by_telegram_id(chat_id, db)
                logger.info(f"Пользователь {chat_id} найден в БД. Имя: {db_user.first_name}")
                is_new_user = False
            except HTTPException as http_exc:
                if http_exc.status_code == 404:
                    logger.info(f"Пользователь {chat_id} не найден, создаем нового.")
                    db_user = await register_user(db, chat_id, username, first_name, last_name, language_code, photo_url)

                    logger.info(f"Зарегистрирован новый пользователь {db_user.first_name}. Photo URL: {db_user.photo_url}")

                    referral_data = await create_referral_data(db, db_user.id)

                    await create_or_update_balance(db, db_user.id, balance=100.0, trade_balance=50.0)

                    logger.info(f"Пользователь {db_user.first_name} зарегистрирован с балансом.")

                    backend_url = "http://localhost:8000/api/user-registered"

                    async with httpx.AsyncClient() as client:
                        response = await client.post(backend_url, json={
                            "telegram_id": chat_id,
                            "username": username,
                            "first_name": first_name,
                            "last_name": last_name,
                            "language_code": language_code,
                            "photo_url": photo_url
                        })

                    if response.status_code == 200:
                        logger.info(f"Уведомление о регистрации пользователя {chat_id} успешно отправлено на бэкенд.")
                    else:
                        logger.error(f"Ошибка при отправке данных на бэкенд: {response.status_code}, {response.text}")

                    is_new_user = True
                else:
                    raise

            try:
                logger.info(f"Вызываем generate_auth_token для пользователя {db_user.telegram_id}")
                token = await generate_auth_token(db, db_user.telegram_id)
                logger.info(f"Токен {token} успешно создан для {db_user.telegram_id}")
            except Exception as e:
                logger.error(f"Ошибка при генерации токена: {e}", exc_info=True)
                await update.message.reply_text("Ошибка при создании токена, попробуйте позже.")
                return

            auth_url = f"{WEBSITE_URL}/auth?token={token}"

            if is_new_user:
                keyboard = [[InlineKeyboardButton("Перейти на сайт", url=auth_url)]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    f"Привет, {db_user.first_name}! Ты успешно зарегистрирован.\n\n"
                    f"Твоя реферальная ссылка: {referral_data.referral_link}\n\n"
                    "Ты можешь использовать эту ссылку, чтобы приглашать других пользователей и получать бонусы!",
                    reply_markup=reply_markup
                )
            else:
                keyboard = [[InlineKeyboardButton("Открыть мини-приложение", web_app=WebAppInfo(url=auth_url))]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    f"Привет, {db_user.first_name}! Ты уже в системе.",
                    reply_markup=reply_markup
                )

    except HTTPException as http_exc:
        logger.error(f"HTTP ошибка: {http_exc.detail}")
        await update.message.reply_text(f"Ошибка: {http_exc.detail}")

    except Exception as e:
        logger.error(f"Ошибка при обработке команды /start: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка, попробуйте снова.")






# Функция для запуска бота
async def main() -> None:
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    # Запуск Telegram бота
    await application.run_polling()
