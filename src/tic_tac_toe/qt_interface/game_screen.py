from pathlib import Path

from PySide6.QtCore import Signal, Property, QPropertyAnimation, QEasingCurve, QByteArray, QUrl, QVariantAnimation, \
    QPoint, QPointF, QTimer
from PySide6.QtGui import QImage, QPaintEvent, QPainter, Qt, QMouseEvent, QPen, QColor
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QWidget, QGridLayout, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel, QColorDialog, QFrame

from tic_tac_toe.model import GameBoard
from tic_tac_toe.qt_interface.model import QtPlayer, GameSettings


class FancyBoardTile(QWidget):
    sig_clicked = Signal(QWidget, name='sig_clicked')

    def __init__(self, row: int, column: int):
        super(FancyBoardTile, self).__init__()
        self.img: QImage | None = None
        self.row = row
        self.column = column
        self.animation = None
        self.opacity = 0

    @Property(float)
    def pix_opacity(self):
        return self.opacity

    @pix_opacity.setter
    def pix_opacity(self, opacity: float):
        self.opacity = opacity
        self.repaint()

    def set_image(self, img: QImage | None):
        self.img = img
        self.animation = QPropertyAnimation(self, QByteArray(b'pix_opacity'), self)
        self.animation.setDuration(95)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.animation.start()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super(FancyBoardTile, self).mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.sig_clicked.emit(self)



class WidgetTicTacToe(QFrame):
    sig_grid_item_clicked = Signal(int, int, name='sig_grid_item_clicked')
    sig_game_end_animation_complete = Signal(name='sig_game_end_animation_complete')

    def __init__(self, rows: int, cols: int, parent=None):
        super(WidgetTicTacToe, self).__init__(parent=parent)
        self.setObjectName('WidgetTicTacToe')
        self.lbl_cmplx: list[list[FancyBoardTile]] = []
        self.rows = rows
        self.cols = cols
        self.m_layout = QGridLayout()
        self.set_layout_objs()
        self.setLayout(self.m_layout)
        self.m_layout.setContentsMargins(0,0,0,0)
        self.m_layout.setSpacing(6)
        self.board_color = QColor(Qt.GlobalColor.black)
        self.setProperty('class', 'ThemeProperties')
        self.sf = None
        self.drawing_point = None
        self.start_point = None
        self.game_win_line_color = QColor(Qt.GlobalColor.black)

    @Property(QColor)
    def defaultBoardColor(self) -> QColor:
        return self.board_color

    @defaultBoardColor.setter
    def defaultBoardColor(self, color: QColor):
        self.board_color = color
        self.repaint()

    @Property(QPointF)
    def drawingPoint(self) -> QPointF:
        return self.drawing_point

    @drawingPoint.setter
    def drawingPoint(self, point: QPointF):
        self.drawing_point = point
        self.repaint()

    @Property(QColor)
    def gameWinLineColor(self) -> QColor:
        return self.game_win_line_color

    @gameWinLineColor.setter
    def gameWinLineColor(self, color: QColor):
        self.game_win_line_color = color
        self.repaint()

    def fancy_board_tile_clicked(self, tile: FancyBoardTile):
        self.sig_grid_item_clicked.emit(tile.row, tile.column)

    def set_image_to_position(self, row: int, column: int, image: QImage):
        self.lbl_cmplx[row][column].set_image(image)
        sf = QSoundEffect(parent=self)
        path = str(Path(__file__).resolve().parent / 'resources/sound_effects/bubble.wav')
        sf.setSource(QUrl.fromLocalFile(path))
        sf.setVolume(float(1))
        sf.play()
        self.sf = sf

    def set_layout_objs(self):
        for i in range(self.rows):
            lbls = []
            self.lbl_cmplx.append(lbls)
            for j in range(self.cols):
                lbl = FancyBoardTile(i, j)
                lbl.sig_clicked.connect(self.fancy_board_tile_clicked)
                lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.m_layout.addWidget(lbl, i, j)
                lbls.append(lbl)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        width = self.width()
        height = self.height()

        spacing = self.m_layout.spacing()
        margins = self.contentsMargins()

        try:
            pen = QPen(Qt.GlobalColor.black)
            pen.setWidth(spacing)
            pen.setColor(self.defaultBoardColor)
            painter.setPen(pen)

            for ex_w in self.lbl_cmplx[0][:-1]:
                x1 = ex_w.x() + ex_w.width()
                x1 += int(spacing / 2)
                painter.drawLine(x1, margins.top(), x1, height-margins.bottom())

            for ex_w in list(x[0] for x in self.lbl_cmplx)[:-1]:
                y1 = ex_w.y() + ex_w.height()
                y1 += int(spacing/2)
                painter.drawLine(margins.left(), y1, width-margins.right(), y1)


            for lbls in self.lbl_cmplx:
                for lbl in lbls:
                    if lbl.img is None:
                        continue
                    painter.setOpacity(max(0.0, lbl.opacity))
                    img = lbl.img.scaled(lbl.size(), aspectMode=Qt.AspectRatioMode.KeepAspectRatio)
                    side_x = lbl.width() - img.width()
                    side_y = lbl.height() - img.height()
                    painter.drawImage(lbl.x() + int(side_x / 2), lbl.y() + int(side_y / 2), img)

            line_width = spacing * 4
            pen.setWidth(line_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setColor(self.gameWinLineColor)
            painter.setPen(pen)

            if self.start_point is not None:
                vend_point:QPointF = self.drawingPoint
                line_offset = QPointF(0, 0)
                if vend_point is not None:
                    painter.drawLine(self.start_point+line_offset, vend_point+line_offset)

        finally:
            painter.end()

    def animate_game_win(self, path: list[tuple[int, int]]):
        start_position = path[0]
        end_position = path[-1]

        margins = self.contentsMargins()

        v_width = self.width() - (margins.left() + margins.right())
        v_height = self.height() - (margins.top() + margins.bottom())

        offset = QPointF((v_width / self.cols) / 2,  (v_height / self.rows) / 2)

        start_x = (start_position[0] * v_width) / self.cols
        start_y = (start_position[1] * v_height) / self.rows

        end_x = (end_position[0] * v_width) / self.cols
        end_y = (end_position[1] * v_height) / self.rows

        start_point = QPointF(start_x, start_y) + offset
        end_point = QPointF(end_x, end_y) + offset
        start_point += QPointF(margins.left(), margins.top())
        end_point += QPointF(margins.left(), margins.right())

        self.start_point = start_point

        self.animation = QPropertyAnimation(self, QByteArray(b'drawingPoint'), self)
        self.animation.setDuration(500)
        self.animation.setStartValue(start_point)
        self.animation.setEndValue(end_point)
        self.animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.timer = QTimer()
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.sig_game_end_animation_complete)
        self.animation.finished.connect(self.timer.start)
        self.animation.start()



