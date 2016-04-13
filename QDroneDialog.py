from PyQt4 import QtCore, QtGui 
from Ui_QDrone import Ui_QDrone
# create the dialog for QDrone
class QDroneDialog(QtGui.QDialog):
  def __init__(self): 
    QtGui.QDialog.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint) 
    # Set up the user interface from Designer. 
    self.ui = Ui_QDrone ()
    self.ui.setupUi(self)