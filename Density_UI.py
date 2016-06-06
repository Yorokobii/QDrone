# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *

class CalculateDensity_Dialog(QtGui.QDialog):
  def __init__(self):
    QtGui.QDialog.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint) 
    # Set up the user interface from Designer.
    self.ui = CalculateDensity_UI()
    self.ui.setupUi(self)

class CalculateDensity_UI(object):

  def setupUi(self, Object):
    Object.setObjectName("Density")
    Object.resize(400, 0)
    Object.setMaximumSize(400, 0)
    Object.setMinimumSize(400, 0)

    self.buttonBox = QtGui.QDialogButtonBox(Object)
    self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
    self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
    self.buttonBox.setObjectName("buttonBox")

    self.layout = QtGui.QFormLayout()

    #################### comboBox Population ou Topo
    self.labelComboBoxType = QtGui.QLabel()
    Str = "Sélectionnez le type de densitée à calculer"
    self.labelComboBoxType.setText(Str.decode('utf-8'))

    self.comboBoxType = QtGui.QComboBox()
    Types = ["Population", "Topographique"]
    self.comboBoxType.addItems(Types)
    ####################

    #################### comboBox pdv
    self.labelComboBoxPdv = QtGui.QLabel()
    Str = "Sélectionnez un vol"
    self.labelComboBoxPdv.setText(Str.decode('utf-8'))

    flightPlans = []
    layerMenu = QgsProject.instance().layerTreeRoot()
    layerIds = layerMenu.findLayerIds()
    for layerId in layerIds:
      layer = layerMenu.findLayer(layerId)
      if layer.layerName()[:11] == "flightPlan_":
        flightPlans.append(layer.layerName()[11:])

    self.comboBoxPdv = QtGui.QComboBox()
    self.comboBoxPdv.addItems(flightPlans)
    ####################

    self.layout.addRow(self.labelComboBoxType)
    self.layout.addRow(self.comboBoxType)
    self.layout.addRow(self.labelComboBoxPdv)
    self.layout.addRow(self.comboBoxPdv)
    self.layout.addRow(self.buttonBox)
    Object.setLayout(self.layout)

    self.retranslateDensityUi(Object)
    QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Object.accept)
    QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Object.reject)
    QtCore.QMetaObject.connectSlotsByName(Object)

  def retranslateDensityUi(self, Object):
    Object.setWindowTitle(QtGui.QApplication.translate("Calcul d'une densitée", "Calcul d'une densitée", None, QtGui.QApplication.UnicodeUTF8))

class Topo_Dialog(QtGui.QDialog):
  def __init__(self):
    QtGui.QDialog.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint) 
    # Set up the user interface from Designer.
    self.ui = Topo_UI()
    self.ui.setupUi(self)

class Topo_UI(object):

  def setupUi(self, Object):
    Object.setObjectName("Topographie")
    Object.resize(400, 0)
    Object.setMaximumSize(400, 0)
    Object.setMinimumSize(400, 0)

    self.buttonBox = QtGui.QDialogButtonBox(Object)
    self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
    self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
    self.buttonBox.setObjectName("buttonBox")

    self.layout = QtGui.QFormLayout()

    #################### checkBoxes types de sites d'activité
    self.label = QtGui.QLabel()
    Str = "Sélectionnez les types de sites d'activités à utiliser"
    self.label.setText(Str.decode('utf-8'))


    self.layout1 = QtGui.QHBoxLayout()
    Str = "établissements scolaires"
    self.schools = QtGui.QCheckBox(Str.decode('utf-8'))
    self.schools.setCheckState(2)
    self.layout1.addWidget(self.schools)
    Str = "sites religieux"
    self.religious = QtGui.QCheckBox(Str.decode('utf-8'))
    self.religious.setCheckState(2)
    self.layout1.addWidget(self.religious)

    self.layout2 = QtGui.QHBoxLayout()
    Str = "sites funéraires"
    self.funerary = QtGui.QCheckBox(Str.decode('utf-8'))
    self.funerary.setCheckState(2)
    self.layout2.addWidget(self.funerary)
    Str = "sites industriels"
    self.indutries = QtGui.QCheckBox(Str.decode('utf-8'))
    self.indutries.setCheckState(2)
    self.layout2.addWidget(self.indutries)

    self.layout3 = QtGui.QHBoxLayout()
    Str = "centres commerciaux"
    self.commercials = QtGui.QCheckBox(Str.decode('utf-8'))
    self.commercials.setCheckState(2)
    self.layout3.addWidget(self.commercials)
    ####################

    self.layout.addRow(self.label)    
    self.layout.addRow(self.layout1)
    self.layout.addRow(self.layout2)
    self.layout.addRow(self.layout3)
    self.layout.addRow(self.buttonBox)
    Object.setLayout(self.layout)

    self.retranslateTopoUi(Object)
    QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Object.accept)
    QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Object.reject)
    QtCore.QMetaObject.connectSlotsByName(Object)

  def retranslateTopoUi(self, Object):
    Object.setWindowTitle(QtGui.QApplication.translate("Details donnees Topo", "Details donnees Topo", None, QtGui.QApplication.UnicodeUTF8))
