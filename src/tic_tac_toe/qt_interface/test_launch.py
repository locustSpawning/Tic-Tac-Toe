from pathlib import Path

from PySide6.QtWidgets import QApplication, QWidget

from tic_tac_toe.model import Symbol
from tic_tac_toe.qt_interface.game_over_screen import TicTacToeGameOverWidget
from tic_tac_toe.qt_interface.game_screen import WidgetGameScreen
from tic_tac_toe.qt_interface.model import QtPlayer, GraphicsSymbol
from tic_tac_toe.qt_interface.run_ui import set_up_app_theme
from tic_tac_toe.qt_interface.model import GameSettings

picture_path = Path(__file__).resolve().parent / 'resources/drop.svg'

def show_end_game_screen(play_name='Monkey') -> QWidget:
    player = QtPlayer(play_name, Symbol.X)
    player.graphic = GraphicsSymbol(picture_path)
    gow = TicTacToeGameOverWidget(player)
    gow.resize(1280, 720)
    gow.show()
    return gow

def show_game_screen() -> QWidget:
    game_settings = GameSettings()
    gs = WidgetGameScreen(game_settings)
    gs.prompt.lbl_prompt.setText('asdlkfjasl;kdfjsa;lkdfj;aslkdfja;slkdfj;lkasdlkfjasl;kdfjsa;lkdfj;aslkdfja;slkdfj;lkasdlkfjasl;kdfjsa;lkdfj;aslkdfja;slkdfj;lkasdlkfjasl;kdfjsa;lkdfj;aslkdfja;slkdfj;lk')
    gs.show()
    return gs

qap = QApplication([])
set_up_app_theme(qap)
gs = show_end_game_screen(play_name='lskdjfklsjadfklskajlskdjfklsjadfklskajlskdjfklsjadfklskajlskdjfklsjadfklskajlskdjfklsjadfklskajlskdjfklsjadfklskajlskdjfklsjadfklskajlskdjfklsjadfklskaj')
gs.resize(1280, 720)
qap.exec()
