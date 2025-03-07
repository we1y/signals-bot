import os

# Определяем структуру проекта
project_structure = {
    "backend": {
        "app": {
            "routers": {"users.py": "", "items.py": ""},
            "services": {},
            "main.py": """from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
""",
            "models.py": "",
            "database.py": "",
        },
        "requirements.txt": "fastapi\nuvicorn\nsqlalchemy\nasyncpg",
        "Dockerfile": """FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
""",
    },
    "frontend": {
        "src": {"App.vue": "<template>\n  <h1>Hello, Frontend</h1>\n</template>"},
        "Dockerfile": """FROM node:18

WORKDIR /app
COPY . .
RUN npm install
CMD ["npm", "run", "dev"]
""",
    },
    "docker-compose.yml": """version: '3.8'

services:
  db:
    image: postgres:15
    container_name: postgres_db
    restart: always
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    container_name: fastapi_backend
    restart: always
    depends_on:
      - db
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@db/mydb

  frontend:
    build: ./frontend
    container_name: frontend
    restart: always
    ports:
      - "3000:3000"

volumes:
  db_data:
""",
    ".gitignore": "venv/\n__pycache__/\nnodemodules/\ndb_data/",
}

# Функция создания файлов и папок
def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):  # Если это папка
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:  # Если это файл
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

# Запуск создания проекта
project_path = os.path.abspath("C:\\Новая папка")
create_structure(project_path, project_structure)

print(f"✅ Проект создан в {project_path}")
