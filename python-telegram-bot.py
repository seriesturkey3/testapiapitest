from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler

TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'

async def start(update, context):
    web_app_url = "https://testapiapitest-5qycf3ejx5nnb97rfwhshn.streamlit.app/"  # Replace with your URL

    button = InlineKeyboardButton(
        text="Play Tic Tac Toe",
        web_app={"url": web_app_url}
    )
    reply_markup = InlineKeyboardMarkup([[button]])
    await update.message.reply_text("Click below to start the game!", reply_markup=reply_markup)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == '__main__':
    main()
