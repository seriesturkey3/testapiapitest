import requests
import asyncio
import random
from telegram import Bot
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters

# Your Telegram bot token
TELEGRAM_TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'
# Files for storing chat IDs and notified deals
CHAT_IDS_FILE = 'chat_ids.txt'
NOTIFIED_DEALS_FILE = 'notified_deals.txt'

bot = Bot(token=TELEGRAM_TOKEN)

# Load chat IDs
def load_chat_ids():
    try:
        with open(CHAT_IDS_FILE, 'r') as f:
            ids = [line.strip() for line in f if line.strip().isdigit()]
        return ids
    except FileNotFoundError:
        return []

# Save chat ID
def save_chat_id(chat_id):
    chat_ids = load_chat_ids()
    if chat_id not in chat_ids:
        with open(CHAT_IDS_FILE, 'a') as f:
            f.write(str(chat_id) + '\n')

# Load notified deals
def load_notified_deals():
    try:
        with open(NOTIFIED_DEALS_FILE, 'r') as f:
            deals = {line.strip() for line in f}
        return deals
    except FileNotFoundError:
        return set()

# Save a deal ID as notified
def save_notified_deal(deal_id):
    with open(NOTIFIED_DEALS_FILE, 'a') as f:
        f.write(str(deal_id) + '\n')

# Telegram message handler for new users
async def handle_message(update, context):
    chat_id = str(update.message.chat_id)
    save_chat_id(chat_id)
    await update.message.reply_text("Thanks! You'll now receive deals.")

# Command handler for /fetchnow
async def fetch_now(update, context):
    await update.message.reply_text("Fetching latest deals now...")
    check_and_notify()
    await update.message.reply_text("Done!")

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

# Check for new deals and notify
def check_and_notify():
    chat_ids = load_chat_ids()
    if not chat_ids:
        print("No users registered.")
        return

    deals = get_discounted_games()
    if not deals:
        print("No deals found.")
        return

    notified_deals = load_notified_deals()

    # Find new deals which have not been notified before
    new_deals = [deal for deal in deals if deal['dealID'] not in notified_deals]

    if not new_deals:
        print("No new deals to notify.")
        return

    # Send each new deal to all chat IDs
    for deal in new_deals:
        deal_id = deal['dealID']
        save_notified_deal(deal_id)

        message = (
            f"🔥 **Steam Deal!** 🔥\n"
            f"Title: {deal['title']}\n"
            f"Price: ${deal['salePrice']}\n"
            f"Discount: {deal['savings']}%\n"
            f"Link: https://store.steampowered.com/app/{deal['steamAppID']}"
        )

        for chat_id in chat_ids:
            try:
                bot.send_message(int(chat_id), message, parse_mode='Markdown')
            except Exception as e:
                print(f"Failed to send to {chat_id}: {e}")

# Periodic task: check deals every 30 minutes
async def periodic_check():
    while True:
        print("Checking for new deals...")
        check_and_notify()
        await asyncio.sleep(1800)  # wait for 30 minutes

# Main function to run the bot and schedule periodic checks
def main():
    async def run():
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        # Initialize the app
        await app.initialize()

        # Register handlers
        app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )
        app.add_handler(
            CommandHandler('fetchnow', fetch_now)
        )

        # Start the bot
        await app.start()

        # Run periodic check in background
        asyncio.create_task(periodic_check())

        # Keep the bot running
        await app.updater.start_polling()
        await app.updater.idle()

    asyncio.run(run())

if __name__ == '__main__':
    main()
