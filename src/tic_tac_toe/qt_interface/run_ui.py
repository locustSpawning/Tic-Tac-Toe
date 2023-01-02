from pathlib import Path

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtGui import QPixmap, QColor, Qt, QFontDatabase, QPalette
from PySide6.QtWidgets import QApplication, QWidget, QLabel

from tic_tac_toe.model import TicTacToeGame, GameBoard
from tic_tac_toe.qt_interface.game_screen import WidgetGameScreen
from tic_tac_toe.qt_interface.model import QtPlayer, GameSettings, GraphicsSymbol
from tic_tac_toe.qt_interface.title_screen import TicTacToeTitleWidget
from tic_tac_toe.qt_interface.game_settings_screen import WidgetGameSettingsScreen
from tic_tac_toe.qt_interface.main_win import MainWin
from tic_tac_toe.qt_interface.game_over_screen import TicTacToeGameOverWidget
from pathlib import Path


fp = Path(__file__).resolve().parent


class QssProperties(QWidget):
    sig_theme_updated = Signal(object, name='sig_theme_updated')

    def __init__(self):
        super(QssProperties, self).__init__()
        self.setObjectName('ThemeProperties')
        self._default_icon_color = QColor(Qt.GlobalColor.white)

    @Property(QColor)
    def defaultIconColor(self) -> QColor:
        return self._default_icon_color

    @defaultIconColor.setter
    def defaultIconColor(self, color: QColor):
        self._default_icon_color = color
        self.sig_theme_updated.emit(self)


APP_QSS = '''
        .ThemeProperties {
            qproperty-defaultIconColor: #c95195;
            qproperty-defaultBoardColor: #c95195;
            qproperty-gameWinLineColor: #43de7c;
        }
        
        QWidget
        {
            font-family: "Press Start K";
            border-color: #9447ba;
            color: palette(text);
            background-color: palette(window);
        }
        QLineEdit {
            background-color: palette(mid);
            padding: 1px;
            border-width: 1px;
            border-style: solid;
            border-radius: 4;
            height: 30px;
        }
        QPushButton 
        {
            border-width: 2px;
            border-style: solid;
            border-radius: 6px;
        }
        .custom_button {
            max-width: 300px;
            max-height: 100px;
            min-width: 300px;
            min-height: 100px;
        }
        QPushButton:hover {
            background-color: palette(text);
            color: black;
        }
        
        QPushButton:hover:pressed {
            background-color:white;
        }
        
        QSpinBox {
            background-color: palette(mid);
            border-width: 1px;
            border-style: outset;
            border-radius: 6px;
            height: 30px;
        } 
        
        QSpinBox::down-button, QSpinBox::up-button {
           border-width: 1px;
        }
        
        QComboBox {
            border-width: 1px;
            border-style: outset;
            border-radius: 6px;
            height: 30px;
            background-color: palette(mid);
        }
        
        QComboBox QAbstractItemView{
            background-color: palette(mid);
            border: 1px solid palette(text);
        }
        '''

def get_app_palette() -> QPalette:
    palette = QPalette()
    text_color = QColor('#c95195')
    background_color = QColor('#0f0f0f')
    boarder_color = QColor('#9447ba')
    mid_color = background_color.lighter()
    palette.setColor(QPalette.ColorGroup.Normal, QPalette.ColorRole.WindowText, text_color)
    palette.setColor(QPalette.ColorGroup.Normal, QPalette.ColorRole.Button, background_color)
    palette.setColor(QPalette.ColorGroup.Normal, QPalette.ColorRole.Light, background_color)
    palette.setColor(QPalette.ColorGroup.Normal, QPalette.ColorRole.Dark, background_color)
    palette.setColor(QPalette.ColorGroup.Normal, QPalette.ColorRole.Mid, mid_color)
    palette.setColor(QPalette.ColorGroup.Normal, QPalette.ColorRole.Text, text_color)
    palette.setColor(QPalette.ColorGroup.Normal, QPalette.ColorRole.BrightText, text_color)
    palette.setColor(QPalette.ColorGroup.Normal, QPalette.ColorRole.Base, background_color)
    palette.setColor(QPalette.ColorGroup.Normal, QPalette.ColorRole.Window, background_color)
    palette.setColor(QPalette.ColorGroup.Normal, QPalette.ColorRole.AlternateBase, boarder_color)
    return palette


def set_up_app_theme(app: QApplication):
    app.setStyle('fusion')
    QFontDatabase.addApplicationFont(str(fp / 'resources/fonts/prstartk.ttf'))
    app.setPalette(get_app_palette())
    app.setStyleSheet(APP_QSS)


