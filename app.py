import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Store active games: key = game_id, value = game data
games = {}
# For simplicity, game_id can be a string combining user IDs
# Example: "user1id_user2id"

def create_board():
    return [' ' for _ in range(9)]  # 3x3 board flattened

def get_board_markup(board):
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            index = i * 3 + j
            cell = board[index]
            text = cell if cell != ' ' else ' '
            callback_data = f"move_{index}"
            row.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def check_winner(board):
    # Winning combinations
    wins = [
        (0,1,2), (3,4,5), (6,7,8),  # rows
        (0,3,6), (1,4,7), (2,5,8),  # columns
        (0,4,8), (2,4,6)            # diagonals
    ]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] != ' ':
            return board[a]
    if ' ' not in board:
        return 'Draw'
    return None

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Welcome to Tic Tac Toe! Challenge a friend with /challenge @username")

@dp.message_handler(commands=['challenge'])
async def challenge_command(message: types.Message):
    if not message.get_args():
        await message.answer("Usage: /challenge @username")
        return
    username = message.get_args().strip()
    # Find user by username (Note: requires user to have interacted with bot before)
    # For simplicity, assume the challenger and challenged are available
    # In real implementation, you'd handle user identification properly
    # Here, just store the challenge info
    challenged_user = username.replace('@', '')
    challenger_id = message.from_user.id
    challenged_id = None  # Placeholder: you'd need to resolve username to user_id
    # For demo purposes, we'll assume challenged_user is known or skip user lookup
    # Instead, we can let the challenged user initiate game via command
    await message.answer(f"Challenge sent to {username}! Now, {username} can accept with /accept {challenger_id}")

@dp.message_handler(commands=['accept'])
async def accept_command(message: types.Message):
    challenger_id = int(message.get_args())
    challenged_id = message.from_user.id
    game_id = f"{challenger_id}_{challenged_id}"

    # Initialize game
    board = create_board()
    games[game_id] = {
        'player_x': challenger_id,
        'player_o': challenged_id,
        'board': board,
        'turn': 'X'  # X starts
    }

    # Send initial game board
    await bot.send_message(challenger_id, "Game started! You are X. Your move.", reply_markup=get_board_markup(board))
    await bot.send_message(challenged_id, "Game started! You are O. Wait for your turn.", reply_markup=get_board_markup(board))

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('move_'))
async def handle_move(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    move_index = int(callback_query.data.split('_')[1])

    # Find the game this user is in
    game_id = None
    for gid, game in games.items():
        if user_id in [game['player_x'], game['player_o']]:
            game_id = gid
            break
    if not game_id:
        await callback_query.answer("You're not in a game.")
        return

    game = games[game_id]
    current_player = game['player_x'] if game['turn'] == 'X' else game['player_o']

    if user_id != current_player:
        await callback_query.answer("It's not your turn.")
        return

    if game['board'][move_index] != ' ':
        await callback_query.answer("Cell already taken.")
        return

    # Make move
    game['board'][move_index] = game['turn']
    winner = check_winner(game['board'])
    if winner:
        # End game
        if winner == 'Draw':
            msg = "It's a draw!"
        else:
            winner_id = game['player_x'] if winner == 'X' else game['player_o']
            msg = f"Player {winner} wins!"
        # Notify players
        await bot.send_message(game['player_x'], msg)
        await bot.send_message(game['player_o'], msg)
        # Remove game
        del games[game_id]
    else:
        # Switch turn
        game['turn'] = 'O' if game['turn'] == 'X' else 'X'
        # Update board for both players
        for player_id in [game['player_x'], game['player_o']]:
            await bot.send_message(player_id, "Your turn." if player_id == current_player else "Waiting for opponent.", reply_markup=get_board_markup(game['board']))

    await callback_query.answer()

if __name__ == '__main__':
    executor.start_polling(dp)
