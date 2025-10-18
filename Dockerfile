# File: Dockerfile

# बेस इमेज के रूप में Python 3.10.8 का स्लिम वर्जन चुनें
FROM python:3.10.8-slim

# वर्किंग डायरेक्टरी सेट करें
WORKDIR /app

# requirements.txt को कॉपी करें
COPY requirements.txt .

# लाइब्रेरीज इनस्टॉल करें
RUN pip install --no-cache-dir -r requirements.txt

# बाकी सभी फाइल्स को कॉपी करें
COPY . .

# बॉट को चलाने के लिए कमांड
CMD ["python3", "bot.py"]
