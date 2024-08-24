# Используем официальный базовый образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все необходимые файлы, а лишнее отфильтруем в dockerignore
COPY . .

# Указываем команду для запуска вашего приложения
CMD ["python", "app.py"]