FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

ENV FLASK_APP=warehouse:create_app()
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"]
