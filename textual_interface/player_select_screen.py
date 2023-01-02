from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Input, Header, Label
from pathlib import Path

tp = Path(__file__).resolve().parent


class PlayerNameButtonBox(Static):
    def compose(self) -> ComposeResult:
        yield Button("Start", id="start", variant="success", classes='confirm_button')


class PlayerNameEntryScreen(Screen):

    def __init__(self):
        super(PlayerNameEntryScreen, self).__init__()
        self.input_player1: None | Input = Input()
        self.input_player2: None | Input = Input()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if event.button.id == "btn_start":
            self.add_class("started")

    def compose(self) -> ComposeResult:
        yield Label('Enter Player 1 Name: ', id='lbl_player1_name')
        yield self.input_player1
        yield Label('Enter Player 2 Name: ', id='lbl_player2_name')
        yield self.input_player2
        yield PlayerNameButtonBox()
