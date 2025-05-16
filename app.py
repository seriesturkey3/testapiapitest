import threading
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'

def run_bot():
    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Build and run the bot
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('ip', ip_command))
    app.run_polling()

async def ip_command(update, context):
    import requests
    try:
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            ip = response.json()['ip']
        else:
            ip = "Unable to fetch IP."
    except Exception as e:
        ip = f"Error: {e}"
    await update.message.reply_text(f"Your public IP address is: {ip}")

# Example usage with threading
if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    # Your Streamlit or other code here
