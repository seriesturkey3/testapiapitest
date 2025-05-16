import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
import aiohttp

TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'

async def ip_command(update, context):
    try:
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

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('ip', ip_command))
    print("Bot is polling...")
    app.run_polling()

if __name__ == '__main__':
    main()
