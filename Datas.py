#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

def LoadVA(file):
  error = ""
  try:
    splited = file.split("/")
    length = len(splited)

    ################# recupere le path du VA ####################
    path = ""
    for i in range(length-2):
      path = path+splited[i]+"/"
    ############################################################
    ################# recupere le nom du VA #################
    name = splited[length-1][:-4]

    ################# on lis le VA #################
    uri = "file:///"+file+"?delimiter=,"
    Str = "Vecteur aérien"
    NewVA = QgsVectorLayer(uri, Str.decode('utf-8'), "delimitedtext")
    ###########################################################

    layerMenu = QgsProject.instance().layerTreeRoot()
    Str = "Données"
    GroupDatas = layerMenu.findGroup(Str.decode('utf-8'))

    ################# on supprime l'ancien VA s'il existe #################
    idList = layerMenu.findLayerIds()
    for layerId in idList:
      layer = layerMenu.findLayer(layerId)
      Str = "Vecteur aérien"
      if layer.layerName() == Str.decode('utf-8'):
        parent = layer.parent()
        parent.removeChildNode(layer)
    ############################################################################

    ################## ajout du layer VA dans le menu de layers #################
    QgsMapLayerRegistry.instance().addMapLayer(NewVA) #ajout dans le menu de layers
    NewVA = layerMenu.findLayer(NewVA.id())
    LayerVA = NewVA.clone()
    GroupDatas.addChildNode(LayerVA) #clonage dans le groupe
    parent = NewVA.parent()
    parent.removeChildNode(NewVA) #suppression du layer mal placé
    LayerVA = LayerVA.layer() #recupération du layer
    LayerVA.setReadOnly()
    LayerVA.setLayerTransparency(100)
    ############################################################################
    error = VACheck()
    if error != True:
      raise RuntimeError(error)

  except RuntimeError:
    errorDialog = QMessageBox()
    errorDialog.setText(error.decode('utf-8'))
    errorDialog.exec_()

def VACheck():
  ret = True

  Str = "Vecteur aérien"
  VA = QgsMapLayerRegistry.instance().mapLayersByName(Str.decode('utf-8'))

  if len(VA) == 0:
    ret = "Aucun vecteur aérien n'est chargé"
  else:
    VA = VA[0]

    feature = None
    for feat in VA.getFeatures():
      feature = feat
    if feature == None:
      ret = "Le vecteur aérien ne contient aucune information.\nVérifiez qu'il soit correctement remplis."

    fields = VA.fields()
    if fields.count() < 5:
      ret = "Le format du vecteur aérien est invalide : pas assez d'attributs.\nVérifiez que le format soit : \"Nom, Montee, Descente, Roulis, Finesse\""
    elif fields.count() > 5:
      ret = "Le format du vecteur aérien est invalide : trop d'attributs.\nVérifiez que le format soit : \"Nom, Montee, Descente, Roulis, Finesse\""
    
    if fields.field(0).name() != "Nom":
      ret = "Le format du vecteur aérien est invalide : le nom du premier attribut est invalide.\nVérifiez que le format soit : \"Nom, Montee, Descente, Roulis, Finesse\""
    elif feature.attribute(fields.field(0).name()) == None:
      ret = "Le format du vecteur aérien est invalide : le premier attribut est null.\nVérifiez les valeurs du vecteur aérien"
    
    elif fields.field(1).name() != "Montee":
      ret = "Le format du vecteur aérien est invalide : le nom du second attribut est invalide.\nVérifiez que le format soit : \"Nom, Montee, Descente, Roulis, Finesse\""
    elif feature.attribute(fields.field(1).name()) == None:
      ret = "Le format du vecteur aérien est invalide : le second attribut est null.\nVérifiez les valeurs du vecteur aérien"
    
    elif fields.field(2).name() != "Descente":
      ret = "Le format du vecteur aérien est invalide : le nom du troisème attribut est invalide.\nVérifiez que le format soit : \"Nom, Montee, Descente, Roulis, Finesse\""
    elif feature.attribute(fields.field(2).name()) == None:
      ret = "Le format du vecteur aérien est invalide : le troisème attribut est null.\nVérifiez les valeurs du vecteur aérien"
    
    elif fields.field(3).name() != "Roulis":
      ret = "Le format du vecteur aérien est invalide : le nom du quatrième attribut est invalide.\nVérifiez que le format soit : \"Nom, Montee, Descente, Roulis, Finesse\""
    elif feature.attribute(fields.field(3).name()) == None:
      ret = "Le format du vecteur aérien est invalide : le quatrième attribut est null.\nVérifiez les valeurs du vecteur aérien"
    
    elif fields.field(4).name() != "Finesse":
      ret = "Le format du vecteur aérien est invalide : le nom du cinquième attribut est invalide.\nVérifiez que le format soit : \"Nom, Montee, Descente, Roulis, Finesse\""
    elif feature.attribute(fields.field(4).name()) == None:
      ret = "Le format du vecteur aérien est invalide : le cinquième attribut est null.\nVérifiez les valeurs du vecteur aérien"
    
    if ret != True:
      layerNode = QgsProject.instance().layerTreeRoot().findLayer(VA.id())
      parent = layerNode.parent()
      parent.removeChildNode(layerNode)

  return ret

