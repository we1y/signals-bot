# balance_actions.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Transaction

async def log_transaction(db: AsyncSession, user_id: int, amount: float, transaction_type: str):
    from datetime import datetime

    transaction = Transaction(
        user_id=user_id,
        amount=amount,
        transaction_type=transaction_type,
        created_at=datetime.utcnow()  # записываем текущее время
    )
    
    db.add(transaction)
    await db.commit()  # сохраняем транзакцию в базу данны