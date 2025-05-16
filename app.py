import threading
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
import streamlit as st

TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'

async def ip_command(update, context):
    try:
        # your async code to fetch IP
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.ipify.org?format=json') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    ip = data['ip']
                else:
                    ip = "Unable to fetch IP."
    except Exception as e:
        ip = f"Error: {e}"
    await update.message.reply_text(f"Your public IP address is: {ip}")

def start_bot():
    async def bot_main():
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('ip', ip_command))
        # Instead of run_polling(), start polling in a background task
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        await asyncio.Event().wait()  # Keep running

    asyncio.run(bot_main())

# Run bot in background thread
threading.Thread(target=start_bot, daemon=True).start()

# Your Streamlit app UI
st.title("Telegram Bot in Streamlit")
st.write("Bot is running in the background.")
