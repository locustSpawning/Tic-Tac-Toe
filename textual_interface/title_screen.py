from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Header
from pathlib import Path

tp = Path(__file__).resolve().parent



class GameStartButtonBox(Static):
    def compose(self) -> ComposeResult:
        yield Button("Play", id="play", variant="success", classes='confirm_button')
        yield Button("Quit", id="quit", variant="error", classes='cancel_button')


class TitleScreen(Screen):
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if event.button.id == "play":
            self.add_class("playing")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(" - -  Welcome to TicTacToe  - - ", id='welcome_text')
        yield GameStartButtonBox()
