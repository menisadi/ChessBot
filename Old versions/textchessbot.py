import chess
import chess.engine
import chess.svg
import os, sys
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram

TOKEN = "5923620449:AAGANQeHrq0da-W3GnKP9bCOmEcJV20gnD8"

def move(update, context):  
    keep_running = True
    while keep_running:
        if board.is_stalemate():
            update.message.reply_text("Game drawn by stalemate.")
            break
        if board.is_insufficient_material():
            update.message.reply_text("Game drawn by insufficient material.")
            break
        if board.can_claim_fifty_moves():
            update.message.reply_text("Game drawn by 50-move rule.")
            break
        if board.can_claim_threefold_repetition():
            update.message.reply_text("Game drawn by threefold repetition.")
            break
        if board.is_checkmate():
            col = "White"
            if board.turn: col = "Black"
            winner = "Engine"
            if col == player_col: winner = "Player"
            update.message.reply_text(col, "(" + winner + ") wins by checkmate.")
            break
        if (board.turn and player_col == 'White') or (not board.turn and player_col == 'Black'):
            move = update.message.text
            # move = input("Enter move: ")
            if move.lower() == "moves":
                legal_moves = ""
                for i, legal_move in enumerate(board.legal_moves):
                    legal_moves += str(board.san(legal_move)) + " "
                update.message.reply_text("Legal moves:", legal_moves)
                continue
            try:
                push = board.push_san(move)
                # if show_only_last: os.system("cls")
                update.message.reply_text(player_col, "(Player) moves", move)
            except ValueError:
                update.message.reply_text(move, "is not a legal move.")
        else:
            col = "White"
            if not board.turn: col = "Black"
            with engine.analysis(board, chess.engine.Limit(time=(1.5))) as analysis:
                for info in analysis:
                    pass
            move = analysis.info['pv'][0]
            move_san = board.san(move)
            board.push(move)
            # if show_only_last: os.system("cls")
            update.message.reply_text(col, "(Engine) moves", str(move_san))
    update.message.reply_text("Thanks for playing!")

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Welcome to Blindfold Chess")

def newgame(update, context):
    engine_file = "stockfish_15.exe"
    if not os.path.exists(engine_file):
        update.message.reply_text()
        print("Engine file not found:", engine_file)
        sys.exit()
    
    player_col = 'White'
    update.message.reply_text("You are playing as " + player_col + ".")
    engine = chess.engine.SimpleEngine.popen_uci(engine_file)
    diff = 1
    engine.configure({"Skill Level": diff})
    update.message.reply_text("Level", str(diff), "difficulty chosen.")
    update.message.reply_text("Type 'moves' at any time to see the legal moves.")
    update.message.reply_text("---")
    update.message.reply_text("Game begins.")
    board = chess.Board()

engine_file = "stockfish_15.exe"
if not os.path.exists(engine_file):
    # update.message.reply_text()
    sys.exit()

player_col = 'White'
# update.message.reply_text("You are playing as " + player_col + ".")
engine = chess.engine.SimpleEngine.popen_uci(engine_file)
diff = 1
engine.configure({"Skill Level": diff})
# update.message.reply_text("Level", str(diff), "difficulty chosen.")
# update.message.reply_text("Type 'moves' at any time to see the legal moves.")
# update.message.reply_text("---")
# update.message.reply_text("Game begins.")
board = chess.Board()

updater = Updater("5631657200:AAEhRNYQkTJcy0eFIZkfVkusPvCzk_KzLZs", use_context=True)
player_col = 'White'

# Get the dispatcher to register handlers
dp = updater.dispatcher

# on different commands - answer in Telegram
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))
dp.add_handler(CommandHandler("newgame", newgame))

# on noncommand i.e message - echo the message on Telegram
dp.add_handler(MessageHandler(Filters.text, move))

# Start the Bot
updater.start_polling()

updater.idle()

# if __name__ == '__main__':
#     main()