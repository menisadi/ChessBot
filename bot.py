import telebot
from telebot import types
import os
import random
import stat
import io
import pickle
from datetime import date
from fenToImage import fenToImage, loadPiecesFolder

from dotenv import load_dotenv

# taken from https://github.com/dn1z/pgn2gif
import pgn2gif.pgn2gif

# from io import BytesIO

# Import the chess library
import chess
import chess.engine
import chess.pgn
import chess.svg

from Engines.andoma.movegeneration import next_move as andoma_gen
from Engines.sunfish import sunfish_uci
from Engines.sunfish.tools import uci


# Token is stored locally for security reasons
# Read the entire contents of the file as a string
# with open("token.txt", "r") as file:
#     # Read the entire contents of the file as a string
#     TOKEN = file.read().strip()

# TOKEN is stored as a environment variable
# TOKEN = os.environ["BOT_TOKEN"]

project_folder = os.path.expanduser(".")  # adjust as appropriate
load_dotenv(os.path.join(project_folder, ".env"))
TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

# Create a dictionary to store the chess game of each user
games = {}

color_keyboard = types.InlineKeyboardMarkup()
white_button = types.InlineKeyboardButton("White", callback_data="color_white")
black_button = types.InlineKeyboardButton("Black", callback_data="color_black")
random_button = types.InlineKeyboardButton(
    "Random", callback_data="color_random"
)
color_keyboard.add(white_button, black_button, random_button)

engine_keyboard = types.InlineKeyboardMarkup()
# stockfish_engine_button = types.InlineKeyboardButton(
#     "Stockfish", callback_data="engine_stockfish"
# )
random_engine_button = types.InlineKeyboardButton(
    "Random", callback_data="engine_random"
)
andoma_engine_button = types.InlineKeyboardButton(
    "Andoma", callback_data="engine_andoma"
)
sunfish_engine_button = types.InlineKeyboardButton(
    "Sunfish", callback_data="engine_sunfish"
)

engine_keyboard.add(
    sunfish_engine_button, andoma_engine_button, random_engine_button
)

# Initiate engine
# TODO - can we put this somehow in a function?
# engine_path = "Engines/stockfish_8_x64"
# engine_path = "Engines/stockfish_14_x64"
# engine_path = "Engines/stockfish-ubuntu-x86-64-modern"
# engine_path = "Engines/stockfish-macos-x86-64-modern"
# os.chmod(engine_path, stat.S_IRUSR | stat.S_IXUSR)
# engine = chess.engine.SimpleEngine.popen_uci(engine_path)

# diff = 1
# engine.configure({"Skill Level": diff})


# Define a handler for the /help command
@bot.message_handler(commands=["help"])
def show_help(message):
    # Define a dictionary of all the available commands and their descriptions
    commands = {
        "/start": "Start a new game",
        "/help": "Show all the available commands",
        "/resign": "Resign",
        "/random": "Bot will make random moves",
        "/andoma": "Play against Andoma engine",
        "/sunfish": "Play against Sunfish engine",
        # "/stockfish": "Play against Stockfish engine (add a number [0-20] to limit its strength",
        "/show": "Show the board",
        "/moves": "Show a list of legal moves",
        "/gif": "Get a GIF of your game",
        "/pgn": "Show game in PGN format",
        "/fen": "Print a FEN representation of the board",
    }

    # Create a list of all the available commands in the format "command - description"
    help_text = [
        "{} - {}".format(command, description)
        for command, description in commands.items()
    ]

    # Join the list of commands into a single string and send it as a message
    bot.send_message(
        message.chat.id,
        "Simply write the moves you wish to play and wait for the bot's move.",
    )
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


