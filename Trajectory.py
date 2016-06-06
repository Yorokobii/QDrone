#!/usr/bin/python
# -*- coding: utf-8 -*-
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from ImpactAreas import *

class Trajectory(object):

	def __init__(self, iface, name, layerMenu, layer_pointTraj, layer_trajectory, layer_Zdr, layer_multiZdr):

		self.name = name
		self.iface = iface
		self.layerMenu = layerMenu
		Folder = QDir(QgsProject.instance().homePath())
		Folder.cd("QDrone")
		Folder.cd("Vols")
		Folder.cd(name)
		self.folderFly = QDir(Folder)

		if layer_trajectory == None: # si la trajectoire est créée

			self.folderFly.cd("Interne")
			self.folderIntern = QDir(self.folderFly.path())
			self.folderFly.cdUp()

			########## pointTraj #########
			tempLayerPointTraj = None
			namePointTraj = "trajectory_" + name
			folderPointTraj = self.folderFly.path() + "/" + namePointTraj + ".shp"
			##########################
			########## layer #########
			tempLayerTraj = None
			nameTraj = "lineTraj_" + name
			folderTraj = self.folderIntern.path() + "/" + nameTraj + ".shp"
			##########################

			self.GroupFly = layerMenu.findGroup("Vols")
			self.GroupCurrentFly = self.GroupFly.findGroup(name)
			self.GroupIntern = self.GroupCurrentFly.findGroup("Interne")

			#create layer
			tempLayerPointTraj = layer_pointTraj
			tempLayerTraj = QgsVectorLayer("LineString", nameTraj.decode('utf-8'), "memory")

			#saving the layers
			QgsVectorFileWriter.writeAsVectorFormat(tempLayerPointTraj, folderPointTraj, "utf-8", None, "ESRI Shapefile")
			QgsVectorFileWriter.writeAsVectorFormat(tempLayerTraj, folderTraj, "utf-8", None, "ESRI Shapefile")
			
			#reloading the layers
			tempLayerPointTraj = QgsVectorLayer(folderPointTraj, namePointTraj, "ogr")
			tempLayerTraj = QgsVectorLayer(folderTraj, nameTraj, "ogr")

			#place the layers
			########## pointTraj #########
			QgsMapLayerRegistry.instance().addMapLayer(tempLayerPointTraj) #ajout dans le menu de layers
			tempLayerPointTraj = layerMenu.findLayer(tempLayerPointTraj.id())
			self.pointTraj = tempLayerPointTraj.clone()
			self.GroupCurrentFly.addChildNode(self.pointTraj) #clonage dans le groupe
			parent = tempLayerPointTraj.parent()
			parent.removeChildNode(tempLayerPointTraj) #suppression du layer mal placé
			self.pointTraj = self.pointTraj.layer() #recupération du layer
			##########################

			########## traj #########
			QgsMapLayerRegistry.instance().addMapLayer(tempLayerTraj) #ajout dans le menu de layers
			tempLayerTraj = layerMenu.findLayer(tempLayerTraj.id())
			self.layer = tempLayerTraj.clone()
			self.GroupIntern.addChildNode(self.layer) #clonage dans le groupe
			parent = tempLayerTraj.parent()
			parent.removeChildNode(tempLayerTraj) #suppression du layer mal placé
			self.layer = self.layer.layer() #recupération du layer
			##########################

			# create the layer from pointTraj

			#################### on crée une liste de points pour créer la polyligne ####################
			points = []
			for feature in self.pointTraj.getFeatures():
				points.append(feature.geometry().asPoint())

			feat = QgsFeature()
			feat.setGeometry(QgsGeometry.fromPolyline(points))
			############################################################################################

			#################### on édite le layer pour changer ça geometrie ####################
			self.layer.startEditing()

			data = self.layer.dataProvider()
			for ft in self.layer.getFeatures():
				data.deleteFeatures([ft.id()])
			data.addFeatures([feat])

			self.layer.commitChanges()
			############################################################################################
			
			#efface les messages du a la creation des layers dans la barre de message Qgis
			self.iface.messageBar().clearWidgets()
			self.GroupIntern.setExpanded(False)

			self.layer.setReadOnly(True)
			self.pointTraj.setReadOnly(True)
			self.pointTraj.setLayerTransparency(100)

		else: # si la trajectoire est importée
			self.pointTraj = layer_pointTraj
			self.layer = layer_trajectory
			#create Zdr if not null

		QgsProject.instance().layerTreeRoot().findLayer(self.layer.id()).visibilityChanged.connect(self.changeLayerVisibility)
		QgsProject.instance().layerTreeRoot().findLayer(self.pointTraj.id()).visibilityChanged.connect(self.changeLayerVisibility)

	def changeLayerVisibility(self, node, state):
		QgsProject.instance().layerTreeRoot().findLayer(self.pointTraj.id()).setVisible(state)
		QgsProject.instance().layerTreeRoot().findLayer(self.layer.id()).setVisible(state)

	def createZdr(self):
		Str = "Météo"
		Weather = QgsMapLayerRegistry.instance().mapLayersByName(Str.decode('utf-8'))[0]
		layerMultiZdr = self.createZdrLayer(self.pointTraj, Weather)
		self.layerMenu = QgsProject.instance().layerTreeRoot()
		self.rmZdr(self.name)
		self.Zdr = ImpactAreas(self.iface, self.name, self.layerMenu, layerMultiZdr, None)


	def createZdrLayer(self, pointTrajLayer, Weather):
		################ recupere le nom du layer de zdr ##################
		name = "multiImpactAreas_" + pointTrajLayer.name()[10:]
		########################################################################

		################## création du layer en memoire ##################
		multiZdrLayer = QgsVectorLayer("Polygon", name, "memory")

		#fields
		multiZdrLayer.dataProvider().addAttributes([QgsField("Densitée de population", QVariant.Double), QgsField("nom Meteo", QVariant.String)]) #ajout des fields
		multiZdrLayer.updateFields()
		########################################################################

		################## calcul de la zdr ##################
		##############################################################

		################## fake modification pour démarquer la zdr ##################
		newFeats = []
		for feature in pointTrajLayer.getFeatures():
			newFeat = QgsFeature()
			newFeat.setGeometry( QgsGeometry.fromPolygon([[QgsPoint(feature.geometry().asPoint().x(), feature.geometry().asPoint().y()), QgsPoint(feature.geometry().asPoint().x() + 100, feature.geometry().asPoint().y()), QgsPoint(feature.geometry().asPoint().x(), feature.geometry().asPoint().y() + 100)]]))
			newFeats.append(newFeat)
		multiZdrLayer.dataProvider().addFeatures(newFeats)
		########################################################################################## 

		return multiZdrLayer #retourne un layer de points

	def rmZdr(self, name):
		for layer in QgsMapLayerRegistry.instance().mapLayers().values():
			if layer.name() == "impactAreas_"+name or layer.name() == "multiImpactAreas_"+name:
				self.layerMenu.findLayer(layer.id()).parent().removeChildNode(self.layerMenu.findLayer(layer.id()))

	def test(self, text):
		dlg = QMessageBox()
		dlg.setText(text)
		dlg.exec_()
