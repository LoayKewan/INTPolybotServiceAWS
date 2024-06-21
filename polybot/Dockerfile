FROM python:3.9-slim

WORKDIR /usr/src/app

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV TELEGRAM_APP_URL=https://loaybot.int-devops.click

CMD ["python3", "app.py"]
