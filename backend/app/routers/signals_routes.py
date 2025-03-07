import logging
import os
import random
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from app.services.get_db import get_db  # Импортируем get_db
from app.models.models import User, Balance, Signal, SignalInvestment
from app.services.balances import freeze_balance, update_trading_balance
from app.services.signals import create_signal  # Импортируем метод создания сигнала

# Отключаем логирование SQL-запросов (уровень logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Настройка логирования в файл logs_signals.txt (рядом с main)
log_file_path = os.path.join(os.path.dirname(__file__), "../logs_signals.txt")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

signalis_router = APIRouter(prefix="/signals", tags=["Signals"])

### 🔹 **Pydantic-модель для запроса**
class JoinSignalRequest(BaseModel):
    telegram_id: int
    signal_id: int
    amount: float

class CustomSignalRequest(BaseModel):
    name: str
    join_time: int  # Время до входа в секундах
    active_time: int  # Длительность активности сигнала в секундах

class RandomSignalRequest(BaseModel):
    name: str  # Имя сигнала

### 🔹 **Маршрут для входа в сигнал**
@signalis_router.post("/join")
async def join_signal(request: JoinSignalRequest, db: AsyncSession = Depends(get_db)):
    """ Пользователь входит в сигнал. Средства с trade_balance переносятся в frozen_balance. """
    telegram_id = request.telegram_id
    signal_id = request.signal_id
    amount = request.amount

    if amount <= 0:
        logging.warning(f"User {telegram_id} tried to join signal {signal_id} with invalid amount {amount}")
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    try:
        user_result = await db.execute(select(User).filter(User.telegram_id == telegram_id))
        user = user_result.scalars().first()
        if not user:
            logging.warning(f"User {telegram_id} not found while trying to join signal {signal_id}")
            raise HTTPException(status_code=404, detail="User not found")

        balance_result = await db.execute(select(Balance).filter(Balance.user_id == user.id))
        balance = balance_result.scalars().first()
        if not balance or balance.trade_balance < amount:
            logging.warning(f"User {user.id} has insufficient balance for signal {signal_id}")
            raise HTTPException(status_code=400, detail="Insufficient trading balance")

        signal_result = await db.execute(select(Signal).filter(Signal.id == signal_id, Signal.join_until > func.now()))
        signal = signal_result.scalars().first()
        if not signal:
            logging.warning(f"Signal {signal_id} is not available for user {user.id}")
            raise HTTPException(status_code=400, detail="Signal is not available for joining")

        # Обновление баланса и заморозка средств
        await update_trading_balance(db, user.id, -amount)
        await freeze_balance(db, user.id, amount)

        # Добавляем инвестицию в базу данных
        investment = SignalInvestment(signal_id=signal_id, user_id=user.id, amount=amount)
        db.add(investment)
        await db.commit()

        logging.info(f"User {user.id} successfully joined signal {signal_id} with {amount} frozen funds.")
        return {"message": "Successfully joined the signal", "signal_id": signal_id, "amount": amount}

    except Exception as e:
        logging.error(f"Error while user {telegram_id} joining signal {signal_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while joining the signal.")

### 🔹 **Создание случайного сигнала**
# Структура запроса для случайного сигнала
class RandomSignalRequest(BaseModel):
    name: str

@signalis_router.post("/create_random")
async def create_random_signal(request: RandomSignalRequest, db: AsyncSession = Depends(get_db)):
    """Создает случайный сигнал со случайными параметрами (время до входа, продолжительность, шанс сгорания, процент прибыли)."""
    name = request.name

    # Генерируем случайные параметры
    join_time = random.randint(60, 600)  # 1-10 минут до входа
    active_time = random.randint(600, 3600)  # 10-60 минут активное время
    burn_chance = random.uniform(1, 10)  # 1-10% шанс сгорания
    profit_percent = round(random.uniform(1.01, 1.20), 2)  # 1.01 - 1.20 (1-20% прибыли)

    try:
        signal = await create_signal(db, name, join_time, active_time, burn_chance, profit_percent)
        logging.info(f"Random signal created: {signal.name} (ID: {signal.id}), join_until: {signal.join_until}, expires_at: {signal.expires_at}, burn_chance: {signal.burn_chance}, profit_percent: {signal.profit_percent}")

        return {
            "message": "Random signal created successfully",
            "signal_id": signal.id,
            "name": signal.name,
            "join_until": signal.join_until,
            "expires_at": signal.expires_at,
            "burn_chance": burn_chance,
            "profit_percent": profit_percent
        }
    except Exception as e:
        logging.error(f"Error while creating random signal {name}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while creating a random signal.")

