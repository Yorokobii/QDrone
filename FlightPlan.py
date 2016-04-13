# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class FlightPlan(QgsVectorLayer):

  trajectory = None
  id_pdv = 0

  def __init__(self, iface, id_pdv, session_name, file_path=None, file_name=None):
    self.iface = iface
    self.id_pdv = id_pdv
    self.session_name = session_name
    self.file_path = file_path
    self.file_name = file_name

    if self.file_path == None: #si on cree un plan de vol
        QgsVectorLayer.__init__(self, "Point", "flightPlan"+str(self.id_pdv), "memory")
        QgsMapLayerRegistry.instance().addMapLayer(self)
        self.startEditing()
        self.data = self.dataProvider()
        self.data.addAttributes([QgsField("Ordre", QVariant.Double), QgsField("Longitude", QVariant.Double), QgsField("Latitude", QVariant.Double), QgsField("Altitude", QVariant.Double), QgsField("Type", QVariant.String), QgsField("Vitesse", QVariant.Double), QgsField("Rayon de virage", QVariant.Double), QgsField("Taux de roulis", QVariant.Double)])
        self.commitChanges()
        directory = QDir(QDir.currentPath())
        directory.cdUp()
        directory.cd("apps/qgis/python/plugins/QDrone/sessions")
        path = directory.path()
        del directory
        QgsVectorFileWriter.writeAsVectorFormat(self, path + "/" + session_name +"/flightPlan"+str(self.id_pdv)+".shp", "utf-8", None, "ESRI Shapefile")
        
    else: #si on charge un plan de vol
        if self.file_name == None: #si on charge un fichier hors d'une session
            QgsVectorLayer.__init__(self, file_path, "flightPlan"+str(self.id_pdv), "ogr")
            QgsMapLayerRegistry.instance().addMapLayer(self)
            directory = QDir(QDir.currentPath())
            directory.cdUp()
            directory.cd("apps/qgis/python/plugins/QDrone/sessions")
            path = directory.path()
            del directory
            QgsVectorFileWriter.writeAsVectorFormat(self, path+"/"+self.session_name+"/flightPlan"+str(self.id_pdv)+".shp", "utf-8", None, "ESRI Shapefile")
        else: #si on charge un fichier de session
            Str = self.file_name[:-4]
            QgsVectorLayer.__init__(self, file_path, Str, "ogr")
            QgsMapLayerRegistry.instance().addMapLayer(self)
    self.iface.messageBar().clearWidgets()
    self.committedGeometriesChanges.connect(self.geoChange)
    self.committedAttributeValuesChanges.connect(self.attrChange)
    self.featureAdded.connect(self.featAdded)
    self.editingStopped.connect(self.rewrite)

  def testDisplay(self, featureID):
    popup = QMessageBox()
    popup.setText("test")
    popup.exec_()

  def featAdded(self, featureID):
    layer = self.iface.activeLayer()
    features = self.getFeatures()
    feat = None
    defaultAltitude = 100
    for feature in features:
        if feature.id() == featureID:

            feat = QgsFeature(feature)
            xfeat = feat.geometry().asPoint().x()
            yfeat = feat.geometry().asPoint().y()

            fieldx = feature.fields().field(1)
            fieldy = feature.fields().field(2)
            null = False
            x = feature.attribute(fieldx.name())
            if x == NULL:
                x = xfeat
                feat.setAttribute(fieldx.name(), xfeat)
                null = True
            y = feature.attribute(fieldy.name())
            if y == NULL:
                y = yfeat
                feat.setAttribute(fieldy.name(), yfeat)
                null = True
            feat.geometry().translate(x-xfeat, y-yfeat)

            if feature.attribute(feature.fields().field(3).name()) == NULL:
                feat.setAttribute(feature.fields().field(3).name(), defaultAltitude)
                null = True

            if xfeat != x or yfeat != y or null == True:
                layer.deleteFeature(feature.id())
                layer.addFeature(feat)

  def geoChange(self, layerid, geoMap):
    layer=None
    for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
        if lyr.id() == layerid:
            layer = lyr
            break

    FeaturesIds = geoMap.keys()

    for i in range(len(FeaturesIds)):
        x = geoMap[FeaturesIds[i]].asPoint().x()
        y = geoMap[FeaturesIds[i]].asPoint().y()
        layer.changeAttributeValue(FeaturesIds[i], 1, x)
        layer.changeAttributeValue(FeaturesIds[i], 2, y)

  def attrChange(self, layerid, changedAttributesValues):
    layer=None
    for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
        if lyr.id() == layerid:
            layer = lyr
            break

    features = layer.getFeatures()
    FeaturesIds = changedAttributesValues.keys()
    del_featID = []
    new_feat = []

    for i in range(len(FeaturesIds)):

        fieldsList = changedAttributesValues[FeaturesIds[i]].keys()
        x = None
        xfeat = None
        y = None
        yfeat = None
        feat = None
        del_feature = None

        for feature in features:

            if feature.id() == FeaturesIds[i]:
                feat = QgsFeature(feature)
                xfeat = feat.geometry().asPoint().x()
                yfeat = feat.geometry().asPoint().y()
                x = xfeat
                y = yfeat
                del_feature = feature
            else:
                feat = None

            if feat != None:
                for j in range(len(fieldsList)):
                    if fieldsList[j] == 1: # si le field est celui de la longitude
                        attrMap = changedAttributesValues[FeaturesIds[i]]
                        x = attrMap[fieldsList[j]]
                    if fieldsList[j] == 2: # si le field est celui de la latitude
                        attrMap = changedAttributesValues[FeaturesIds[i]]
                        y = attrMap[fieldsList[j]]

                feat.geometry().translate(x-xfeat, y-yfeat)
                del_featID.append(del_feature.id())
                new_feat.append(feat)

    for i in range(len(del_featID)):
        layer.deleteFeature(del_featID[i])
        layer.addFeature(new_feat[i])

  def rewrite(self):
    directory = QDir(QDir.currentPath())
    directory.cdUp()
    directory.cd("apps/qgis/python/plugins/QDrone/sessions")
    path = directory.path()
    del directory
    QgsVectorFileWriter.writeAsVectorFormat(self, path+"/"+self.session_name+"/flightPlan"+str(self.id_pdv)+".shp", "utf-8", None, "ESRI Shapefile")