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

        self.radio_label = QLabel('Calculate TC for:')
        self.layer_button = QRadioButton('Entire Layer')
        self.layer_button.setChecked(True)
        self.feature_button = QRadioButton('Single Feature')
        self.layer_box = QgsMapLayerComboBox()
        self.layer_box.setFilters(Qgis.LayerFilter.LineLayer)
        self.select_button = QPushButton(icon=select_icon, text='Select Feature')
        self.select_button.setDisabled(True)
        self.feature_button.toggled.connect(self.setFeatureVisibility)
        self.radio_layout = QHBoxLayout()
        self.radio_layout.addWidget(self.layer_button)
        self.radio_layout.addWidget(self.feature_button)
        self.layout.addLayout(self.radio_layout)
        self.layer_layout = QHBoxLayout()
        self.layer_layout.addWidget(self.layer_box)
        self.layer_layout.addWidget(self.select_button)
        self.layout.addLayout(self.layer_layout)

        self.name_label = QLabel('Subbasin Name:')
        self.name_box = QLineEdit()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_box)

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

    def setFeatureVisibility(self):
        if self.select_button.isEnabled() is True:
            self.select_button.setDisabled(True)
            self.layer_box.setEnabled(True)
        else:
            self.select_button.setEnabled(True)
            self.layer_box.setDisabled(True)

    def setSaveVisibility(self, state):
        enabled = state == 2
        self.save_file_box.setEnabled(enabled)
        self.save_file_button.setEnabled(enabled)