def loadWeather(file):
  error = ""
  try:
    splited = file.split("/")
    length = len(splited)

    ################# recupere le path de la météo ####################
    path = ""
    for i in range(length-2):
      path = path+splited[i]+"/"
    ############################################################

    ################# on lis la Meteo #################
    uri = "file:///"+file+"?delimiter=,"
    Str = "Météo"
    NewMeteo = QgsVectorLayer(uri, Str.decode('utf-8'), "delimitedtext")
    ###########################################################
    ################# gestion d'erreurs #################
    feature = None
    for feat in NewMeteo.getFeatures():
      feature = feat
    if feature == None:
      error = "La météo chargé n'est pas correct.\nVérifiez qu'elle soit correctement remplie."
      raise RuntimeError(error)
    ###########################################################

    layerMenu = QgsProject.instance().layerTreeRoot()
    Str = "Données"
    GroupDatas = layerMenu.findGroup(Str.decode('utf-8'))

    ################# on supprime l'ancienne Meteo si elle existe #################
    idList = layerMenu.findLayerIds()
    for layerId in idList:
      layer = layerMenu.findLayer(layerId)
      Str = "Météo"
      if layer.layerName() == Str.decode('utf-8'):
        parent = layer.parent()
        parent.removeChildNode(layer)
    ############################################################################

    ################## ajout du layer Meteo dans le menu de layers #################
    QgsMapLayerRegistry.instance().addMapLayer(NewMeteo) #ajout dans le menu de layers
    NewMeteo = layerMenu.findLayer(NewMeteo.id())
    LayerMeteo = NewMeteo.clone()
    GroupDatas.addChildNode(LayerMeteo) #clonage dans le groupe
    parent = NewMeteo.parent()
    parent.removeChildNode(NewMeteo) #suppression du layer mal placé
    LayerMeteo = LayerMeteo.layer() #recupération du layer
    LayerMeteo.setReadOnly()
    LayerMeteo.setLayerTransparency(100)
    ############################################################################

    error = WeatherCheck()
    if error != True:
      raise RuntimeError(error)

  except RuntimeError:
    errorDialog = QMessageBox()
    errorDialog.setText(error.decode('utf-8'))
    errorDialog.exec_()

