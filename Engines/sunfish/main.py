import tools.uci
import chess
import chess.engine

board = chess.Board()
print(board)

engine = chess.engine.SimpleEngine.popen_uci(
    r"/users/meni/code/personal/chess/sunfish/build/pack.sh"
)

while not board.is_game_over():
    result = engine.play(board, chess.engine.Limit(time=0.1))
    board.push(result.move)

engine.quit()
