from flask import Flask
from threading import Thread
import asyncio
import os
from bot import app 

# Flask app
server = Flask(__name__)

@server.route('/')
def home():
    return "Bot is alive!"

# Bot ko alag thread mein run karne ka naya function
def run_bot():
    # Naya event loop banayein (Fixes the RuntimeError)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Pyrogram app.run() ko seedhe chalaane ki jagah 
    # hum manually start aur idle ko call karte hain
    loop.run_until_complete(app.start())
    print("Bot Started!") # Yeh message ab log mein dikhega!
    
    # Bot ko hamesha chalu rakhne ke liye idle state mein rakhein
    # Note: app.run() se yeh apne aap hota tha, ab manually karna hoga
    loop.run_until_complete(asyncio.Future()) # Bot ko infinite loop mein rakhega

if __name__ == "__main__":
    # Start the bot in a separate thread
    t = Thread(target=run_bot)
    t.start()
    
    # Start the web server in the main thread
    # Render ke liye port 8080 mandatory hai
    server.run(host="0.0.0.0", port=os.environ.get('PORT', 8080))
    
