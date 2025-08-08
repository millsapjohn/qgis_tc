from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QCheckBox,
    QLineEdit,
    QDoubleSpinBox,
    QRadioButton,
)
from qgis.PyQt.QtGui import QIcon
from qgis.gui import (
    QgsMapLayerComboBox,
)
from qgis.core import Qgis
from qgis.utils import iface

select_icon = QIcon(':/images/themes/default/mActionSelectRectangle.svg')


class LaunchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.iface = iface
        self.success = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ToC Options')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.raster_label = QLabel('Raster Layer')
        self.raster_box = QgsMapLayerComboBox()
        self.raster_box.setFilters(Qgis.LayerFilter.RasterLayer)
        self.layout.addWidget(self.raster_label)
        self.layout.addWidget(self.raster_box)

        self.rain_label = QLabel('2yr, 24hr Rainfall:')
        self.rain_box = QDoubleSpinBox()
        self.rain_box.setDecimals(2)
        self.rain_box.setMinimum(0.00)
        self.rain_box.setSuffix(' in')
        self.rain_box.setValue(4.14)
        self.layout.addWidget(self.rain_label)
        self.layout.addWidget(self.rain_box)
        
        self.slope_label = QLabel('Minimum Slope:')
        self.slope_box = QDoubleSpinBox()
        self.slope_box.setDecimals(3)
        self.slope_box.setMinimum(0.000)
        self.slope_box.setSuffix(' ft/ft')
        self.slope_box.setValue(0.005)
        self.layout.addWidget(self.slope_label)
        self.layout.addWidget(self.slope_box)
        
        self.min_time_label = QLabel('Minimum Total Time of Concentration:')
        self.min_time_box = QDoubleSpinBox()
        self.min_time_box.setDecimals(2)
        self.min_time_box.setMinimum(0.00)
        self.min_time_box.setSuffix(' min')
        self.min_time_box.setValue(5.00)
        self.layout.addWidget(self.min_time_label)
        self.layout.addWidget(self.min_time_box)

        self.save_file_checkbox = QCheckBox('Save Results to File?')
        self.layout.addWidget(self.save_file_checkbox)
        try:
            self.save_file_checkbox.checkStateChanged.connect(self.setSaveVisibility)
        except AttributeError:
            self.save_file_checkbox.stateChanged.connect(self.setSaveVisibility)
        self.save_file_box = QLineEdit('Save File Location:')
        self.save_file_box.setDisabled(True)
        self.save_file_button = QPushButton(text='...')
        self.save_file_button.setDisabled(True)
        self.save_file_button.clicked.connect(self.getSaveFile)
        self.save_file_layout = QHBoxLayout()
        self.save_file_layout.addWidget(self.save_file_box)
        self.save_file_layout.addWidget(self.save_file_button)
        self.layout.addLayout(self.save_file_layout)

        self.ok_button = QPushButton(text='Ok')
        self.ok_button.clicked.connect(self.getValues)
        self.cancel_button = QPushButton(text='Cancel')
        self.cancel_button.clicked.connect(self.close)
        self.ok_layout = QHBoxLayout()
        self.ok_layout.addWidget(self.ok_button)
        self.ok_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.ok_layout)

    def getSaveFile(self):
        self.fn_dialog = QFileDialog()
        self.filename = self.fn_dialog.getSaveFileName(self, 'Specify Save Location:', '', 'Text File (*.txt)')[0]
        self.save_file_box.setText(self.filename)

    def getValues(self):
        self.success = True
        if self.save_file_checkbox.isChecked() is True:
            self.save_intended = True
        else:
            self.save_intended = False
        self.raster = self.raster_box.currentLayer()
        self.rain = self.rain_box.value()
        self.min_slope = self.slope_box.value()
        self.min_time = self.min_time_box.value()
        self.save_file = self.save_file_box.text()
        self.close()

    def setSaveVisibility(self, state):
        enabled = state == 2
        self.save_file_box.setEnabled(enabled)
        self.save_file_button.setEnabled(enabled)
