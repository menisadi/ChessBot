from fenToImage import fenToImage, loadPiecesFolder

start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
is_black = True

board_image_PIL = fenToImage(
    fen=start_fen,
    darkColor="#D18B47",
    lightColor="#FFCE9E",
    squarelength=40,
    pieceSet=loadPiecesFolder("./staunty"),
    flipped=is_black,
)

board_image_PIL.show()
