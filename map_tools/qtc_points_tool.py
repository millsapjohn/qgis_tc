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
from ..segment_data import SegmentData


class QTCPointsTool(QgsMapTool):
    completedRequest = pyqtSignal(str)
    abandonedRequest = pyqtSignal(str)

    def __init__(self, canvas, iface, feature_list, raster):
        self.canvas = canvas
        self.iface = iface
        self.feature_list = feature_list
        self.raster = raster
        self.arrow_down_action = None
        self.arrow_up_action = None
        self.regime_selected = None
        self.cover_selected = None
        self.is_calculating = False
        self.feature = self.feature_list[0].getFeature(self.feature_list[1])
        self.feature_geom = self.feature.geometry()
        self.start_point = self.feature_geom.startPoint()
        self.start_xy = QgsPointXY(self.start_point)
        self.end_point = self.feature_geom.endPoint()
        self.end_xy = QgsPointXY(self.end_point)
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
        self.regime_option_table = QTableWidget()
        self.regime_option_table.setColumnCount(1)
        self.regime_option_table.setRowCount(4)
        self.regime_option_table.setFixedHeight(124)
        self.regime_option_table.setFixedWidth(118)
        self.regime_option_table.verticalHeader().setVisible(False)
        self.regime_option_table.horizontalHeader().setVisible(False)
        self.regime_option_table.setItem(0, 0, QTableWidgetItem("Sheet Flow"))
        self.regime_option_table.setItem(1, 0, QTableWidgetItem("Unpaved Shallow Concentrated Flow"))
        self.regime_option_table.setItem(2, 0, QTableWidgetItem("Paved Shallow Concentrated Flow"))
        self.regime_option_table.setItem(3, 0, QTableWidgetItem("Channelized Flow"))
        self.regime_option_table.item(0, 0).setSelected(True)
        self.regime_option_table.setParent(self.canvas)
        self.regime_option_table.move(
            QPoint(
                (self.canvas.mouseLastXY().x() + 10),
                (self.canvas.mouseLastXY().y() + 10),
            )
        )
        self.sheet_option_table = QTableWidget()
        self.sheet_option_table.setColumnCount(1)
        self.sheet_option_table.setRowCount(10)
        self.sheet_option_table.setFixedWidth(118)
        self.sheet_option_table.verticalHeader().setVisible(False)
        self.sheet_option_table.horizontalHeader().setVisible(False)
        self.sheet_option_table.setItem(0, 0, QTableWidgetItem("Concrete (0.015)"))
        self.sheet_option_table.setItem(1, 0, QTableWidgetItem("Asphalt (0.016)"))
        self.sheet_option_table.setItem(2, 0, QTableWidgetItem("Fallow no Residue (0.05)"))
        self.sheet_option_table.setItem(3, 0, QTableWidgetItem("Cultivated Soil <20% Cover (0.06)"))
        self.sheet_option_table.setItem(4, 0, QTableWidgetItem("Cultivated Soil >20% Cover (0.17)"))
        self.sheet_option_table.setItem(5, 0, QTableWidgetItem("Short-Grass Prairie (0.15)"))
        self.sheet_option_table.setItem(6, 0, QTableWidgetItem("Dense Grasses (0.24)"))
        self.sheet_option_table.setItem(7, 0, QTableWidgetItem("Range (Natural) (0.13)"))
        self.sheet_option_table.setItem(8, 0, QTableWidgetItem("Woods, Light Underbrush (0.4)"))
        self.sheet_option_table.setItem(9, 0, QTableWidgetItem("Woods, Dense Underbrush (0.8)"))
        self.sheet_option_table.item(5, 0).setSelected(True)
        self.sheet_option_table.setParent(self.canvas)
        self.sheet_option_table.move(
            QPoint(
                (self.canvas.mouseLastXY().x() + 10),
                (self.canvas.mouseLastXY().y() + 10),
            )
        )
        self.r_provider = self.raster.dataProvider()
        start_val, start_res = self.r_provider.sample(self.start_xy, 1)
        end_val, end_res = self.r_provider.sample(self.end_xy, 1)
        if start_res is False or end_res is False:
            self.iface.messagebar().pushMessage("TC line outside raster boundary")
            self.deactivate()
        elif start_val == end_val:
            self.iface.messageBar().pushMessage("no slope along TC line")
            self.deactivate()
        elif end_val > start_val:
            vlayer = self.feature_list[0]
            vlayer.startEditing()
            nodes = self.feature_geom.asPolyline()
            nodes.reverse()
            new_geom = QgsGeometry.fromPolyline(nodes)
            vlayer.changeGeometry(self.feature.id(), new_geom)
            vlayer.commitChanges()
        else:
            pass

        self.start_point = nodes[0]
        self.end_point = nodes[-1]

        self.point_band.addPoint(self.start_point)

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
                if self.regime_option_table.isVisible is True:
                    pass
                elif self.sheet_option_table.isVisible is True:
                    pass
                else:
                    self.abandonedRequest.emit("Request Abandoned")
                    self.deactivate()
            case Qt.Key_Escape:
                self.abandonedRequest.emit("Request Abandoned")
                self.deactivate()

    def canvasPressEvent(self, e):
        if self.is_calculating is True:
            pass
        else:
            self.is_calculating = True
            self.point_band.addPoint(self.line_point)
            self.regime_option_table.show()

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
        self.regime_option_table.move(
            QPoint(
                e.pixelPoint().x() + 10,
                e.pixelPoint().y() + 10,
            )
        )
        self.sheet_option_table.move(
            QPoint(
                e.pixelPoint().x() + 10,
                e.pixelPoint().y() + 10,
            )
        )

    def handleUpArrow(self):
        if self.regime_option_table.isHidden is False:
            if self.regime_selected is None:
                self.regime_selected = 0
            else:
                raw_regime = self.regime_selected - 1
                if raw_regime < 0:
                    self.regime_selected = 3
                else:
                    self.regime_selected = raw_regime
            for i in range(4):
                self.regime_option_table.item(i, 0).setSelected(False)
            self.regime_option_table.item(self.regime_selected, 0).setSelected(True)
        elif self.sheet_option_table.isHidden is False:
            if self.cover_selected is None:
                self.cover_selected = 0
            else:
                raw_cover = self.cover_selected - 1
                if raw_cover < 0:
                    self.cover_selected = 3
                else:
                    self.cover_selected = raw_cover
            for i in range(4):
                self.sheet_option_table.item(i, 0).setSelected(False)
            self.sheet_option_table.item(self.cover_selected, 0).setSelected(True)
        else:
            pass

    def handleDownArrow(self):
        if self.regime_option_table.isHidden is False:
            if self.regime_selected is None:
                self.regime_selected = 0
            else:
                raw_regime = self.regime_selected + 1
                if raw_regime > 4:
                    self.regime_selected = 0
                else:
                    self.regime_selected = raw_regime
            for i in range(4):
                self.regime_option_table.item(i, 0).setSelected(False)
            self.regime_option_table.item(self.regime_selected, 0).setSelected(True)
        elif self.sheet_option_table.isHidden is False:
            if self.cover_selected is None:
                self.cover_selected = 0
            else:
                raw_cover = self.cover_selected + 1
                if raw_cover > 4:
                    self.cover_selected = 0
                else:
                    self.cover_selected = raw_cover
            for i in range(4):
                self.sheet_option_table.item(i, 0).setSelected(False)
            self.sheet_option_table.item(self.cover_selected, 0).setSelected(True)
        else:
            pass
