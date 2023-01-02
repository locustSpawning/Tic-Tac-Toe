import logging

from TeachChelsea.TickTacToe.model import GameBoard
from TeachChelsea.TickTacToe.textual_interface.communication_interface import VmToViewMessage, VmToViewCmd
from TeachChelsea.TickTacToe.textual_interface.view import TicTacToeTextualizeApp


def show_game_won_screen(app, player_won: str | None):
    app.hack.append(
        lambda: app.view_recv_game_won(VmToViewMessage(VmToViewCmd.GAME_WON, data=player_won, sender=app)))

def show_player_name_screen(app):
    app.hack.append(
        lambda: app.view_player_selection_state(VmToViewMessage(VmToViewCmd.SHOW_PLAYER_SELECT, data=None, sender=app)))

def show_tic_tac_toe_screen(app):
    gb = GameBoard(3)
    gb.initialize_game_board()
    app.hack.extend([
        lambda: app.recv_game_begin_state(VmToViewMessage(VmToViewCmd.GAME_BEGIN, data=None, sender=app)),
        lambda : app.recv_game_board_updated(VmToViewMessage(VmToViewCmd.BOARD_UPDATED, data=(gb, None), sender=app))
    ])

def run_textual_game():
    logging.basicConfig(filename='dumb.log', encoding='utf-8', level=logging.DEBUG)
    app = TicTacToeTextualizeApp()
    show_tic_tac_toe_screen(app)
    app.run()

run_textual_game()
