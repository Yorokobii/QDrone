# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *

class CreateFlightPlan_Dialog(QtGui.QDialog):
  def __init__(self):
    QtGui.QDialog.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint) 
    # Set up the user interface from Designer.
    self.ui = CreateFlightPlan_UI()
    self.ui.setupUi(self)

class CreateFlightPlan_UI(object):

  def setupUi(self, Object):
    Object.setObjectName("flightPlan")
    Object.resize(400, 0)
    Object.setMaximumSize(400, 0)
    Object.setMinimumSize(400, 0)

    self.buttonBox = QtGui.QDialogButtonBox(Object)
    self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
    self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
    self.buttonBox.setObjectName("buttonBox")

    self.layout = QtGui.QFormLayout()
    self.label = QtGui.QLabel()
    Str = "Entrez le nom du plan de vol"
    self.label.setText(Str.decode('utf-8'))
    self.edit = QtGui.QLineEdit()

    self.layout.addRow(self.label)
    self.layout.addRow(self.edit)
    self.layout.addRow(self.buttonBox)
    Object.setLayout(self.layout)

    self.retranslateUi(Object)
    QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Object.accept)
    QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Object.reject)
    QtCore.QMetaObject.connectSlotsByName(Object)
    self.edit.setFocus()

  def retranslateUi(self, Object):
    Object.setWindowTitle(QtGui.QApplication.translate("Creation d'un plan de vol", "Creation d'un plan de vol", None, QtGui.QApplication.UnicodeUTF8))

