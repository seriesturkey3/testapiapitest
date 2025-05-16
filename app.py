import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your bot token
TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'  # <-- Put your bot token here

# Store game states
games = {}

def create_board():
    return [[' ' for _ in range(3)] for _ in range(3)]

def board_to_markup(board):
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            cell_text = board[i][j] if board[i][j] != ' ' else ' '
            row.append(InlineKeyboardButton(cell_text, callback_data=f'{i},{j}'))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def check_winner(board):
    lines = []

    # Rows and columns
    for i in range(3):
        lines.append(board[i])  # rows
        lines.append([board[0][i], board[1][i], board[2][i]])  # columns

    # Diagonals
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

async def handle_button(update, context):
    query = update.callback_query
    chat_id = query.message.chat.id

    if chat_id not in games:
        await query.answer("Game not found. Start a new game with /start.")
        return

    game = games[chat_id]
    board = game['board']

    i, j = map(int, query.data.split(','))
    if board[i][j] != ' ':
        await query.answer("Cell already taken!")
        return

    # Player move
    board[i][j] = 'X'

    # Check for player win
    winner = check_winner(board)
    if winner:
        await query.edit_message_text("🎉 You win!", reply_markup=None)
        del games[chat_id]
        return

    # Check for draw
    if is_draw(board):
        await query.edit_message_text("It's a draw!", reply_markup=None)
        del games[chat_id]
        return

    # Bot's turn
    empty_cells = [(x, y) for x in range(3) for y in range(3) if board[x][y] == ' ']
    if empty_cells:
        x, y = random.choice(empty_cells)
        board[x][y] = 'O'

        # Check if bot wins
        winner = check_winner(board)
        if winner:
            await query.edit_message_text("🤖 Bot wins!", reply_markup=None)
            del games[chat_id]
            return

        # Check for draw
        if is_draw(board):
            await query.edit_message_text("It's a draw!", reply_markup=None)
            del games[chat_id]
            return

    # Continue game
    await query.edit_message_text("Your turn!", reply_markup=board_to_markup(board))
    await query.answer()

async def help_command(update: Update, context):
    await update.message.reply_text(
        "/start - start a new game\n"
        "Use the buttons to make your moves."
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.run_polling()

if __name__ == '__main__':
    main()
