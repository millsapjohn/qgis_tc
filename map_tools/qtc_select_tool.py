from qgis.gui import QgsMapTool
from qgis.PyQt.QtGui import QCursor
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsRectangle,
    QgsGeometry,
    Qgis,
    QgsLineString
)


class QTCSelectTool(QgsMapTool):
    completedRequest = pyqtSignal(list)
    abandonedRequest = pyqtSignal(str)

    def __init__(self, canvas, iface):
        self.canvas = canvas
        self.iface = iface
        QgsMapTool.__init__(self, self.canvas)
        self.selfeature = []

    def activate(self):
        self.iface.messageBar().pushMessage("Select TC Polyline:", duration=0)
        self.press_success = False
        self.cursor = QCursor()
        self.cursor.setShape(Qt.ArrowCursor)
        self.setCursor(self.cursor)
        self.order = QgsProject.instance().layerTreeRoot().layerOrder()
        self.line_layers = []
        self.getLineLayers()

    def on_map_tool_set(self, new_tool, old_tool):
        if new_tool == self:
            pass
        else:
            self.reset()

    def reset(self):
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage("Select TC Polyline:", duration=0)

    def deactivate(self):
        self.completedRequest.emit("task complete")
        self.iface.messageBar().clearWidgets()
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
        sel_rect = QgsRectangle(
            (e.mapPoint().x() - 5),
            (e.mapPoint().y() - 5),
            (e.mapPoint().x() + 5),
            (e.mapPoint().y() + 5)
        )
        sel_geom = QgsGeometry.fromRect(sel_rect)
        sel_engine = QgsGeometry.createGeometryEngine(sel_geom.constGet())
        sel_engine.prepareGeometry()
        selected = []
        for layer in self.order:
            if selected != []:
                break
            if layer.source() not in self.line_layers:
                continue
            else:
                for feature in layer.getFeatures():
                    if selected != []:
                        break
                    geom = feature.geometry()
                    if sel_engine.intersects(geom.constGet()):
                        layer.selectByIds(
                            [feature.id()],
                            Qgis.SelectBehavior.SetSelection
                        )
                        selected = [layer, feature.id()]
        if selected != []:
            self.selfeature = selected
            self.completedRequest.emit(selected)
        else:
            pass

    def getLineLayers(self):
        for layer in QgsProject.instance().layerTreeRoot().findLayers():
            if layer.isVisible() and isinstance(layer.layer(), QgsVectorLayer):
                if layer.layer().geometryType() == Qgis.GeometryType.Line:
                    self.line_layers.append(layer.layer().source())
