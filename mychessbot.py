import telebot
import os

# Import the chess library
import chess
import chess.svg

os.environ['path'] += r';C:\Drivers\vips-dev-8.13\bin'

# package which handles the graphics
import pyvips

# print(os.environ['path'])

# Token is stored locally for security resaons 
# Open the token file in reading mode
with open('token.txt', 'r') as file:
  # Read the entire contents of the file as a string
  TOKEN = file.read()

# Create the bot using the token provided by the BotFather
bot = telebot.TeleBot(TOKEN)

# Create a chess board
board = chess.Board()

@bot.message_handler(commands=['start'])
def start_game(message):
    # Send the initial board to the user
    # bot.send_message(message.chat.id, board.fen())
    bot.send_message(message.chat.id, "Hi! Lets begin")
    board.set_fen(chess.STARTING_FEN)

@bot.message_handler(commands=['fen'])
def fen(message):
    # Send the board to the user
    bot.send_message(message.chat.id, board.fen())


@bot.message_handler(commands=['move'])
def make_move(message):
    # Parse the move from the message
    move = message.text[6:]

    # Make the move on the board
    board.push_san(move)

@bot.message_handler(commands=['show'])
def show_board(message):
    svgboard = chess.svg.board(board)

    with open('board.svg', 'w') as f:
        f.write(svgboard)
    image = pyvips.Image.thumbnail("board.svg", 200)
    image.write_to_file("board.png")
    photo = open("board.png",'rb')

    # Send the updated board to the user
    bot.send_photo(message.chat.id, photo=photo)

# Start the bot
bot.infinity_polling()