import logging

from observer_hooks import notify
from textual.app import ComposeResult
from textual.events import Click
from textual.screen import Screen
from textual.widgets import DataTable, Label, Header

from TeachChelsea.TickTacToe.model import Player, GameBoard, Symbol
from TeachChelsea.TickTacToe.textual_interface.communication_interface import SimpleMessage, ViewToVmCmd, \
    VmToViewMessage
from pathlib import Path

tp = Path(__file__).resolve().parent



class TicTacToeBoardTable(DataTable):
    def on_click(self, event: Click) -> None:
        meta = event.style.meta
        self.cell_clicked(meta["row"], meta["column"])

    @notify(no_origin=True)
    def cell_clicked(self, row: int, column: int):
        pass


class TicTacToeScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(TicTacToeScreen, self).__init__(*args, **kwargs)
        self.wid_board = TicTacToeBoardTable(id='lbl_board', show_header=False)
        self.wid_board.cell_clicked.subscribe(self.cell_clicked)
        self.lbl_prompt = Label('this is some text', id='lbl_prompt')
        self.current_player: None | Player = None
        self.picking_move = False

    def cell_clicked(self, row: int, column: int):
        logging.debug(f'click row: {row}, col {column}')
        if self.picking_move:
            self.app.pack_data_for_vm(SimpleMessage(ViewToVmCmd.PLAYER_MOVE_CHOICE, (column, row)))
            self.picking_move = False

    def recv_move_inquery(self, msg: VmToViewMessage):
        # Ask the player for their move
        player: Player = self.current_player
        self.picking_move = True
        self.lbl_prompt.update(f'{player.name}, it\'s your turn!')

    def recv_game_board_updated(self, msg: VmToViewMessage):
        # redraw the game board
        game_board: GameBoard = msg.data[0]
        logging.debug(game_board)
        position: tuple[int, int] = msg.data[1]

        self.wid_board.clear()
        self.wid_board.fixed_rows = game_board.board_size
        self.wid_board.fixed_columns = game_board.board_size
        self.wid_board.add_columns(*([''] * (game_board.board_size - len(self.wid_board.columns))))

        def convert_symbol_to_str(s: Symbol):
            if s is None:
                return ' '
            else:
                return str(s.name)

        for i in range(game_board.board_size):
            row = [convert_symbol_to_str(column[i]) for column in game_board.game_board]
            self.wid_board.add_row(*row)

    def recv_player_turn_begin(self, msg: VmToViewMessage):
        # Display whos turn it is
        player: Player = msg.data
        self.lbl_prompt.update(f'{player.name}, it\'s your turn!')
        self.current_player = player

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.wid_board
        yield self.lbl_prompt
        yield TicTacToeBoardTable()


    def on_mount(self):
        self.app.pack_data_for_vm(SimpleMessage(ViewToVmCmd.GAME_SCREEN_PUSHED, None))