def WeatherCheck():
  ret = True

  Str = "Météo"
  Meteo = QgsMapLayerRegistry.instance().mapLayersByName(Str.decode('utf-8'))

  if len(Meteo) == 0:
    ret = "Aucune météo n'est chargée"
  else:
    Meteo = Meteo[0]

    feature = None
    for feat in Meteo.getFeatures():
      feature = feat
    if feature == None:
      ret = "La météo ne contient aucune information.\nVérifiez qu'elle soit correctement remplis."

    fields = Meteo.fields()
    if fields.count() < 14:
      ret = "Le format de la météo est invalide : pas assez d'attributs.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""
    elif fields.count() > 14:
      ret = "Le format de la météo est invalide : trop d'attributs.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""
    
    elif fields.field(0).name() != "Nom":
      ret = "Le format de la météo est invalide : le nom du premier attribut est invalide.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""
    elif feature.attribute(fields.field(0).name()) == None:
      ret = "Le format de la météo est invalide : l'attribut " + fields.field(0).name() + " est null.\nVérifiez les valeurs de la météo"
    
    elif fields.field(1).name() != "Force":
      ret = "Le format de la météo est invalide : le nom du second attribut est invalide.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""
    elif feature.attribute(fields.field(1).name()) == None:
      ret = "Le format de la météo est invalide : l'attribut " + fields.field(1).name() + " est null.\nVérifiez les valeurs de la météo"
    
    elif fields.field(2).name() != "Force max":
      ret = "Le format de la météo est invalide : le nom du troisème attribut est invalide.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""

    elif fields.field(3).name() != "Cap":
      ret = "Le format de la météo est invalide : le nom du quatrième attribut est invalide.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""

    elif fields.field(4).name() != "Date min":
      ret = "Le format de la météo est invalide : le nom du cinquième attribut est invalide.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""

    elif fields.field(5).name() != "Date max":
      ret = "Le format de la météo est invalide : le nom du sixième attribut est invalide.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""
 
    elif fields.field(6).name() != "Heure min":
      ret = "Le format de la météo est invalide : le nom du septième attribut est invalide.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""

    elif fields.field(7).name() != "Heure max":
      ret = "Le format de la météo est invalide : le nom du huitième attribut est invalide.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""

    elif fields.field(8).name() != "Lati min":
      ret = "Le format de la météo est invalide : le nom du neuvième attribut est invalide.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""
 
    elif fields.field(9).name() != "Lati max":
      ret = "Le format de la météo est invalide : le nom du dixième attribut est invalide.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""
 
    elif fields.field(10).name() != "Longi min":
      ret = "Le format de la météo est invalide : le nom du onzième attribut est invalide.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""

    elif fields.field(11).name() != "Longi max":
      ret = "Le format de la météo est invalide : le nom du douzième attribut est invalide.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""
  
    elif fields.field(12).name() != "Alti min":
      ret = "Le format de la météo est invalide : le nom du treizième attribut est invalide.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""
   
    elif fields.field(13).name() != "Alti max":
      ret = "Le format de la météo est invalide : le nom du quatorzième attribut est invalide.\nVérifiez que le format soit : \"Nom, Force, Force max, Cap, Date min, Date max, Heure min, Heure max, Lati min, Lati max, Longi min, Longi max, Alti min, Alti max\""

    if ret != True:
      layerNode = QgsProject.instance().layerTreeRoot().findLayer(Meteo.id())
      parent = layerNode.parent()
      parent.removeChildNode(layerNode)

  return ret

def loadPopulation(file, iface):
  error = ""
  try:
    splited = file.split("/")
    length = len(splited)

    ################# recupere le path ####################
    path = ""
    for i in range(length-2):
      path = path+splited[i]+"/"
    ############################################################

    ################# on lis le shapefile #################
    Str = "Population"
    NewPop = QgsVectorLayer(file, Str.decode('utf-8'), "ogr")
    ###########################################################

    layerMenu = QgsProject.instance().layerTreeRoot()
    Str = "Données"
    GroupDatas = layerMenu.findGroup(Str.decode('utf-8'))

    ################# on supprime l'ancienne shapefile s'il existe #################
    idList = layerMenu.findLayerIds()
    for layerId in idList:
      layer = layerMenu.findLayer(layerId)
      Str = "Population"
      if layer.layerName() == Str.decode('utf-8'):
        parent = layer.parent()
        parent.removeChildNode(layer)
    ############################################################################

    ################## ajout du layer Meteo dans le menu de layers #################
    QgsMapLayerRegistry.instance().addMapLayer(NewPop) #ajout dans le menu de layers
    NewPop = layerMenu.findLayer(NewPop.id())
    LayerPop = NewPop.clone()
    GroupDatas.addChildNode(LayerPop) #clonage dans le groupe
    parent = NewPop.parent()
    parent.removeChildNode(NewPop) #suppression du layer mal placé
    LayerPop = LayerPop.layer() #recupération du layer
    LayerPop.setReadOnly(True)
    iface.legendInterface().setLayerVisible(LayerPop, False)
    ############################################################################

    if LayerPop.crs().authid() != iface.mapCanvas().mapSettings().destinationCrs().authid():
      LayerPop.setCrs(QgsCoordinateReferenceSystem(iface.mapCanvas().mapSettings().destinationCrs().authid()), True)

    PopGraduation(LayerPop)

    error = PopulationCheck(iface)
    if error != True:
      raise RuntimeError(error)

  except RuntimeError:
    errorDialog = QMessageBox()
    errorDialog.setText(error.decode('utf-8'))
    errorDialog.exec_()

