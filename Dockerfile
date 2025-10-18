# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Gunicorn वेब सर्वर को चलाएगा, जो bot.py में Flask ऐप को शुरू करेगा
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "bot:web_app"]
