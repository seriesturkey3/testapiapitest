import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Замените на ваш токен
TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'

# Храним игры по chat_id
games = {}

def create_board():
    return [[' ' for _ in range(3)] for _ in range(3)]

def board_to_markup(board):
    markup = []
    for i in range(3):
        row = []
        for j in range(3):
            cell = board[i][j]
            text = cell if cell != ' ' else ' '
            row.append(InlineKeyboardButton(text, callback_data=f'{i},{j}'))
        markup.append(row)
    return InlineKeyboardMarkup(markup)

def check_winner(board):
    lines = []

    # Проверка строк и столбцов
    for i in range(3):
        lines.append(board[i])  # строка
        lines.append([board[0][i], board[1][i], board[2][i]])  # столбец

    # Диагонали
    lines.append([board[0][0], board[1][1], board[2][2]])
    lines.append([board[0][2], board[1][1], board[2][0]])

    for line in lines:
        if line[0] != ' ' and line.count(line[0]) == 3:
            return line[0]
    return None

def is_draw(board):
    return all(cell != ' ' for row in board for cell in row)

async def start(update: Update, context):
    chat_id = update.effective_chat.id
    games[chat_id] = {'board': create_board()}
    await update.message.reply_text(
        "Let's play Tic-Tac-Toe!\nYou are 'X'. Make your move.",
        reply_markup=board_to_markup(games[chat_id]['board'])
    )

async def button(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    if chat_id not in games:
        await query.answer("Start a game with /start")
        return

    game = games[chat_id]
    board = game['board']

    i, j = map(int, query.data.split(','))
    if board[i][j] != ' ':
        await query.answer("Cell already taken!")
        return

    # Ход пользователя
    board[i][j] = 'X'

    # Проверка победы
    winner = check_winner(board)
    if winner:
        await query.edit_message_text(f"🎉 You win!", reply_markup=None)
        del games[chat_id]
        return

    # Проверка ничьей
    if is_draw(board):
        await query.edit_message_text("It's a draw!", reply_markup=None)
        del games[chat_id]
        return

    # Ход бота
    empty_cells = [(x, y) for x in range(3) for y in range(3) if board[x][y] == ' ']
    if empty_cells:
        x, y = random.choice(empty_cells)
        board[x][y] = 'O'
        # Проверка победы бота
        winner = check_winner(board)
        if winner:
            await query.edit_message_text(f"🤖 Bot wins!", reply_markup=None)
            del games[chat_id]
            return
        # Проверка ничьей
        if is_draw(board):
            await query.edit_message_text("It's a draw!", reply_markup=None)
            del games[chat_id]
            return

    # Продолжение
    await query.edit_message_text("Your turn!", reply_markup=board_to_markup(board))
    await query.answer()

async def help_command(update, context):
    await update.message.reply_text(
        "/start - Начать новую игру\n"
        "Используйте кнопки, чтобы сделать ход."
    )

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
