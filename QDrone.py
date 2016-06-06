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
from Datas import *
from FlightPlan import *
from FlightPlan_UI import *
from Trajectory_UI import *
from ImpactAreas_UI import *
from Density import *
from Density_UI import *

class QDrone:

  pdv_list = []
  initialized = False

############################################## INITIALISATIONS ##########################################

  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface
    self.iface.projectRead.connect(self.projectRead)#connecte le signal de lecture d'un projet
    self.iface.newProjectCreated.connect(self.unload)#connecte le signal de creation d'un nouveau projet
    #                                                 afin de reinitialiser QDrone

    # Set the project's default SCR Projection
    self.iface.mapCanvas().setMapUnits(0)
    self.iface.mapCanvas().refresh()
    self.s = QSettings()
    self.s.setValue( "/Projections/defaultBehaviour", "useProject" )
    self.project = QgsProject.instance()
    self.layerMenu = self.project.layerTreeRoot()

  ######fonction d'initialisation des items menu et icones
  def initGui(self):

    #Initialisation des items de menu
    self.menu = QMenu()
    self.menu.setTitle("QDrone")

    Str = "Initialiser QDrone"
    self.init_btn = QAction(Str.decode('utf-8'), self.iface.mainWindow())
    self.menu.addAction(self.init_btn)

    menuBar = self.iface.mainWindow().menuBar()
    menuBar.addMenu(self.menu)

    self.menu2 = QMenu()
    self.menu2.setTitle("QDrone")

    self.pdv_menu2 = self.menu2.addMenu("Vol")
    #############plan de vol
    self.createPdv_btn = QAction("Nouveau", self.iface.mainWindow())
    self.pdv_menu2.addAction(self.createPdv_btn)

    self.pdv_menu2.addSeparator()

    self.importPdv_btn = QAction("Importer", self.iface.mainWindow())
    self.pdv_menu2.addAction(self.importPdv_btn)
    ########################

    Str = "Calculer une trajectoire"
    self.trajectory_btn = QAction(Str.decode('utf-8'), self.iface.mainWindow())
    self.menu2.addAction(self.trajectory_btn)

    Str = "Calculer des zones de retombées"
    self.zdr_btn = QAction(Str.decode('utf-8'), self.iface.mainWindow())
    self.menu2.addAction(self.zdr_btn)

    Str = "Calcul de densités"
    self.density_btn = QAction(Str.decode('utf-8'), self.iface.mainWindow())
    self.menu2.addAction(self.density_btn)

    self.menu2.addSeparator()

    Str = "Visualisation verticale"
    self.verticalView_btn = QAction(Str.decode('utf-8'), self.iface.mainWindow())
    self.menu2.addAction(self.verticalView_btn)

    self.menu2.addSeparator()

    Str = "Altitude de sécurité"
    self.safetyAltitude_btn = QAction(Str.decode('utf-8'), self.iface.mainWindow())
    self.menu2.addAction(self.safetyAltitude_btn)

    Str = "Inter-visibilité"
    self.inter_visibility_btn = QAction(Str.decode('utf-8'), self.iface.mainWindow())
    self.menu2.addAction(self.inter_visibility_btn)

    self.menu2.addSeparator()

    Str = "Visualisation TR/TD"
    self.visualisation_TR_TD_btn = QAction(Str.decode('utf-8'), self.iface.mainWindow())
    self.menu2.addAction(self.visualisation_TR_TD_btn)

    self.menu2.addSeparator()

    Str = "Caractéristiques d'une zone"
    self.areaCaracteristics_btn = QAction(Str.decode('utf-8'), self.iface.mainWindow())
    self.menu2.addAction(self.areaCaracteristics_btn)

    self.menu2.addSeparator()

    self.loadMenu = self.menu2.addMenu("Charger...")
    #############Chargement de fichiers
    Str = "...Un vecteur aérien"
    self.loadVA_btn = QAction(Str.decode('utf-8'), self.iface.mainWindow())
    self.loadMenu.addAction(self.loadVA_btn)

    Str = "...Une météo"
    self.loadWeather_btn = QAction(Str.decode('utf-8'), self.iface.mainWindow())
    self.loadMenu.addAction(self.loadWeather_btn)

    Str = "...Des données de population"
    self.loadPopulation_btn = QAction(Str.decode('utf-8'), self.iface.mainWindow())
    self.loadMenu.addAction(self.loadPopulation_btn)

    Str = "...Des données topographiques"
    self.loadTopo_btn = QAction(Str.decode('utf-8'), self.iface.mainWindow())
    self.loadMenu.addAction(self.loadTopo_btn)
    ########################

    #Connection des signaux
    QObject.connect(self.init_btn, SIGNAL("activated()"), self.init)
    QObject.connect(self.createPdv_btn, SIGNAL("activated()"), self.run_createPdv)
    QObject.connect(self.importPdv_btn, SIGNAL("activated()"), self.run_importPdv)
    QObject.connect(self.trajectory_btn, SIGNAL("activated()"), self.run_trajectory)
    QObject.connect(self.zdr_btn, SIGNAL("activated()"), self.run_zdr)
    QObject.connect(self.density_btn, SIGNAL("activated()"), self.run_density)
    #QObject.connect(self.verticalView_btn, SIGNAL("activated()"), self.run_verticalView)
    #QObject.connect(self.safetyAltitude_btn, SIGNAL("activated()"), self.run_safetyAltitude)
    #QObject.connect(self.inter_visibility_btn, SIGNAL("activated()"), self.run_inter_visibility)
    #QObject.connect(self.visualisation_TR_TD_btn, SIGNAL("activated()"), self.run_visualisation_TR_TD)
    #QObject.connect(self.areaCaracteristics_btn, SIGNAL("activated()"), self.run_areaCaracteristics)
    QObject.connect(self.loadVA_btn, SIGNAL("activated()"), self.run_LoadVA)
    QObject.connect(self.loadWeather_btn, SIGNAL("activated()"), self.run_loadWeather)
    QObject.connect(self.loadPopulation_btn, SIGNAL("activated()"), self.run_loadPopulation)
    QObject.connect(self.loadTopo_btn, SIGNAL("activated()"), self.run_loadTopo)

    self.layerMenu.removedChildren.connect(self.removeFromPdvList)

  #####fonction appelé quand le plugin est quitte
  def unload(self):
    #si le plugin a ete initialise on enleve les icons de la barre d'icons
    if self.initialized == True:
      self.iface.removeToolBarIcon(self.newPdv_btn)
      self.iface.removeToolBarIcon(self.trajectory_btn)
      self.iface.removeToolBarIcon(self.zdr_btn)
      self.iface.removeToolBarIcon(self.density_btn)
      self.initGui()
      self.initialized = False

  #####fonction appelé quand un projet est chargé afin d'initialiser ou non QDrone'
  def projectRead(self):
    self.project = QgsProject.instance()
    if self.project.readBoolEntry("QDrone", "Qgs_Project", False)[0] == True:
      self.init()
    else:
      self.unload()
      self.initialized = False

  #####fonction pour initialiser les boutons et le menu de layers si le projet est un projet QDrone
  def init(self):
    if self.initialized == False:
      self.Folder = QDir(self.project.homePath())

      #si le setting initialized est a false on crée les couches et groupes dans le menu de layers
      if self.project.readBoolEntry("QDrone", "Qgs_Project", False)[0] == False:
        ####################dossiers du projet###################
        self.Folder.mkdir("QDrone")
        self.Folder.cd("QDrone")

        self.Folder.mkdir("Vols")
        self.Folder.cd("Vols")
        self.FolderFly = QDir(self.Folder.path())
        self.Folder.cdUp()

        Str = "Données"
        self.Folder.mkdir(Str.decode('utf-8'))
        self.Folder.cd(Str.decode('utf-8'))
        self.FolderDatas = QDir(self.Folder.path())
        self.Folder.cdUp()
        ############################################################################

        #######################################groupes######################################
        self.GroupQDrone = self.layerMenu.addGroup("QDrone")

        self.GroupFly = self.GroupQDrone.addGroup("Vols")
        self.GroupFly.setExpanded(False)

        Str = "Données"
        self.GroupDatas = self.GroupQDrone.addGroup(Str.decode('utf-8'))
        self.GroupDatas.setExpanded(False)
        self.GroupDatas.setVisible(False)
        ############################################################################

        ####################################### layers ######################################
        tempLayerRadio = QgsVectorLayer("Point", "Antennes radio", "memory") #création du layer en memoire
        tempLayerCollectionSites = QgsVectorLayer("Point", "Sites de recueil", "memory") #création du layer en memoire
        tempLayerAreas = QgsVectorLayer("Polygon", "Zones", "memory") #création du layer en memoire
        
        #ajout des fields
        tempLayerRadio.dataProvider().addAttributes([QgsField("altitude", QVariant.Double), QgsField("hauteur", QVariant.Double)])
        tempLayerRadio.updateFields()
        tempLayerCollectionSites.dataProvider().addAttributes([QgsField("altitude", QVariant.Double)])
        tempLayerCollectionSites.updateFields()
        tempLayerAreas.dataProvider().addAttributes([QgsField("alti min", QVariant.Double), QgsField("alti max", QVariant.Double), QgsField("type", QVariant.String)])
        tempLayerAreas.updateFields()

        QgsVectorFileWriter.writeAsVectorFormat(tempLayerRadio, self.FolderDatas.path()+"/Antennes radio.shp", "utf-8", None, "ESRI Shapefile")
        self.LayerRadio = QgsVectorLayer(self.FolderDatas.path()+"/Antennes radio.shp", "Antennes radio", "ogr")
        QgsVectorFileWriter.writeAsVectorFormat(tempLayerCollectionSites, self.FolderDatas.path()+"/Sites de recueil.shp", "utf-8", None, "ESRI Shapefile")
        self.LayerCollectionSites = QgsVectorLayer(self.FolderDatas.path()+"/Sites de recueil.shp", "Sites de recueil", "ogr")
        QgsVectorFileWriter.writeAsVectorFormat(tempLayerAreas, self.FolderDatas.path()+"/Zones.shp", "utf-8", None, "ESRI Shapefile")
        self.LayerAreas = QgsVectorLayer(self.FolderDatas.path()+"/Zones.shp", "Zones", "ogr")
        
        QgsMapLayerRegistry.instance().addMapLayer(self.LayerRadio) #ajout dans le menu de layers
        self.GroupQDrone.addLayer(self.LayerRadio) #clonage dans le groupe
        QgsMapLayerRegistry.instance().addMapLayer(self.LayerCollectionSites)
        self.GroupQDrone.addLayer(self.LayerCollectionSites)
        QgsMapLayerRegistry.instance().addMapLayer(self.LayerAreas)
        self.GroupQDrone.addLayer(self.LayerAreas)

        self.iface.mapCanvas().refreshAllLayers()
        ###############################################################################################

        ########suppression des layer en doubles###################
        self.layerMenu.removeLayer(self.LayerRadio)
        self.layerMenu.removeLayer(self.LayerCollectionSites)
        self.layerMenu.removeLayer(self.LayerAreas)
        #########################################################

        #efface les messages du a la creation des layers dans la barre de message Qgis
        self.iface.messageBar().clearWidgets()
   
      #sinon on récupère les groupes et layers fixes dans des variables
      else:
        #######################################dossier du projet######################################
        self.Folder.cd("QDrone")

        self.Folder.cd("Vols")
        self.FolderFly = QDir(self.Folder.path())
        self.Folder.cdUp()

        Str = "Données"
        self.Folder.cd(Str.decode('utf-8'))
        self.FolderDatas = QDir(self.Folder.path())
        self.Folder.cdUp()
        ###############################################################################################

        #######################################groupes#########################################################
        
        self.GroupQDrone = self.layerMenu.findGroup("QDrone")

        self.GroupFly = self.GroupQDrone.findGroup("Vols")

        Str = "Données"
        self.GroupDatas = self.GroupQDrone.findGroup(Str.decode('utf-8'))
        ###############################################################################################

        #######################################layers#########################################################

        ##instancie les pdv
        pdvLayers = self.GroupFly.findLayers()
        for i in range(len(pdvLayers)):
          if pdvLayers[i].layerName()[:10] == "flightPlan":
            #recupère le layer du plan de vol
            layer = pdvLayers[i].layer()
            #recupère le layer vue en lignes du plan de vol
            layer_lineView = QgsMapLayerRegistry.instance().mapLayersByName("lineView_" + layer.name()[11:])[0]
            #recupère le layer de la trajectoire liée au plan de vol si elle existe
            layer_trajectory = QgsMapLayerRegistry.instance().mapLayersByName("lineTraj_" + layer.name()[11:])
            if layer_trajectory != []:
              layer_trajectory = layer_trajectory[0]
            else:
              layer_trajectory = None
            #recupère le layer des points de la trajectoire
            layer_pointsTraj = QgsMapLayerRegistry.instance().mapLayersByName("trajectory_" + layer.name()[11:])
            if layer_pointsTraj != []:
              layer_pointsTraj = layer_pointsTraj[0]
            else:
              layer_pointsTraj = None
            #recupère le layer de zone de retombées si il existe
            layer_impactArea = QgsMapLayerRegistry.instance().mapLayersByName("impactArea_" + layer.name()[11:])
            if layer_impactArea != []:
              layer_impactArea = layer_impactArea[0]
            else:
              layer_impactArea = None
            #recupère le layer de zones multiples
            layer_multiZdr = QgsMapLayerRegistry.instance().mapLayersByName("multiImpactArea_" + layer.name()[11:])
            if layer_multiZdr != []:
              layer_multiZdr = layer_multiZdr[0]
            else:
              layer_multiZdr = None
            #crée le plan de vol
            pdv = FlightPlan(self.iface, None, None, self.layerMenu, self.Folder.path(), layer, layer_lineView, layer_trajectory, layer_pointsTraj, layer_impactArea, layer_multiZdr)
            self.pdv_list.append(pdv)

        ##recup des données
        self.LayerRadio = QgsMapLayerRegistry.instance().mapLayersByName("Antennes radio")[0]
        self.LayerCollectionSites = QgsMapLayerRegistry.instance().mapLayersByName("Sites de recueil")[0]
        self.LayerAreas = QgsMapLayerRegistry.instance().mapLayersByName("Zones")[0]

        ###############################################################################################

      self.menu = self.menu2
      menuBar = self.iface.mainWindow().menuBar()
      menuBar.addMenu(self.menu)

      #######################################init des boutons######################################
      self.newPdv_btn = QAction("&Nouveau Pdv", self.iface.mainWindow())
      self.iface.addToolBarIcon(self.newPdv_btn)
      QObject.connect(self.newPdv_btn, SIGNAL("activated()"), self.run_createPdv)

      self.trajectory_btn = QAction("&Calculer trajectoire", self.iface.mainWindow())
      self.iface.addToolBarIcon(self.trajectory_btn)
      QObject.connect(self.trajectory_btn, SIGNAL("activated()"), self.run_trajectory)

      self.zdr_btn = QAction("&Calculer zdr", self.iface.mainWindow())
      self.iface.addToolBarIcon(self.zdr_btn)
      QObject.connect(self.zdr_btn, SIGNAL("activated()"), self.run_zdr)

      self.density_btn = QAction("&Calculer densite", self.iface.mainWindow())
      self.iface.addToolBarIcon(self.density_btn)
      QObject.connect(self.density_btn, SIGNAL("activated()"), self.run_density)
      ###############################################################################################

      self.initialized = True
      self.project.writeEntry("QDrone", "Qgs_Project", True)

