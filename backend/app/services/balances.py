import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.models import Balance, Referrals
from app.statistics_services.balance_actions import log_transaction
from app.database import get_db
# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Отключаем логирование SQL-запросов (уровень logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Получение баланса пользователя
async def get_balance(db: AsyncSession, user_id: int) -> Balance:
    try:
        logger.info(f"Получение баланса для пользователя {user_id}")
        result = await db.execute(select(Balance).filter(Balance.user_id == user_id))
        balance = result.scalars().first()

        if balance:
            logger.info(f"Баланс: {balance.balance}, Торговый баланс: {balance.trade_balance}, Замороженный баланс: {balance.frozen_balance}")
        else:
            logger.warning(f"Баланс для пользователя {user_id} не найден.")

        return balance
    except SQLAlchemyError as e:
        logger.error(f"Ошибка получения баланса пользователя {user_id}: {e}")
        return None

# Создание или обновление баланса
async def create_or_update_balance(db: AsyncSession, user_id: int, balance: float, trade_balance: float, frozen_balance: float = 0.0) -> Balance:
    try:
        logger.info(f"Создание/обновление баланса для пользователя {user_id}")
        result = await db.execute(select(Balance).filter(Balance.user_id == user_id))
        user_balance = result.scalars().first()

        if user_balance is None:
            logger.info(f"Баланс не найден, создаем новый.")
            user_balance = Balance(user_id=user_id, balance=balance, trade_balance=trade_balance, frozen_balance=frozen_balance)
            db.add(user_balance)
        else:
            logger.info(f"Баланс найден, обновляем данные.")
            user_balance.balance = balance
            user_balance.trade_balance = trade_balance
            user_balance.frozen_balance = frozen_balance

        await db.commit()
        await db.refresh(user_balance)
        return user_balance
    except SQLAlchemyError as e:
        logger.error(f"Ошибка обновления баланса {user_id}: {e}")
        await db.rollback()
        return None

# Обновление основного баланса
async def update_balance(db: AsyncSession, user_id: int, amount: float) -> bool:
    try:
        logger.info(f"Обновление баланса {user_id} на {amount}")
        result = await db.execute(select(Balance).filter(Balance.user_id == user_id))
        balance = result.scalars().first()

        if balance:
            balance.balance += amount
            await db.commit()
            await db.refresh(balance)

            # Логируем операцию
            await log_transaction(db, user_id, amount, "balance_update")

            return True
        return False
    except SQLAlchemyError as e:
        logger.error(f"Ошибка обновления баланса {user_id}: {e}")
        await db.rollback()
        return False

# Обновление торгового баланса
async def update_trading_balance(db: AsyncSession, user_id: int, amount: float) -> bool:
    try:
        logger.info(f"Обновление торгового баланса {user_id} на {amount}")
        result = await db.execute(select(Balance).filter(Balance.user_id == user_id))
        balance = result.scalars().first()

        if balance:
            balance.trade_balance += amount
            await db.commit()
            await db.refresh(balance)

            # Логируем операцию
            await log_transaction(db, user_id, amount, "trade_balance_update")

            return True
        return False
    except SQLAlchemyError as e:
        logger.error(f"Ошибка обновления торгового баланса {user_id}: {e}")
        await db.rollback()
        return False

# Заморозка средств
async def freeze_balance(db: AsyncSession, user_id: int, amount: float) -> bool:
    try:
        logger.info(f"Замораживаем {amount} для пользователя {user_id}")
        result = await db.execute(select(Balance).filter(Balance.user_id == user_id))
        balance = result.scalars().first()

        if balance and balance.balance >= amount:
            balance.balance -= amount
            balance.frozen_balance += amount
            await db.commit()
            await db.refresh(balance)

            # Логируем операцию
            await log_transaction(db, user_id, amount, "freeze")

            return True
        logger.warning(f"Недостаточно средств для заморозки у пользователя {user_id}")
        return False
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при заморозке баланса {user_id}: {e}")
        await db.rollback()
        return False

