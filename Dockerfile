# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем все файлы в контейнер
COPY . /app

# Установить supervisor
RUN apt-get update && apt-get install -y supervisor

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем конфигурацию для супервизора
COPY supervisord.conf /etc/supervisord.conf

# Открываем порты, которые использует приложение
EXPOSE 5000
EXPOSE 8443

# Запускаем supervisord, который будет управлять процессами
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
