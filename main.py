from flask import Flask
from threading import Thread
from bot import app # bot.py se app ko import karein

# Flask app
server = Flask(__name__)

@server.route('/')
def home():
    return "Bot is alive!"

# Bot ko alag thread mein run karein
def run_bot():
    app.run()

if __name__ == "__main__":
    # Start the bot
    t = Thread(target=run_bot)
    t.start()
    
    # Start the web server
    server.run(host="0.0.0.0", port=8080)
  
