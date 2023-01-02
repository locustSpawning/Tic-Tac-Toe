# - * -coding: utf - 8 - * -
"""


@author: ☙ Ryan McConnell ❧
"""
import asyncio
from enum import Enum
from types import NoneType
from typing import Any, Callable

from textual.message import Message
from textual.message_pump import MessagePump

from TeachChelsea.TickTacToe.model import TicTacToeGameView, GameBoard, Player


class VmToViewCmd(Enum):
    SHOW_PLAYER_SELECT = 'recv_player_selection_state'
    GAME_WON = 'recv_game_won'
    GAME_DRAW = 'recv_game_draw'
    GAME_BEGIN = 'recv_game_begin_state'
    MOVE_INQUERY = 'recv_move_inquery'
    BOARD_UPDATED = 'recv_game_board_updated'
    TURN_BEGIN = 'recv_player_turn_begin'
    SHUTDOWN = 'recv_shutdown'


class ViewToVmCmd(Enum):
    PLAYER_NAMES_CHOICE = 'emit_player_names_set'
    PLAYER_MOVE_CHOICE = 'emit_player_move_choice'
    INITIALIZED = 'emit_initialized'

    GAME_STARTED = 'emit_game_started'
    GAME_SCREEN_PUSHED = 'game_screen'

    GAME_RESET = 'emit_reset_game'
    GAME_RESTART = 'emit_game_restart'


class SimpleMessage:
    def __init__(self, cmd: ViewToVmCmd, data: Any, end_callback: Callable | NoneType=None):
        self.cmd = cmd
        self.data = data
        self.end_callback = end_callback

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.end_callback is not None:
            self.end_callback()

    def __str__(self):
        return f'SimpleMessage(cmd={self.cmd}, data={self.data})'


class TextualTicTacToeView(TicTacToeGameView):
    def __init__(self, message_pump: MessagePump):
        self.pump = message_pump

    def emit_player_names_set(self, names: tuple[str, str]):
        pass

    def emit_player_move_choice(self, choice: tuple[int, int]):
        pass

    def emit_initialized(self):
        pass

    def emit_game_started(self):
        pass

    def emit_reset_game(self):
        pass

    def emit_game_restart(self):
        pass

    def post_message_to_app(self, cmd: VmToViewCmd, data: Any = None):
        msg = VmToViewMessage(cmd, self.pump, data=data)
        asyncio.run(self.pump.post_message(msg))

    def recv_game_won(self, winner: str):
        self.post_message_to_app(VmToViewCmd.GAME_WON, data=winner)

    def recv_game_draw(self):
        self.post_message_to_app(VmToViewCmd.GAME_DRAW)

    def recv_player_selection_state(self):
        self.post_message_to_app(VmToViewCmd.SHOW_PLAYER_SELECT)

    def recv_game_begin_state(self):
        self.post_message_to_app(VmToViewCmd.GAME_BEGIN)

    def recv_move_inquery(self):
        self.post_message_to_app(VmToViewCmd.MOVE_INQUERY)

    def recv_game_board_updated(self, game_board: GameBoard, coordinate=None):
        self.post_message_to_app(VmToViewCmd.BOARD_UPDATED, data=(game_board, coordinate))

    def recv_player_turn_begin(self, player: Player):
        self.post_message_to_app(VmToViewCmd.TURN_BEGIN, data=player)

    def recv_shutdown(self):
        self.post_message_to_app(VmToViewCmd.SHUTDOWN)



class VmToViewMessage(Message):
    __slots__ = 'cmd', 'data'
    namespace = 'recv_model_cmd'

    def __init__(self, cmd: VmToViewCmd, *args, data=None, **kwargs):
        super(VmToViewMessage, self).__init__(*args, **kwargs)
        self.cmd = cmd
        self.data = data

    def __rich_repr__(self):
        yield from super(VmToViewMessage, self).__rich_repr__()
        yield self.cmd
        yield self.data
