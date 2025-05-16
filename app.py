import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            return response.json()['ip']
        else:
            return "Unable to fetch IP."
    except Exception as e:
        return f"Error: {e}"

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ip = get_public_ip()
    await update.message.reply_text(f"Your public IP address is: {ip}")

async def main():
    # Initialize the bot application
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('ip', ip_command))
    
    # Run polling asynchronously
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