############################################################################################################

############################################## FONCTIONS ###################################################

  def run_createPdv(self):
    dlg_createFlightPlan = CreateFlightPlan_Dialog()
    dlg_createFlightPlan.show()
    res = dlg_createFlightPlan.exec_()
    if res == 1: #si l'utilisateur a clique sur OK et pas ANNULER
      name = dlg_createFlightPlan.ui.edit.text()
      exists = False
      
      fly_list = []
      children = self.GroupFly.children()
      for child in children:
        if child.nodeType() == 0: # si l'enfant est un group
          fly_list.append(child.name())

      for fly in fly_list:
        if name == fly:
          dlg = QMessageBox()
          dlg.setWindowTitle("Erreur")
          Str = "le nom du vol est déjà existant."
          dlg.setText(Str.decode('utf-8'))
          dlg.exec_()
          exists = True
          self.run_createPdv()
      if name == "":
        dlg = QMessageBox()
        dlg.setWindowTitle("Erreur")
        Str = "Erreur dans le nom du vol."
        dlg.setText(Str.decode('utf-8'))
        dlg.exec_()
        self.run_createPdv()
      elif exists == False:
        pdv = FlightPlan(self.iface, name, self.layerMenu, "", self.Folder.path(), None, None, None, None, None, None)
        self.pdv_list.append(pdv)

  def run_importPdv(self):
    Str = "Choisir le plan de vol à importer"
    file = QFileDialog.getOpenFileName(None, Str.decode('utf-8'), QgsProject.instance().homePath(), "ESRI Shapefile (*.shp *.SHP)")
    if file != "":
      #recupere le nom du VA
      splited = file.split("/")
      length = len(splited)
      name = splited[length-1][:-4]
      if name[:11] == "flightPlan_":
        name = name[11:]

      exists = False
      fly_list = []
      children = self.GroupFly.children()
      for child in children:
        if child.nodeType() == 0: # si l'enfant est un group
          fly_list.append(child.name())

      for fly in fly_list:
        if name == fly:
          dlg = QMessageBox()
          dlg.setWindowTitle("Erreur")
          Str = "le nom du vol est déjà existant, le plan de vol n'est pas chargé."
          dlg.setText(Str.decode('utf-8'))
          dlg.exec_()
          exists = True

      if exists == False:
        pdv = FlightPlan(self.iface, name, self.layerMenu, file, self.Folder.path(), None, None, None, None, None, None)
        self.pdv_list.append(pdv)

  def run_trajectory(self):
    check = VACheck()
    res = 0
    if check == True:
        if len(self.pdv_list) == 0:
          dlg = QMessageBox()
          Str = "Aucun vol existant."
          dlg.setText(Str.decode('utf-8'))
          dlg.exec_()
        else:
          dlg_createTrajectory = CreateTrajecory_Dialog(self.iface, self.layerMenu)
          dlg_createTrajectory.show()
          res = dlg_createTrajectory.exec_()
          if res == 1: #si l'utilisateur a clique sur OK et pas ANNULER
            flight = dlg_createTrajectory.ui.comboBox.currentText()
            for i in range(len(self.pdv_list)):
              if self.pdv_list[i].layer.name() == "flightPlan_"+flight:
                check = self.pdv_list[i].selfCheck()
                if check == True:
                  if is_int(dlg_createTrajectory.ui.edit.text()) == False:
                    check = "le pas de calcul n'est pas un entier."
                    dlg = QMessageBox()
                    dlg.setText(check.decode('utf-8'))
                    dlg.exec_()
                  elif int(dlg_createTrajectory.ui.edit.text()) <= 0:
                    check = "le pas de calcul est inférieur ou égal à zero."
                    dlg = QMessageBox()
                    dlg.setText(check.decode('utf-8'))
                    dlg.exec_()
                  elif self.pdv_list[i].layer.featureCount() != 0:
                    self.pdv_list[i].createTrajectory(int(dlg_createTrajectory.ui.edit.text()))
                else:
                  dlg = QMessageBox()
                  dlg.setText(check.decode('utf-8'))
                  dlg.exec_()
    else:
      dlg = QMessageBox()
      dlg.setText(check.decode('utf-8'))
      dlg.exec_()
    return res

  def run_zdr(self):
    check = WeatherCheck()
    res = 0
    if check == True:
        if len(self.pdv_list) == 0:
          dlg = QMessageBox()
          Str = "Aucun vol existant."
          dlg.setText(Str.decode('utf-8'))
          dlg.exec_()
        else:
          dlg_createImpactAreas = CreateImpactAreas_Dialog(self.iface, self.layerMenu)
          dlg_createImpactAreas.show()
          res = dlg_createImpactAreas.exec_()
          if res == 1: #si l'utilisateur a clique sur OK et pas ANNULER
            flight = dlg_createImpactAreas.ui.comboBox.currentText()
            for i in range(len(self.pdv_list)):
              if self.pdv_list[i].layer.name() == "flightPlan_"+flight:
                check = self.pdv_list[i].selfCheck()
                if check == True:
                  Str = "trajectory_"+flight
                  if QgsMapLayerRegistry.instance().mapLayersByName(Str.decode('utf-8')) == []:
                    res = self.run_trajectory()
                    if QgsMapLayerRegistry.instance().mapLayersByName(Str.decode('utf-8')) != []:
                      self.pdv_list[i].traj.createZdr()
                  else:
                    self.pdv_list[i].traj.createZdr()
                else:
                  dlg = QMessageBox()
                  dlg.setText(check.decode('utf-8'))
                  dlg.exec_()
    else:
      dlg = QMessageBox()
      dlg.setText(check.decode('utf-8'))
      dlg.exec_()
    return res

  def run_density(self):
    res = 0
    if len(self.pdv_list) == 0:
      dlg = QMessageBox()
      Str = "Aucun vol existant."
      dlg.setText(Str.decode('utf-8'))
      dlg.exec_()
    else:
      dlg_calculateDensity = CalculateDensity_Dialog()
      dlg_calculateDensity.show()
      res = dlg_calculateDensity.exec_()
      if res == 1: #si l'utilisateur a clique sur OK et pas ANNULER
        flight = dlg_calculateDensity.ui.comboBoxPdv.currentText()
        for i in range(len(self.pdv_list)):
          if self.pdv_list[i].layer.name() == "flightPlan_"+flight:
            check = self.pdv_list[i].selfCheck()
            if check == True:
              # action selon le type de densité
              densityType = dlg_calculateDensity.ui.comboBoxType.currentText()
              if densityType == "Population": # calcul de la densitée de population
                #check et création des traj et pdv
                Str = "impactAreas_"+flight
                if QgsMapLayerRegistry.instance().mapLayersByName(Str.decode('utf-8')) == []:
                  res = self.run_zdr()
                  if res == 1:
                    if QgsMapLayerRegistry.instance().mapLayersByName(Str.decode('utf-8')) != []:
                      self.population = Population(flight, self.iface)
                      self.population.start()
                      self.iface.messageBar().pushWidget(self.population.widget)
                    else:
                      check = "Erreur dans la création des zones de retombées."
                      dlg = QMessageBox()
                      dlg.setText(check.decode('utf-8'))
                      dlg.exec_()
                else:
                  self.population = Population(flight, self.iface)
                  self.population.start()
                  self.iface.messageBar().pushWidget(self.population.widget)
              else: # calcul de la densitée de sites d'activitées
                #check et création des traj et pdv
                Str = "impactAreas_"+flight
                if QgsMapLayerRegistry.instance().mapLayersByName(Str.decode('utf-8')) == []:
                  dlg_topo = Topo_Dialog()
                  dlg_topo.show()
                  res = dlg_topo.exec_()
                  if res == 1:
                    res = self.run_zdr()
                    if res == 1:
                      if QgsMapLayerRegistry.instance().mapLayersByName(Str.decode('utf-8')) != []:
                        self.topographie = Topographie(flight, self.iface)
                        self.topographie.start()
                        self.iface.messageBar().pushWidget(self.topographie.widget)
                      else:
                        check = "Erreur dans la création des zones de retombées."
                        dlg = QMessageBox()
                        dlg.setText(check.decode('utf-8'))
                        dlg.exec_()
                else:
                  dlg_topo = Topo_Dialog()
                  dlg_topo.show()
                  res = dlg_topo.exec_()
                  if res == 1:
                    self.topographie = Topographie(flight, self.iface)
                    self.topographie.start()
                    self.iface.messageBar().pushWidget(self.topographie.widget)
            else:
              dlg = QMessageBox()
              dlg.setText(check.decode('utf-8'))
              dlg.exec_()

  def run_LoadVA(self):
    file = QFileDialog.getOpenFileName(None, "Choisir le VA", QgsProject.instance().homePath(), "Comma Separated Values (*.csv *.CSV)")
    if file != "":
      LoadVA(file)

  def run_loadWeather(self):
    Str = "Choisir la météo"
    file = QFileDialog.getOpenFileName(None, Str.decode('utf-8'), QgsProject.instance().homePath(), "Comma Separated Values (*.csv *.CSV)")
    if file != "":
      loadWeather(file)

  def run_loadPopulation(self):
    Str = "Choisir le fichier de données de population"
    file = QFileDialog.getOpenFileName(None, Str.decode('utf-8'), QgsProject.instance().homePath(), "ESRI Shapefile (*.shp *.SHP)")
    if file != "":
      loadPopulation(file, self.iface)

  def run_loadTopo(self):
    Str = "Choisir le fichier de données topographiques"
    file = QFileDialog.getOpenFileName(None, Str.decode('utf-8'), QgsProject.instance().homePath(), "Comma Separated Values (*.csv *.CSV)")
    if file != "":
      loadTopo(file)

  def removeFromPdvList(self, node, indexFrom, indexTo):
    for pdv in self.pdv_list:
      if QgsProject.instance().layerTreeRoot().findGroup(pdv.name) == None:
        self.pdv_list.remove(pdv)

def is_int(s):
  try:
    int(s)
    return True
  except ValueError:
    return False