@bot.message_handler(commands=["start"])
def start_game(message):
    cid = message.chat.id
    # bot.send_message(message.chat.id, board.fen())
    bot.send_message(message.chat.id, "Hi! Lets begin")
    if cid not in games:
        games[cid] = dict()
        games[cid]["Board"] = chess.Board()
        games[cid]["Engine"] = "random"
        games[cid]["Count"] = 0
        games[cid]["PGN"] = ""
        games[cid]["No. Games"] = 0
        games[cid]["Color"] = chess.WHITE
        games[cid]["Turn"] = chess.WHITE

    games[cid]["Board"].set_fen(chess.STARTING_FEN)
    games[cid]["Count"] = 0
    games[cid]["PGN"] = ""
    games[cid]["Ended"] = False
    games[cid]["Turn"] = chess.WHITE

    games[cid]["No. Games"] += 1
    with open("users.pickle", "wb") as f:
        # Serialize the users dictionary and write it to the file
        games_counter = {user: v["No. Games"] for user, v in games.items()}
        pickle.dump(games_counter, f, protocol=pickle.HIGHEST_PROTOCOL)

    bot.send_message(
        message.chat.id, "Please select engine:", reply_markup=engine_keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("color"))
def handle_color_callback(call):
    chosen_color = call.data.split("_")[-1]
    chosen_color_bool = string_color_to_bool_color(chosen_color)
    games[call.message.chat.id]["Color"] = chosen_color_bool
    if chosen_color_bool == chess.WHITE:
        bot.send_message(call.message.chat.id, "You will be playing white")
    else:
        bot.send_message(call.message.chat.id, "You will be playing black")
        bot_makes_a_move(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("engine"))
def handle_engine_callback(call):
    chosen_engine = call.data.split("_")[-1]
    print(chosen_engine)
    games[call.message.chat.id]["Engine"] = chosen_engine
    bot.send_message(
        call.message.chat.id,
        f"You will be playing against the {chosen_engine} Bot",
    )

    bot.send_message(
        call.message.chat.id,
        "Please select your color:",
        reply_markup=color_keyboard,
    )


def bot_makes_a_move(cid):
    move = random.choice(list(games[cid]["Board"].legal_moves))
    if games[cid]["Engine"] == "andoma":
        move = andoma_gen(depth=4, board=games[cid]["Board"], debug=False)
    elif games[cid]["Engine"] == "sunfish":
        position = uci.from_fen(*games[cid]["Board"].fen().split())
        current_hist = (
            [position]
            if uci.get_color(position) == uci.WHITE
            else [position.rotate(), position]
        )
        total_time = random.randint(10, 60)
        _, uci_move_str = sunfish_uci.generate_move(current_hist, total_time)
        move = chess.Move.from_uci(uci_move_str)
    # elif games[cid]["Engine"] == "stockfish":
    #     move_time = random.uniform(0.5, 1.5)
    #     with engine.analysis(
    #         games[cid]["Board"], chess.engine.Limit(time=(move_time))
    #     ) as analysis:
    #         for info in analysis:
    #             pass
    #
    #     move = analysis.info["pv"][0]

    move_san = games[cid]["Board"].san(move)
    games[cid]["Board"].push(move)
    if games[cid]["Turn"] == chess.WHITE:
        games[cid]["Count"] = games[cid]["Count"] + 1
        games[cid]["PGN"] = (
            games[cid]["PGN"]
            + "\n"
            + str(games[cid]["Count"])
            + ". "
            + move_san
        )
    else:
        games[cid]["PGN"] = games[cid]["PGN"] + " " + move_san
    bot.send_message(cid, str(move_san))
    check_draw, draw_type = is_a_draw(games[cid]["Board"])
    if check_draw:
        bot.send_message(cid, f"Draw: {draw_type}")
        games[cid]["PGN"] = (
            games[cid]["PGN"] + " { The game is a draw. } 1/2-1/2"
        )
        games[cid]["Ended"] = True
        games[cid]["Board"].set_fen(chess.STARTING_FEN)
        return
    if games[cid]["Board"].is_checkmate():
        bot.send_message(cid, "Game Over - You lost")
        result = "0-1"[:: (2 * games[cid]["Color"] - 1)]
        games[cid]["PGN"] = (
            games[cid]["PGN"]
            + " { "
            + bool_color_to_string(games[cid]["Color"])
            + "  wins by checkmate. } "
            + result
        )
        games[cid]["Ended"] = True
        games[cid]["Board"].set_fen(chess.STARTING_FEN)
        return
    games[cid]["Turn"] = not games[cid]["Turn"]


