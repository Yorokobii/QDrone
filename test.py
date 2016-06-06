#########log
QgsMessageLog.logMessage("lol", 'tests', QgsMessageLog.INFO)

#########write csv
QgsVectorFileWriter.writeAsVectorFormat(layer, "C:/Users/user/Desktop/Nouveau dossier/test.csv", "utf-8", None, "csv")

layer = QgsVectorLayer("LineString", "test", "memory")
data = layer.dataProvider()
seg = QgsFeature()
seg.setGeometry(QgsGeometry.fromPolyline([QgsPoint(0,0), QgsPoint(10,0), QgsPoint(0,10)]))
data.addFeatures([seg])
layer.updateExtents()
QgsMapLayerRegistry.instance().addMapLayers([layer])
