import pytest
from qgis.core import QgsApplication, QgsProviderRegistry
from qgis.utils import iface

@pytest.fixture(scope='session')
def qgis_app():
    QgsApplication.setPrefixPath('C:\\Program Files\\QGIS 3.40.0\\bin', True)
    qgs_app = QgsApplication([], False)
    qgs_app.initQgis()
    yield qgs_app
    qgs_app.exitQgis()
