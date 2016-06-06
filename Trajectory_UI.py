# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *

class CreateTrajecory_Dialog(QtGui.QDialog):
  def __init__(self, iface, layerMenu):
    QtGui.QDialog.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint) 
    # Set up the user interface from Designer.
    self.ui = CreateTrajectory_UI()
    self.ui.setupUi(self, iface, layerMenu)

class CreateTrajectory_UI(object):

  def setupUi(self, Object, iface, layerMenu):
    Object.setObjectName("trajectory")
    Object.resize(300, 0)
    Object.setMaximumSize(300, 0)
    Object.setMinimumSize(300, 0)

    self.buttonBox = QtGui.QDialogButtonBox(Object)
    self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
    self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
    self.buttonBox.setObjectName("buttonBox")

    self.layout = QtGui.QFormLayout()

    self.labelComboBox = QtGui.QLabel()
    Str = "Sélectionnez un vol"
    self.labelComboBox.setText(Str.decode('utf-8'))

    flightPlans = []
    layerIds = layerMenu.findLayerIds()
    for layerId in layerIds:
        layer = layerMenu.findLayer(layerId)
        if layer.layerName()[:11] == "flightPlan_":
            flightPlans.append(layer.layerName()[11:])

    self.comboBox = QtGui.QComboBox()
    self.comboBox.addItems(flightPlans)

    self.labelEdit = QtGui.QLabel()
    Str = "Entrez une intervalle de distance de calcul (m)"
    self.labelEdit.setText(Str.decode('utf-8'))

    self.edit = QtGui.QLineEdit("1")

    self.layout.addRow(self.labelComboBox)
    self.layout.addRow(self.comboBox)
    self.layout.addRow(self.labelEdit)
    self.layout.addRow(self.edit)
    self.layout.addRow(self.buttonBox)
    Object.setLayout(self.layout)

    self.retranslateUi(Object)
    QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Object.accept)
    QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Object.reject)
    QtCore.QMetaObject.connectSlotsByName(Object)
    self.comboBox.setFocus()

  def retranslateUi(self, Object):
    Object.setWindowTitle(QtGui.QApplication.translate("Creation d'une trajectoire", "Creation d'une trajectoire", None, QtGui.QApplication.UnicodeUTF8))

