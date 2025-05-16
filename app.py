import requests
from telegram.ext import Updater, CommandHandler

# Replace 'YOUR_BOT_TOKEN' with your Telegram bot token
TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'

# Function to get public IP
def get_public_ip():
    response = requests.get('https://api.ipify.org?format=json')
    if response.status_code == 200:
        ip = response.json()['ip']
        return ip
    else:
        return 'Unable to fetch IP.'

# Command handler for /ip
def ip_command(update, context):
    ip = get_public_ip()
    update.message.reply_text(f'Your public IP address is: {ip}')

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add handler for /ip command
    dp.add_handler(CommandHandler('ip', ip_command))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
