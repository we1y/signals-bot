import logging
import os
import random
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
import pytz
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.models.models import Signal, SignalInvestment, Balance, User
from app.services.balances import freeze_balance, unfreeze_balance, update_trading_balance

# Получаем процент прибыли/убытка из .env
PROFIT_PERCENT = float(os.getenv("PROFIT_PERCENT", 1.01))  # 1% прибыль (1.01 = +1%)
BURN_CHANCE = float(os.getenv("BURN_CHANCE", 0.1))  # 10% шанс сгорания

# Получаем параметры из .env
JOIN_TIME = int(os.getenv("JOIN_TIME", 300))  # 300 секунд (5 минут) по умолчанию
ACTIVE_TIME = int(os.getenv("ACTIVE_TIME", 1800))  # 1800 секунд (30 минут) по умолчанию

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Максимально допустимое время для сигналов (10 лет)
MAX_SECONDS = 10 * 365 * 24 * 60 * 60

def current_moscow_time():
    """Возвращает текущее время в Москве, сконвертированное в UTC"""
    return datetime.now(timezone.utc) + timedelta(hours=3)

async def create_signal(db: AsyncSession, name: str, join_time: int, active_time: int, burn_chance: float, profit_percent: float):
    """Создаёт новый торговый сигнал с корректной обработкой временных зон"""
    
    # Ограничиваем максимальные значения, чтобы не выходить за пределы БД
    if join_time > MAX_SECONDS or active_time > MAX_SECONDS:
        raise ValueError("join_time или active_time слишком велики! Максимум — 10 лет.")
        
    try:
        now = current_moscow_time()

        # Время для join_until (время, до которого сигнал доступен для входа)
        join_until = now + timedelta(seconds=join_time)
        
        # Время для expires_at (время, когда сигнал заканчивает своё действие)
        expires_at = join_until + timedelta(seconds=active_time)  # expires_at должно быть позже join_until
        
        signal = Signal(
            name=name,
            join_until=join_until,
            expires_at=expires_at,
            burn_chance=burn_chance,
            profit_percent=profit_percent
        )

        db.add(signal)
        await db.commit()
        return signal
    except Exception as e:
        await db.rollback()
        logging.error(f"Ошибка при создании сигнала: {e}")
        raise e


async def create_static_signals(db: AsyncSession):
    """Создает или перезаписывает 9 статичных сигналов при запуске сервера"""
    try:
        # Удаляем старые сигналы
        await db.execute(text("DELETE FROM signals WHERE name LIKE 'Статичный сигнал%'"))
        await db.commit()

        # Генерация времени для добавления 6 часов
        six_hours_in_seconds = 6 * 60 * 60  # 6 часов = 21600 секунд

        # Создаем 9 новых статичных сигналов
        for i in range(9):
            risk = random.uniform(0.1, 0.8)  # Риск от 10% до 80%
            work_time = random.randint(10, 17) * 60  # Время работы от 10 до 17 минут в секундах
            profit = random.uniform(0.01, 0.04)  # Доход от 1% до 4%

            # Генерация времени для join_time и active_time
            join_time = 30 * 60  # Сигналы доступны для входа 30 минут
            active_time = work_time  # Время работы сигнала

            # Добавляем 6 часов (21600 секунд) ко времени
            join_time += six_hours_in_seconds
            active_time += six_hours_in_seconds

            # Создаём сигнал с рандомизированными параметрами
            await create_signal(
                db=db,
                name=f"Статичный сигнал {i + 1}",
                join_time=join_time,
                active_time=active_time,  # Просто передаем active_time
                burn_chance=risk,
                profit_percent=profit
            )

            logging.info(f"Создан сигнал Статичный сигнал {i + 1} с риском {risk * 100:.2f}%, временем работы {work_time // 60} мин и доходом {profit * 100:.2f}%")

        logging.info("9 статичных сигналов успешно созданы.")
    except Exception as e:
        logging.error(f"Ошибка при создании статичных сигналов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при создании статичных сигналов: {e}")




async def process_signals(db: AsyncSession):
    """
    Обрабатывает завершенные сигналы, обновляет балансы пользователей.
    """
    now = current_moscow_time()

    try:
        result = await db.execute(
            select(Signal)
            .options(joinedload(Signal.investments))
            .filter(Signal.expires_at <= now, Signal.is_successful.is_(None))
        )

        signals = result.unique().scalars().all()

        for signal in signals:
            success = random.random() > BURN_CHANCE  # Если больше шанса на успех
            signal.is_successful = success

            for investment in signal.investments:
                user_id = investment.user_id
                amount = investment.amount

                # Логика для успешного сигнала
                if success:
                    profit = amount * (PROFIT_PERCENT - 1)
                    total_earned = amount + profit

                    await update_trading_balance(db, user_id, total_earned)
                    await update_earned_balance(db, user_id, profit)

                    logging.info(f"Сигнал {signal.id} УСПЕШЕН. {user_id} получил {total_earned}")
                else:
                    logging.info(f"Сигнал {signal.id} СГОРЕЛ. {user_id} потерял {amount}.")

                # Размораживаем средства пользователя
                await unfreeze_balance(db, user_id, amount)

        logging.info("Обновление сигналов завершено")
    except Exception as e:
        logging.error(f"Ошибка при обработке сигналов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке сигналов: {e}")


async def update_earned_balance(db: AsyncSession, user_id: int, earned_amount: float):
    """
    Добавляет чистый заработок пользователю и начисляет 1% реферального бонуса.
    """
    balance_result = await db.execute(select(Balance).filter(Balance.user_id == user_id))
    balance = balance_result.scalars().first()

    if not balance:
        raise HTTPException(status_code=404, detail="Баланс не найден")

    balance.earned_balance += earned_amount
    balance.balance += earned_amount

    await db.commit()
    await process_referral_bonus(db, user_id)

async def process_referral_bonus(db: AsyncSession, user_id: int):
    """
    Начисляет 1% реферального бонуса.
    """
    user_result = await db.execute(select(User).filter(User.id == user_id))
    user = user_result.scalars().first()

    if not user or not user.referred_by_id:
        logging.info(f"Рефералка: У пользователя {user_id} нет пригласившего.")
        return

    referrer_id = user.referred_by_id

    balance_result = await db.execute(select(Balance).filter(Balance.user_id == user_id))
    balance = balance_result.scalars().first()

    if not balance:
        logging.warning(f"Баланс не найден для {user_id}, невозможно начислить реферальный бонус.")
        return

    referral_bonus = balance.earned_balance * 0.01

    if referral_bonus > 0:
        ref_balance_result = await db.execute(select(Balance).filter(Balance.user_id == referrer_id))
        ref_balance = ref_balance_result.scalars().first()

        if ref_balance:
            ref_balance.balance += referral_bonus
            await db.commit()
            logging.info(f"Реферальный бонус {referral_bonus} начислен {referrer_id} от {user_id}")
        else:
            logging.warning(f"Баланс реферера {referrer_id} не найден.")
