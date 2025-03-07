import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.services.get_db import get_db  # Импортируем get_db
from app.models.models import Referrals, User, Balance 
from app.services.balances import (
    has_sufficient_trading_balance,
    update_balance, 
    has_sufficient_balance,
    get_balance,
    update_referral_by_url,
    update_trading_balance,
    freeze_balance,  # 🔹 Функция заморозки
    unfreeze_balance  # 🔹 Функция разблокировки
)

router = APIRouter()

### 🔹 **Pydantic-модель для сумм транзакций**
class AmountRequest(BaseModel):
    amount: float

class ReferralRequest(BaseModel):
    telegram_id: int
    referral_link: str
# Отключаем логирование SQL-запросов (уровень logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

### 🔹 **Получение баланса с учетом замороженных средств**
@router.get("/balance/{telegram_id}")
async def get_balance_by_telegram_id(telegram_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).options(joinedload(User.balance)).filter(User.telegram_id == telegram_id)
    )
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "balance": user.balance.balance if user.balance else 0.0,
        "trade_balance": user.balance.trade_balance if user.balance else 0.0,
        "frozen_balance": user.balance.frozen_balance if user.balance else 0.0  # 🔹 Добавили
    }

### 🔹 **Перевод на торговый баланс (с заморозкой)**
@router.post("/transfer_to_trading/{telegram_id}")
async def transfer_to_trading(telegram_id: int, request: AmountRequest, db: AsyncSession = Depends(get_db)):
    amount = request.amount

    if amount <= 0:
        logging.warning(f"Invalid transfer amount: {amount}")
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    result = await db.execute(select(User).filter(User.telegram_id == telegram_id))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if await has_sufficient_balance(db, user.id, amount):
        if await update_balance(db, user.id, -amount):  # Уменьшаем основной баланс
            if await update_trading_balance(db, user.id, amount):  # Добавляем в торговый баланс
                await freeze_balance(db, user.id, amount)  # 🔹 Замораживаем средства
                logging.info(f"Transferred {amount} to trading balance for user_id {user.id}, funds frozen")
                return {"message": "Transfer successful, funds frozen"}

    raise HTTPException(status_code=400, detail="Insufficient balance")

@router.get("/unfreeze_balance/{telegram_id}")
async def unfreeze(telegram_id: int, db: AsyncSession = Depends(get_db)):
    # Ищем пользователя по telegram_id
    result = await db.execute(select(User).filter(User.telegram_id == telegram_id))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем баланс пользователя
    balance_result = await db.execute(select(Balance).filter(Balance.user_id == user.id))
    balance = balance_result.scalars().first()

    if not balance or balance.frozen_balance <= 0:
        raise HTTPException(status_code=400, detail="No frozen balance to unfreeze")

    # Размораживаем весь баланс
    amount_to_unfreeze = balance.frozen_balance
    balance.trade_balance += amount_to_unfreeze
    balance.frozen_balance = 0

    await db.commit()

    logging.info(f"Unfroze {amount_to_unfreeze} for user {user.id}")

    return {
        "message": "Balance unfrozen",
        "unfrozen_amount": amount_to_unfreeze,
        "new_trade_balance": balance.trade_balance
    }
