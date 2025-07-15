from qgis.utils import iface
from .launch_dialog import LaunchDialog
try:
    from qgis.PyQt.QtWidgets import QAction
except ImportError:
    from qgis.PyQt.QtGui import QAction
from qgis.PyQt.QtGuil import QIcon

plugin_icon = QIcon(':/images/themes/default/mIconFieldTime.svg')


class QTCPlugin:
    def __init__(self, iface):
        super().__init__()
        self.iface = iface

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
