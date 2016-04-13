#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from PyQt4.QtGui import QAction, QMainWindow
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from QDroneDialog import QDroneDialog
from ParametersDialog import ParametersDialog
from SessionsDialog import SessionsDialog
from FlightPlan import FlightPlan

class QDrone:

  pdv_count = 0
  session = "NOSESSION"
  pdv_list = []

############################################## INITIALISATIONS ##########################################

  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface

    self.dlg_QDrone = QDroneDialog();
    self.dlg_parameters = ParametersDialog();
    self.dlg_session = SessionsDialog();

    self.dlg_session.ui.deco_btn.clicked.connect(self.disconnect_session)
    self.dlg_session.ui.del_button.clicked.connect(self.delete_session)

    # Set the project's default SCR Projection
    self.iface.mapCanvas().setMapUnits(0)
    self.iface.mapCanvas().refresh()
    self.s = QSettings()
    self.s.setValue( "/Projections/defaultBehaviour", "useProject" )

  def __del__(self):
    for layer in QgsMapLayerRegistry.instance().mapLayers().values():
      if layer.name().find("flightPlan") != -1:
        QgsMapLayerRegistry.instance().removeMapLayer( layer.id() )

  def initGui(self):

    self.menu = QMenu()
    self.menu.setTitle("QDrone")
    self.pdv_menu = self.menu.addMenu("&Plan de vol")
    self.trj_menu = self.menu.addMenu("&Trajectoire")
    Str = "&Zones de retombées"
    self.zdr_menu = self.menu.addMenu(Str.decode('utf-8'))

    self.session_btn = QAction("&Session", self.iface.mainWindow())
    self.menu.addAction(self.session_btn)
    self.iface.addToolBarIcon(self.session_btn)
    QObject.connect(self.session_btn, SIGNAL("activated()"), self.run_session)

    Str = "Paramètres"
    self.parameters_btn = QAction(Str.decode('utf-8'), self.iface.mainWindow())
    self.menu.addAction(self.parameters_btn)
    QObject.connect(self.parameters_btn, SIGNAL("activated()"), self.run_parameters)

    ######sous actions

    ###plan de vol
    self.create_pdv_btn = QAction("&Nouveau", self.iface.mainWindow())
    self.pdv_menu.addAction(self.create_pdv_btn)
    QObject.connect(self.create_pdv_btn, SIGNAL("activated()"), self.create_pdv)

    self.pdv_menu.addSeparator()

    self.import_pdv_btn = QAction("&Importer", self.iface.mainWindow())
    self.pdv_menu.addAction(self.import_pdv_btn)

    self.export_pdv_btn = QAction("&Exporter", self.iface.mainWindow())
    self.pdv_menu.addAction(self.export_pdv_btn)

    ###trajectoire
    self.create_traj_btn = QAction("&Calculer", self.iface.mainWindow())
    self.trj_menu.addAction(self.create_traj_btn)

    self.trj_menu.addSeparator()

    self.export_traj_btn = QAction("&Exporter", self.iface.mainWindow())
    self.trj_menu.addAction(self.export_traj_btn)

    ###zones de retombées
    self.create_zdr_btn = QAction("&Calculer", self.iface.mainWindow())
    self.zdr_menu.addAction(self.create_zdr_btn)

    menuBar = self.iface.mainWindow().menuBar()
    menuBar.addMenu(self.menu)

  #####unload fonction

  def unload(self):
    # Remove the plugin menu item and icon
    self.iface.removeToolBarIcon(self.session_btn)

############################################## FONCTIONS LIEE A LA CREATION DES PDV ##########################################

  def create_pdv(self):
    if self.session != "NOSESSION":
      directory = QDir(QDir.currentPath())
      directory.cdUp()
      directory.cd("apps\qgis\python\plugins\QDrone\sessions\\"+self.session)
      list_shp = directory.entryList(QDir.Files)
      del directory

      self.pdv_count = 0
      for i in range(len(list_shp)):
        if list_shp[i].find("flightPlan") != -1 and list_shp[i].find(".shp") != -1:
          self.pdv_count = self.pdv_count + 1

      pdv = FlightPlan(self.iface, self.pdv_count, self.session)
      self.pdv_list.append(pdv)

    else:
      popup = QMessageBox()
      Str = "Vous devez être connecté a une session."
      popup.setText(Str.decode('utf-8'))
      popup.exec_()
      self.run_session()

  def load_pdv(self, path):
    if self.session != "NOSESSION":
      directory = QDir(QDir.currentPath())
      directory.cdUp()
      directory.cd("apps\qgis\python\plugins\QDrone\sessions\\"+self.session)
      list_shp = directory.entryList(QDir.Files)
      del directory

      self.pdv_count = 0
      for i in range(len(list_shp)):
        if list_shp[i].find("flightPlan") != -1 and list_shp[i].find(".shp") != -1:
          self.pdv_count = self.pdv_count + 1

      pdv = FlightPlan(self.iface, self.pdv_count, self.session, path)
      self.pdv_list.append(pdv)

    else:
      popup = QMessageBox()
      Str = "Vous devez être connecté a une session."
      popup.setText(Str.decode('utf-8'))
      popup.exec_()
      self.run_session()


