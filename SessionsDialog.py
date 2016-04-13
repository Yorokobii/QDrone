from PyQt4 import QtCore, QtGui 
from Ui_Sessions import Ui_Sessions
# create the dialog for Sessions
class SessionsDialog(QtGui.QDialog):
  def __init__(self): 
    QtGui.QDialog.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint) 
    # Set up the user interface from Designer. 
    self.ui = Ui_Sessions ()
    self.ui.setupUi(self)