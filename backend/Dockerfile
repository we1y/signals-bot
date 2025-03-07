# В Dockerfile указываем правильный путь к файлу requirements.txt
FROM python:3.11

WORKDIR /app

# Убедись, что файл requirements.txt находится в той же директории, где находится Dockerfile
COPY backend/requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
