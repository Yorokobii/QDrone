#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from Datas import *

class Population():
  def __init__(self, flight, iface):
    self.flight = flight
    self.iface = iface
    self.widget = QWidget()
    self.progressBar = QProgressBar()
    self.label = QLabel()
    self.label.setText("Calcul de densite.")
    self.cancel = QPushButton("Cancel")
    self.cancel.clicked.connect(self.killThread)
    self.layout = QHBoxLayout()
    self.layout.addWidget(self.label)
    self.layout.addWidget(self.progressBar)
    self.layout.addWidget(self.cancel)
    self.widget.setLayout(self.layout)
    self.running = False
    self.prepareDlg = QMessageBox()
    self.prepareDlg.setStandardButtons(QMessageBox.NoButton)
    Str = "Préparation du calcul."
    self.prepareDlg.setText(Str.decode('utf-8'))

  def start(self):
    self.thread = PThread(self.flight, self.iface)
    QObject.connect( self.thread, SIGNAL( "setProgressBar" ), self.setProgressBar )
    QObject.connect( self.thread, SIGNAL( "ProgressValue" ), self.ProgressValue )
    QObject.connect( self.thread, SIGNAL( "result" ), self.result )
    QObject.connect( self.thread, SIGNAL( "exitThread" ), self.exitThread )
    self.thread.start()
    self.running = True
    self.prepareDlg.exec_()


  def setProgressBar(self, maxi):
    if self.running == True:
      self.prepareDlg.accept()
      self.progressBar.setMaximum(maxi)

  def ProgressValue(self, value):
    if self.running == True:
      self.progressBar.setValue(value)

  def result(self, ret):
    if self.running == True:
      dlg = QMessageBox()
      dlg.setText(ret.decode('utf-8'))
      dlg.exec_()

  def killThread(self):
    if self.running == True:
      self.iface.messageBar().clearWidgets()
      self.running = False

  def exitThread(self):
    if self.running == True:
      self.thread.exit(0)
      self.iface.messageBar().clearWidgets()
      self.running = False


class PThread(QThread):

  def __init__(self, flight, iface):
    QThread.__init__(self, iface.mainWindow())
    self.flight = flight
    self.iface = iface

  def run(self):
    #Load existing layers
    error = "Unexpected RuntimeError"
    try:

      error = PopulationCheck(self.iface)
      if error != True:
        raise RuntimeError(error)
      else:
        error = "Unexpected RuntimeError"

      densLayer=(QgsMapLayerRegistry.instance().mapLayersByName("Population"))[0]
      impactLayer=(QgsMapLayerRegistry.instance().mapLayersByName("multiImpactAreas_"+self.flight))[0]

      ProgressRequest = QgsFeatureRequest()
      totalsurface = 0.0
      for feature in (QgsMapLayerRegistry.instance().mapLayersByName("impactAreas_"+self.flight))[0].getFeatures():
        ProgressRequest.setFilterRect(feature.geometry().boundingBox())
        totalsurface = feature.geometry().area()/1000

      #Update population Field
      densFeatures=densLayer.getFeatures()
      buffFeatures=impactLayer.getFeatures()

      #recupere le maximum de la progress bar et l'envoi
      densCount = 0
      for feature in (QgsMapLayerRegistry.instance().mapLayersByName("impactAreas_"+self.flight))[0].getFeatures():
        for f in densLayer.getFeatures(ProgressRequest):
          if feature.geometry().intersects(f.geometry()):
            densCount = densCount + 1
      self.emit( SIGNAL("setProgressBar"), densCount )
      #########################

      #calcul de la densité de population
      totalPopulation=0.0
      progress = 0
      for impactZone in buffFeatures:
        request=QgsFeatureRequest()
        request.setFilterRect(impactZone.geometry().boundingBox())

        for f in densLayer.getFeatures(request):
          progress = progress + 1
          self.emit( SIGNAL("ProgressValue"), progress )
          if impactZone.geometry().intersects(f.geometry()):
            population=f.attribute("c_ind_c")
            totalPopulation=totalPopulation+population

      if (totalsurface==0.0 or totalPopulation==0.0):
        densite=0.0
        ret = "Pas d'intersection"
      else:
        densite=totalPopulation/totalsurface
        ret = "La densitée de population moyenne est de : %0.0f Hab/km²"%densite
      self.emit( SIGNAL("result"), ret )
      #####################################
    except RuntimeError:
      self.emit( SIGNAL("result"), error )

    self.emit( SIGNAL("exitThread"), "OK" )



class Topographie():
  def __init__(self, flight, iface):
    self.flight = flight
    self.iface = iface
    self.widget = QWidget()
    self.progressBar = QProgressBar()
    self.label = QLabel()
    self.label.setText("Calcul de densite.")
    self.cancel = QPushButton("Cancel")
    self.cancel.clicked.connect(self.killThread)
    self.layout = QHBoxLayout()
    self.layout.addWidget(self.label)
    self.layout.addWidget(self.progressBar)
    self.layout.addWidget(self.cancel)
    self.widget.setLayout(self.layout)
    self.running = False

  def start(self):
    self.thread = TThread(self.flight, self.iface)
    QObject.connect( self.thread, SIGNAL( "setProgressBar" ), self.setProgressBar )
    QObject.connect( self.thread, SIGNAL( "ProgressValue" ), self.ProgressValue )
    QObject.connect( self.thread, SIGNAL( "result" ), self.result )
    QObject.connect( self.thread, SIGNAL( "exitThread" ), self.exitThread )
    self.thread.start()
    self.running = True

  def setProgressBar(self, maxi):
    if self.running == True:
      self.progressBar.setMaximum(maxi)

  def ProgressValue(self, value):
    if self.running == True:
      self.progressBar.setValue(value)

  def result(self, ret):
    if self.running == True:
      dlg = QMessageBox()
      dlg.setText(ret.decode('utf-8'))
      dlg.exec_()

  def killThread(self):
    if self.running == True:
      self.iface.messageBar().clearWidgets()
      self.running = False

  def exitThread(self):
    if self.running == True:
      self.thread.exit(0)
      self.iface.messageBar().clearWidgets()
      self.running = False


class TThread(QThread):

  def __init__(self, flight, iface):
    QThread.__init__(self, iface.mainWindow())
    self.flight = flight
    self.iface = iface

  def run(self):
    #Load existing layers
    error = "Unexpected RuntimeError"
    try:

      error = TopoCheck(self.iface)
      if error != True:
        raise RuntimeError(error)
      else:
        error = "Unexpected RuntimeError"

    #calcul densité des sites d'activités
    #####################################

    except RuntimeError:
      self.emit( SIGNAL("result"), error )

    self.emit( SIGNAL("exitThread"), "OK" )