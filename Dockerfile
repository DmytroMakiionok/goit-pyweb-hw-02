# Використовуємо офіційний образ Python для бази
FROM python:3.10

# Встановлюємо необхідні пакети
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо файли додатку в контейнер
COPY . /app
WORKDIR /app

# Встановлюємо залежності Python
RUN pip install -r requirements.txt

# Вказуємо команду для запуску програми при старті контейнера
CMD ["python", "assistant.py"]
