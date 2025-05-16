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

# Replace with your bot's token
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'

# Store game states: { chat_id: game_data }
games = {}

def create_board():
    """Create an empty 3x3 game board."""
    return [[' ' for _ in range(3)] for _ in range(3)]

def board_to_markup(board):
    """Convert the game board into inline keyboard markup."""
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            cell = board[i][j]
            text = cell if cell != ' ' else ' '
            callback_data = f'{i},{j}'
            row.append(InlineKeyboardButton(text, callback_data=callback_data))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def check_winner(board):
    """Check if there is a winner. Return 'X', 'O' or None."""
    lines = []

    # Rows and columns
    for i in range(3):
        lines.append(board[i])  # row
        lines.append([board[0][i], board[1][i], board[2][i]])  # column

    # Diagonals
    lines.append([board[0][0], board[1][1], board[2][2]])
    lines.append([board[0][2], board[1][1], board[2][0]])

    for line in lines:
        if line[0] != ' ' and line.count(line[0]) == 3:
            return line[0]
    return None

def is_draw(board):
    """Determine if the game is a draw."""
    for row in board:
        if ' ' in row:
            return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a new game."""
    chat_id = update.effective_chat.id
    games[chat_id] = {
        'board': create_board(),
        'current_player': 'X'  # User is X
    }
    await update.message.reply_text(
        "Let's play Tic-Tac-Toe!\nYou are 'X'. Make your move.",
        reply_markup=board_to_markup(games[chat_id]['board'])
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses for moves."""
    query = update.callback_query
    chat_id = query.message.chat_id

    if chat_id not in games:
        await query.answer("Start a game with /start")
        return

    game = games[chat_id]
    board = game['board']

    # Parse move
    i, j = map(int, query.data.split(','))
    # Check if cell is empty
    if board[i][j] != ' ':
        await query.answer("Cell already taken!")
        return

    # Player move
    board[i][j] = 'X'

    # Check if player wins
    winner = check_winner(board)
    if winner:
        await query.edit_message_text(f"🎉 You win!", reply_markup=None)
        del games[chat_id]
        return

    # Check for draw
    if is_draw(board):
        await query.edit_message_text("It's a draw!", reply_markup=None)
        del games[chat_id]
        return

    # Bot's move ('O') - simple random move
    empty_cells = [(x, y) for x in range(3) for y in range(3) if board[x][y] == ' ']
    if empty_cells:
        x, y = random.choice(empty_cells)
        board[x][y] = 'O'
        # Check if bot wins
        winner = check_winner(board)
        if winner:
            await query.edit_message_text(f"🤖 Bot wins!", reply_markup=None)
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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    await update.message.reply_text(
        "/start - Start a new Tic-Tac-Toe game\n"
        "Make your move by pressing the buttons."
    )

def main():
    """Run the bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
