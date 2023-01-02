from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton


class TicTacToeTitleWidget(QWidget):
    sig_exit_requested = Signal(int, name='sig_exit_requested')
    sig_play = Signal(name='sig_play')

    def __init__(self):
        super(TicTacToeTitleWidget, self).__init__()
        self.setStyleSheet('''
        #lbl_title_screen_title {
            padding-top: 50px;
            font: bold 60px; 
            alignment: center;
            text-align: center;
            qproperty-alignment: AlignCenter;
        }
        ''')
        self.m_layout = QVBoxLayout()

        self.lbl_main = QLabel('- T i c T a c T o e -')
        self.lbl_main.setObjectName('lbl_title_screen_title')
        self.wid_button_box = QWidget()
        self.wid_button_box_layout = QHBoxLayout()
        self.cmd_play = QPushButton('Play')
        self.cmd_play.setProperty('class', 'custom_button')
        self.wid_button_box_layout.addWidget(self.cmd_play)
        self.cmd_exit = QPushButton('Exit')
        self.cmd_exit.setProperty('class', 'custom_button')
        self.wid_button_box_layout.addWidget(self.cmd_exit)
        self.wid_button_box.setLayout(self.wid_button_box_layout)

        self.m_layout.addWidget(self.lbl_main)
        self.m_layout.addWidget(self.wid_button_box)

        self.setLayout(self.m_layout)

        self.cmd_play.clicked.connect(self.cmd_play_clicked)
        self.cmd_exit.clicked.connect(self.cmd_exit_clicked)

    def cmd_play_clicked(self):
        self.sig_play.emit()

    def cmd_exit_clicked(self):
        self.sig_exit_requested.emit(0)