#fonction pour graduer la couche de population selon le nombre de personnes
def PopGraduation(layer):
  PopulationField = "c_ind_c"
  RangeList = []
  Opacity = 1

  #range 0 - 10
  Min = 0.0
  Max = 10.0
  Label = "0 - 10"
  Color = QColor("#0000ff")
  Symbol1 = QgsSymbolV2.defaultSymbol(layer.geometryType())
  Symbol1.setColor(Color)
  Symbol1.setAlpha(Opacity)
  Range1 = QgsRendererRangeV2(Min, Max, Symbol1, Label)
  RangeList.append(Range1)

  #range 10 - 20
  Min = 10.0
  Max = 20.0
  Label = "10 - 20"
  Color = QColor("#00bfff")
  Symbol2 = QgsSymbolV2.defaultSymbol(layer.geometryType())
  Symbol2.setColor(Color)
  Symbol2.setAlpha(Opacity)
  Range2 = QgsRendererRangeV2(Min, Max, Symbol2, Label)
  RangeList.append(Range2)

  #range 20 - 50
  Min = 20.0
  Max = 50.0
  Label = "20 - 50"
  Color = QColor("#00ff00")
  Symbol3 = QgsSymbolV2.defaultSymbol(layer.geometryType())
  Symbol3.setColor(Color)
  Symbol3.setAlpha(Opacity)
  Range3 = QgsRendererRangeV2(Min, Max, Symbol3, Label)
  RangeList.append(Range3)

  #range 50 - 100
  Min = 50.0
  Max = 100.0
  Label = "50 - 100"
  Color = QColor("#ffff00")
  Symbol4 = QgsSymbolV2.defaultSymbol(layer.geometryType())
  Symbol4.setColor(Color)
  Symbol4.setAlpha(Opacity)
  Range4 = QgsRendererRangeV2(Min, Max, Symbol4, Label)
  RangeList.append(Range4)

  #range 100 - 150
  Min = 100.0
  Max = 150.0
  Label = "100 - 150"
  Color = QColor("#ff8000")
  Symbol5 = QgsSymbolV2.defaultSymbol(layer.geometryType())
  Symbol5.setColor(Color)
  Symbol5.setAlpha(Opacity)
  Range5 = QgsRendererRangeV2(Min, Max, Symbol5, Label)
  RangeList.append(Range5)

  #range 150- 10000000
  Min = 150.0
  Max = 10000000.0
  Label = "150+"
  Color = QColor("#ff0000")
  Symbol6 = QgsSymbolV2.defaultSymbol(layer.geometryType())
  Symbol6.setColor(Color)
  Symbol6.setAlpha(Opacity)
  Range6 = QgsRendererRangeV2(Min, Max, Symbol6, Label)
  RangeList.append(Range6)

  Renderer = QgsGraduatedSymbolRendererV2('', RangeList)
  Renderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
  Renderer.setClassAttribute(PopulationField)
  layer.setRendererV2(Renderer)


def PopulationCheck(iface):
  PopulationField = "c_ind_c"
  ret = True
  Str = "Population"
  Population = QgsMapLayerRegistry.instance().mapLayersByName(Str.decode('utf-8'))

  if len(Population) == 0:
    ret = "Aucune donnée de population n'est chargée."
  else:
    Population = Population[0]

    ########### teste si l'attribut de population est présent dans le layer #######
    ret = "L'attribut " + PopulationField + " est manquant."
    for i in range(Population.fields().count()):
      if Population.fields().field(i).name() == PopulationField:
        ret = True
    if ret == True: # si l'attribut est présent
      for feature in Population.getFeatures():
        if feature.attribute(PopulationField) == None: # erreur si un feature a une population nulle (pas 0)
          ret = "Le feature ID: " + str(feature.id()) + " a une population nulle."
      if ret == True: # si aucun attribut de population n'est null
        #teste si le systeme de coord est bon
        if Population.crs().authid() != iface.mapCanvas().mapSettings().destinationCrs().authid():
          ret = "Le système de coordonnées du layer de population est mauvais.\n" + iface.mapCanvas().mapSettings().destinationCrs().authid() + " est attendu."
        else: # si le systeme de coordonnées est bon
          pass

    if ret != True:
      layerNode = QgsProject.instance().layerTreeRoot().findLayer(Population.id())
      parent = layerNode.parent()
      parent.removeChildNode(layerNode)

  return ret

def loadTopo(file):
  pass

def TopoCheck(iface):
  ret = True

  return ret