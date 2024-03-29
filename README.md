<h1 align="center">Blind-Chess Bot</h1>
<div align="center" id="logo">
    <img src="./Graphics/chess_logo.jpeg" width="200", height="200">
</div>

<p align="center">
    <a href="https://www.gnu.org/licenses/gpl-3.0">
      <img alt="License: GPL v3" src="https://img.shields.io/badge/License-GPLv3-blue.svg">
    </a>
    <a href="https://github.com/menisadi/ChessBot/pulse">
      <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/menisadi/ChessBot">
    </a>
</p>


A chat bot that allows users to play chess via a messaging platform.


## Requirements

- Python 3.x
- [pyTelegramBotAPI - A simple, but extensible Python implementation for the Telegram Bot API](https://github.com/eternnoir/pyTelegramBotAPI)
- [python-chess: a chess library for Python](https://github.com/niklasf/python-chess)
- [pgn2gif](https://github.com/dn1z/pgn2gif)

## Running the bot locally

1. Create a bot and obtain its API token by talking to the [Bot Father](https://telegram.me/botfather) on Telegram.
2. Clone the repository and navigate to the directory:
    ```
    git clone https://github.com/menisadi/ChessBot.git
    cd ChessBot
    ```
3. Create a file named `token.txt` and paste in it your API token.
4. Run the script: `python3 bot.py`

## Usage

1. Start a conversation with the bot and use the following commands to play chess:
- `/start` - start a new game
- `<move>` - make a move on the chess board (in standard algebraic notation e.g. `e4`, `Nxe4`, `a8=Q`)
- `/moves` - show a list of legal move
- `/resign` - resign from the current game
- `/stockfish` -  Play against Stockfish engine (add a number [0-20] to limit its strength). [binary file](https://stockfishchess.org/download/) of Stockfish is not included so you need to download it and add to your local folder
- `/random` - Bot will make random moves
- `/show` - show the board
- `/pgn` - print the entire game in PGN format

## Notes

- The bot supports one game at a time per user
- The bot has been tested on Python 3.10. It may work on other versions of Python, but this has not been tested.

## License

This project is licensed under GNU GPL v3 License - see the [LICENSE](LICENSE) file for details.  

<img src="Graphics/gplv3.png" alt="drawing" width="80"/>

