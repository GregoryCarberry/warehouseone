# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y     build-essential libpq-dev curl     && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app

# Writable session dir
RUN mkdir -p /tmp/flask_session

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app /tmp/flask_session
USER appuser

ENV FLASK_APP=app:create_app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

EXPOSE 5000

# Self-heal migrations; then migrate/upgrade; then run
CMD bash -lc '  if [ -d migrations ] && [ ! -f migrations/env.py ]; then rm -rf migrations; fi &&   if [ ! -d migrations ]; then flask db init; fi &&   flask db migrate -m "init" || true &&   flask db upgrade &&   python run.py'
