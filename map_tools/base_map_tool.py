from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.PyQt.QtGui import QCursor
from qgis.PyQt.QtCore import Qt
from qgis.core import (
    QgsLineString,
    QgsPoint,
    QgsGeometry,
)


class BaseMapTool(QgsMapTool):
    def __init__(self, canvas, iface):
        self.canvas = canvas
        self.iface = iface
        super().__init__(self, self.canvas)

    def activate(self):
        self.selfeature = None
        self.box_size_raw = 10
        self.box_size_calc = self.canvas.mapUnitsPerPixel() * self.box_size_raw
        self.canvas.extentsChanged.connect(self.setBoxSize)
        self.crosshair_size_raw = 100
        self.cursor = QCursor()
        self.cursor.setShape(Qt.BlankCursor)
        self.setCursor(self.cursor)
        self.icon = QgsRubberBand(self.canvas)
        self.icon.setColor(self.cursor_color)
        self.initx = self.canvas.mouseLastXY().x()
        self.inity = self.canvas.mouseLastXY().y()
        self.drawCursor(self.canvas, self.icon, self.initx, self.inity)

    def on_map_tool_set(self, new_tool, old_tool):
        if new_tool == self:
            pass
        else:
            self.reset()

    def reset(self):
        self.icon.reset()

    def deactivate(self):
        self.icon.reset()
        super().deactivate(self)
        self.deactivated.emit()

    def canvasMoveEvent(self, e):
        self.drawCursor(self.canvas, self.icon, e.pixelPoint().x(), e.pixelPoint().y())

    def setBoxSize(self):
        scale = self.iface.mapCanvas().mapUnitsPerPixel()
        self.box_size_calc = scale * self.box_size_raw

    def drawCursor(self, canvas, icon, pixelx, pixely):
        # method for dynamic drawing of the cursor
        # won't extend beyond map extents
        icon.reset()
        self.extent = canvas.extent()
        self.xmax = self.extent.xMaximum()
        self.xmin = self.extent.xMinimum()
        self.ymax = self.extent.yMaximum()
        self.ymin = self.extent.yMinimum()
        self.factor = canvas.mapUnitsPerPixel()
        self.box_size = self.box_size_raw * self.factor
        self.crosshair_size = self.crosshair_size_raw * self.factor
        self.mapx = (pixelx * self.factor) + self.xmin
        self.mapy = self.ymax - (pixely * self.factor)
        self.map_position = QgsPoint(self.mapx, self.mapy)
        self.box_left = QgsGeometry(
            QgsLineString(
                QgsPoint((self.mapx - self.box_size), (self.mapy - self.box_size)),
                QgsPoint((self.mapx - self.box_size), (self.mapy + self.box_size)),
            )
        )
        self.box_right = QgsGeometry(
            QgsLineString(
                QgsPoint((self.mapx + self.box_size), (self.mapy - self.box_size)),
                QgsPoint((self.mapx + self.box_size), (self.mapy + self.box_size)),
            )
        )
        self.box_top = QgsGeometry(
            QgsLineString(
                QgsPoint((self.mapx - self.box_size), (self.mapy - self.box_size)),
                QgsPoint((self.mapx + self.box_size), (self.mapy - self.box_size)),
            )
        )
        self.box_bot = QgsGeometry(
            QgsLineString(
                QgsPoint((self.mapx - self.box_size), (self.mapy + self.box_size)),
                QgsPoint((self.mapx + self.box_size), (self.mapy + self.box_size)),
            )
        )
        if self.map_position.x() - self.box_size - self.crosshair_size > self.xmin:
            self.left_len = self.crosshair_size
        else:
            self.left_len = self.map_position.x() - self.box_size - self.xmin
        if self.map_position.x() + self.box_size + self.crosshair_size < self.xmax:
            self.right_len = self.crosshair_size
        else:
            self.right_len = self.xmax - self.box_size - self.map_position.x()
        if self.map_position.y() - self.box_size - self.crosshair_size > self.ymin:
            self.down_len = self.crosshair_size
        else:
            self.down_len = self.map_position.y() - self.box_size - self.ymin
        if self.map_position.y() + self.box_size + self.crosshair_size < self.ymax:
            self.up_len = self.crosshair_size
        else:
            self.up_len = self.ymax - self.box_size - self.map_position.y()
        self.left_start = QgsPoint(
            (self.map_position.x() - self.box_size), self.map_position.y()
        )
        self.left_end = QgsPoint(
            (self.map_position.x() - self.box_size - self.left_len),
            self.map_position.y(),
        )
        self.left_line = QgsGeometry(QgsLineString(self.left_end, self.left_start))
        self.right_start = QgsPoint(
            (self.map_position.x() + self.box_size), self.map_position.y()
        )
        self.right_end = QgsPoint(
            (self.map_position.x() + self.box_size + self.right_len),
            self.map_position.y(),
        )
        self.right_line = QgsGeometry(QgsLineString(self.right_start, self.right_end))
        self.up_start = QgsPoint(
            self.map_position.x(), (self.map_position.y() + self.box_size)
        )
        self.up_end = QgsPoint(
            self.map_position.x(), (self.map_position.y() + self.box_size + self.up_len)
        )
        self.up_line = QgsGeometry(QgsLineString(self.up_start, self.up_end))
        self.down_start = QgsPoint(
            self.map_position.x(), (self.map_position.y() - self.box_size)
        )
        self.down_end = QgsPoint(
            self.map_position.x(),
            (self.map_position.y() - self.box_size - self.down_len),
        )
        self.down_line = QgsGeometry(QgsLineString(self.down_start, self.down_end))
        icon.addGeometry(self.box_left, doUpdate=False)
        icon.addGeometry(self.box_right, doUpdate=False)
        icon.addGeometry(self.box_top, doUpdate=False)
        icon.addGeometry(self.box_bot, doUpdate=False)
        icon.addGeometry(self.left_line, doUpdate=False)
        icon.addGeometry(self.right_line, doUpdate=False)
        icon.addGeometry(self.up_line, doUpdate=False)
        icon.addGeometry(self.down_line)
