# - * -coding: utf - 8 - * -
"""


@author: ☙ Ryan McConnell ❧
"""
import logging

from TeachChelsea.TickTacToe.model import TicTacToeGame, GameBoard
from TeachChelsea.TickTacToe.textual_interface.communication_interface import TextualTicTacToeView
from TeachChelsea.TickTacToe.textual_interface.view import TicTacToeTextualizeApp
from TeachChelsea.TickTacToe.textual_interface.view_model import GameLogicThread


def run_textual_game():
    logging.basicConfig(filename='dumb.log', encoding='utf-8', level=logging.DEBUG)

    app = TicTacToeTextualizeApp()

    game = TicTacToeGame(GameBoard(3))
    view = TextualTicTacToeView(app)

    thrd = GameLogicThread(game, view)
    thrd.start()
    try:
        app.run()
    finally:
        thrd.pull_the_plug()


run_textual_game()