############################################## FONCTIONS LIEE AU PARAMETRES ##########################################

  def run_parameters(self):
    if self.session != "NOSESSION":
      # show the dialog
      self.dlg_parameters.show()
      result = self.dlg_parameters.exec_()
      # See if OK was pressed
      if result == 1:
        # do something useful (delete the line containing pass and
        # substitute with your code
        pass 
    else:
      popup = QMessageBox()
      Str = "Vous devez être connecté a une session."
      popup.setText(Str.decode('utf-8'))
      popup.exec_()
      self.run_session()

############################################## FONCTIONS LIEE AU SESSIONS ##########################################

  def run_session(self):
    # show the dialog
    self.dlg_session.ui.input.setText("")
    self.dlg_session.ui.refreshComboBox()
    if self.session != "NOSESSION":
      self.dlg_session.ui.comboBox.setCurrentIndex(self.dlg_session.ui.comboBox.findText(self.session))
    else:
      self.dlg_session.ui.comboBox.setCurrentIndex(0)
    self.dlg_session.show()
    result = self.dlg_session.exec_()
    # See if OK was pressed
    if result == 1:
      # do something useful (delete the line containing pass and
      # substitute with your code
      if self.dlg_session.ui.comboBox.currentText() == "Nouvelle session":
        session_name = self.dlg_session.ui.input.text()
        directory = QDir(QDir.currentPath())
        directory.cdUp()
        directory.cd("apps\qgis\python\plugins\QDrone\sessions")
        if session_name != "" and session_name != "Nouvelle session":
          if self.dlg_session.ui.new_session(session_name) == False:
            if directory.exists(session_name):
              self.session = session_name
              self.open_session(session_name)
              popup = QMessageBox()
              Str = "La session " + session_name.encode('utf-8') + " déjà existante a été ouverte."
              popup.setText(Str.decode('utf-8'))
              popup.exec_()
            else:
              self.session = "NOSESSION"
              popup = QMessageBox()
              Str = "Nom de la session non autorisé ou droits d'administrateur requis sur le dossier destination."
              popup.setText(Str.decode('utf-8'))
              popup.exec_()
              self.run_session()
          else:
            self.session = session_name
            self.open_session(session_name)
            popup = QMessageBox()
            Str = "La session " + session_name.encode('utf-8') + " a été créé et ouverte."
            popup.setText(Str.decode('utf-8'))
            popup.exec_()

        else:
          self.session = "NOSESSION"
          popup = QMessageBox()
          popup.setText("Nom de la session incorrect (\"Nouvelle session\" ou \"\" ).")
          popup.exec_()
          self.run_session()
        del directory
      else:
        if self.session != self.dlg_session.ui.comboBox.currentText():
          self.session = self.dlg_session.ui.comboBox.currentText()
          self.open_session(self.dlg_session.ui.comboBox.currentText())
          popup = QMessageBox()
          session_name_msg = "La session " + self.dlg_session.ui.comboBox.currentText().encode('utf-8') + " a été ouverte."
          popup.setText(session_name_msg.decode('utf-8'))
          popup.exec_()
        else:
          popup = QMessageBox()
          session_name_msg = "La session " + self.dlg_session.ui.comboBox.currentText().encode('utf-8') + " est déjà ouverte."
          popup.setText(session_name_msg.decode('utf-8'))
          popup.exec_()


  def open_session(self, name):
    #clear le Layer menu
    for layer in QgsMapLayerRegistry.instance().mapLayers().values():
      if layer.name().find("flightPlan") != -1:
        QgsMapLayerRegistry.instance().removeMapLayer( layer.id() )

    #charger les pdv presents dans la session
    directory = QDir(QDir.currentPath())
    directory.cdUp()
    directory.cd("apps\qgis\python\plugins\QDrone\sessions\\"+self.session)

    list_shp = directory.entryList(QDir.Files)
    path = directory.path()
    del directory

    for i in range(len(list_shp)):
      if list_shp[i].find("flightPlan") != -1 and list_shp[i].find(".shp") != -1:
        self.pdv = FlightPlan(self.iface, self.pdv_count, self.session, path + "\\" + list_shp[i], list_shp[i])
        self.pdv_list.append(self.pdv)


  def disconnect_session(self):
    if self.session != "NOSESSION":
      self.session = "NOSESSION"
      self.dlg_session.ui.refreshComboBox()
      for layer in QgsMapLayerRegistry.instance().mapLayers().values():
        if layer.name().find("flightPlan") != -1:
          QgsMapLayerRegistry.instance().removeMapLayer( layer.id() )
      self.dlg_session.ui.objet_sessions.reject()

  def delete_session(self):
    self.session = "NOSESSION"
    self.pdv_list = []
    self.dlg_session.ui.refreshComboBox()

##############################################  ##########################################