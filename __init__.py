from .qtc import QTCPlugin

def classFactory(iface):
    return QTCPlugin(iface)
