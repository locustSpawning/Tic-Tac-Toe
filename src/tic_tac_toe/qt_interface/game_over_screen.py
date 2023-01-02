from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy

from tic_tac_toe.qt_interface.model import QtPlayer


class TicTacToeGameOverWidget(QWidget):
    sig_quit_requested = Signal(name='sig_quit_requested')
    sig_play_again = Signal(name='sig_play_again')



    def __init__(self, winner: QtPlayer | None):
        super(TicTacToeGameOverWidget, self).__init__()

        self.setStyleSheet('''
                QLabel{
                    text-align: center;
                    qproperty-alignment: AlignCenter;
                    padding-top: 25px;
                    font: 25px;
                }
                #lbl_game_over_screen_title{
                    padding-top: 95px;
                    padding-bottom: 20px;
                    font: bold 65px;
                }
                
                #lbl_game_over_screen_congrat{
                    padding-top: 25px;
                    padding-bottom: 30px;
                    font: bold 35px;
                }
                ''')

        self.m_layout = QVBoxLayout()
        self.lbl_player_symbol = QLabel()
        self.lbl_player_symbol.setObjectName('lbl_player_symbol')
        self.lbl_player_symbol.resize(128,128)
        self.lbl_main = QLabel('Game Over!')
        self.lbl_congrat = QLabel('Congratulations,')
        self.lbl_winner = QLabel()
        if winner is None:
            winner_txt = "You're both losers!"
            self.lbl_player_symbol.setVisible(False)
            #self.lbl_congrat.setVisible(False)
        else:
            if winner.graphic is None:
                self.lbl_player_symbol.setVisible(False)
            else:
                self.lbl_player_symbol.setPixmap(winner.graphic.pixmap.scaled(self.lbl_player_symbol.size(), aspectMode=Qt.AspectRatioMode.KeepAspectRatio))
            winner_txt = f'The winner is, {winner.name}!'
            self.lbl_winner.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
            #self.lbl_congrat.setVisible(True)

        self.lbl_winner.setText(winner_txt)
        self.lbl_main.setObjectName('lbl_game_over_screen_title')
        self.lbl_congrat.setObjectName('lbl_game_over_screen_congrat')
        self.lbl_winner.setObjectName('lbl_game_over_screen_winner')

        self.lbl_play_again = QLabel('Play again?')

        self.wid_button_box = QWidget()
        self.wid_button_box_layout = QHBoxLayout()
        self.cmd_play_again = QPushButton('Play Again!')
        self.cmd_play_again.setProperty('class', 'custom_button')
        self.wid_button_box_layout.addWidget(self.cmd_play_again)
        self.cmd_quit = QPushButton('No')
        self.cmd_quit.setProperty('class', 'custom_button')
        self.wid_button_box_layout.addWidget(self.cmd_quit)
        self.wid_button_box.setLayout(self.wid_button_box_layout)

        self.m_layout.addWidget(self.lbl_main)
        self.m_layout.addItem(QSpacerItem(1,1,QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding))
        self.m_layout.addWidget(self.lbl_congrat)
        self.m_layout.addWidget(self.lbl_player_symbol)
        self.m_layout.addWidget(self.lbl_winner)
        self.m_layout.addWidget(self.lbl_play_again)
        self.m_layout.addItem(QSpacerItem(1, 1, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding))
        self.m_layout.addWidget(self.wid_button_box)


        self.setLayout(self.m_layout)

        self.cmd_play_again.clicked.connect(self.cmd_play_again_clicked)
        self.cmd_quit.clicked.connect(self.cmd_quit_clicked)

    def cmd_play_again_clicked(self):
        self.sig_play_again.emit()

    def cmd_quit_clicked(self):
        self.sig_quit_requested.emit()
