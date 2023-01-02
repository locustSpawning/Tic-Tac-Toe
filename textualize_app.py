import logging

from TeachChelsea.TickTacToe.model import GameBoard, TicTacToeGame
from TeachChelsea.TickTacToe.textual_interface.view_model import GameLogicThread, TextualTicTacToeView
from TeachChelsea.TickTacToe.textual_interface.view import TicTacToeTextualizeApp



def run_textual_game():
    logging.basicConfig(filename='dumb.log', encoding='utf-8', level=logging.DEBUG)
    app = TicTacToeTextualizeApp()
    game = TicTacToeGame(GameBoard(3))
    view = TextualTicTacToeView(app)
    gmt = GameLogicThread(game, view)
    gmt.start()
    try:
        app.run()
    finally:
        gmt.pull_the_plug()

run_textual_game()
