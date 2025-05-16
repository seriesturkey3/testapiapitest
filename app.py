import requests
from telegram.ext import ApplicationBuilder, CommandHandler

# Your Telegram Bot Token
TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'

def get_public_ip():
    """Fetch the current public IP address."""
    try:
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            return response.json()['ip']
        else:
            return "Unable to fetch IP."
    except Exception as e:
        return f"Error: {e}"

async def ip_command(update, context):
    """Handler for /ip command."""
    ip = get_public_ip()
    await update.message.reply_text(f"Your public IP address is: {ip}")

def main():
    """Start the bot."""
    # Initialize the application
    app = ApplicationBuilder().token(TOKEN).build()
    # Add command handler for /ip
    app.add_handler(CommandHandler('ip', ip_command))
    # Run the bot - this is blocking and handles signals properly
    app.run_polling()

if __name__ == '__main__':
    main()
