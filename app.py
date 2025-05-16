import requests
import random
from telegram import Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# Your Telegram bot token
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
# File to store chat IDs
CHAT_IDS_FILE = 'chat_ids.txt'

# Initialize bot instance
bot = Bot(token=TELEGRAM_TOKEN)

# Load chat IDs from file
def load_chat_ids():
    try:
        with open(CHAT_IDS_FILE, 'r') as f:
            ids = [line.strip() for line in f if line.strip().isdigit()]
        return ids
    except FileNotFoundError:
        return []

# Save a new chat ID
def save_chat_id(chat_id):
    chat_ids = load_chat_ids()
    if chat_id not in chat_ids:
        with open(CHAT_IDS_FILE, 'a') as f:
            f.write(str(chat_id) + '\n')

# Handler for incoming messages to register users
async def handle_message(update, context):
    chat_id = str(update.message.chat_id)
    save_chat_id(chat_id)
    await update.message.reply_text("Thanks! You'll now receive deals.")

# Fetch deals from API
def get_discounted_games():
    url = 'https://www.cheapshark.com/api/1.0/deals'
    params = {
        'storeID': 1,
        'upperPrice': 60,
        'sortBy': 'DealRating',
        'desc': 1,
        'pageSize': 50
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error fetching deals: {response.status_code}")
            return []
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return []

# Broadcast deals to all registered users
def broadcast_deal():
    chat_ids = load_chat_ids()
    if not chat_ids:
        print("No users registered.")
        return
    deals = get_discounted_games()
    if not deals:
        print("No deals found.")
        return
    # Filter for deals with savings >= 50%
    discounted_games = [deal for deal in deals if float(deal['savings']) >= 50]
    if not discounted_games:
        print("No discounted games with ≥50% off.")
        return
    game = random.choice(discounted_games)
    message = (
        f"🔥 **Steam Discount!** 🔥\n"
        f"Title: {game['title']}\n"
        f"Price: ${game['salePrice']}\n"
        f"Discount: {game['savings']}%\n"
        f"Link: https://store.steampowered.com/app/{game['steamAppID']}"
    )
    for chat_id in chat_ids:
        try:
            bot.send_message(int(chat_id), message, parse_mode='Markdown')
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")

# Main function to run the bot
def main():
    # Build the application
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Register message handler
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Run the bot
    app.run_polling()

if __name__ == '__main__':
    main()
