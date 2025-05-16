import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace this with your actual Telegram bot token
TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'

# Store game states
games = {}
scores = {}

# Helper functions
def create_board():
    return [' ' for _ in range(9)]

def check_winner(board):
    win_conditions = [
        [0,1,2], [3,4,5], [6,7,8],  # rows
        [0,3,6], [1,4,7], [2,5,8],  # columns
        [0,4,8], [2,4,6]            # diagonals
    ]
    for condition in win_conditions:
        a,b,c = condition
        if board[a] == board[b] == board[c] != ' ':
            return board[a]
    if ' ' not in board:
        return 'Draw'
    return None

def get_player_symbol(user_id, game):
    if user_id == game['player_x']:
        return 'X'
    elif user_id == game['player_o']:
        return 'O'
    return None

def switch_turn(game):
    game['current_turn'] = game['player_o'] if game['current_turn'] == game['player_x'] else game['player_x']

def create_board_keyboard(board):
    keyboard = []
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            idx = i + j
            text = board[idx] if board[idx] != ' ' else ' '
            callback_data = str(idx)
            row.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

# Command handlers
async def start(update: Update, context: 'ContextTypes.DEFAULT_TYPE'):
    user_id = update.effective_user.id
    scores.setdefault(user_id, {'X':0, 'O':0})
    await update.message.reply_text(
        "Welcome to Tic Tac Toe!\nUse /newgame to start a new game.\nUse /score to see your scores."
    )

async def score(update: Update, context: 'ContextTypes.DEFAULT_TYPE'):
    user_id = update.effective_user.id
    user_score = scores.get(user_id, {'X':0, 'O':0})
    await update.message.reply_text(
        f"Your Scores:\nX: {user_score['X']}\nO: {user_score['O']}"
    )

async def newgame(update: Update, context: 'ContextTypes.DEFAULT_TYPE'):
    user_id = update.effective_user.id

    # Find a game waiting for a second player
    waiting_game = None
    for g in games.values():
        if g['status'] == 'waiting':
            waiting_game = g
            break

    if waiting_game:
        # Assign second player
        game_id = waiting_game['id']
        waiting_game['player_o'] = user_id
        waiting_game['status'] = 'playing'
        waiting_game['board'] = create_board()
        waiting_game['current_turn'] = waiting_game['player_x']
        # Notify players
        try:
            await context.bot.send_message(
                waiting_game['player_x'],
                "Second player joined! The game begins.\nYou are 'X'. Your turn."
            )
        except:
            pass
        try:
            await context.bot.send_message(
                user_id,
                "You joined the game as 'O'. The game begins.\nWaiting for 'X' to move."
            )
        except:
            pass
        # Send initial board
        await send_board(update, context, waiting_game)
    else:
        # Create a new game waiting for a second player
        game_id = len(games) + 1
        games[game_id] = {
            'id': game_id,
            'player_x': user_id,
            'player_o': None,
            'board': create_board(),
            'current_turn': user_id,
            'status': 'waiting'
        }
        await update.message.reply_text("Waiting for an opponent to join. Send /newgame again to find a game.")

async def send_board(update, context, game):
    keyboard = create_board_keyboard(game['board'])
    current_player_id = game['current_turn']
    # Send board message
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Current turn: {'X' if get_player_symbol(current_player_id, game)=='X' else 'O'}",
        reply_markup=keyboard
    )

async def button(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    game = None

    # Find the game involving this user and is active
    for g in games.values():
        if g['status'] == 'playing' and (g['player_x'] == user_id or g['player_o'] == user_id):
            game = g
            break

    if not game:
        await query.answer("You're not in an active game.")
        return

    # Check if it's this player's turn
    if game['current_turn'] != user_id:
        await query.answer("It's not your turn.")
        return

    idx = int(data)
    if game['board'][idx] != ' ':
        await query.answer("Cell already taken.")
        return

    symbol = get_player_symbol(user_id, game)
    game['board'][idx] = symbol

    # Check for winner
    winner = check_winner(game['board'])
    if winner:
        if winner == 'Draw':
            msg = "It's a draw!"
        else:
            msg = f"Player '{winner}' wins!"
            # Update scores
            for uid in [game['player_x'], game['player_o']]:
                scores.setdefault(uid, {'X':0,'O':0})
                if winner == 'X':
                    scores[uid]['X'] += 1
                elif winner == 'O':
                    scores[uid]['O'] += 1

        # Send result to both players
        for uid in [game['player_x'], game['player_o']]:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=msg + "\nUse /newgame to play again or /score to see your scores."
                )
            except:
                pass
        game['status'] = 'ended'
        return
    else:
        # Switch turn
        switch_turn(game)
        # Update both players
        for uid in [game['player_x'], game['player_o']]:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text="Your turn." if game['current_turn'] == uid else "Waiting for opponent...",
                    reply_markup=create_board_keyboard(game['board'])
                )
            except:
                pass

    await query.answer()

# Main async function to run the bot
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('score', score))
    application.add_handler(CommandHandler('newgame', newgame))
    application.add_handler(CallbackQueryHandler(button))
    print("Bot is running...")
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
