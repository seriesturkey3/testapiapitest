import threading
import asyncio
import aiohttp
from telegram.ext import ApplicationBuilder, CommandHandler
import streamlit as st

# Replace with your actual Telegram bot token
TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'

# Function to fetch the public IP asynchronously
async def get_public_ip():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.ipify.org?format=json') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['ip']
                else:
                    return "Unable to fetch IP."
    except Exception as e:
        return f"Error: {e}"

# Telegram command handler for /ip
async def ip_command(update, context):
    ip = await get_public_ip()
    await update.message.reply_text(f"Your public IP address is: {ip}")

# Function to run the bot in a separate thread
def start_bot():
    async def bot_main():
        # Initialize the application
        app = ApplicationBuilder().token(TOKEN).build()

        # Add command handler
        app.add_handler(CommandHandler('ip', ip_command))

        # Start the bot
        await app.initialize()
        await app.start()
        # Use start_polling() to listen for updates
        await app.updater.start_polling()
        # Keep running indefinitely
        await asyncio.Event().wait()

    # Run the async bot_main in a new event loop
    asyncio.run(bot_main())

# Start the bot in a background thread
threading.Thread(target=start_bot, daemon=True).start()

# Streamlit UI
st.title("Telegram Bot with Public IP Fetcher")
st.write("The bot is running in the background. Send /ip command to get your real public IP address.")

# Optional: Add a refresh button or other UI elements
if st.button("Check Bot Status"):
    st.write("Bot is running in the background...")

# Keep the Streamlit app running
