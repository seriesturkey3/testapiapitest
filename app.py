import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Your Steam Storefront API key
STEAM_API_KEY = 'YOUR_STEAM_API_KEY'

# Your Telegram Bot Token
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Function to fetch discounted games
def get_discounted_games():
    url = (
        "https://store.steampowered.com/api/featured/?cc=us&l=english&v=1"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        deals = []

        if 'specials' in data:
            specials = data['specials']
            for game in specials:
                deals.append(game)
        return deals
    except Exception as e:
        print(f"Error fetching deals: {e}")
        return []

# Function to check if "The Forest" is on discount
def check_the_forest_deal():
    deals = get_discounted_games()
    for deal in deals:
        # Deal structure may vary; adapt as needed
        title = deal.get('title', '')
        sale_price = deal.get('salePrice', '')
        normal_price = deal.get('normalPrice', '')
        steam_app_id = deal.get('steamAppID', '')

        if 'The Forest' in title:
            try:
                sale_price_float = float(sale_price)
            except:
                sale_price_float = 0.0
            try:
                normal_price_float = float(normal_price)
            except:
                normal_price_float = 0.0

            if sale_price_float < normal_price_float:
                return True, {
                    'title': title,
                    'salePrice': sale_price,
                    'steamAppID': steam_app_id
                }
            else:
                return False, {
                    'title': title,
                    'salePrice': sale_price,
                    'steamAppID': steam_app_id
                }
    return False, None

# Handler for /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Use /discount to see current deals and /name to check The Forest deal.")

# Handler for /discount command
async def discount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deals = get_discounted_games()
    if not deals:
        await update.message.reply_text("No deals found at the moment.")
        return
    message = "Current Deals:\n\n"
    for deal in deals:
        title = deal.get('title', 'No title')
        sale_price = deal.get('salePrice', 'N/A')
        normal_price = deal.get('normalPrice', 'N/A')
        link = f"https://store.steampowered.com/app/{deal.get('steamAppID', '')}"
        message += f"🎮 {title}\nPrice: ${sale_price} (was ${normal_price})\nLink: {link}\n\n"
    await update.message.reply_text(message)

# Handler for /name command
async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    discounted, deal = check_the_forest_deal()
    if deal:
        title = deal.get('title', 'The Forest')
        sale_price = deal.get('salePrice', 'N/A')
        steam_app_id = deal.get('steamAppID', '')
        if discounted:
            message = (
                f"🎉 The Forest is currently on discount!\n"
                f"Title: {title}\n"
                f"Price: ${sale_price}\n"
                f"Link: https://store.steampowered.com/app/{steam_app_id}"
            )
        else:
            message = (
                f"The Forest is currently not on discount.\n"
                f"Title: {title}\n"
                f"Price: ${sale_price}\n"
                f"Link: https://store.steampowered.com/app/{steam_app_id}"
            )
    else:
        message = "The Forest is not currently available in the deals."
    await update.message.reply_text(message)

# Main function to run the bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('discount', discount))
    app.add_handler(CommandHandler('name', handle_name))

    # Run the bot
    app.run_polling()

if __name__ == '__main__':
    main()
