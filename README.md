# ChessBot

A Telegram text-based chat bot.
    <div align="center">
    <img src="Graphics/banner.pn" alt="Logo" width="200"/>
    <br>
    [![HitCount](http://hits.dwyl.com/menisadi/ChessBot.svg)](http://hits.dwyl.com/menisadi/ChessBot)
    [![License][license-badge]][license-link]
</div>

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
4. Run the script: `python3 mychessbot.py`

## Usage

1. Start a conversation with the bot and use the following commands to play chess:
- `/start` - start a new game
- `<move>` - make a move on the chess board (in standard algebraic notation e.g. `e4`, `Nxe4`, `a8=Q`)
- `/moves` - show a list of legal move
- `/resign` - resign from the current game
- `/show` - show the board
- `/pgn` - print the entire game in PGN format

## Notes

- The bot supports one game at a time per user
- The bot has been tested on Python 3.10. It may work on other versions of Python, but this has not been tested.

## License

This project is licensed under GNU GPL v3 License - see the [LICENSE](LICENSE) file for details.  

<img src="Graphics/gplv3.png" alt="drawing" width="80"/>

