import telebot
import os
import random 
import io
from datetime import date

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

# Create a dictionary to store the chess game of each user
games = {}

# Initiate engine
# TODO - can we put this somehow in a function?
engine_file = "stockfish_15.exe"
engine = chess.engine.SimpleEngine.popen_uci(engine_file)

# Define a handler for the /help command
@bot.message_handler(commands=["help"])
def show_help(message):
    # Define a dictionary of all the available commands and their descriptions
    commands = {
        "/start": "Start a new game",
        "/help": "Show all the available commands",
        "/resign": "Resign :(",
        "/random": "Bot will make random moves",
        "/stockfish": "Play against Stockfish engine (add a number to limit its strength",
        "/moves": "Show a list of legal moves",
        "/fen": "Print a FEN representation of the current board",
        "/show": "Show the board (using piece-letters on a 8x8 textual matrix)"
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
    cid = message.chat.id
    # bot.send_message(message.chat.id, board.fen())
    bot.send_message(message.chat.id, "Hi! Lets begin")
    if cid not in games:
        games[cid] = dict()
        games[cid]['Board'] = chess.Board()
        games[cid]['Engine'] = 'random'
        games[cid]['Count'] = 0
        games[cid]['PGN'] = ""

    games[cid]['Board'].set_fen(chess.STARTING_FEN)

@bot.message_handler(commands=['stockfish'])
def stockfish(message):
    cid = message.chat.id
    try:
        diff = int(message.text.split()[1])
    except:
        diff = 20
    games[cid]['Engine'] = 'stockfish'
    bot.send_message(message.chat.id, f'Stockfish Level {diff} activated')
    engine.configure({"Skill Level": diff})


@bot.message_handler(commands=['random'])
def random_mode(message):
    cid = message.chat.id
    games[cid]['Engine'] = 'random'
    bot.send_message(message.chat.id, f'Random move activated')

@bot.message_handler(commands=['fen'])
def fen(message):
    cid = message.chat.id
    # Send the board to the user
    bot.send_message(message.chat.id, games[cid]['Board'].fen())

@bot.message_handler(commands=['moves'])
def legal_moves(message):
    # Send the list of legal moves
    cid = message.chat.id
    moves_in_uci = list(games[cid]['Board'].legal_moves)
    moves_in_san = [games[cid]['Board'].san(move) for move in moves_in_uci]
    bot.send_message(message.chat.id, ' '.join(moves_in_san))


@bot.message_handler(commands=['pgn'])
def pgn(message):
    cid = message.chat.id
    final_pgn = games[cid]['PGN'] + '\n\n'
    game_pgn = chess.pgn.read_game(io.StringIO(final_pgn))
    game_pgn.headers["Event"] = 'Blind-chess match'
    game_pgn.headers["Site"] = 'Telegram'
    game_pgn.headers["White"] = 'Me'
    game_pgn.headers["Black"] = 'Telegram Bot'
    game_pgn.headers["Date"] = date.today()
    # Send the pgn to the user
    bot.send_message(message.chat.id, game_pgn)


@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def make_move(message):
    # Parse the move from the message
    move = message.text # [6:]
    cid = message.chat.id
    # Make the move on the board
    legal_move = False
    while legal_move == False:
        try:
            try:
                games[cid]['Board'].push_san(move)
            except KeyError: # If user played a move without first pushing /start
                games[cid] = dict()
                games[cid]['Board'] = chess.Board()
                games[cid]['Engine'] = 'random'
                games[cid]['Count'] = 0
                games[cid]['PGN'] = ""              
                games[cid]['Board'].set_fen(chess.STARTING_FEN)                
                games[cid]['Board'].push_san(move)
            legal_move = True
            # node = node.add_variation(chess.Move.from_uci(move))
        except ValueError:
            bot.send_message(message.chat.id, f"{move} is not a legal move.")
            return
    
    games[cid]['Count'] = games[cid]['Count'] + 1
    games[cid]['PGN'] = games[cid]['PGN'] + "\n" + str(games[cid]['Count']) + ". " + move
    check_draw, draw_type = is_a_draw(games[cid]['Board'])
    if check_draw:
        bot.send_message(message.chat.id, f"Draw: {draw_type}")
        games[cid]['PGN'] = games[cid]['PGN'] + " { The game is a draw. } 1/2-1/2"
        games[cid]['Board'].set_fen(chess.STARTING_FEN)
        return

    if games[cid]['Board'].is_checkmate():
        bot.send_message(message.chat.id, "Game Over - You won!")
        games[cid]['PGN'] = games[cid]['PGN'] + " { White wins by checkmate. } 1-0"
        games[cid]['Board'].set_fen(chess.STARTING_FEN)
        return
    

    move = random.choice(list(games[cid]['Board'].legal_moves))
    if games[cid]['Engine'] == 'stockfish':
        with engine.analysis(games[cid]['Board'], chess.engine.Limit(time=(1.5))) as analysis:
            for info in analysis:
                pass

        move = analysis.info['pv'][0]
    move_san = games[cid]['Board'].san(move)
    
    games[cid]['Board'].push(move)
    games[cid]['PGN'] = games[cid]['PGN'] + " " + move_san

    # node = node.add_variation(chess.Move.from_uci(move))
    bot.send_message(message.chat.id, f"Bot moves {str(move_san)}")
    if check_draw:
        bot.send_message(message.chat.id, f"Draw: {draw_type}")
        games[cid]['PGN'] = games[cid]['PGN'] + " { The game is a draw. } 1/2-1/2"
        games[cid]['Board'].set_fen(chess.STARTING_FEN)
        return
    if games[cid]['Board'].is_checkmate():
        bot.send_message(message.chat.id, "Game Over - You lost :(")
        games[cid]['PGN'] = games[cid]['PGN'] + " { Black wins by checkmate. } 0-1"
        games[cid]['Board'].set_fen(chess.STARTING_FEN)
        return

@bot.message_handler(commands=['show'])
def show_board(message):
    cid = message.chat.id
    # bot.send_message(message.chat.id, games[cid]['Board'])
    svgboard = chess.svg.board(games[cid]['Board'])

    with open('board.svg', 'w') as f:
        f.write(svgboard)
    image = pyvips.Image.thumbnail("board.svg", 200)
    image.write_to_file("board.png")
    photo = open("board.png",'rb')

    # Send the updated board to the user
    bot.send_photo(message.chat.id, photo=photo)

@bot.message_handler(commands=['resign'])
def resign(message):
    cid = message.chat.id
    bot.send_message(message.chat.id, "Too bad :(")
    games[cid]['PGN'] = games[cid]['PGN'] + " { White resigns. } 0-1"
    games[cid]['Board'].set_fen(chess.STARTING_FEN)

# Start the bot
# keep_alive.keep_alive()
bot.infinity_polling()