class ViewModel(QObject):
    def __init__(self):
        super(ViewModel, self).__init__()
        self.app = QApplication([])


        set_up_app_theme(self.app)
        self.main_win = MainWin()
        self.main_win.resize(1280, 720)
        self.show_title_screen()
        self.main_win.show()
        self.symbol_images: dict[str, GraphicsSymbol] = {}
        self.game_settings: GameSettings = GameSettings()

        self.game: TicTacToeGame | None = None
        self.qss_props = QssProperties()
        self.qss_props.sig_theme_updated.connect(self.theme_updated)
        self.populate_symbol_images()

    def theme_updated(self, obj):
        for graphic in self.symbol_images.values():
            graphic.color = self.qss_props.defaultIconColor

    def initialize_game(self):
        self.game = TicTacToeGame(GameBoard(self.game_settings.game_size))
        self.game.initialize()
        self.game.set_players(self.game_settings.players)
        self.game_settings.populate_graphics()


    def populate_symbol_images(self):
        path = Path(__file__).resolve().parent / 'resources/player_icons'
        for fil in path.iterdir():
            if fil.suffix == '.svg':
                self.symbol_images[fil.stem] = GraphicsSymbol(fil, color=self.qss_props.defaultIconColor)

    def validate_game_settings(self) -> str | None:
        player_names = set()
        player_symbols = set()
        for i, player in enumerate(self.game_settings.players):
            if len(player.name) > 20:
                return f'Player {i+1}\'s name is too dang long!'
            if player.name in player_names:
                return f'Player {i+1} has the same name as another player'
            if player.graphic is None:
                return f'Player {i+1} has not chosen a symbol'
            if player.graphic.name in player_symbols:
                return f'Player {i+1} has the same symbol as another player'
            player_symbols.add(player.graphic.name)
            player_names.add(player.name)
        return None

    def title_play_clicked(self):
        self.show_settings_screen()

    def settings_screen_sig_player_chose_symbol(self, player: QtPlayer, symbol_name: str):
        taken_symbols = set(p.graphic.name for p in self.game_settings.players if p.graphic is not None)
        # noinspection PyTypeChecker
        screen: WidgetGameSettingsScreen = self.screen
        screen.clear_error()
        if symbol_name in taken_symbols:
            screen.reject_player_takes_symbol(player, symbol_name)
        else:
            color = self.qss_props.defaultIconColor
            if player.graphic is not None and player.graphic.name in taken_symbols:
                taken_symbols.remove(player.graphic.name)
                color = player.graphic.color
            player.graphic = self.symbol_images[symbol_name].duplicate()
            player.graphic.color = color
            taken_symbols.add(symbol_name)
        screen.set_available_symbol_images(dict(x for x in self.symbol_images.items() if x[0] not in taken_symbols))

    def settings_screen_sig_play_game(self):
        # noinspection PyTypeChecker
        screen: WidgetGameSettingsScreen = self.screen

        for i, player in enumerate(screen.players):
            player.name = screen.player_txt_boxes[i].text()
        self.game_settings.game_size = screen.spin_game_size.value()

        screen.clear_error()
        if (p := self.validate_game_settings()) is not None:
            screen.display_error(p)
        else:
            self.show_game_screen()

    def game_screen_tile_clicked(self, row: int, col: int):
        # noinspection PyTypeChecker
        screen: WidgetGameScreen = self.screen
        screen.clear_err()
        try:
            self.game.register_turn((col, row))
        except ValueError as e:
            screen.display_err(str(e))
        else:
            screen.update_game_board(self.game.board)
            self.game_loop()

    def game_loop(self):
        # noinspection PyTypeChecker
        screen: WidgetGameScreen = self.screen
        if self.game.winner == -1:
            player_turn = self.game.current_player
            screen.set_player_turn(player_turn)
        else:
            try:
                screen.tic_tac_toe.sig_grid_item_clicked.disconnect(self.game_screen_tile_clicked)
            except TypeError:
                pass
            if self.game.winner == None:
                self.show_end_screen()
            else:
                screen.tic_tac_toe.animate_game_win(self.game.winning_path)
                screen.tic_tac_toe.sig_game_end_animation_complete.connect(self.show_end_screen)
            #

    def show_settings_screen(self):
        settings_screen = WidgetGameSettingsScreen(self.game_settings)
        settings_screen.set_available_symbol_images(self.symbol_images)
        settings_screen.sig_player_chose_symbol.connect(self.settings_screen_sig_player_chose_symbol)
        settings_screen.sig_play_game.connect(self.settings_screen_sig_play_game)
        self.set_screen(settings_screen)

    def show_title_screen(self):
        title = TicTacToeTitleWidget()
        title.sig_exit_requested.connect(self.app.exit)
        title.sig_play.connect(self.title_play_clicked)
        self.set_screen(title)

    def show_game_screen(self):
        self.initialize_game()
        screen = WidgetGameScreen(self.game_settings)
        screen.tic_tac_toe.sig_grid_item_clicked.connect(self.game_screen_tile_clicked)
        self.set_screen(screen)
        self.game_loop()

    def game_over_quit_requested(self):
        self.game = None
        self.game_settings = GameSettings()
        self.show_title_screen()

    def show_end_screen(self):
        game_over = TicTacToeGameOverWidget(self.game.winner)
        game_over.sig_quit_requested.connect(self.game_over_quit_requested)
        game_over.sig_play_again.connect(self.title_play_clicked)
        self.set_screen(game_over)

    def set_screen(self, screen: QWidget):
        self.main_win.setCentralWidget(screen)
        self.screen = screen


    def run(self):
        self.app.exec()


def start_vm():
    vm = ViewModel()
    vm.run()

if __name__ == '__main__':
    start_vm()
