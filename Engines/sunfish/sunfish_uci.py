import time
from Engines.sunfish.sunfish import (
    Searcher,
    Position,
    initial,
    parse,
    render,
    Move,
)


def uci_to_sun(move, ply):
    i, j, prom = (
        parse(move[:2]),
        parse(move[2:4]),
        move[4:].upper(),
    )
    if ply % 2 == 1:
        i, j = 119 - i, 119 - j

    return Move(i, j, prom)


def sun_to_uci(move, hist):
    i, j = move.i, move.j
    if len(hist) % 2 == 0:
        i, j = 119 - i, 119 - j
    move_str = render(i) + render(j) + move.prom.lower()
    return move_str


def generate_move(hist, bwtime, bwinc=0):
    wtime, btime, winc, binc = bwtime, bwtime, bwinc, bwinc

    if len(hist) % 2 == 0:
        wtime, winc = btime, binc

    think = min(wtime / 40 + winc, wtime / 2 - 1)

    start = time.time()
    move_str = None
    move = None
    for depth, gamma, score, move in Searcher().search(hist):
        if score >= gamma:
            move_str = sun_to_uci(move, hist)
        if move_str and time.time() - start > think * 0.8:
            break

    return move, move_str


def starting_hist():
    return [Position(initial, 0, (True, True), (True, True), 0, 0)]
