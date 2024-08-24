# Используем официальный базовый образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Создаем виртуальное окружение и активируем его
RUN python -m venv /venv

# Устанавливаем pip и устанавливаем зависимости внутри виртуального окружения
RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Указываем команду для запуска вашего приложения
CMD ["/venv/bin/python", "app.py"]