class CustomSignalRequest(BaseModel):
    name: str
    join_time: int
    active_time: int
    burn_chance: float
    profit_percent: float

@signalis_router.post("/create_custom")
async def create_custom_signal(request: CustomSignalRequest, db: AsyncSession = Depends(get_db)):
    """Создает сигнал с пользовательскими параметрами (время до входа, продолжительность, шанс сгорания, процент прибыли)."""
    name = request.name
    join_time = request.join_time
    active_time = request.active_time
    burn_chance = request.burn_chance
    profit_percent = request.profit_percent

    # Проверка валидности значений
    if join_time <= 0 or active_time <= 0 or burn_chance < 0 or profit_percent < 1:
        logging.warning(f"Invalid parameters for {name}: join_time={join_time}, active_time={active_time}, burn_chance={burn_chance}, profit_percent={profit_percent}")
        raise HTTPException(status_code=400, detail="Invalid parameters: join_time and active_time must be > 0, burn_chance >= 0, profit_percent >= 1")

    try:
        signal = await create_signal(db, name, join_time, active_time, burn_chance, profit_percent)
        logging.info(f"Custom signal created: {signal.name} (ID: {signal.id}), join_until: {signal.join_until}, expires_at: {signal.expires_at}, burn_chance: {signal.burn_chance}, profit_percent: {signal.profit_percent}")

        return {
            "message": "Custom signal created successfully",
            "signal_id": signal.id,
            "name": signal.name,
            "join_until": signal.join_until,
            "expires_at": signal.expires_at,
            "burn_chance": burn_chance,
            "profit_percent": profit_percent
        }
    except Exception as e:
        logging.error(f"Error while creating custom signal {name}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while creating a custom signal.")

@signalis_router.get("/active")
async def get_active_signals(db: AsyncSession = Depends(get_db)):
    """ Получает список всех активных сигналов, которые доступны для входа. """
    try:
        active_signals_result = await db.execute(
            select(Signal).filter(Signal.join_until > func.now())
        )
        active_signals = active_signals_result.scalars().all()

        if not active_signals:
            return {"message": "No active signals available."}

        signals_data = [
            {
                "signal_id": signal.id,
                "name": signal.name,
                "join_until": signal.join_until,
                "expires_at": signal.expires_at
            }
            for signal in active_signals
        ]
        
        return {"active_signals": signals_data}
    except Exception as e:
        logging.error(f"Error retrieving active signals: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving active signals.")
    
@signalis_router.get("/investments/{telegram_id}")
async def get_user_investments(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Ищет user_id по telegram_id, затем получает все инвестиции пользователя.
    """
    # 1. Ищем user_id по telegram_id
    user_result = await db.execute(select(User.id).filter(User.telegram_id == telegram_id))
    user = user_result.scalar()

    if not user:
        return {"message": "Пользователь не найден"}

    # 2. Ищем все инвестиции пользователя
    investments_result = await db.execute(select(SignalInvestment).filter(SignalInvestment.user_id == user))
    investments = investments_result.scalars().all()

    if not investments:
        return {"message": "У пользователя нет инвестиций"}

    # 3. Формируем ответ
    return {
        "user_id": user,
        "investments": [
            {
                "id": inv.id,
                "signal_id": inv.signal_id,
                "amount": inv.amount,
                "profit": inv.profit,
                "created_at": inv.created_at
            }
            for inv in investments
        ]
    }