from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from fastapi import Depends

# Функция для получения сессии
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as db:
        try:
            yield db  # Возвращаем сессию для работы с ней
        finally:
            await db.close()  # Закрытие сессии после завершения работы с ней
