FROM python:3.13-slim


RUN apt-get update && apt-get install -y \
    supervisor \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgthread-2.0-0 \
    curl gnupg \
    && rm -rf /var/lib/apt/lists/*

# Установка Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Установка Python зависимостей
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копирование проекта
COPY . .

# Конфигурация supervisord
RUN echo '[supervisord]\n\
nodaemon=true\n\
\n\
[program:django]\n\
directory=/check_screen_backend\n\
command=python manage.py runserver 0.0.0.0:8000\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
\n\
[program:nextjs]\n\
directory=/screen-check\n\
command=npm start\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
' > /etc/supervisor/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]