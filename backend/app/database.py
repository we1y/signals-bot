from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'app', '.env')
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не задан в .env файле!")

# Строка подключения для asyncpg
DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Создаем асинхронный движок SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Создаем асинхронный sessionmaker для SQLAlchemy
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Создаём базовый класс для моделей
Base = declarative_base()

# Если у вас есть отдельный Base для 'lazy load' моделей
BaseReferral = declarative_base()

@asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db  # ✅ Теперь можно использовать `async with get_db()`
        except Exception as e:
            await db.rollback()
            raise

