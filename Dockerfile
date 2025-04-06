FROM python:3.13-rc-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Установка зависимостей и копирование проекта
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем исходники проекта (кроме того, что указано в .dockerignore)
COPY . .

# Запуск бота
CMD ["python", "main.py"]
