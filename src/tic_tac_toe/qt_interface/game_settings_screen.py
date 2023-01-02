from functools import partial

from pathlib import Path

from PySide6.QtCore import Signal, Property
from PySide6.QtGui import QImage, QIcon, QPixmap, Qt, QColor
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QComboBox, QHBoxLayout, \
    QColorDialog, QSpacerItem, QSizePolicy

from tic_tac_toe.qt_interface.model import GameSettings, QtPlayer, GraphicsSymbol, colorize_pixmap

pt = Path(__file__).resolve().parent
PATH_EYE_DROPPER = pt / 'resources/drop.svg'


class WidgetGameSettingsScreen(QWidget):
    sig_play_game = Signal(name='sig_play_game')
    sig_player_chose_symbol = Signal(QtPlayer, str, name='sig_player_chose_symbol')  # player name, image name

    def __init__(self, game_settings: GameSettings):
        super(WidgetGameSettingsScreen, self).__init__()

        self.setStyleSheet('''
        #err_lbl{
            color: red;
        }
        #lbl_game_settings_heading {
            padding-top: 30px;
            padding-bottom: 40px;
            font: bold 65px; 
            alignment: center;
            text-align: center;
            qproperty-alignment: AlignCenter;
        }

        ''')

        self.setObjectName('WidgetGameSettingsScreen')
        self.lbl_main = QLabel('Game Settings')
        self.lbl_main.setObjectName('lbl_game_settings_heading')
        self.error_lbl = QLabel()
        self.error_lbl.setObjectName('err_lbl')
        self.error_lbl.setVisible(False)
        self.available_images = dict()
        self.grid_rows = 0

        self.m_layout = QGridLayout()
        self.m_layout.setObjectName('WidgetGameSettingsScreen_layout')
        self.add_widget(self.lbl_main)
        self.m_layout.setVerticalSpacing(35)
        self.m_layout.setContentsMargins(40,40,40,40)

        self.lbl_game_size = QLabel('Game Size')
        self.spin_game_size = QSpinBox()
        self.spin_game_size.setMinimum(2)
        self.spin_game_size.setMaximum(100)
        self.spin_game_size.setValue(game_settings.game_size)
        self.add_widgets(self.lbl_game_size, self.spin_game_size)

        self.players = game_settings.players
        self.player_txt_boxes: list[QLineEdit] = []
        self.player_combo_boxes: list[QComboBox] = []
        self.picture_wids = []
        self.color_wids = []
        self.color_picker_widgets = []
        self.dropper_icon = QIcon(str(PATH_EYE_DROPPER.absolute()))

        for i, player in enumerate(self.players):
            lbl = QLabel(f'Player {i+1} name:')
            txt_box = QLineEdit(player.name)
            wid_container = QWidget()
            wid_container_layout = QHBoxLayout()

            cmb = QComboBox()
            picket_btn = QPushButton()
            picket_btn.clicked.connect(self.color_pick_click)

            wid_container_layout.addWidget(cmb)
            wid_container_layout.addWidget(picket_btn)
            wid_container_layout.setContentsMargins(0,0,0,0)
            wid_container.setLayout(wid_container_layout)


            cmb.currentIndexChanged.connect(self.cmb_idx_changed)
            self.player_txt_boxes.append(txt_box)
            self.player_combo_boxes.append(cmb)
            self.picture_wids.append(wid_container)
            self.color_wids.append(picket_btn)
            self.add_widgets(lbl, txt_box)
            self.add_widgets(QLabel(f'Player {i+1} symbol: '), wid_container)
            picket_btn.setFixedSize(30, cmb.sizeHint().height())
            picket_btn.setIcon(self.dropper_icon)
            self.color_picker_widgets.append(picket_btn)

        self.m_layout.addItem(QSpacerItem(1,1, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding))
        self.add_widget(self.error_lbl)

        self.cmd_play = QPushButton('Play')
        container_widget = QWidget()
        container_widget_layout = QHBoxLayout()
        container_widget_layout.setContentsMargins(0, 0, 0, 0)
        container_widget_layout.addItem(QSpacerItem(1,1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored))
        container_widget_layout.addWidget(self.cmd_play)
        container_widget.setLayout(container_widget_layout)


        self.add_widget(container_widget)

        self.setLayout(self.m_layout)

        self.cmd_play.clicked.connect(self.cmd_play_clicked)
        self.cmd_play.setProperty('class', 'custom_button play_button')

        self.icon_color = QColor(Qt.GlobalColor.black)
        self.setProperty('class', 'ThemeProperties')

    @Property(QColor)
    def defaultIconColor(self) -> QColor:
        return self.icon_color

    @defaultIconColor.setter
    def defaultIconColor(self, color: QColor):
        self.icon_color = color
        self.icon_color_updated()

    def icon_color_updated(self):
        pixmap = QPixmap(str(PATH_EYE_DROPPER.absolute()))
        colorized = colorize_pixmap(pixmap, self.icon_color)
        self.dropper_icon = QIcon(colorized)
        for btn in self.color_picker_widgets:
            btn.setIcon(self.dropper_icon)

    def color_pick_click(self):
        cmd: QPushButton = self.sender()

        color_dialog = QColorDialog()
        color = color_dialog.getColor(initial=Qt.GlobalColor.black, parent=self)
        if color.isValid():
            player_idx = self.color_wids.index(cmd)
            player = self.players[player_idx]
            if player.graphic is not None:
                player.graphic.color = color
                cmb = self.player_combo_boxes[player_idx]
                cmb.setItemIcon(0, QIcon(player.graphic.pixmap))

    def cmb_idx_changed(self, idx: int):
        cmb: QComboBox = self.sender()
        text = cmb.itemText(idx)
        if text in {''}:
            return
        player_idx = self.player_combo_boxes.index(cmb)
        player = self.players[player_idx]
        self.sig_player_chose_symbol.emit(player, text)

    def add_widgets(self, wid1: QWidget, wid2: QWidget):
        self.m_layout.addWidget(wid1, self.grid_rows, 0)
        self.m_layout.addWidget(wid2, self.grid_rows, 1)
        self.grid_rows += 1

    def add_widget(self, wid: QWidget):
        self.m_layout.addWidget(wid, self.grid_rows, 0, 1, 2)
        self.grid_rows += 1

    def cmd_play_clicked(self):
        self.sig_play_game.emit()

    def display_error(self, msg):
        self.error_lbl.setText(msg)
        self.error_lbl.setVisible(True)

    def clear_error(self):
        self.error_lbl.setVisible(False)

    def reject_player_takes_symbol(self, player: QtPlayer, symbol: str):
        player_idx = self.players.index(player)
        self.player_combo_boxes[player_idx].clear()
        self.display_error(f'Could not set player {player_idx+1} to symbol {symbol}')

    def set_combo_box_choices(self, cmb: QComboBox, imgs: dict[str, GraphicsSymbol]):
        pp = cmb.signalsBlocked()
        cmb.blockSignals(True)
        try:
            cmb.clear()
            player_idx = self.player_combo_boxes.index(cmb)
            player = self.players[player_idx]
            if player.graphic is None:
                cmb.addItem('')
            else:
                cmb.addItem(QIcon(player.graphic.pixmap), player.graphic.name)
            for name, graphic in imgs.items():
                cmb.addItem(QIcon(graphic.pixmap), graphic.name)
        finally:
            cmb.blockSignals(pp)

    def set_available_symbol_images(self, imgs: dict[str, GraphicsSymbol]):
        for cmb in self.player_combo_boxes:
            self.set_combo_box_choices(cmb, imgs)
