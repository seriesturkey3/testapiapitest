import threading
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests

TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'

def check_proxy(proxy):
    if ':' not in proxy:
        return "Invalid format. Use ip:port."
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
            return f"Proxy {proxy} is working! Your IP as seen: {origin_ip}"
        else:
            return f"Proxy {proxy} returned status code {response.status_code}."
    except Exception as e:
        return f"Proxy {proxy} is not working. Error: {e}"

def check_command(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /check ip:port")
        return
    proxy = context.args[0]
    result = check_proxy(proxy)
    update.message.reply_text(result)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("check", check_command))

    # Run bot in a separate thread so it doesn't block other code
    threading.Thread(target=updater.start_polling).start()

if __name__ == '__main__':
    main()
    # You can run your Streamlit app or other code here