def string_color_to_bool_color(color_s):
    if color_s == "white":
        return True
    elif color_s == "black":
        return False
    else:
        return bool(random.randint(0, 1))


def bool_color_to_string(color_b):
    if color_b:
        return "white"
    else:
        return "black"


# @bot.message_handler(commands=["stockfish"])
# def stockfish(message):
#     cid = message.chat.id
#     try:
#         diff = int(message.text.split()[1])
#     except:
#         diff = 20
#     games[cid]["Engine"] = "stockfish"
#     bot.send_message(message.chat.id, f"Stockfish Level {diff} activated")
#     engine.configure({"Skill Level": diff})


@bot.message_handler(commands=["andoma"])
def andoma(message):
    cid = message.chat.id
    games[cid]["Engine"] = "andoma"
    bot.send_message(message.chat.id, "Andome activated")


@bot.message_handler(commands=["random"])
def random_mode(message):
    cid = message.chat.id
    games[cid]["Engine"] = "random"
    bot.send_message(message.chat.id, "Random move activated")


@bot.message_handler(commands=["fen"])
def fen(message):
    cid = message.chat.id
    # Send the board to the user
    bot.send_message(message.chat.id, games[cid]["Board"].fen())


@bot.message_handler(commands=["moves"])
def legal_moves(message):
    # Send the list of legal moves
    cid = message.chat.id
    moves_in_uci = list(games[cid]["Board"].legal_moves)
    moves_in_san = [games[cid]["Board"].san(move) for move in moves_in_uci]
    bot.send_message(message.chat.id, " ".join(moves_in_san))


def finalize_pgn(pgn_str, player_color):
    final_pgn = pgn_str + "\n\n"
    # print(final_pgn)
    game_pgn = chess.pgn.read_game(io.StringIO(final_pgn))
    # print(type(game_pgn))
    # print(game_pgn)
    game_pgn.headers["Event"] = "Blind-chess match"
    game_pgn.headers["Site"] = "Telegram"

    if player_color == chess.WHITE:
        game_pgn.headers["White"] = "Me"
        game_pgn.headers["Black"] = "Telegram Bot"
    else:
        game_pgn.headers["White"] = "Telegram Bot"
        game_pgn.headers["Black"] = "Me"

    game_pgn.headers["Date"] = date.today()
    return game_pgn


@bot.message_handler(commands=["pgn"])
def pgn(message):
    cid = message.chat.id
    # Send the pgn to the user
    bot.send_message(
        message.chat.id, finalize_pgn(games[cid]["PGN"], games[cid]["Color"])
    )


def is_ambigious(move, cid):
    moves_in_uci = list(games[cid]["Board"].legal_moves)
    moves_in_san = [games[cid]["Board"].san(move) for move in moves_in_uci]
    possible_intended_moves = [
        m for m in moves_in_san if move == m[0] + m[-2:]
    ]
    return possible_intended_moves