class WidgetPromptBox(QWidget):
    def __init__(self):
        super(WidgetPromptBox, self).__init__()
        self.m_layout = QHBoxLayout()
        self.lbl_prompt = QLabel()
        self.lbl_prompt.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.picture = QLabel()
        self.picture.setFixedSize(128, 128)

        self.m_layout.addWidget(self.lbl_prompt)
        self.m_layout.addWidget(self.picture)
        self.setLayout(self.m_layout)

    def set_prompt(self, msg: str):
        self.lbl_prompt.setText(msg)

    def set_player_turn(self, player: QtPlayer):
        self.picture.setPixmap(player.graphic.pixmap.scaled(self.picture.size(), aspectMode=Qt.AspectRatioMode.KeepAspectRatio))


class WidgetGameScreen(QWidget):
    def __init__(self, game_settings: GameSettings):
        super(WidgetGameScreen, self).__init__()
        self.setStyleSheet('''
        #WidgetTicTacToe {
            margin: 50px;
        }
        
        #lbl_instructions_game_screen {
            padding-top: 20px;
            padding-bottom: 35px;
            font: bold 20px; 
            alignment: center;
            text-align: center;
            qproperty-alignment: AlignCenter;
        }
        #prompt QLabel{
            font-size: 35px;
        }
        ''')


        self.game_settings = game_settings
        self.tic_tac_toe = WidgetTicTacToe(game_settings.game_size, game_settings.game_size, parent=self)
        self.prompt = WidgetPromptBox()
        self.prompt.setObjectName('prompt')

        self.err_lbl = QLabel()
        self.err_lbl.setVisible(False)

        self.m_layout = QVBoxLayout()

        self.lbl_instrucitons = QLabel('Click the board to place your piece')
        self.lbl_instrucitons.setObjectName('lbl_instructions_game_screen')
        self.m_layout.addWidget(self.lbl_instrucitons)
        self.m_layout.addWidget(self.tic_tac_toe)
        self.m_layout.addWidget(self.prompt)
        self.m_layout.addWidget(self.err_lbl)
        self.setLayout(self.m_layout)

    def change_color(self):
        cd = QColorDialog()
        color = cd.getColor(parent=self)
        if color.isValid():
            self.tic_tac_toe.defaultBoardColor = color

    def display_err(self, msg: str):
        self.err_lbl.setText(msg)
        self.err_lbl.setVisible(True)

    def clear_err(self):
        self.err_lbl.setText('')
        self.err_lbl.setVisible(False)

    def set_player_turn(self, player: QtPlayer):
        self.prompt.set_prompt(f'➤ {player.name}\'s turn')
        self.prompt.set_player_turn(player)

    def update_game_board(self, board: GameBoard):
        lbl_complx = self.tic_tac_toe.lbl_cmplx
        for ic, colum in enumerate(board.game_board):
            for ir, row_symb in enumerate(colum):
                if row_symb is not None:
                    image = self.game_settings.graphics[row_symb]
                    if lbl_complx[ir][ic].img is not image:
                        self.tic_tac_toe.set_image_to_position(ir, ic, image)
