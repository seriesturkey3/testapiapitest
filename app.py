import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Replace with your bot token
TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'

# Function to get current public IP
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            return response.json()['ip']
        else:
            return "Unable to fetch IP."
    except Exception as e:
        return f"Error: {e}"

# Async command handler for /ip
async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ip = get_public_ip()
    await update.message.reply_text(f"Your public IP address is: {ip}")

def main():
    # Create and set event loop (fix for Python 3.11+)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(TOKEN).build()

    # Register the command handler
    app.add_handler(CommandHandler('ip', ip_command))

    # Run the bot
    app.run_polling()

if __name__ == '__main__':
    main()
