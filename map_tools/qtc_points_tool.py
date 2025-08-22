from qgis.gui import QgsMapTool, QgsRubberBand, QgsMapToolPan
from qgis.PyQt.QtGui import QCursor, QAction, QColor
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
    QgsLineString,
)


class QTCPointsTool(QgsMapTool):
    completedRequest = pyqtSignal(str)
    abandonedRequest = pyqtSignal(str)

    def __init__(self, canvas, iface, feature_list, raster):
        self.canvas = canvas
        self.iface = iface
        self.feature_list = feature_list
        self.raster = raster
        self.feature = self.feature_list[0].getFeature(self.feature_list[1])
        self.feature_geom = self.feature.geometry()
        self.start_point = self.feature_geom.startPoint()
        self.end_point = self.feature_geom.endPoint()
        QgsMapTool.__init__(self, self.canvas)
        self.line_point = None
        self.panTool = QgsMapToolPan(self.iface.mapCanvas())

    def activate(self):
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage("Select regime change point:", duration=0)
        self.cursor = QCursor()
        self.cursor.setShape(Qt.CrossCursor)
        self.setCursor(self.cursor)
        self.point_band = QgsRubberBand(self.canvas, Qgis.GeometryType.Point)
        self.line_band = QgsRubberBand(self.canvas, Qgis.GeometryType.Line)
        self.line_band.setStrokeColor(QColor(0, 18, 255))
        self.point_band.setStrokeColor(QColor(0, 18, 255))
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
        self.iface.messageBar().clearWidgets()
        self.point_band.reset()
        self.line_band.reset()
        self.hint_bar.hide()
        self.response_bar.hide()
        self.option_table.hide()
        for layer in QgsProject.instance().layerTreeRoot().findLayers():
            if isinstance(layer.layer(), QgsVectorLayer):
                ids = layer.layer().selectedFeatureIds()
                for id in ids:
                    layer.layer().deselect(id)
        QgsMapTool.deactivate(self)
        self.deactivated.emit()
        self.iface.mapCanvas().setMapTool(self.panTool)

    def keyPressEvent(self, e):
        match e.key():
            case Qt.Key_Return:
                self.abandonedRequest.emit("Request Abandoned")
                self.deactivate()
            case Qt.Key_Escape:
                self.abandonedRequest.emit("Request Abandoned")
                self.deactivate()

    def canvasPressEvent(self, e):
        self.point_band.addPoint(self.line_point)

    def canvasMoveEvent(self, e):
        mouse_point = QgsPointXY(
            e.mapPoint().x(),
            e.mapPoint().y()
        )
        feature_geom = self.feature.geometry()
        _, self.line_point, _, _ = feature_geom.closestSegmentWithContext(mouse_point)
        band_line = QgsGeometry().fromPolylineXY([mouse_point, self.line_point])
        self.line_band.reset()
        self.line_band.addGeometry(band_line)
