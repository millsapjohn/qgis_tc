from qgis.utils import iface
from .launch_dialog import LaunchDialog
try:
    from qgis.PyQt.QtWidgets import QAction
except ImportError:
    from qgis.PyQt.QtGui import QAction
from qgis.PyQt.QtGui import QIcon
from .map_tools.qtc_select_tool import QTCSelectTool

plugin_icon = QIcon(':/images/themes/default/mIconFieldTime.svg')


class QTCPlugin:
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.valid = True

    def initGui(self):
        self.launchAction = QAction(plugin_icon, 'Calculate TC')
        self.iface.addPluginToMenu('Time of Concentration', self.launchAction)
        self.launchAction.triggered.connect(self.launch)

    def unload(self):
        self.iface.removePluginMenu('Time of Concentration', self.launchAction)
        self.launchAction.deleteLater()

    def launch(self):
        self.dlg = LaunchDialog()
        self.dlg.exec()
        if self.dlg.success is True:
            self.getVariables()
            if self.valid:
                self.runSelectTool()

    def getVariables(self):
        self.raster = self.dlg.raster
        self.rain = self.dlg.rain
        self.min_slope = self.dlg.min_slope
        self.min_time = self.dlg.min_time
        if self.dlg.save_intended is True:
            self.save_file = self.dlg.save_file
            if self.save_file is None or self.save_file == "Save File Location:":
                self.valid = False
                self.iface.messageBar().pushMessage("No Save File Specified")

    def runSelectTool(self):
        self.select_tool = QTCSelectTool(self.iface.mapCanvas(), self.iface, self.raster)
        self.iface.mapCanvas().setMapTool(self.select_tool)
