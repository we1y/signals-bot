from fastapi import FastAPI, HTTPException
import asyncio
import nest_asyncio
from app.database import get_db  # Импортируем функцию для получения сессии
from app.services.signals import process_signals, create_static_signals  # Импортируем функции для обработки сигналов и создания статичных сигналов
from app.routers import users, balances, signals_routes, general_routes  # Подключаем новые роутеры
from app.telegram_bot import main as start_telegram_bot
from fastapi.middleware.cors import CORSMiddleware
import logging

# Применяем nest_asyncio для разрешения работы с текущим event loop
nest_asyncio.apply()

app = FastAPI()

# Разрешённые источники (укажи свои домены)
origins = [
    "http://localhost",
    "http://localhost:3001",  # Например, для React/Vue/Angular фронта
    "http://194.87.92.198:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешённые источники
    allow_credentials=True,  # Разрешить передачу cookies
    allow_methods=["*"],  # Разрешённые методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешённые заголовки
)

# Подключаем маршруты
app.include_router(users.router)
app.include_router(balances.router)
app.include_router(signals_routes.signalis_router)
app.include_router(general_routes.router)

@app.on_event("startup")
async def startup_event():
    """Запуск Telegram бота, создание статичных сигналов и фоновая задача для обработки сигналов."""
    try:
        # Создаем статичные сигналы
        async with get_db() as db:
            await create_static_signals(db)

        # Запускаем Telegram бота
        asyncio.create_task(start_telegram_bot())
        
        # Запускаем фоновую задачу для обработки сигналов каждые 60 секунд
        asyncio.create_task(process_signals_task())
        
    except Exception as e:
        logging.error(f"Ошибка при запуске фоновых задач: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при запуске фоновых задач")

async def process_signals_task():
    """Обработка сигналов каждые 60 секунд."""
    while True:
        try:
            async with get_db() as db:
                await process_signals(db)
            await asyncio.sleep(60)  # Подождать 1 минуту перед следующим запуском
        except Exception as e:
            logging.error(f"Ошибка при обработке сигналов: {e}")
            await asyncio.sleep(60)  # Даже если ошибка, ждем 60 секунд

@app.get("/")
def read_root():
    """Проверка работы сервера"""
    return {"message": "FastAPI is running!"}
