from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.PyQt.QtGui import QCursor, QAction
from qgis.PyQt.QtCore import Qt, pyqtSignal, QPoint
from qgis.PyQt.QtWidgets import (
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
)
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsGeometry,
    Qgis,
    QgsPoint,
    QgsPointXY,
)


class QTCPointsTool(QgsMapTool):
    completedRequest = pyqtSignal(str)
    abandonedRequest = pyqtSignal(str)

    def __init__(self, canvas, iface):
        self.canvas = canvas
        self.iface = iface
        QgsMapTool.__init__(self, self.canvas)
        self.arrow_down_action = None
        self.arrow_up_action = None

    def activate(self):
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage("Select regime change point:", duration=0)
        self.cursor = QCursor()
        self.cursor.setShape(Qt.CrossCursor)
        self.setCursor(self.cursor)
        self.point_band = QgsRubberBand(self.canvas, Qgis.GeometryType.Point)
        self.line_band = QgsRubberBand(self.canvas, Qgis.GeometryType.Line)
        self.hint_bar = QLineEdit()
        self.response_bar = QLineEdit()
        self.option_table = QTableWidget()
        self.option_table.setColumnCount(1)
        self.option_table.setFixedHeight(124)
        self.option_table.setFixedWidth(118)
        self.option_table.verticalHeader().setVisible(False)
        self.option_table.horizontalHeader().setVisible(False)
        self.option_table.setParent(self.canvas)
        self.option_table.move(
            QPoint(
                (self.canvas.mouseLastXY().x() + 10),
                (self.canvas.mouseLastXY().y() + 10),
            )
        )

        if not self.arrow_down_action:
            self.arrow_down_action = QAction(self.canvas)
            self.arrow_down_action.setShortcut(Qt.Key_Down)
            self.arrow_down_action.triggered.connect(self.handleDownArrow)
            self.canvas.addAction(self.arrow_down_action)
        elif self.arrow_down_action not in self.canvas.actions():
            self.canvas.addAction(self.arrow_down_action)
        if not self.arrow_up_action:
            self.arrow_up_action = QAction(self.canvas)
            self.arrow_up_action.setShortcut(Qt.Key_Up)
            self.arrow_up_action.triggered.connect(self.handleUpArrow)
            self.canvas.addAction(self.arrow_up_action)
        elif self.arrow_up_action not in self.canvas.actions():
            self.canvas.addAction(self.arrow_up_action)

    def on_map_tool_set(self, new_tool, old_tool):
        if new_tool == self:
            pass
        else:
            self.reset()

    def reset(self):
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage("Select Regime Change Point:", duration=0)
        self.point_band.reset(Qgis.GeometryType.Point)
        self.line_band.reset(Qgis.GeometryType.Line)
        self.hint_bar.hide()
        self.response_bar.hide()
        self.option_table.hide()

    def deactivate(self):
        if self.arrow_down_action and self.arrow_down_action in self.canvas.actions():
            self.arrow_down_action.triggered.disconnect(self.handleDownArrow)
            self.canvas.removeAction(self.arrow_down_action)
        if self.arrow_up_action and self.arrow_up_action in self.canvas.actions():
            self.arrow_up_action.triggered.disconnect(self.handleUpArrow)
            self.canvas.removeAction(self.arrow_up_action)
        self.completedRequest.emit("task complete")
        self.iface.messageBar().clearWidgets()
        self.point_band.reset()
        self.line_band.reset()
        self.hint_bar.hide()
        self.response_bar.hide()
        self.option_table.hide()
        QgsMapTool.deactivate(self)
        self.deactivated.emit()

    def keyPressEvent(self, e):
        match e.key():
            case Qt.Key_Return:
                self.abandonedRequest.emit("Request Abandoned")
                self.deactivate()
            case Qt.Key_Escape:
                self.abandonedRequest.emit("Request Abandoned")
                self.deactivate()

    def canvasPressEvent(self, e):
        pass

    def canvasMoveEvent(self, e):
        mouse_point = QgsPointXY(
            e.mapPoint().x(),
            e.mapPoint().y()
        )
