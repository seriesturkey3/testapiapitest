import requests
import random
from telegram import Bot

# Your Telegram bot token and chat ID
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'

bot = Bot(token=TELEGRAM_TOKEN)

def get_discounted_games():
    # Fetch deals with at least 50% off, for example
    response = requests.get('https://www.cheapshark.com/api/1.0/deals', params={
        'storeID': 1,          # Steam store
        'upperPrice': 60,      # Max price
        'sortBy': 'DealRating',
        'desc': 1,
        'pageSize': 50
    })
    deals = response.json()
    # Filter deals with significant discounts
    discounted_games = [deal for deal in deals if float(deal['savings']) >= 50]
    return discounted_games

def send_random_discount_game():
    discounted_games = get_discounted_games()
    if not discounted_games:
        print("No discounted games found.")
        return

    game = random.choice(discounted_games)
    message = (
        f"🔥 **Steam Discount!** 🔥\n"
        f"Title: {game['title']}\n"
        f"Price: ${game['salePrice']}\n"
        f"Discount: {game['savings']}%\n"
        f"Link: https://store.steampowered.com/app/{game['steamAppID']}"
    )
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

if __name__ == '__main__':
    send_random_discount_game()