# Размораживание средств
async def unfreeze_balance(db: AsyncSession, user_id: int, amount: float) -> bool:
    try:
        logger.info(f"Размораживаем {amount} для пользователя {user_id}")
        result = await db.execute(select(Balance).filter(Balance.user_id == user_id))
        balance = result.scalars().first()

        if balance and balance.frozen_balance >= amount:
            balance.frozen_balance -= amount
            balance.balance += amount
            await db.commit()
            await db.refresh(balance)

            # Логируем операцию
            await log_transaction(db, user_id, amount, "unfreeze")

            return True
        logger.warning(f"Недостаточно замороженных средств для разморозки у пользователя {user_id}")
        return False
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при разморозке баланса {user_id}: {e}")
        await db.rollback()
        return False

# Проверка достаточности основного баланса
async def has_sufficient_balance(db: AsyncSession, user_id: int, amount: float) -> bool:
    try:
        result = await db.execute(select(Balance).filter(Balance.user_id == user_id))
        balance = result.scalars().first()

        if balance and balance.balance >= amount:
            return True
        return False
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при проверке баланса {user_id}: {e}")
        return False

# Проверка достаточности торгового баланса
async def has_sufficient_trading_balance(db: AsyncSession, user_id: int, amount: float) -> bool:
    try:
        result = await db.execute(select(Balance).filter(Balance.user_id == user_id))
        balance = result.scalars().first()

        if balance and balance.trade_balance >= amount:
            return True
        return False
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при проверке торгового баланса {user_id}: {e}")
        return False

async def update_referral_by_url(referral_by_telegram: Referrals, referral_by_link: Referrals) -> bool:
    try:
        async with get_db() as db:  # Используем get_db(), чтобы получить сессию базы данных
            # Извлекаем данные из объектов
            telegram_id = referral_by_telegram.telegram_id
            referral_link = referral_by_link.referral_link
            
            # Разбираем referral_link, чтобы извлечь telegram_id
            if isinstance(referral_link, str):
                # Разделяем ссылку по "/" и по "-"
                referral_parts = referral_link.split("/")[-1].split("-")
                
                if len(referral_parts) != 2:
                    logger.error(f"Неверный формат referral_link: {referral_link}")
                    return False
                
                # Извлекаем только telegram_id из второй части
                link_telegram_id = int(referral_parts[1])  # Преобразуем вторую часть в целое число (telegram_id)
                
            else:
                logger.error(f"Неверный формат referral_link: {referral_link}")
                return False

            # Ищем владельца URL по link_telegram_id (это тот, кто создал ссылку)
            result = await db.execute(select(Referrals).filter(Referrals.telegram_id == link_telegram_id))
            referral_owner = result.scalars().first()

            if not referral_owner:
                logger.error(f"Запись с referral_link {referral_link} не найдена.")
                return False

            # Используем merge для привязки объекта к текущей сессии
            referral_owner = await db.merge(referral_owner)
            referral_by_telegram = await db.merge(referral_by_telegram)

            # Обновляем invited_count у владельца URL
            referral_owner.invited_count += 1
            
            # Обновляем referred_by у пользователя, который перешел по ссылке
            referral_by_telegram.referred_by = link_telegram_id  # Присваиваем ему ID владельца ссылки

            # Сохраняем изменения в базе данных
            await db.commit()  # Подтверждаем изменения
            await db.refresh(referral_by_telegram)  # Обновляем данные после коммита
            await db.refresh(referral_owner)  # Обновляем данные после коммита

            # Логируем операцию
            logger.info(f"Обновлены данные для telegram_id {telegram_id}. Referred_by: {referral_by_telegram.referred_by}, Invited_count: {referral_owner.invited_count}")

            return True

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при обновлении данных для telegram_id {telegram_id}: {e}")
        # Откатываем изменения в случае ошибки
        if db:
            await db.rollback()
        return False
