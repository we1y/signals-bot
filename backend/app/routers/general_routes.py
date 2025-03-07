import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import AuthTokens, User
from app.services.get_db import get_db
from datetime import datetime, timezone
from tzlocal import get_localzone
from sqlalchemy.orm import subqueryload
from app.database import get_db as main
# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Auth"])  # Используем ОДИН роутер

@router.get("/auth")
async def auth_with_token(token: str, db: AsyncSession = Depends(get_db)):
    """Проверка токена и вход в систему"""
    
    logger.info(f"Получаем токен: {token}")
    
    result = await db.execute(select(AuthTokens).filter(AuthTokens.token == token))
    auth_token = result.scalars().first()

    if auth_token:
        logger.info(f"Найден токен: {auth_token.token}, Время истечения: {auth_token.expires_at}")
    else:
        logger.warning(f"Токен {token} не найден в базе данных")
        raise HTTPException(status_code=403, detail="Недействительный или просроченный токен")

    if auth_token.expires_at < datetime.now(timezone.utc):
        logger.warning(f"Токен {token} просрочен.")
        raise HTTPException(status_code=403, detail="Недействительный или просроченный токен")

    logger.info(f"Получаем пользователя с ID: {auth_token.user_id}")
    result = await db.execute(select(User).filter(User.telegram_id == auth_token.user_id))
    user = result.scalars().first()

    if user:
        logger.info(f"Найден пользователь: {user.username}, Telegram ID: {user.telegram_id}")
    else:
        logger.warning(f"Пользователь с ID {auth_token.user_id} не найден в базе данных")
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    local_tz = get_localzone()
    expires_at_local = auth_token.expires_at.astimezone(local_tz)

    logger.info(f"Время истечения токена в локальном часовом поясе: {expires_at_local}")

    return {
        "telegram_id": user.telegram_id,
        "username": user.username,
        "message": "Успешный вход!",
        "token_expires_at": expires_at_local.strftime("%Y-%m-%d %H:%M:%S %z")
    }



# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Функция получения пользователя по telegram_id
@router.get("/user/{telegram_id}")
async def get_user_by_telegram_id(telegram_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(User)
            .options(
                subqueryload(User.balance),
                subqueryload(User.referred_by)
            )
            .filter(User.telegram_id == telegram_id)
        )
        user = result.scalars().first()

        if not user:
            logger.warning(f"Пользователь с telegram_id {telegram_id} не найден.")
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "language_code": user.language_code,
            "is_bot": user.is_bot,
            "photo_url": user.photo_url,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "balance": user.balance.balance if user.balance else 0.0,
            "trade_balance": user.balance.trade_balance if user.balance else 0.0,
            "referred_by": {
                "id": user.referred_by.id if user.referred_by else None,
                "telegram_id": user.referred_by.telegram_id if user.referred_by else None,
                "username": user.referred_by.username if user.referred_by else None
            } if user.referred_by else None
        }

    except HTTPException:
        raise  # Оставляем только исходное исключение 404

    except Exception as e:
        logger.error(f"Ошибка при получении пользователя {telegram_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

