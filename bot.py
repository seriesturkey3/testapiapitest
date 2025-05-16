import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Replace with your actual bot token
TOKEN = '7340903364:AAET-jHiIsLGmdyz_UAEfFGmpwbzWNqRt7I'

# Data structures to hold game states
games = {}  # key: chat_id, value: game data

# Helper functions

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to Tic Tac Toe!\n"
        "Use /challenge @username to start a game."
    )

def challenge(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /challenge @username")
        return

    challenger = update.message.from_user
    challenged_username = context.args[0]

    # Remove '@' if present
    if challenged_username.startswith('@'):
        challenged_username = challenged_username[1:]

    # Search for the challenged user in chat members
    # Note: Telegram Bot API doesn't allow bots to get user info by username directly
    # So this approach relies on the challenged user being active and having started the bot
    # Alternatively, you can use inline queries or user IDs

    # For simplicity, we'll just send a message to the challenged user asking to accept
    message = (
        f"{challenger.first_name} has challenged you to a game of Tic Tac Toe!\n"
        f"To accept, reply with /accept {challenger.id}"
    )

    # Send challenge message
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )

    # Store the challenge info
    # We'll keep a simple mapping: challenged_user_id -> challenger_id
    # For simplicity, just store in a global dict
    # In production, you'd want a more robust system

    # For this example, we won't enforce username matching, just store challenger info
    # But to keep it simple, we can skip this and handle challenge directly

def accept(update: Update, context: CallbackContext):
    user = update.message.from_user
    args = context.args

    if len(args) != 1:
        update.message.reply_text("Usage: /accept challenger_user_id")
        return

    challenger_id = int(args[0])
    challenger_user = None

    # Note: In real implementation, you'd verify challenger_id corresponds to an actual user
    # For this example, we'll just proceed

    # Generate a chat_id for the game
    chat_id = f"{user.id}_{challenger_id}"

    # Initialize game board
    game_board = [' ' for _ in range(9)]

    # Save game state
    games[chat_id] = {
        'players': {
            'X': user.id,
            'O': challenger_id
        },
        'board': game_board,
        'turn': 'X'  # X starts
    }

    # Send initial game board
    send_board(update, chat_id)

def send_board(update: Update, chat_id):
    game = games.get(chat_id)
    if not game:
        return

    board = game['board']
    turn = game['turn']
    player_x = game['players']['X']
    player_o = game['players']['O']

    # Create inline keyboard
    keyboard = []
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            idx = i + j
            cell = board[idx]
            text = cell if cell != ' ' else str(idx + 1)
            callback_data = str(idx)
            row.append(InlineKeyboardButton(text, callback_data=callback_data))
        keyboard.append(row)

    message_text = (
        f"Tic Tac Toe!\n"
        f"Player X: {player_x} | Player O: {player_o}\n"
        f"Current turn: {'X' if turn=='X' else 'O'}"
    )

    # Send or edit message
    # For simplicity, we'll send a new message each time
    update.effective_chat.send_message(
        text=message_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = query.from_user
    data = query.data  # index of cell clicked

    # Find the game this move belongs to
    # Since multiple games can be ongoing, identify by chat_id or by user IDs
    # For simplicity, assume each game is in a separate chat

    # We'll need to find the game involving this user
    # For this example, we'll iterate over games to find one where user is a player

    chat_id = None
    for gid, game in games.items():
        players = game['players']
        if user.id in players.values():
            chat_id = gid
            break

    if not chat_id:
        query.answer("You're not in a game.")
        return

    game = games[chat_id]
    board = game['board']
    turn = game['turn']
    players = game['players']

    # Check if it's this user's turn
    if (turn == 'X' and users_match(user.id, players['X'])) or \
       (turn == 'O' and users_match(user.id, players['O'])):
        pass
    else:
        query.answer("It's not your turn.")
        return

    index = int(data)

    # Check if cell is empty
    if board[index] != ' ':
        query.answer("Cell already taken.")
        return

    # Make the move
    board[index] = turn

    # Check for win or draw
    if check_winner(board, turn):
        # Announce winner
        message = f"Player {turn} wins!"
        # Highlight the game over
        update.effective_chat.send_message(text=message)
        # Remove game
        del games[chat_id]
        return
    elif ' ' not in board:
        # Draw
        update.effective_chat.send_message(text="It's a draw!")
        del games[chat_id]
        return

    # Switch turn
    game['turn'] = 'O' if turn == 'X' else 'X'

    # Update board
    send_board(update, chat_id)

def users_match(user_id, player_id):
    return user_id == player_id

def check_winner(board, mark):
    # Winning combinations
    wins = [
        [0,1,2], [3,4,5], [6,7,8],  # rows
        [0,3,6], [1,4,7], [2,5,8],  # columns
        [0,4,8], [2,4,6]            # diagonals
    ]
    return any(all(board[i] == mark for i in combo) for combo in wins)

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("challenge", challenge))
    dispatcher.add_handler(CommandHandler("accept", accept))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
