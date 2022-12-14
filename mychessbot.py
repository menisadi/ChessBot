import telebot
import os

# Import the chess library
import chess
import chess.engine
import chess.pgn
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

# Initiate engine
# TODO - can we put this somehow in a function?
engine_file = "stockfish_15.exe"
engine = chess.engine.SimpleEngine.popen_uci(engine_file)
diff = 1
engine.configure({"Skill Level": diff})

# # Initiate game's PGN
# game = chess.pgn.Game()
# game.headers["Event"] = "Telegram"
# node = game
# print(node)

# Define a handler for the /help command
@bot.message_handler(commands=["help"])
def show_help(message):
    # Define a dictionary of all the available commands and their descriptions
    commands = {
        "/start": "Start the bot",
        "/help": "Show all the available commands",
        "/resign": "Resign :(",
        "/moves": "Show a list of legal moves",
        "/show": "Show the current board",
        "/fen": "Print a FEN representation of the current board"
    }

    # Create a list of all the available commands in the format "command - description"
    help_text = ["{} - {}".format(command, description) for command, description in commands.items()]

    # Join the list of commands into a single string and send it as a message
    bot.send_message(message.chat.id, "Simply write the moves you wish to play and wait for the bot's move.")
    bot.send_message(message.chat.id, "Here are some additional commands")
    bot.send_message(message.chat.id, "\n".join(help_text))

def is_a_draw(board):
    message = ""
    isdraw = False
    if board.is_stalemate():
        message = "Stalemate"
        isdraw = True
    elif board.is_insufficient_material():
        message = "Insufficient Material"
        isdraw = True
    elif board.can_claim_fifty_moves():
        message = "Fifty Moves Rule"
        isdraw = True
    elif board.can_claim_threefold_repetition():
        message = "Threefold Repetition"
        isdraw = True
        
    return isdraw, message

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

@bot.message_handler(commands=['moves'])
def legal_moves(message):
    # Send the list of legal moves
    moves_in_uci = list(board.legal_moves)
    moves_in_san = [board.san(move) for move in moves_in_uci]
    bot.send_message(message.chat.id, ' '.join(moves_in_san))


# @bot.message_handler(commands=['pgn'])
# def pgn(message):
#     # Send the pgn to the user
#     bot.send_message(message.chat.id, game)


@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def make_move(message):
    # Parse the move from the message
    move = message.text # [6:]

    # Make the move on the board
    legal_move = False
    while legal_move == False:
        try:
            board.push_san(move)
            legal_move = True
            # node = node.add_variation(chess.Move.from_uci(move))
        except ValueError:
            bot.send_message(message.chat.id, f"{move} is not a legal move.")
            return

    check_draw, draw_type = is_a_draw(board)
    if check_draw:
        bot.send_message(message.chat.id, f"Draw: {draw_type}")
        return

    if board.is_checkmate():
        bot.send_message(message.chat.id, "Game Over - You won!")
        return
    
    with engine.analysis(board, chess.engine.Limit(time=(1.5))) as analysis:
        for info in analysis:
            pass

    move = analysis.info['pv'][0]
    move_san = board.san(move)
    board.push(move)
    # node = node.add_variation(chess.Move.from_uci(move))
    bot.send_message(message.chat.id, f"Bot moves {str(move_san)}")
    if check_draw:
        bot.send_message(message.chat.id, f"Draw: {draw_type}")
        return
    if board.is_checkmate():
        bot.send_message(message.chat.id, "Game Over - You lost :(")
        return

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

@bot.message_handler(commands=['resign'])
def resign(message):
    bot.send_message(message.chat.id, "Too bad :(")

# Start the bot
bot.infinity_polling()