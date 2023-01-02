# - * -coding: utf - 8 - * -
"""


@author: ☙ Ryan McConnell ❧
"""
import logging
from queue import Queue

from textual.app import ComposeResult, App
from textual.screen import Screen
from textual.widgets import Button, Header, Footer

from TeachChelsea.TickTacToe.textual_interface.communication_interface import VmToViewCmd, ViewToVmCmd, SimpleMessage, \
    VmToViewMessage
from TeachChelsea.TickTacToe.textual_interface.game_over_screen import GameOverScreen
from TeachChelsea.TickTacToe.textual_interface.game_screen import TicTacToeScreen
from TeachChelsea.TickTacToe.textual_interface.player_select_screen import PlayerNameEntryScreen
from TeachChelsea.TickTacToe.textual_interface.title_screen import TitleScreen

from pathlib import Path

tp = Path(__file__).resolve().parent


class TicTacToeTextualizeApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self, *args, **kwargs):
        super(TicTacToeTextualizeApp, self).__init__(*args, **kwargs)
        self.queue = Queue()
        self.hack = []
        self.collect_all_css()

    def collect_all_css(self):
        tpp = tp / 'css'
        bs = []
        for fil in tpp.iterdir():
            if fil.suffix == '.css':
                self.stylesheet.read(str(fil))
                with open(fil.absolute(), 'r') as f:
                    bs.append(f.read())
        return '\n'.join(bs)

    def compose(self) -> ComposeResult:
        # create child widgets for the app
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        # An action to toggle dark mode
        self.dark = not self.dark

    def get_next_message(self, block=True) -> SimpleMessage:
        return self.queue.get(block=block)

    def pack_data_for_vm(self, sm: SimpleMessage):
        sm.end_callback = self.queue.task_done
        self.queue.put(sm)

    def view_player_selection_state(self, msg: VmToViewMessage):
        self.show_player_entry_screen()

    def pop_screen(self) -> Screen:
        if len(self.screen_stack) > 1:
            logging.debug(str(self.screen_stack))
            return super(TicTacToeTextualizeApp, self).pop_screen()

    def view_recv_game_won(self, msg: VmToViewMessage):
        self.pop_screen()
        self.push_screen(GameOverScreen(msg.data))

    def recv_game_draw(self, msg: VmToViewMessage):
        self.pop_screen()
        self.push_screen(GameOverScreen(None))

    def recv_game_begin_state(self, msg: VmToViewMessage):
        self.push_screen(TicTacToeScreen())

    def recv_move_inquery(self, msg: VmToViewMessage):
        # Ask the player for their move

        # This is unsafe because it is not guaranteed that the screen is the correct one.
        # Checking the type would work, but when there is a mismatch that could cause problems if it cant be corrected in the protocol spec
        screen = self.screen
        if isinstance(screen, TicTacToeScreen):
            screen.recv_move_inquery(msg)
        else:  # PANIC
            raise ValueError(f'Screen type was not expected. Current screen is: {type(screen)} expecting : {TicTacToeScreen}')

    def recv_game_board_updated(self, msg: VmToViewMessage):
        # redraw the game board
        # This is unsafe because it is not guaranteed that the screen is the correct one.
        # Checking the type would work, but when there is a mismatch that could cause problems if it cant be corrected in the protocol spec

        screen = self.screen
        if isinstance(screen, TicTacToeScreen):
            screen.recv_game_board_updated(msg)
        else:  # PANIC
            raise ValueError(f'Screen type was not expected. Current screen is: {type(screen)} expecting : {TicTacToeScreen}')

    def recv_player_turn_begin(self, msg: VmToViewMessage):
        # Display whos turn it is
        # This is unsafe because it is not guaranteed that the screen is the correct one.
        # Checking the type would work, but when there is a mismatch that could cause problems if it cant be corrected in the protocol spec
        screen = self.screen
        if isinstance(screen, TicTacToeScreen):
            screen.recv_player_turn_begin(msg)
        else:  # PANIC
            raise ValueError(f'Screen type was not expected. Current screen is: {type(screen)} expecting : {TicTacToeScreen}')

    def on_recv_model_cmd_vm_to_view_message(self, msg: VmToViewMessage):
        logging.debug('recv message ' + str(msg))
        {
            VmToViewCmd.SHOW_PLAYER_SELECT: self.view_player_selection_state,
            VmToViewCmd.GAME_WON: self.view_recv_game_won,
            VmToViewCmd.GAME_DRAW: self.recv_game_draw,
            VmToViewCmd.GAME_BEGIN: self.recv_game_begin_state,
            VmToViewCmd.MOVE_INQUERY: self.recv_move_inquery,
            VmToViewCmd.BOARD_UPDATED: self.recv_game_board_updated,
            VmToViewCmd.TURN_BEGIN: self.recv_player_turn_begin,
            VmToViewCmd.SHUTDOWN: self.shutdown
        }[msg.cmd](msg)

    def shutdown(self, msg: VmToViewMessage):
        self.exit(0)

    def on_mount(self):
        self.push_screen(TitleScreen())
        for f in self.hack:
            f()

    def show_player_entry_screen(self):
        self.push_screen(PlayerNameEntryScreen())

    def confirm_button_clicked(self):
        self.pack_data_for_vm(SimpleMessage(ViewToVmCmd.GAME_STARTED, None))

    def quit_clicked(self):
        self.exit(0)

    def yes_clicked(self):
        self.pop_screen()
        self.pack_data_for_vm(SimpleMessage(ViewToVmCmd.GAME_RESET, None))

    def no_clicked(self):
        self.pop_screen()
        self.pack_data_for_vm(SimpleMessage(ViewToVmCmd.GAME_RESTART, None))

    def on_button_pressed(self, event: Button.Pressed):
        try:
            button_id = event.button.id
            {
                'start': self.btn_enter_clicked,
                'play': self.confirm_button_clicked,
                'quit': self.quit_clicked,
                'yes': self.yes_clicked,
                'no': self.no_clicked
            }[button_id]()
        except KeyError:
            pass

    def btn_enter_clicked(self):
        logging.debug('Clicked player name enter')
        screen = self.screen
        if isinstance(screen, PlayerNameEntryScreen):
            player_name_str1 = screen.input_player1.value
            player_name_str2 = screen.input_player2.value
            self.pack_data_for_vm(SimpleMessage(ViewToVmCmd.PLAYER_NAMES_CHOICE, (player_name_str1, player_name_str2)))
        else:  # PANIC
            raise ValueError(f'Screen type was not expected. Current screen is: {type(screen)} expecting : {PlayerNameEntryScreen}')
        self.pop_screen()

    def action_add_stopwatch(self):
        pass