### 🔹 **Пополнение баланса**
@router.post("/deposit/{telegram_id}")
async def deposit(telegram_id: int, request: AmountRequest, db: AsyncSession = Depends(get_db)):
    amount = request.amount
    
    if amount <= 0:
        logging.warning(f"Invalid deposit amount: {amount}")
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    result = await db.execute(select(User).filter(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user is None:
        logging.warning(f"User with telegram_id {telegram_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

    balance = await get_balance(db, user.id)
    if balance is None:
        logging.warning(f"Balance not found for user {user.id}")
        raise HTTPException(status_code=404, detail="Balance not found")

    success = await update_balance(db, user.id, amount)

    if success:
        # ✅ Запрашиваем обновленный баланс из базы
        updated_balance = await get_balance(db, user.id)

        logging.info(f"Deposited {amount} to user_id {user.id}, new_balance: {updated_balance.balance}")
        return {"message": "Deposit successful", "new_balance": updated_balance.balance}


    raise HTTPException(status_code=500, detail="Failed to update balance")


@router.get("/referral_tree/{telegram_id}")
async def get_referral_tree(telegram_id: str, db: AsyncSession = Depends(get_db)):
    async def fetch_referrals(telegram_id):
        """Рекурсивно получаем всех приглашённых пользователей по их Telegram ID"""
        logging.info(f"Fetching referrals for telegram_id: {telegram_id}")  

        result = await db.execute(
            select(Referrals).filter(Referrals.referred_by == telegram_id)  # Ищем рефералов по telegram_id
        )
        referrals = result.scalars().all()

        logging.info(f"Found {len(referrals)} referrals for telegram_id: {telegram_id}")  

        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "telegram_id": r.telegram_id,
                "referral_link": r.referral_link,
                "invited_count": r.invited_count,
                "referrer_id": r.referrer_id,
                "referred_by": r.referred_by,
                "invited_users": await fetch_referrals(r.telegram_id)  # Рекурсивно получаем рефералов
            }
            for r in referrals
        ]

    try:
        logging.info(f"Received request to fetch referral tree for telegram_id: {telegram_id}")  

        # Приводим telegram_id к int
        telegram_id = int(telegram_id)

        # Ищем пользователя по его telegram_id
        result = await db.execute(
            select(Referrals).filter(Referrals.telegram_id == telegram_id)
        )
        user = result.scalars().first()

        if not user:
            logging.warning(f"User not found for telegram_id: {telegram_id}")  
            raise HTTPException(status_code=404, detail="User not found")

        logging.info(f"Found user: {user.user_id} with telegram_id: {telegram_id}")  

        # Получаем всех приглашённых пользователей (рефералов)
        referral_tree = {
            "id": user.id,
            "user_id": user.user_id,
            "telegram_id": user.telegram_id,
            "referral_link": user.referral_link,
            "invited_count": user.invited_count,
            "referrer_id": user.referrer_id,
            "referred_by": user.referred_by,
            "invited_users": await fetch_referrals(user.telegram_id)  # Исправленный вызов
        }

        logging.info(f"Referral tree successfully retrieved for telegram_id: {telegram_id}")  

        return referral_tree

    except Exception as e:
        logging.error(f"Error retrieving referral tree for telegram_id: {telegram_id}: {e}", exc_info=True)  
        raise HTTPException(status_code=500, detail="An error occurred while retrieving referral tree.")

@router.post("/transfer_to_main/{telegram_id}")
async def transfer_to_main(telegram_id: int, request: AmountRequest, db: AsyncSession = Depends(get_db)):
    amount = request.amount

    if amount <= 0:
        logging.warning(f"Invalid transfer amount: {amount}")
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    result = await db.execute(select(User).filter(User.telegram_id == telegram_id))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем, хватает ли средств на торговом балансе
    if await has_sufficient_trading_balance(db, user.id, amount):
        # Уменьшаем торговый баланс
        if await update_trading_balance(db, user.id, -amount):
            # Добавляем на основной баланс
            if await update_balance(db, user.id, amount):
                logging.info(f"Transferred {amount} from trading to main balance for user_id {user.id}")
                
                # Получаем актуальные данные баланса
                result = await db.execute(
                    select(User).options(joinedload(User.balance)).filter(User.telegram_id == telegram_id)
                )
                user = result.scalars().first()

                if user is None:
                    raise HTTPException(status_code=404, detail="User not found")

                # Возвращаем актуальные значения балансов
                return {
                    "id": user.id,
                    "telegram_id": user.telegram_id,
                    "balance": user.balance.balance if user.balance else 0.0,
                    "trade_balance": user.balance.trade_balance if user.balance else 0.0,
                    "frozen_balance": user.balance.frozen_balance if user.balance else 0.0  # 🔹 Замороженные средства
                }

    raise HTTPException(status_code=400, detail="Insufficient trading balance")


     