
from flask import Flask
import threading
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "running"}, 200

def run_server():
    logger.info("Starting web server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def start_webserver():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    logger.info("Web server thread started")
