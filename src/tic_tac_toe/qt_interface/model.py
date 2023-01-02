from pathlib import Path

from PySide6.QtCore import Property
from PySide6.QtGui import QPixmap, QImage, Qt, QColor, QPainter

from tic_tac_toe.model import Player, Symbol



def colorize_pixmap(pixmap: QPixmap, color='black') -> QPixmap:
    pm = pixmap.copy()
    qp = QPainter(pm)
    qp.setCompositionMode(QPainter.CompositionMode_SourceIn)
    qp.fillRect(pm.rect(), QColor(color))
    qp.end()
    return pm


class GraphicsSymbol:
    def __init__(self, path: Path, color: QColor | None=None):
        self.path = path
        self.pixmap = QPixmap(str(self.path))
        self.name = path.stem
        self._color = QColor(Qt.GlobalColor.white)
        if color is not None:
            self.color = QColor(color)

    @property
    def color(self) -> QColor:
        return self._color

    @color.setter
    def color(self, color: QColor):
        self.pixmap = colorize_pixmap(self.pixmap, color)
        self._color = color

    def duplicate(self) -> 'Self':
        return GraphicsSymbol(self.path)


class QtPlayer(Player):
    def __init__(self, name:str, symbol: Symbol):
        super(QtPlayer, self).__init__(name, symbol)
        self.graphic: GraphicsSymbol | None = None


class GameSettings:
    def __init__(self):
        self.players = [QtPlayer(' ', s) for s in Symbol]
        self.game_size = 3
        self.graphics: dict[Symbol, QImage] = {}

    def populate_graphics(self):
        for player in self.players:
            self.graphics[player.symbol] = player.graphic.pixmap.toImage()