@bot.message_handler(func=lambda message: not message.text.startswith("/"))
def make_move(message):
    # Parse the move from the message
    move = message.text  # [6:]
    cid = message.chat.id
    # Make the move on the board
    legal_move = False
    while legal_move == False:
        try:
            if not games[cid]["Ended"]:
                games[cid]["Board"].push_san(move)
            else:  # If user played a move without first pushing /start
                games[cid] = dict()
                games[cid]["Board"] = chess.Board()
                games[cid]["Engine"] = "random"
                games[cid]["Count"] = 0
                games[cid]["PGN"] = ""
                games[cid]["Board"].set_fen(chess.STARTING_FEN)
                games[cid]["No. Games"] += 1
                with open("users.pickle", "wb") as f:
                    # Serialize the users dictionary and     write it to the file
                    games_counter = {
                        user: v["No. Games"] for user, v in games.items()
                    }
                    pickle.dump(
                        games_counter, f, protocol=pickle.HIGHEST_PROTOCOL
                    )
                games[cid]["Board"].push_san(move)
                games[cid]["Ended"] = False
                games[cid]["Color"] = chess.WHITE
                games[cid]["Turn"] = chess.WHITE
            legal_move = True
            # node = node.add_variation(chess.Move.from_uci(move))
        except ValueError:
            possible_moves = is_ambigious(move, cid)
            if possible_moves == []:
                bot.send_message(
                    message.chat.id, f"{move} is not a legal move."
                )
            else:
                bot.send_message(
                    message.chat.id,
                    f"{move} is not a legal move, did you mean: {' or '.join(possible_moves)}",
                )
            return

    if games[cid]["Turn"] == chess.WHITE:
        games[cid]["Count"] = games[cid]["Count"] + 1
        games[cid]["PGN"] = (
            games[cid]["PGN"] + "\n" + str(games[cid]["Count"]) + ". " + move
        )
    else:
        games[cid]["PGN"] = games[cid]["PGN"] + " " + move

    check_draw, draw_type = is_a_draw(games[cid]["Board"])
    if check_draw:
        bot.send_message(message.chat.id, f"Draw: {draw_type}")
        games[cid]["PGN"] = (
            games[cid]["PGN"] + " { The game is a draw. } 1/2-1/2"
        )
        games[cid]["Board"].set_fen(chess.STARTING_FEN)
        games[cid]["Ended"] = True
        return

    if games[cid]["Board"].is_checkmate():
        bot.send_message(message.chat.id, "Game Over - You won!")
        result = "1-0"[:: (2 * games[cid]["Color"] - 1)]
        games[cid]["PGN"] = (
            games[cid]["PGN"]
            + " { "
            + bool_color_to_string(games[cid]["Color"])
            + " wins by checkmate. } "
            + result
        )
        games[cid]["Board"].set_fen(chess.STARTING_FEN)
        games[cid]["Ended"] = True
        return

    games[cid]["Turn"] = not games[cid]["Turn"]
    bot_makes_a_move(cid)


@bot.message_handler(commands=["show"])
def show_board(message):
    cid = message.chat.id

    # If the graphics is making problem use the following line as a temporary substitute
    # bot.send_message(message.chat.id, games[cid]['Board'])

    board_image_PIL = fenToImage(
        fen=games[cid]["Board"].fen(),
        darkColor="#D18B47",
        lightColor="#FFCE9E",
        squarelength=40,
        pieceSet=loadPiecesFolder("./staunty"),
        flipped=not games[cid]["Color"],
    )

    # board_image_PIL.save()
    bot.send_photo(message.chat.id, photo=board_image_PIL)


@bot.message_handler(commands=["resign"])
def resign(message):
    cid = message.chat.id
    bot.send_message(message.chat.id, "Too bad")
    result = "0-1"[:: (2 * games[cid]["Color"] - 1)]
    games[cid]["PGN"] = (
        games[cid]["PGN"]
        + " { "
        + bool_color_to_string(games[cid]["Color"])
        + " resigns. } "
        + result
    )
    games[cid]["Ended"] = True
    games[cid]["Board"].set_fen(chess.STARTING_FEN)


@bot.message_handler(commands=["gif"])
def gif(message):
    cid = message.chat.id
    game_pgn_str = str(finalize_pgn(games[cid]["PGN"], games[cid]["Color"]))
    with open("game.pgn", "w") as f:
        f.write(game_pgn_str)
    creator = pgn2gif.PgnToGifCreator(
        reverse=not games[cid]["Color"],
        duration=1,
        ws_color="#B58962",
        bs_color="#F1D9B5",
    )
    creator.create_gif("game.pgn", out_path="game.gif")
    gif_data = telebot.types.InputFile("game.gif")

    # Send the gif to the user
    bot.send_animation(message.chat.id, gif_data, width=240, height=240)


# Start the bot
bot.infinity_polling()
