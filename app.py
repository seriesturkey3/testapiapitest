import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Replace with your token
TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send /check ip:port to test a proxy.")

async def check_proxy(proxy: str):
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

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /check ip:port")
        return
    proxy = context.args[0]
    result = await check_proxy(proxy)
    await update.message.reply_text(result)

def main():
    # Create the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Build the application
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))

    # Run polling without setting signal handlers
    app.run_polling(close_loop=False)

if __name__ == '__main__':
    main()
