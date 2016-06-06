#!/usr/bin/python
# -*- coding: utf-8 -*-
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class ImpactAreas(object):

	def __init__(self, iface, name, layerMenu, layer_multiZdr, layer_Zdr):

		self.iface = iface
		self.layerMenu = layerMenu

		if layer_Zdr == None: # si la trajectoire est créée

			Folder = QDir(QgsProject.instance().homePath())
			Folder.cd("QDrone")
			Folder.cd("Vols")
			Folder.cd(name)
			self.folderFly = QDir(Folder)

			self.folderFly.cd("Interne")
			self.folderIntern = QDir(self.folderFly.path())
			self.folderFly.cdUp()

			########## multiZdr #########
			tempLayerMultiZdr = None
			nameMultiZdr = "multiImpactAreas_" + name
			folderMultiZdr = self.folderIntern.path() + "/" + nameMultiZdr + ".shp"
			##########################
			########## Zdr #########
			tempLayerZdr = None
			nameZdr = "impactAreas_" + name
			folderZdr = self.folderFly.path() + "/" + nameZdr + ".shp"
			##########################

			self.GroupFly = layerMenu.findGroup("Vols")
			self.GroupCurrentFly = self.GroupFly.findGroup(name)
			self.GroupIntern = self.GroupCurrentFly.findGroup("Interne")

			#create layer
			tempLayerMultiZdr = layer_multiZdr
			tempLayerZdr = QgsVectorLayer("Polygon", nameZdr.decode('utf-8'), "memory")

			#saving the layers
			QgsVectorFileWriter.writeAsVectorFormat(tempLayerMultiZdr, folderMultiZdr, "utf-8", None, "ESRI Shapefile")
			QgsVectorFileWriter.writeAsVectorFormat(tempLayerZdr, folderZdr, "utf-8", None, "ESRI Shapefile")
			
			#reloading the layers
			tempLayerMultiZdr = QgsVectorLayer(folderMultiZdr, nameMultiZdr, "ogr")
			tempLayerZdr = QgsVectorLayer(folderZdr, nameZdr, "ogr")

			#place the layers
			########## multiZdr #########
			QgsMapLayerRegistry.instance().addMapLayer(tempLayerMultiZdr) #ajout dans le menu de layers
			tempLayerMultiZdr = layerMenu.findLayer(tempLayerMultiZdr.id())
			self.multiZdr = tempLayerMultiZdr.clone()
			self.GroupIntern.addChildNode(self.multiZdr) #clonage dans le groupe
			parent = tempLayerMultiZdr.parent()
			parent.removeChildNode(tempLayerMultiZdr) #suppression du layer mal placé
			self.multiZdr = self.multiZdr.layer() #recupération du layer
			##########################

			########## Zdr #########
			QgsMapLayerRegistry.instance().addMapLayer(tempLayerZdr) #ajout dans le menu de layers
			tempLayerZdr = layerMenu.findLayer(tempLayerZdr.id())
			self.Zdr = tempLayerZdr.clone()
			self.GroupCurrentFly.addChildNode(self.Zdr) #clonage dans le groupe
			parent = tempLayerZdr.parent()
			parent.removeChildNode(tempLayerZdr) #suppression du layer mal placé
			self.Zdr = self.Zdr.layer() #recupération du layer
			##########################

			# create the layer from multiZdr
			geom = QgsGeometry().fromPolygon([[]])
			for feature in self.multiZdr.getFeatures():
				geom = geom.combine(feature.geometry())
			feat = QgsFeature()
			feat.setGeometry(geom)

			self.Zdr.startEditing()
			data = self.Zdr.dataProvider()
			for ft in self.Zdr.getFeatures():
				data.deleteFeatures([ft.id()])
			data.addFeatures([feat])
			self.Zdr.commitChanges()

			#efface les messages du a la creation des layers dans la barre de message Qgis
			self.iface.messageBar().clearWidgets()
			self.GroupIntern.setExpanded(False)

			self.multiZdr.setReadOnly(True)
			self.Zdr.setReadOnly(True)
			self.multiZdr.setLayerTransparency(100)

		else: # si la zdr est importée
			self.multiZdr = layer_multiZdr
			self.Zdr = layer_Zdr
			#create Zdr if not null

		QgsProject.instance().layerTreeRoot().findLayer(self.multiZdr.id()).visibilityChanged.connect(self.changeLayerVisibility)
		QgsProject.instance().layerTreeRoot().findLayer(self.Zdr.id()).visibilityChanged.connect(self.changeLayerVisibility)

	def changeLayerVisibility(self, node, state):
		QgsProject.instance().layerTreeRoot().findLayer(self.Zdr.id()).setVisible(state)
		QgsProject.instance().layerTreeRoot().findLayer(self.multiZdr.id()).setVisible(state)

	def test(self, text):
		dlg = QMessageBox()
		dlg.setText(text)
		dlg.exec_()
