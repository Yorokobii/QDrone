#!/usr/bin/python
# -*- coding: utf-8 -*-
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from Trajectory import *
from QGeometrie import *

class FlightPlan(object):

	def __init__(self, iface, name, layerMenu, file, folder, layer, layer_lineView, layer_trajectory, layer_pointTraj, layer_Zdr, layer_multiZdr):

		self.iface = iface
		self.orderValid = True
		self.automaticOrderChange = False
		self.feat_removed = False
		self.layerMenu = layerMenu
		self.featAddGeomChange = False
		self.committing = False

		if layer == None: # le constructeur si le pdv est créé ou importé
			self.name = name

			Folder = QDir(QgsProject.instance().homePath())
			Folder.cd("QDrone")
			Folder.cd("Vols")
			Folder.mkdir(name)
			Folder.cd(name)
			self.folderFly = QDir(Folder.path())
			Folder.cdUp()

			self.folderFly.mkdir("Interne")
			self.folderFly.cd("Interne")
			self.folderIntern = QDir(self.folderFly.path())
			self.folderFly.cdUp()

			########## PDV #########
			tempLayerPdv = None
			namePdv = "flightPlan_" + name
			folderPdv = self.folderFly.path() + "/" + namePdv + ".shp"
			##########################
			########## LineView #########
			tempLayerLineView = None
			nameLineView = "lineView_" + name
			folderLineView = self.folderIntern.path() + "/" + nameLineView + ".shp"
			##########################

			########## ajout du groupe du vol ##########
			self.GroupFly = layerMenu.findGroup("Vols")
			self.GroupCurrentFly = self.GroupFly.addGroup(name)
			self.GroupIntern = self.GroupCurrentFly.addGroup("Interne")

			##################################################

			if file == "":
				##################### création des layers ########################
				tempLayerPdv = QgsVectorLayer("Point", namePdv.decode('utf-8'), "memory") #PDV
				tempLayerLineView = QgsVectorLayer("LineString", nameLineView.decode('utf-8'), "memory") #LineView
				#####################################################################

				############################### ajout des fields au layers #############

				########## PDV #########
				repetitions_str = "répét"
				tempLayerPdv.dataProvider().addAttributes([QgsField("ordre", QVariant.Int), QgsField("longitude", QVariant.Double), QgsField("latitude", QVariant.Double), QgsField("alti (m)", QVariant.Double), QgsField("vit (m/s)", QVariant.Double), QgsField("virage", QVariant.Double), QgsField("roulis", QVariant.Double), QgsField("type", QVariant.String), QgsField("passage", QVariant.String), QgsField(repetitions_str.decode('utf-8'), QVariant.Int), QgsField("sens", QVariant.String), QgsField("rayon", QVariant.Double), QgsField("branche", QVariant.Double), QgsField("route", QVariant.Double)]) #ajout des fields
				tempLayerPdv.updateFields()
				##########################

				#####################################################################
			########################## on lit le layer pour le réécrire dans le dossier s'il est distant ##################
			elif file != folderPdv:
				tempLayerPdv = QgsVectorLayer(file, namePdv, "ogr") #PDV est lu
				tempLayerLineView = QgsVectorLayer("LineString", nameLineView.decode('utf-8'), "memory") #LineView est créé
			#########################################################################################################################
			########################## sinon si le pdv est importé depuis le bon dossier ##########################
			else:
				########################## folders ##########################
				########## trajectoire #########
				nameTraj = "trajectory_" + name
				folderTraj = self.folderFly.path() + "/" + nameTraj + ".shp"
				##########################
				########## trajPoints #########
				namePointsTraj = "pointsTraj_" + name
				folderPointsTraj = self.folderIntern.path() + "/" + namePointsTraj + ".shp"
				##########################
				########## Zones de retombées #########
				nameImpactArea = "impactArea_" + name
				folderImpactArea = self.folderFly.path() + "/" + nameImpactArea + ".shp"
				##########################
				########## Zones de retombées mulitples #########
				nameMultiImpactArea = "multiImpactArea_" + name
				folderMultiImpactArea = self.folderIntern.path() + "/" + nameMultiImpactArea + ".shp"
				##########################
				##############################################################################

				########################## création des instances de layer ##########################
				layer_trajectory = QgsVectorLayer(folderTraj, nameTraj, "ogr")
				layer_pointTraj = QgsVectorLayer(folderPointsTraj, namePointsTraj, "ogr")
				layer_Zdr = QgsVectorLayer(folderImpactArea, nameImpactArea, "ogr")
				layer_multiZdr = QgsVectorLayer(folderMultiImpactArea, nameMultiImpactArea, "ogr")
				##############################################################################

			#######################################################################################################

			######################## on écrit les layers dans le dossier QDrone #######################
			QgsVectorFileWriter.writeAsVectorFormat(tempLayerPdv, folderPdv, "utf-8", None, "ESRI Shapefile") #PDV
			QgsVectorFileWriter.writeAsVectorFormat(tempLayerLineView, folderLineView, "utf-8", None, "ESRI Shapefile") #LineView
			#####################################################################


			########################## on reouvre les layers pour ne plus travailler en mémoire ##################
			tempLayerPdv = QgsVectorLayer(folderPdv, namePdv, "ogr") #PDV
			tempLayerLineView = QgsVectorLayer(folderLineView, nameLineView, "ogr") #LineView
			#####################################################################

			############## ajout du layer pdv dans le menu de layers ############

			########## PDV #########
			QgsMapLayerRegistry.instance().addMapLayer(tempLayerPdv) #ajout dans le menu de layers
			tempLayerPdv = layerMenu.findLayer(tempLayerPdv.id())
			self.layer = tempLayerPdv.clone()
			self.GroupCurrentFly.addChildNode(self.layer) #clonage dans le groupe
			parent = tempLayerPdv.parent()
			parent.removeChildNode(tempLayerPdv) #suppression du layer mal placé
			self.layer = self.layer.layer() #recupération du layer
			##########################

			########## LineView #########
			QgsMapLayerRegistry.instance().addMapLayer(tempLayerLineView) #ajout dans le menu de layers
			tempLayerLineView = layerMenu.findLayer(tempLayerLineView.id())
			self.LineView = tempLayerLineView.clone()
			self.GroupIntern.addChildNode(self.LineView) #clonage dans le groupe
			parent = tempLayerLineView.parent()
			parent.removeChildNode(tempLayerLineView) #suppression du layer mal placé
			self.LineView = self.LineView.layer() #recupération du layer
			###### on bloque la modif des layers a ne pas changer #######
			self.LineView.setReadOnly()
			#############################################################
			##########################

			####################################################################

			#efface les messages du a la creation des layers dans la barre de message Qgis
			self.iface.messageBar().clearWidgets()

			#redessine la ligne du plan de vol si le plan de vol est chargé seul d'un dossier distant
			if file != folderPdv:
				self.rewriteLineView()

			self.GroupIntern.setExpanded(False)

		else: # le constructeur si le pdv est seulement instancié avec un layer déjà existant
			self.name = layer.name()[11:]
			self.layer = layer
			self.LineView = layer_lineView
			self.LineView.setReadOnly()

			if layer_trajectory != None:
				self.folderFly = QDir(folder)
				self.folderFly.cd("Vols")
				self.folderFly.cd(name)
				self.traj = Trajectory(self.iface, self.layer.name()[11:], None, layer_pointTraj, layer_trajectory, layer_Zdr, layer_multiZdr)

		######### affiche les etiquettes du plan de vol #########
		self.layer.setCustomProperty("labeling", "pal")
		self.layer.setCustomProperty("labeling/enabled", "true")
		self.layer.setCustomProperty("labeling/fieldName", "ordre")
		self.layer.setCustomProperty("labeling/fontSize", "9")
		self.iface.mapCanvas().refresh()
		self.iface.mapCanvas().refreshAllLayers()
		######################################################

		################### connecte les signaux #########################

		########## PDV #########
		self.layer.editingStopped.connect(self.rewriteLineView)
		self.layer.featureAdded.connect(self.PdvFeatureAdded)
		self.layer.committedFeaturesRemoved.connect(self.commitFeaturesRemoved)
		self.layer.editingStopped.connect(self.PdvCommittedFeaturesRemoved)
		self.layer.committedAttributeValuesChanges.connect(self.PdvCommittedAttributeChanged)
		self.layer.committedGeometriesChanges.connect(self.PdvCommittedGeometriesChanged)
		self.layer.attributeValueChanged.connect(self.attrChanged)
		self.layer.editingStarted.connect(self.editStart)
		self.layer.editCommandEnded.connect(self.editEnd)
		##########################

		#####################################################################

		################### defini les type d'edition des attributs des layers #########################

		########## PDV #########
		editConfig = self.layer.editFormConfig()
		editConfig.setWidgetType(0, "ValueMap") # type
		editConfig.setWidgetType(7, "ValueMap") # type
		editConfig.setWidgetConfig(7, {"ordinaire" : "ordinaire", "boucle" : "boucle", "orbite" : "orbite", "hippodrome" : "hippodrome", "huit" : "huit"})
		editConfig.setWidgetType(8, "ValueMap") # passage
		editConfig.setWidgetConfig(8, {"fly-by" : "fly-by", "fly-over" : "fly-over"})
		editConfig.setWidgetType(10, "ValueMap") # sens
		editConfig.setWidgetConfig(10, {"droite" : "droite", "gauche" : "gauche"})
		##########################

		self.verifyOrder()
		self.rewriteLineView()
		QgsProject.instance().layerTreeRoot().findLayer(self.layer.id()).visibilityChanged.connect(self.changeLayerVisibility)
		QgsProject.instance().layerTreeRoot().findLayer(self.LineView.id()).visibilityChanged.connect(self.changeLayerVisibility)

		######################################################################################

	def test(self):
		dlg = QMessageBox()
		dlg.setText("lol")
		dlg.exec_()

	def changeLayerVisibility(self, node, state):
		QgsProject.instance().layerTreeRoot().findLayer(self.LineView.id()).setVisible(state)
		QgsProject.instance().layerTreeRoot().findLayer(self.layer.id()).setVisible(state)

	def editStart(self):
		committing = False

	def editEnd(self):
		if self.featAddGeomChange == True:
			self.layer.commitChanges()
			self.layer.startEditing()
			self.iface.actionAddFeature().activate(QAction.ActionEvent())
			self.featAddGeomChange = False

	# fonction appelé quand un attribut a été changé dans la table d'attributs
	def attrChanged(self, featureID, field, value):
		# si l'attribut changé est l'ordre on inverse les deux ordres concernés
		if field == 0 and self.feat_removed == False:
			feat_list = []
			for feature in self.layer.getFeatures():
				feat_list.append(feature)

			def getKey(item):
				return int(item.attribute(item.fields().field(0).name()))
			feat_list = sorted(feat_list, key=getKey)

			missing = None
			if feat_list[0].attribute(feat_list[0].fields().field(0).name()) > 1:
				missing = 1
			elif feat_list[len(feat_list)-1].attribute(feat_list[len(feat_list)-1].fields().field(0).name()) < len(feat_list):
				missing = len(feat_list)
			for i in range(len(feat_list)-1):
				if feat_list[i+1].attribute(feat_list[i+1].fields().field(0).name()) > feat_list[i].attribute(feat_list[i].fields().field(0).name()) + 1:
					missing = feat_list[i].attribute(feat_list[i].fields().field(0).name()) + 1

			for feat in self.layer.getFeatures():
				if feat.id() != featureID and feat.attribute(feat.fields().field(0).name()) == value:
					self.layer.dataProvider().changeAttributeValues({ feat.id() : {field : missing} })
			table = QgsApplication.activeWindow()
			table.close()
			self.iface.showAttributeTable(self.layer)
			self.iface.messageBar().clearWidgets()

	def commitFeaturesRemoved(self, noneed, noneed2):
		self.feat_removed = True

	# fonction appelé par editingStopped qui remet les points en ordre
	def PdvCommittedFeaturesRemoved(self):
		if self.feat_removed == True:
			feat_list = []
			for feature in self.layer.getFeatures():
				feat_list.append(feature)
			def getKey(item):
				return int(item.attribute(item.fields().field(0).name()))
			feat_list = sorted(feat_list, key=getKey)

			for i in range(len(feat_list)):
				self.layer.dataProvider().changeAttributeValues({ feat_list[i].id() : {0 : i+1} })

			self.feat_removed = False
			self.verifyOrder()
			self.rewriteLineView()

	#################### fonction appelé a la creation d'un point de passage ####################
	def PdvFeatureAdded(self, featureID):
		feat_list = []
		for feature in self.layer.getFeatures():
			feat_list.append(feature)
			longitude = None
			latitude = None
			#si un champ d'une feature n'est pas renseigné ou est incorrect on appelle la fonction default----() qui correspond
			if feature.id() == featureID:
				if feature.attribute(feature.fields().field(0).name()) == None or feature.attribute(feature.fields().field(0).name()) <= 0:
					self.defaultOrder(featureID)
				else:
					self.addWithOrder(featureID, feature.attribute(feature.fields().field(0).name()))
				if feature.attribute(feature.fields().field(1).name()) == None:
					self.defaultLongitude(featureID)
					longitude = feature.geometry().asPoint().x()
				else:
					longitude = feature.attribute(feature.fields().field(1).name())
					self.featAddGeomChange = True
				if feature.attribute(feature.fields().field(2).name()) == None:
					self.defaultLatitude(featureID)
					latitude = feature.geometry().asPoint().y()
				else:
					latitude = feature.attribute(feature.fields().field(2).name())
					self.featAddGeomChange = True

				######### change la geometry a la creation si les fields sont remplis ###########
				self.changePdvGeom(featureID, longitude, latitude)
				########################################################################################
				if feature.attribute(feature.fields().field(3).name()) == None:
					self.defaultAltitude(featureID)
				if feature.attribute(feature.fields().field(4).name()) == None:
					self.defaultSpeed(featureID)
				if feature.attribute(feature.fields().field(7).name()) == None:
					self.defaultType(featureID)
				if feature.attribute(feature.fields().field(8).name()) == None:
					self.defaultPassage(featureID)
				if feature.attribute(feature.fields().field(9).name()) == None:
					self.defaultRepetitions(featureID)
				if feature.attribute(feature.fields().field(10).name()) == None:
					self.defaultSens(featureID)
		self.setOrderEditList(feat_list)
		self.iface.mapCanvas().refreshAllLayers()
	##########################################################################################

	############################## fonction qui donne une valeur par defaut a l'attribut ordre ####################
	def defaultOrder(self, featureID):
		order = 1
		for feature in self.layer.getFeatures(): # boucle qui recupere l'attribut ordre le plus grand et lui ajoute 1
			if feature.attribute(feature.fields().field(0).name()) != None and feature.attribute(feature.fields().field(0).name()) >= order:
					order = feature.attribute(feature.fields().field(0).name()) + 1
		self.layer.dataProvider().changeAttributeValues({ featureID : {0 : order} })
		#efface les messages du a la modif du feature
		self.iface.messageBar().clearWidgets()
	##############################################################################################################

	def addWithOrder(self, featureID, value):
		if self.automaticOrderChange == 0:
			for feature in self.layer.getFeatures():
				if feature.attribute(feature.fields().field(0).name()) >= value and feature.id() != featureID:
					self.layer.dataProvider().changeAttributeValues({ feature.id() : {0 : feature.attribute(feature.fields().field(0).name())+1} })
		self.automaticOrderChange = self.automaticOrderChange + 1
		if self.automaticOrderChange == 2:
			self.automaticOrderChange = 0

	def defaultLongitude(self, featureID):
		features = self.layer.getFeatures()
		feature = None
		for feat in features:
			if feat.id() == featureID:
				feature = feat
		self.layer.dataProvider().changeAttributeValues({ featureID : {1 : feature.geometry().asPoint().x()} })
		#efface les messages du a la modif du feature
		self.iface.messageBar().clearWidgets()
	def defaultLatitude(self, featureID):
		features = self.layer.getFeatures()
		feature = None
		for feat in features:
			if feat.id() == featureID:
				feature = feat
		self.layer.dataProvider().changeAttributeValues({ featureID : {2 : feature.geometry().asPoint().y()} })
		#efface les messages du a la modif du feature
		self.iface.messageBar().clearWidgets()

	def defaultAltitude(self, featureID):
		feat_list = []
		for feature in self.layer.getFeatures():
			feat_list.append(feature)

		if len(feat_list) > 1:
			for i in range(len(feat_list)):
				if feat_list[i].id() == featureID:
					self.layer.dataProvider().changeAttributeValues({ feat_list[i].id() : {3 : feat_list[i-1].attribute(feat_list[i-1].fields().field(3).name())} })
					#efface les messages du a la modif du feature
					self.iface.messageBar().clearWidgets()

	def defaultSpeed(self, featureID):
		feat_list = []
		for feature in self.layer.getFeatures():
			feat_list.append(feature)

		if len(feat_list) > 1:
			for i in range(len(feat_list)):
				if feat_list[i].id() == featureID:
					self.layer.dataProvider().changeAttributeValues({ feat_list[i].id() : {4 : feat_list[i-1].attribute(feat_list[i-1].fields().field(4).name())} })
					#efface les messages du a la modif du feature
					self.iface.messageBar().clearWidgets()

	#################### fonction qui donne une valeur par defaut a l'attribut type ####################
	def defaultType(self, featureID):
		self.layer.dataProvider().changeAttributeValues({ featureID : {7 : "ordinaire"} })
		#efface les messages du a la modif du feature
		self.iface.messageBar().clearWidgets()
	####################################################################################################

	#################### fonction qui donne une valeur par defaut a l'attribut passage ####################
	def defaultPassage(self, featureID):
		self.layer.dataProvider().changeAttributeValues({ featureID : {8 : "fly-over"} })
		#efface les messages du a la modif du feature
		self.iface.messageBar().clearWidgets()
	####################################################################################################

	#################### fonction qui donne une valeur par defaut a l'attribut repetitions ####################
	def defaultRepetitions(self, featureID):
		self.layer.dataProvider().changeAttributeValues({ featureID : {9 : 1} })
		#efface les messages du a la modif du feature
		self.iface.messageBar().clearWidgets()
	####################################################################################################

	#################### fonction qui donne une valeur par defaut a l'attribut sens ####################
	def defaultSens(self, featureID):
		self.layer.dataProvider().changeAttributeValues({ featureID : {10 : "droite"} })
		#efface les messages du a la modif du feature
		self.iface.messageBar().clearWidgets()
	####################################################################################################

	#################### fonction qui verifie si l'ordre des points de passage est cohérent ou non ####################
	def verifyOrder(self):
		feat_list = []
		for feature in self.layer.getFeatures():
			feat_list.append(QgsFeature(feature))

		########## trie la liste de feature par ordre ##########
		def getKey(item):
			return int(item.attribute(item.fields().field(0).name()))
		feat_list = sorted(feat_list, key=getKey)
		##################################################

		########## verifie si l'ordre est cohérent ##########
		count = 1
		self.orderValid = True
		for i in range(len(feat_list)):
			if feat_list[i].attribute(feat_list[i].fields().field(0).name()) != count:
				self.orderValid = False
			count = count + 1
		##################################################

		########## met a jour la table d'attributs ##########
		self.setOrderEditList(feat_list)
	##############################################################################################################

	#################### fonction qui met a jour la liste d'ordres dans la table d'attributs ####################
	def setOrderEditList(self, feat_list):
		editConfig = self.layer.editFormConfig()
		tempListString = []
		tempList = []

		maxLength = len(str(len(feat_list)))

		for i in range(len(feat_list)):
			str0 = ""
			for j in range( maxLength - len(str(i+1)) ):
				str0 = str0 +("0")
			tempListString.append(str0 + str(i+1))
			tempList.append(i+1)
		maplist = dict(zip(tempListString, tempList))
		editConfig.setWidgetConfig(0, maplist)
	##############################################################################################################

	#################### fonction appelé quand un commit de changement d'attributs est lancé ####################
	def PdvCommittedAttributeChanged(self, layerID, changedAttributesValues):
		FeaturesIds = changedAttributesValues.keys()

		for i in range(len(FeaturesIds)):
			features = self.layer.getFeatures()
			fieldsList = changedAttributesValues[FeaturesIds[i]].keys()

			for feature in features:
				if feature.id() == FeaturesIds[i]:
					changeGeom = False
					x = feature.geometry().asPoint().x()
					y = feature.geometry().asPoint().y()
					for j in range(len(fieldsList)):
						################ si le field est celui de la longitude ####################
						if fieldsList[j] == 1:
							attrMap = changedAttributesValues[FeaturesIds[i]]
							x = attrMap[fieldsList[j]]
							if x != None:
								changeGeom = True
						################################################################################
						################# si le field est celui de la latitude ################
						if fieldsList[j] == 2:
							attrMap = changedAttributesValues[FeaturesIds[i]]
							y = attrMap[fieldsList[j]]
							if y != None:
								changeGeom = True
						################################################################################
					if changeGeom == True:
						self.changePdvGeom(feature.id(), x, y)

		##################### vérifie si l'ordre est valide ####################
		self.verifyOrder()
		################################################################################

		#### on recalcule le layer LineView
		self.rewriteLineView()
	####################################################################################################

	#################### fonction appelé pour changer la position d'un point de passage ####################
	def changePdvGeom(self, featureID, longitude, latitude):
		if latitude != None or longitude != None:
			newGeom = QgsGeometry.fromPoint(QgsPoint(longitude, latitude))
			self.layer.dataProvider().changeGeometryValues({ featureID : newGeom})
			self.iface.mapCanvas().refreshAllLayers()
	####################################################################################################

	#################### fonction appelé quand un commit de changement de geometrie est lancé ####################
	def PdvCommittedGeometriesChanged(self, layerID, geoMap):
		features = self.layer.getFeatures()
		FeaturesIds = geoMap.keys()

		for feature in features:
			for i in range(len(FeaturesIds)):
				if feature.id() == FeaturesIds[i]:
					self.changePdvAttr(FeaturesIds[i], geoMap[FeaturesIds[i]].asPoint().x(), geoMap[FeaturesIds[i]].asPoint().y())
	########################################################################################################################

	#################### fonction appelé pour mettre a jour les attributs lors d'un changement de position d'un point de passage ####################
	def changePdvAttr(self, featureID, longitude, latitude):
		self.layer.dataProvider().changeAttributeValues({ featureID : {1 : longitude , 2 : latitude}})
	############################################################################################################################################

	#################### fonction appelé pour redessiner la vue en ligne du plan de vol ####################
	def rewriteLineView(self):
		self.rmTraj(self.name)
		feat_list = []
		for feature in self.layer.getFeatures():
			feat_list.append(QgsFeature(feature))

		if len(feat_list) > 0:
			self.LineView.setLayerTransparency(0)
			if self.orderValid == True: #### si l'ordre est valide
				#################### tri par ordre des features ########################
				def getKey(item):
					return int(item.attribute(item.fields().field(0).name()))

				feat_list = sorted(feat_list, key=getKey)
				########################################################################

				#################### on crée une liste de points pour créer la polyligne ####################
				points = []
				for i in range(len(feat_list)):
					points.append(feat_list[i].geometry().asPoint())

				feat = QgsFeature()
				feat.setGeometry(QgsGeometry.fromPolyline(points))
				############################################################################################

				#################### on édite le layer LineView pour changer ça geometrie ####################
				self.LineView.startEditing()

				data = self.LineView.dataProvider()
				for ft in self.LineView.getFeatures():
					data.deleteFeatures([ft.id()])
				data.addFeatures([feat])

				self.LineView.commitChanges()
				############################################################################################
				self.iface.mapCanvas().refreshAllLayers()
			else: #### si l'ordre n'est pas valide on envoi un message d'erreur
				self.iface.messageBar().pushMessage("Erreur", "L'ordre des points de passage du PDV "+ self.layer.name() +" est invalide", duration=5)

			self.setOrderEditList(feat_list)
		else:
			self.LineView.setLayerTransparency(100)
		self.iface.mapCanvas().refreshAllLayers()
	##################################################################################################################################

	def selfCheck(self):
		ret = True
		try:
			self.verifyOrder()
			if self.orderValid == False:
				ret = "l'ordre est invalide, vérifiez l'ordre et recommencez."
				raise RuntimeError(ret)
			for feature in self.layer.getFeatures():
				for i in range(feature.fields().count()):
					if feature.attribute(feature.fields().field(i).name()) == None:
						ret = "Le champ \"" + feature.fields().field(i).name() + "\" du point a l'ordre " + str(feature.attribute(feature.fields().field(0).name())) + " est null."
						raise RuntimeError(ret)
		except RuntimeError:
			pass
		return ret

	def createTrajectory(self, step):
		Str = "Vecteur aérien"
		va = QgsMapLayerRegistry.instance().mapLayersByName(Str.decode('utf-8'))[0]
		layerPointTraj = self.createTrajLayer(self.layer, step, va)
		self.layerMenu = QgsProject.instance().layerTreeRoot()
		self.rmTraj(self.layer.name()[11:])
		self.traj = Trajectory(self.iface, self.layer.name()[11:], self.layerMenu, layerPointTraj, None, None, None)

	def createTrajLayer(self, pdvLayer, step, VA): #(self, layer de points du plan de vol, le pas de calcul, le layer du VA)
		################ recupere le nom du layer de trajectoire ##################
		name = "trajectory_" + pdvLayer.name()[11:]
		########################################################################

		################## récupère le seul feature du layer VA qui représente en fait le VA ##################
		VAFeat = None
		for f in VA.getFeatures():
			VAFeat = f
		##########################################################################################

		################## création du layer en memoire ##################
		trajLayer = QgsVectorLayer("Point", name, "memory")

		trajLayer.dataProvider().addAttributes([QgsField("altitude", QVariant.Double), QgsField("vitesse", QVariant.Double), QgsField("nom VA", QVariant.String)]) #ajout des fields
		trajLayer.updateFields()
		########################################################################

		################## calcul les points de la trajectoire ##################

		points = []
		feat_list = []
		geometryObject = QGeometrie(QgsProject.instance())

		for feature in self.layer.getFeatures():
			feat_list.append(feature)

		#################### tri par ordre des features ########################
		def getKey(item):
			return int(item.attribute(item.fields().field(0).name()))
		feat_list = sorted(feat_list, key=getKey)
		########################################################################

		#################### remplit le tableau "points" de QgsPoints du pdv ########################
		for feat in feat_list:
			points.append(feat.geometry().asPoint())
		########################################################################

		#################### ecrase points avec les points de la trajectoire ########################
		points = geometryObject.generateTrajectory(points, 1)
		########################################################################

		##############################################################

		################## fake modification pour démarquer la trajectoire ##################
		newFeats = []
		for point in points:
			newFeat = QgsFeature(trajLayer.pendingFields())
			newFeat.setAttribute("nom VA", VAFeat.attribute("Nom"))
			newFeat.setGeometry(QgsGeometry.fromPoint(point))
			newFeats.append(newFeat)
		trajLayer.dataProvider().addFeatures(newFeats)
		########################################################################################## 

		return trajLayer #retourne un layer de points

	# fonction pour supprimer la trajectoire si le pdv est changé 
	def rmTraj(self, name):
		if QgsProject.instance().layerTreeRoot() != None:
			for layer in QgsMapLayerRegistry.instance().mapLayers().values():
				if layer.name() == "lineTraj_"+name or layer.name() == "trajectory_"+name or layer.name() == "impactAreas_"+name or layer.name() == "multiImpactAreas_"+name:
					QgsProject.instance().layerTreeRoot().findLayer(layer.id()).parent().removeChildNode(QgsProject.instance().layerTreeRoot().findLayer(layer.id()))