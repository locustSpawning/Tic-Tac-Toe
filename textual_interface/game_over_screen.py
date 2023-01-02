from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Header
from pathlib import Path

tp = Path(__file__).resolve().parent


class GameOverButtonBox(Static):
    def compose(self) -> ComposeResult:
        yield Button("Yes", id="yes", variant="success", classes='confirm_button')
        yield Button("No", id="no", variant="error", classes='cancel_button')


class GameOverScreen(Screen):
    def __init__(self, winner:str|None, *args, **kwargs):
        super(GameOverScreen, self).__init__(*args, **kwargs)
        self.winner = winner

    def compose(self) -> ComposeResult:
        yield Header(id='asscheecks')
        if self.winner is not None:
            ste = f'\n \n \n Congratulations! \n {self.winner} is the winner!'
        else:
            ste = 'Game Over! You\'re both losers!'
        yield Static(ste + f' \n \n \n \n \n Play again?', id='label_play_again')
        yield GameOverButtonBox()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if event.button.id == "yes":
            self.add_class("yes_accept")
        elif event.button.id == "no":
            self.add_class("no_return")
