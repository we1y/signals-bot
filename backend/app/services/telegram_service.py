import secrets
import logging
from datetime import datetime, timedelta
import pytz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import User
from app.models.models import AuthTokens

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Уровень логирования INFO для логов

TOKEN_EXPIRATION = timedelta(minutes=10)  # Время жизни токена
MOSCOW_TZ = pytz.timezone("Europe/Moscow")  # Часовой пояс Москвы

async def generate_auth_token(db: AsyncSession, telegram_id: int) -> str:
    """Генерация и сохранение одноразового токена с часовым поясом +03:00 для пользователя по telegram_id"""
    
    # Логируем начало работы функции
    logger.info(f"Начало генерации токена для пользователя с telegram_id {telegram_id}")
    
    try:
        # Ищем пользователя по telegram_id
        user = await db.execute(select(User).filter(User.telegram_id == telegram_id))
        user = user.scalars().first()
        
        if not user:
            raise ValueError(f"Пользователь с telegram_id {telegram_id} не найден в базе данных.")

        # Генерация безопасного токена
        token = secrets.token_urlsafe(32)
        logger.info(f"Сгенерирован токен: {token}")

        # Получаем текущее время в Москве
        current_time_msk = datetime.now(MOSCOW_TZ)
        expiration_time_msk = current_time_msk + TOKEN_EXPIRATION

        # Логируем текущее время и время истечения токена
        logger.info(f"Текущее время в Москве: {current_time_msk} (UTC{current_time_msk.utcoffset()})")
        logger.info(f"Время истечения токена: {expiration_time_msk} (UTC{expiration_time_msk.utcoffset()})")

        # Принудительно сохраняем время в формате +03:00
        current_time_msk = current_time_msk.astimezone(MOSCOW_TZ)
        expiration_time_msk = expiration_time_msk.astimezone(MOSCOW_TZ)

        # Записываем данные в базу данных, используя telegram_id для user_id в auth_tokens
        auth_token = AuthTokens(user_id=telegram_id, token=token, expires_at=expiration_time_msk)
        db.add(auth_token)
        logger.info(f"Токен добавлен в базу для пользователя с telegram_id {telegram_id}")

        # Выполняем commit
        await db.commit()
        logger.info(f"Токен успешно сохранен для пользователя с telegram_id {telegram_id}.")

        # Возвращаем сгенерированный токен
        return token

    except Exception as e:
        # Логируем исключения в случае ошибок
        logger.error(f"Ошибка при генерации токена для пользователя с telegram_id {telegram_id}: {e}", exc_info=True)
        raise  # Повторно выбрасываем исключение, чтобы оно было обработано выше


