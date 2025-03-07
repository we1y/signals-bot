import random
import string
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.models import User, Referrals
from app.database import get_db


# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)



# Функция генерации уникального реферального кода
async def generate_unique_referral_code(db: AsyncSession, user_id: int, telegram_id: int) -> str:
    while True:
        # Используем telegram_id вместо случайного кода
        referral_link = f"https://app.com/ref/{user_id}-{telegram_id}"

        # Проверяем, не существует ли уже такая реферальная ссылка
        result = await db.execute(select(Referrals).filter(Referrals.referral_link == referral_link))
        existing_referral = result.scalars().first()

        if not existing_referral:
            logger.info(f"Генерирован уникальный реферальный код для пользователя {user_id} с telegram_id {telegram_id}: {referral_link}")
            return referral_link


    
# Функция для создания реферальной записи
async def create_referral_data(db: AsyncSession, user_id: int, referrer_id: int = None):
    try:
        logger.info(f"Создание реферальной записи для пользователя {user_id}...")

        # Проверяем, есть ли уже реферальная запись
        result = await db.execute(select(Referrals).filter(Referrals.user_id == user_id))
        existing_referral = result.scalars().first()

        if existing_referral:
            logger.info(f"Реферальная запись для пользователя {user_id} уже существует.")
            return existing_referral

        # Получаем пользователя
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()

        if not user:
            logger.error(f"Не найден пользователь с ID {user_id}. Операция отменена.")
            return None

        # Генерируем уникальную реферальную ссылку с использованием telegram_id
        referral_link = await generate_unique_referral_code(db, user_id, user.telegram_id)

        # Проверяем реферера, если он указан
        referrer = None
        if referrer_id:
            result = await db.execute(select(User).filter(User.id == referrer_id))
            referrer = result.scalars().first()

            if not referrer:
                logger.warning(f"Реферер с ID {referrer_id} не найден, запись будет создана без реферера.")
                referrer_id = None  # Если реферера нет, оставляем поле пустым

        # Создаем запись в таблице Referrals
        new_referral = Referrals(
            user_id=user_id,
            telegram_id=user.telegram_id,
            referral_link=referral_link,
            referrer_id=referrer_id,  # используем правильное имя поля
            invited_count=0,
            referred_by=referrer_id  # исправляем на правильное поле
        )

        db.add(new_referral)

        # Если есть реферер — увеличиваем ему счетчик приглашенных
        if referrer_id:
            referrer_referral = await db.execute(select(Referrals).filter(Referrals.user_id == referrer_id))
            referrer_ref = referrer_referral.scalars().first()

            if referrer_ref:
                referrer_ref.invited_count += 1
                logger.info(f"Увеличен счетчик приглашенных у пользователя {referrer_id}.")

        await db.commit()
        await db.refresh(new_referral)

        logger.info(f"Реферальная запись для пользователя {user_id} успешно создана: {referral_link}")
        return new_referral

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при создании реферальной записи для {user_id}: {e}", exc_info=True)
        await db.rollback()
        return None


# Функция для регистрации пользователя
async def register_user(db: AsyncSession, chat_id: int, username: str, first_name: str, last_name: str, language_code: str, photo_url: str = None):
    try:
        logger.info(f"Пытаемся зарегистрировать пользователя с chat_id: {chat_id}")

        # Проверяем, существует ли пользователь с таким chat_id
        result = await db.execute(select(User).filter(User.telegram_id == chat_id))
        db_user = result.scalars().first()

        if not db_user:
            # Если пользователя нет, создаем нового
            db_user = User(
                telegram_id=chat_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code,
                photo_url=photo_url  # Обработка photo_url, если оно передано
            )
            db.add(db_user)
            await db.commit()  # Коммитим нового пользователя
            await db.refresh(db_user)
            logger.info(f"Пользователь {first_name} {last_name} (ID: {chat_id}) успешно зарегистрирован!")
        else:
            logger.info(f"Пользователь с chat_id {chat_id} уже существует.")

        return db_user

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при регистрации пользователя с chat_id {chat_id}: {e}", exc_info=True)
        await db.rollback()  # Откат транзакции в случае ошибки
        raise  # Повторно генерируем исключение для дальнейшей обработки


async def add_referral(db: AsyncSession, telegram_id: int, referral_link: str):
    """
    Добавляет пользователя в реферальную систему.

    :param db: Асинхронная сессия SQLAlchemy.
    :param telegram_id: Telegram ID того, кого добавляем.
    :param referral_link: Реферальная ссылка (Telegram ID пригласившего).
    
    :return: Объект Referrals, если успешно, иначе None.
    """
    try:
        logger.info(f"Добавляем реферала: {telegram_id} через ссылку {referral_link}")

        # Извлекаем telegram_id из referral_link (например, если ссылка вида "https://app.com/ref/27-5592773679")
        referrer_telegram_id = extract_telegram_id_from_link(referral_link)

        # Ищем пригласившего пользователя по его Telegram ID
        referrer_result = await db.execute(select(User).filter(User.telegram_id == referrer_telegram_id))
        referrer = referrer_result.scalars().first()

        if not referrer:
            logger.warning(f"Пользователь с referral_link {referral_link} не найден.")
            return None

        # Проверяем, существует ли уже пользователь с таким telegram_id
        existing_user = await db.execute(select(User).filter(User.telegram_id == telegram_id))
        existing_user = existing_user.scalars().first()

        if existing_user:
            logger.warning(f"Пользователь с telegram_id {telegram_id} уже существует.")
            return None  # Если пользователь уже существует, ничего не делаем

        # Создаем нового пользователя в таблице Users, если он еще не существует
        new_user = User(
            telegram_id=telegram_id,  # Telegram ID пользователя
            username="",               # Здесь можно добавить логику для получения других данных, если нужно
            first_name="",
            last_name="",
            language_code="en",  # Можно оставить по умолчанию или изменить в зависимости от данных
            is_bot=False
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)  # Получаем объект нового пользователя

        # Создаем запись в таблице Referrals для нового пользователя
        new_referral = Referrals(
            user_id=new_user.id,           # ID нового пользователя в системе
            telegram_id=telegram_id,       # Telegram ID приглашенного
            referral_link=referral_link,   # Ссылка с реферальным кодом
            referred_by=referrer.id        # ID пригласившего пользователя (ссылается на пользователя)
        )
        db.add(new_referral)

        # Увеличиваем счетчик приглашенных у реферера
        referrer_ref_result = await db.execute(select(Referrals).filter(Referrals.user_id == referrer.id))
        referrer_ref = referrer_ref_result.scalars().first()

        if referrer_ref:
            referrer_ref.invited_count += 1
            logger.info(f"Увеличен счетчик приглашенных у пользователя {referrer.id}.")

        await db.commit()
        await db.refresh(new_referral)

        logger.info(f"Реферальная запись для {telegram_id} успешно создана!")
        return new_referral

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении реферала {telegram_id}: {e}", exc_info=True)
        await db.rollback()
        return None


def extract_telegram_id_from_link(referral_link: str) -> int:
    """
    Извлекает telegram_id из реферальной ссылки.
    Например, если ссылка в формате: 'https://app.com/ref/27-5592773679',
    то извлекается 5592773679.
    """
    try:
        parts = referral_link.split('/')
        # Получаем часть, которая является telegram_id, например: '27-5592773679'
        return int(parts[-1].split('-')[-1])  # Возвращаем только последний числовой элемент
    except Exception as e:
        logger.error(f"Ошибка при извлечении Telegram ID из ссылки {referral_link}: {e}")
        return None

