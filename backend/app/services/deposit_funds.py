import os
import aiohttp
import logging
from app.models.models import Balance, Transaction
from app.database import get_db as main
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Логирование
logger = logging.getLogger(__name__)

# Ваш API ключ NOWPayments
API_KEY = os.getenv("API_KEY")

# URL для создания платежа
NOWPAYMENTS_API_URL = "https://api.nowpayments.io/v1/payment"

async def create_payment_address(user_id: int, amount: float, session: AsyncSession = None):
    """
    Метод для создания платежа через NOWPayments для пополнения баланса пользователя.

    :param user_id: ID пользователя
    :param amount: Сумма для пополнения баланса
    :param session: Сессия для работы с базой данных
    :return: URL для оплаты и информация о транзакции
    """
    if session is None:
        session = main()

    try:
        # Получаем баланс пользователя (если нужно)
        result = await session.execute(select(Balance).filter_by(user_id=user_id))
        balance = result.scalars().first()

        if balance is None:
            # Если у пользователя нет записи о балансе, создаем новую
            balance = Balance(user_id=user_id, amount=0)

        # Создаем запрос на API NOWPayments для генерации адреса для пополнения
        async with aiohttp.ClientSession() as client:
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            }
            data = {
                "amount": amount,
                "currency": "usd",  # Замените на нужную валюту
                "pay_currency": "usdttrc20",  # Указываем криптовалюту для оплаты
                "ipn_callback_url": "https://yourdomain.com/callback",  # URL для обратного вызова
                "order_id": f"user_{user_id}_deposit"
            }
            
            # Отправляем POST запрос
            async with client.post(NOWPAYMENTS_API_URL, json=data, headers=headers) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    payment_url = response_data.get('invoice_url')
                    transaction_id = response_data.get('payment_id')

                    # Создаем запись о транзакции
                    transaction = Transaction(
                        user_id=user_id,
                        amount=amount,
                        transaction_type="deposit",
                        status="pending",
                        external_transaction_id=transaction_id
                    )
                    session.add(transaction)

                    # Сохраняем изменения
                    await session.commit()

                    logger.info(f"Платеж для пользователя {user_id} успешно создан. Ссылка на оплату: {payment_url}")

                    return {
                        "payment_url": payment_url,
                        "transaction_id": transaction_id
                    }
                else:
                    logger.error(f"Ошибка при создании платежа через NOWPayments: {response_data}")
                    return {"error": "Не удалось создать платеж"}
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса для пользователя {user_id}: {str(e)}")
        return {"error": "Ошибка при обработке запроса"}
