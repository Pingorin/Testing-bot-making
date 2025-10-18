# Dockerfile

FROM python:3.11-slim

# वर्किंग डायरेक्टरी सेट करें
WORKDIR /app

# requirements.txt को कॉपी और इंस्टॉल करें
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# बाकी कोड को कॉपी करें
COPY . .

# बॉट को चलाएं
CMD ["python3", "bot.py"]
