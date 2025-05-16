import threading
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import os

# --- Configuration ---
TELEGRAM_TOKEN = os.getenv('7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I')  # Set your bot token as environment variable
API_PORT = int(os.getenv('API_PORT', 5000))  # Port for Flask API

# --- Proxy Checking Function ---
def check_proxy(proxy: str) -> dict:
    """
    Checks if the proxy is working.
    Returns a dict with status and message.
    """
    if ':' not in proxy:
        return {'status': 'error', 'message': 'Invalid format. Use ip:port.'}
    ip, port = proxy.split(':', 1)
    proxies = {
        "http": f"http://{ip}:{port}",
        "https": f"http://{ip}:{port}"
    }
    test_url = "http://httpbin.org/ip"
    try:
        response = requests.get(test_url, proxies=proxies, timeout=5)
        if response.status_code == 200:
            origin_ip = response.json().get('origin', 'Unknown')
            return {'status': 'success', 'message': f'Proxy {proxy} is working! Your IP as seen: {origin_ip}'}
        else:
            return {'status': 'fail', 'message': f'Proxy {proxy} returned status code {response.status_code}.'}
    except Exception as e:
        return {'status': 'fail', 'message': f'Proxy {proxy} failed. Error: {str(e)}'}

# --- Flask API for external proxy checks ---
app = Flask(__name__)

@app.route('/api/check_proxy', methods=['POST'])
def api_check_proxy():
    data = request.json
    proxy = data.get('proxy')
    if not proxy:
        return jsonify({'status': 'error', 'message': 'Missing proxy parameter.'}), 400
    result = check_proxy(proxy)
    return jsonify(result)

def run_flask():
    app.run(host='0.0.0.0', port=API_PORT)

# --- Telegram Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I'm Proxy Checker Bot.\n"
        "Use /check <ip:port> to test a proxy."
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a proxy in format ip:port.\nExample: /check 123.45.67.89:8080")
        return
    proxy = context.args[0]
    result = check_proxy(proxy)
    await update.message.reply_text(result['message'])

# --- Main function ---
def main():
    # Start Flask API in a separate thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Initialize Telegram bot
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('check', check))

    # Run bot
    application.run_polling()

if __name__ == '__main__':
    main()
