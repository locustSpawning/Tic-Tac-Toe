# - * -coding: utf - 8 - * -
"""


@author: ☙ Ryan McConnell ❧
"""
import logging
from queue import Empty
from threading import Thread
from time import sleep

from TeachChelsea.TickTacToe.model import TicTacToeGame, Player, Symbol
from TeachChelsea.TickTacToe.textual_interface.communication_interface import TextualTicTacToeView, SimpleMessage, \
    ViewToVmCmd


class GameLogicThread(Thread):
    GAME_STATE_INIT = 'init'
    STATE_GAME_START = 'game_start'
    STATE_AWAIT_PLAYER_NAMES = 'await_player_names'
    STATE_GAME_INITIALIZE = 'game_initialize'
    STATE_AWAIT_PLAYER_MOVE = 'await_player_move'
    STATE_PLAYER_MOVE_INITIALIZE = 'player_move_initialize'
    STATE_GAME_OVER = 'game_over'


    def __init__(self, game: TicTacToeGame, v: TextualTicTacToeView):
        super(GameLogicThread, self).__init__()
        self.game = game
        self.view = v
        self.live = True

        self.game_state = self.GAME_STATE_INIT

    def set_game_state(self, state: str):
        self.game_state = state

    def do_player_names_choice(self, msg: SimpleMessage):
        logging.debug(f'recved player names {msg.data}')
        self.game.set_players(tuple(Player(x,s) for x,s in zip(msg.data, Symbol)))
        self.view.recv_game_begin_state()

    def do_game_screen_pushed(self, msg: SimpleMessage):
        self.set_game_state(self.STATE_GAME_INITIALIZE)

    def do_player_move_choice(self, msg: SimpleMessage):
        if self.game_state == self.STATE_AWAIT_PLAYER_MOVE:
            self.game.register_turn(msg.data)

            if self.game.is_game_over():
                if self.game.winner is None:
                    self.view.recv_game_draw()
                else:
                    self.view.recv_game_won(self.game.winner.name)
                self.set_game_state(self.STATE_GAME_OVER)
            else:
                self.set_game_state(self.STATE_PLAYER_MOVE_INITIALIZE)
        else: # PANIC
            raise ValueError()

    def do_game_started(self, msg: SimpleMessage):
        self.set_game_state(self.STATE_GAME_START)

    def do_game_reset(self, msg: SimpleMessage):
        self.view.recv_game_begin_state()

    def do_game_restart(self, msg: SimpleMessage):
        self.set_game_state(self.GAME_STATE_INIT)

    def game_state_game_start(self):
        self.view.recv_player_selection_state()
        self.set_game_state(self.STATE_AWAIT_PLAYER_NAMES)

    def game_state_game_initialize(self):
        self.game.initialize()

    def game_state_player_move(self):
        self.view.recv_game_board_updated(self.game.board, coordinate=None)
        self.view.recv_player_turn_begin(self.game.current_player)
        self.set_game_state(self.STATE_AWAIT_PLAYER_MOVE)
        self.view.recv_move_inquery()

    def game_state_over(self):
        pass

    def game_loop(self):
        state_actions = {
            self.STATE_GAME_START: [self.game_state_game_start],
            self.STATE_GAME_INITIALIZE: [self.game_state_game_initialize, self.game_state_player_move],
            self.STATE_PLAYER_MOVE_INITIALIZE: [self.game_state_player_move],
            self.STATE_GAME_OVER: [self.game_state_over]
        }
        if self.game_state in state_actions:
            for action in state_actions[self.game_state]:
                action()

    def run(self) -> None:
        try:
            while self.live:
                sleepy = False
                try:
                    with self.view.pump.get_next_message(block=False) as msg:
                        logging.debug(f'VM Thread recv: {msg}')
                        {
                            ViewToVmCmd.PLAYER_NAMES_CHOICE: self.do_player_names_choice,
                            ViewToVmCmd.GAME_SCREEN_PUSHED: self.do_game_screen_pushed,
                            ViewToVmCmd.PLAYER_MOVE_CHOICE: self.do_player_move_choice,
                            ViewToVmCmd.GAME_STARTED: self.do_game_started,
                            ViewToVmCmd.GAME_RESET: self.do_game_reset,
                            ViewToVmCmd.GAME_RESTART: self.do_game_restart
                        }[msg.cmd](msg)
                except Empty:
                    sleepy = True

                self.game_loop()
                if sleepy:
                    sleep(0.1)
        except Exception as e:
            logging.debug(f'VM EXCEPTION: {e}')

        logging.debug('VM event loop terminating')

    def pull_the_plug(self):
        self.live = False
