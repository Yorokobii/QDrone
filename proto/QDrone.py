# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QDrone
                                 A QGIS plugin
 Compute Overflown Population Density
                              -------------------
        begin                : 2014-10-13
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Yann LEPAGE
        email                : yann.lepage@intradef.gouv.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os.path
import os
import re
import subprocess
import socket
import types
import math
import qgis.analysis
import processing

from subprocess import *
from PIL import Image
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from QDrone_dialog import QDroneDialog
from QDConfReader import *
from QDCamcopterExporter import *
from math import *
from qgis.gui import *
from owslib.crs import *
from osgeo import  *
import gc
from msilib.schema import SelfReg
from _socket import SOCK_STREAM


#from _overlapped import *


# Initialize Qt resources from file resources.py
# Import the code for the dialog
class QDrone:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'QDrone_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = QDroneDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&QDrone')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'QDrone3')
        self.toolbar.setObjectName(u'QDrone4')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('QDrone', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the InaSAFE toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = QgsApplication.prefixPath()+"/python/plugins/QDrone/"
        self.add_action(
            icon_path+"QDrone_Init_icons_256.png",
            text=self.tr(u'Initialize project...'),
            callback=self.runInitialize,
            parent=self.iface.mainWindow())
        self.add_action(
            icon_path+"QDrone_Density_icons_256.png",
            text=self.tr(u'Compute density'),
            callback=self.runComputeDensity,
            parent=self.iface.mainWindow())
        self.add_action(
            icon_path+"QDrone_Intervisi_icons_256.png",
            text=self.tr(u'Compute aerea density'),
            callback=self.runComputeDensityArea,
            parent=self.iface.mainWindow())
        self.add_action(
            icon_path+"QDrone_Intervisi_icons_256.png",
            text=self.tr(u'Compute intervisibility'),
            callback=self.runIntervisibility,
            parent=self.iface.mainWindow())
        self.add_action(
            icon_path+"QDrone_Intervisi_icons_256.png",
            text=self.tr(u'Schiebel Export'),
            callback=self.runSchiebelExport,
            parent=self.iface.mainWindow())




    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&QDrone'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass 

    def runInitialize(self):
        """Run method that performs all the real work"""
        # show the dialog
        msgBox=QMessageBox ()
        msgBox.setText("Caution !\r\nBy performing this action, you will reset your project and probably loosing all your curent work.")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        # Run the dialog event loop
        result = msgBox.exec_()
        # See if OK was pressed
        if result==QMessageBox.Ok :
            self.initializeActions()
            pass
    

    
    def initializeActions(self):
        mapCanvas=self.iface.mapCanvas()
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        #TODO : Remove all folders
        #QgsProject.instance().clear()
        #QgsProject.instance().clearProperties()
        confReader=QDConfReader(QgsProject.instance())
        #Updating Conf Reader    
        filename = QFileDialog.getOpenFileName(None, 'Select Q-Drone property file',QgsProject.instance().readPath("./"),'*.qdr')
        print("FileName")
        print(filename)
        if len(filename)>0:
            confReader.processReading(filename)

            # Flight Plan layer, Impact area Layer and Trajectory Layer Init
            flightPlanLayerTemp=QgsVectorLayer("LineString?crs=epsg:32631&field=id:string&field=altitude_ft:double&field=speed_kt:double&field=wind_kt:double","flightPlan","memory")
            trajectoryLayerTemp=QgsVectorLayer("LineString?crs=epsg:32631&field=id:string&field=altitude_ft:double&field=speed_kt:double&field=wind_kt:double","trajectory","memory")
            impactAreaLayerTemp=QgsVectorLayer("Polygon?crs=epsg:32631&field=id:string&field=area:double&field=populationCovered:double&field=densite:double","Impact area","memory")
            gcsLayerTemp=QgsVectorLayer("Point?crs=epsg:32631&field=id:string","Control station","memory")
            gridTemp=QgsVectorLayer("LineString?crs=epsg:4326&field=id:string","Grid","memory")
            #Create Layers on disk
            error1=QgsVectorFileWriter.writeAsVectorFormat(impactAreaLayerTemp,QgsProject.instance().readPath("./")+"/"+"impactAreaLayer.shp","utf-8",None,"ESRI Shapefile")
            error2=QgsVectorFileWriter.writeAsVectorFormat(flightPlanLayerTemp,QgsProject.instance().readPath("./")+"/"+"flightPlan.shp","utf-8",None,"ESRI Shapefile")
            error3=QgsVectorFileWriter.writeAsVectorFormat(trajectoryLayerTemp,QgsProject.instance().readPath("./")+"/"+"trajectory.shp","utf-8",None,"ESRI Shapefile")      
            error4=QgsVectorFileWriter.writeAsVectorFormat(gcsLayerTemp,QgsProject.instance().readPath("./")+"/"+"gcs.shp","utf-8",None,"ESRI Shapefile")      
            error5=QgsVectorFileWriter.writeAsVectorFormat(gridTemp,QgsProject.instance().readPath("./")+"/"+"grid.shp","utf-8",None,"ESRI Shapefile")      
            print("Error Impact %d"%error1)
            print("Error Flight plan %d"%error2)
            print("Error Trajectory %d"%error3)
            
            # Load Layers from Disk
            flightPlanLayer=QgsVectorLayer(QgsProject.instance().readPath("./")+"/"+"flightPlan.shp","flightPlan","ogr")
            trajectoryLayer=QgsVectorLayer(QgsProject.instance().readPath("./")+"/"+"trajectory.shp","trajectory","ogr")
            impactAreaLayer=QgsVectorLayer(QgsProject.instance().readPath("./")+"/"+"impactAreaLayer.shp","Impact area","ogr")
            gcsLayer=QgsVectorLayer(QgsProject.instance().readPath("./")+"/"+"gcs.shp","Control station","ogr")
            #gridLayer=QgsVectorLayer(QgsProject.instance().readPath("./")+"/"+"grid.shp","Grid","ogr")
            
            # Load density Layer
            self.densityLayerType=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.DENSITY_FILE_TYPE_LABEL,"default")[0]
  
            pathDensityLayer=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.DENSITY_FILE_LABEL,"default")[0]
            print ("path %s"%pathDensityLayer)
            densityLayer=QgsVectorLayer(pathDensityLayer,"Population Density","ogr")
            if not densityLayer.isValid():
                print("Loading density fail")
            
            #Setup FlightPlan colors
            registry = QgsSymbolLayerV2Registry.instance()
            lineMeta = registry.symbolLayerMetadata("SimpleLine")
            markerMeta = registry.symbolLayerMetadata("MarkerLine")
            symbol = QgsSymbolV2.defaultSymbol(flightPlanLayer.geometryType())
            lineLayer = lineMeta.createSymbolLayer({'width': '0.6', 'color': '0,255,0', 'offset': '0', 'penstyle': 'dash', 'use_custom_dash': '0', 'joinstyle': 'bevel', 'capstyle': 'square'})
            markerLayer = markerMeta.createSymbolLayer({'width': '0.26', 'color': '255,0,0', 'rotate': '1', 'placement': 'vertex', 'offset': '0'})
            subSymbol = markerLayer.subSymbol()
            subSymbol.deleteSymbolLayer(0)
            triangle = registry.symbolLayerMetadata("SimpleMarker").createSymbolLayer({'name': 'diamond', 'color': '0,255,0', 'color_border': '0,0,0', 'offset': '0,0', 'size': '5', 'angle': '0'})
            subSymbol.appendSymbolLayer(triangle)
            symbol.deleteSymbolLayer(0)
            symbol.appendSymbolLayer(lineLayer)
            symbol.appendSymbolLayer(markerLayer)
            
            #Replace the renderer of the current layer
            renderer = QgsSingleSymbolRendererV2(symbol)
            flightPlanLayer.setRendererV2(renderer)
            
            #Setup trajectory colors
            registry = QgsSymbolLayerV2Registry.instance()
            lineMeta = registry.symbolLayerMetadata("SimpleLine")
            markerMeta = registry.symbolLayerMetadata("MarkerLine")
            symbol = QgsSymbolV2.defaultSymbol(trajectoryLayer.geometryType())
            lineLayer = lineMeta.createSymbolLayer({'width': '0.5', 'color': '0,0,255', 'offset': '0', 'joinstyle': 'bevel', 'capstyle': 'square'})
            markerLayer = markerMeta.createSymbolLayer({'width': '0.3', 'color': '0,0,255', 'rotate': '1', 'placement': 'vertex', 'offset': '0'})
            subSymbol = markerLayer.subSymbol()
            subSymbol.deleteSymbolLayer(0)
            triangle = registry.symbolLayerMetadata("SimpleMarker").createSymbolLayer({'name': 'circle', 'color': '0,0,255', 'color_border': '0,0,255', 'offset': '0,0', 'size': '0,1', 'angle': '0'})
            subSymbol.appendSymbolLayer(triangle)
            symbol.deleteSymbolLayer(0)
            symbol.appendSymbolLayer(lineLayer)
            symbol.appendSymbolLayer(markerLayer)
            #Replace the renderer of the current layer
            renderer = QgsSingleSymbolRendererV2(symbol)
            trajectoryLayer.setRendererV2(renderer)             
            
            #Setup Impact Area colors
            opacity=0.6
            yellowLimit=QgsProject.instance().readNumEntry(QDConfReader.QDRONE_LABEL,QDConfReader.UAV_DENSITY_YELLOW_LABEL,0)[0]
            redLimit=QgsProject.instance().readNumEntry(QDConfReader.QDRONE_LABEL,QDConfReader.UAV_DENSITY_RED_LABEL,0)[0]
            rangeList=[]
            
            # green range
            greenColor=QColor('#00ff00')
            greenSymbol=QgsFillSymbolV2()
            greenSymbol.setColor(greenColor)
            greenSymbol.setAlpha(opacity)

            greenRange=QgsRendererRangeV2(0,yellowLimit,greenSymbol,"<%10.0f inhbt/km2"%yellowLimit)
            rangeList.append(greenRange)
            # orange range
            orangeColor=QColor('#ff8000')
            orangeSymbol=QgsFillSymbolV2()
            orangeSymbol.setColor(orangeColor)
            orangeSymbol.setAlpha(opacity)
            orangeRange=QgsRendererRangeV2(yellowLimit,999999999999,orangeSymbol,">%10.0f inhbt/km2"%yellowLimit)
            rangeList.append(orangeRange)       
            impactRenderer=QgsGraduatedSymbolRendererV2('',rangeList)
            impactRenderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
            impactRenderer.setClassAttribute("densite")
            impactAreaLayer.setRendererV2(impactRenderer)
            
            # Setup Density colors    
            opacity=0.8
            rangeList=[]
            # Yellow range
            yellowColor=QColor('#ffff80')
            yellowSymbol=QgsFillSymbolV2()
            yellowSymbol.setColor(yellowColor)
            yellowSymbol.setAlpha(opacity)      
            innerSymbol=yellowSymbol.symbolLayer(0)
            innerSymbol.setBorderColor(yellowColor)
            yellowRange=QgsRendererRangeV2(yellowLimit,redLimit,yellowSymbol,">%10.0f inhbt/km2"%yellowLimit)
            rangeList.append(yellowRange)
            # Red range
            redColor=QColor('#ff0000')
            redSymbol=yellowSymbol=QgsFillSymbolV2()
            redSymbol.setColor(redColor)
            redSymbol.setAlpha(opacity)            
            innerSymbol=redSymbol.symbolLayer(0)
            innerSymbol.setBorderColor(redColor)
            redRange=QgsRendererRangeV2(redLimit,999999999999,redSymbol,">%10.0f inhbt/km2"%redLimit)
            rangeList.append(redRange)       
            densityRenderer=QgsGraduatedSymbolRendererV2('',rangeList)
            densityRenderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
            densityRenderer.setClassAttribute("densite")
            densityLayer.setRendererV2(densityRenderer)
            
            #Setup GCS point and appareance
            gcsProvider=gcsLayer.dataProvider()
            fet = QgsFeature()
            crsSrc=QgsCoordinateReferenceSystem(4326)#WGS84
            crsDest=QgsCoordinateReferenceSystem(32631) #UTM 31N
            transfo=QgsCoordinateTransform(crsSrc,crsDest)
            lat0=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GCS_POSITION_LAT_LABEL,"default")[0])
            lon0=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GCS_POSITION_LON_LABEL,"default")[0])
            gcsPoint=transfo.transform(QgsPoint(lon0,lat0))
            fet.setGeometry( QgsGeometry.fromPoint(gcsPoint) )
            gcsProvider.addFeatures( [ fet ] )
            gcsLayer.commitChanges()
            #GCS appareance
            registry = QgsSymbolLayerV2Registry.instance()
            symbol = QgsSymbolV2.defaultSymbol(gcsLayer.geometryType())
            triangle = registry.symbolLayerMetadata("SimpleMarker").createSymbolLayer({'name': 'triangle', 'color': '0,255,0', 'color_border': '0,255,0', 'offset': '0,0', 'size': '2', 'angle': '0'})
            symbol.deleteSymbolLayer(0)
            symbol.appendSymbolLayer(triangle)
            #Replace the renderer of the current layer
            renderer = QgsSingleSymbolRendererV2(symbol)
            gcsLayer.setRendererV2(renderer)          
            
            #Setup Grid (WGS84)
            lat0=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GCS_POSITION_LAT_LABEL,"default")[0])
            lon0=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GCS_POSITION_LON_LABEL,"default")[0])
            deltaLat=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.DTED_DELTA_DEG_LABEL,"default")[0])
            #print("deltalat ")
            #print(deltaLat)
            centerx=floor(10*lon0)/10
            centery=floor(10*lat0)/10
            width=ceil(2*deltaLat)
            height=ceil(2*deltaLat)
            cellsize = 0.1
            crsDest=QgsCoordinateReferenceSystem(4326)
            gridPath=QgsProject.instance().readPath("./")+"/"+"grid.shp"
            processing.runandload("qgis:creategrid", cellsize, cellsize, width, height, centerx, centery, 1,crsDest.authid(), gridPath)
            gridLayer=QgsVectorLayer(QgsProject.instance().readPath("./")+"/"+"grid.shp","Grid","ogr")
            blackColor=QColor(0, 0, 0, 255)
            noColor=QColor(255, 255, 255, 0)
            blackSymbol=QgsFillSymbolV2()        
            innerSymbol=blackSymbol.symbolLayer(0)
            innerSymbol.setColor(noColor)
            innerSymbol.setBorderColor(blackColor)
            innerSymbol.setBorderWidth(0.1)
            renderer = QgsSingleSymbolRendererV2(blackSymbol)
            gridLayer.setRendererV2(renderer)
            #Create Groups in registry
            root=QgsProject.instance().layerTreeRoot()
            root.removeAllChildren()
            rasterNode=root.insertGroup(0,"Rasters")
            dtedNode=root.insertGroup(1,"DTED")
            
            
            #init DTED and GeoTIFF files
            
            self.initDTEDandGeoTIFF(rasterNode,dtedNode)
            
            # Update QgsMapLayerRegistry
            QgsMapLayerRegistry.instance().addMapLayer(densityLayer)  
            QgsMapLayerRegistry.instance().addMapLayer(impactAreaLayer)  
            QgsMapLayerRegistry.instance().addMapLayer(flightPlanLayer)
            QgsMapLayerRegistry.instance().addMapLayer(gridLayer)
            QgsMapLayerRegistry.instance().addMapLayer(gcsLayer)
            QgsMapLayerRegistry.instance().addMapLayer(trajectoryLayer)
            
            
            
            
    def initDTEDandGeoTIFF(self,rasterNode,dtedNode):
         #Create Groups
         #QgsMapLayerRegistry.instance().addGroup("DTED")
         #QgsMapLayerRegistry.instance().addGroup("Rasters")
         
         #Read DTED, GeoTIFF and GCS parameters
         pathRelativeDTED=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.DTED_FOLDER_LABEL,"default")[0]
         #print(pathRelativeDTED)
         pathRelativeGeoTIFF=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GEOTIFF_FOLDER_LABEL,"default")[0]
         pathRelativeMergedDTED=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.MERGED_DTED_FILE_LABEL,"default")[0]
         #print(pathRelativeMergedDTED)        
         
         DTEDType=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.DTED_TYPE_LABEL,"default")[0]
         print(DTEDType)      
         GeoTIFFType=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GEOTIFF_TYPE_LABEL,"default")[0]
         worldFileType=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GEOTIFF_WORLDFILE_LABEL,"default")[0]
         projFileType=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GEOTIFF_PROJECTION_LABEL,"default")[0]      
         deltaDegDTED=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.DTED_DELTA_DEG_LABEL,"default")[0])
         deltaDegGeoTIFF=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GEOTIFF_DELTA_DEG_LABEL,"default")[0])
         gcsLatDeg=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GCS_POSITION_LAT_LABEL,"default")[0])
         gcsLonDeg=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GCS_POSITION_LON_LABEL,"default")[0])
         
         #Compute list of relevant DTED and GeoTIFF File
         dtedNameList=self.parseDTEDFolder(QgsProject.instance().readPath(pathRelativeDTED), DTEDType,gcsLatDeg,gcsLonDeg,deltaDegDTED)
         #print(dtedNameList)
         geoTIFFNameList=self.parseGeoTIFFFolder(QgsProject.instance().readPath(pathRelativeGeoTIFF),gcsLatDeg,gcsLonDeg,deltaDegGeoTIFF,GeoTIFFType,worldFileType,projFileType)
         for geoTIFFName in geoTIFFNameList:
             rLayer=QgsRasterLayer(geoTIFFName,QFileInfo(geoTIFFName).baseName())
             QgsMapLayerRegistry.instance().addMapLayer(rLayer,False)
             rasterNode.insertChildNode(0, QgsLayerTreeLayer(rLayer))         
         mergedDTEDAbsolutePath=QgsProject.instance().readPath(pathRelativeMergedDTED)
         #print(mergedDTEDAbsolutePath)

         self.mergeAndWrapDTED(dtedNameList,mergedDTEDAbsolutePath )
         rLayer=QgsRasterLayer(mergedDTEDAbsolutePath,QFileInfo(mergedDTEDAbsolutePath).baseName())
         QgsMapLayerRegistry.instance().addMapLayer(rLayer,False)
         dtedNode.insertChildNode(0, QgsLayerTreeLayer(rLayer))  
    
    
    def mergeAndWrapDTED(self,dtedNameList,exportFilePath):
        cmdLineDelete="rm "+exportFilePath
        #print(cmdLineDelete)
        call(cmdLineDelete)

        dtedNameConcat=""
        for dtedName in dtedNameList:
            dtedNameConcat=dtedNameConcat+" "+dtedName
        #print("dtedNameConcat")
        #print(dtedNameConcat)
        cmdLineMerge="gdal_merge.bat -o "+exportFilePath[:-4]+"temps.TIF "+dtedNameConcat
        #print(cmdLineMerge)
        call(cmdLineMerge)
        cmdLineWarp="gdalwarp -t_srs EPSG:32631 "+exportFilePath[:-4]+"temps.TIF "+exportFilePath
        #print(cmdLineWarp)
        call(cmdLineWarp)
        cmdLineDelete="rm "+exportFilePath[:-4]+"temps.TIF"
        call(cmdLineDelete)


    def runComputeDensityArea(self): 

        #Load existing layers
        print("Load existing layers ... ")
        densLayer=(QgsMapLayerRegistry.instance().mapLayersByName("Population Density"))[0]
        impactLayer=(QgsMapLayerRegistry.instance().mapLayersByName("Zone"))[0]
                        
       #Update population Field
        print("Update population Field ... ")
        densFeatures=densLayer.getFeatures()
        buffFeatures=impactLayer.getFeatures()
        for impactZone in buffFeatures:
            totalPopulation=0
            totalsurface=0
            request=QgsFeatureRequest()    
            request.setFilterRect(impactZone.geometry().boundingBox())

            for f in densLayer.getFeatures(request):
                if f.geometry().overlaps(impactZone.geometry()):
                    #if (self.DensityLayerType==200):
                    population=f.attributes()[3]
                    #else:
					#	population=f.attributes()[3]
                    totalPopulation=totalPopulation+population
                                        

        totalsurface = impactZone.geometry().area()/1000000

        if (totalsurface==0):
           densite=0
           #print "!!! Pas d'intersection "
           self.iface.messageBar().pushMessage("QDrone","Pas d'intersection")
        else:
           densite=totalPopulation/totalsurface
           #print "D = ", densite, " - S = ", totalsurface, " - P = ", totalPopulation, " - nbIntersections = ", nbZones  
           self.iface.messageBar().pushMessage("QDrone","D = %0.0f"%densite)

        
        print ("END")
        
        
    def runComputeDensity(self): 
 
        #Load existing layers
        print("Load existing layers ... ")
        densLayer=(QgsMapLayerRegistry.instance().mapLayersByName("Population Density"))[0]
        fpLayer=(QgsMapLayerRegistry.instance().mapLayersByName("flightPlan"))[0]
        impactLayer=(QgsMapLayerRegistry.instance().mapLayersByName("Impact area"))[0]
        trajectoryLayer=(QgsMapLayerRegistry.instance().mapLayersByName("trajectory"))[0]
        
        fpFeatures=fpLayer.getFeatures()
        
        tempSegment=QgsVectorLayer("LineString?crs=epsg:32631&field=segmentId:string&field=sideBuffer:double","tempSegment","memory")
        
        fieldsSegment=QgsFields()
        fieldsSegment.append(QgsField("segmentId"))
        fieldsSegment.append(QgsField("sideBuffer"))

        tempImpact=QgsVectorLayer("Polygon?crs=epsg:32631&field=segmentId:string&field=area:double&field=population:double&field=density:double","tempImpact","memory")    
        
        fieldsBuffer=QgsFields()
        fieldsBuffer.append(QgsField("segmentId"))
        fieldsBuffer.append(QgsField("area"))
        fieldsBuffer.append(QgsField("population"))
        fieldsBuffer.append(QgsField("density"))

        fieldsImpact=QgsFields()
        fieldsImpact.append(QgsField("segmentId"))
        fieldsImpact.append(QgsField("area"))
        fieldsImpact.append(QgsField("population"))
        fieldsImpact.append(QgsField("density"))
        
        fieldsTrajectory=QgsFields()
        fieldsTrajectory.append(QgsField("segmentId"))
        fieldsTrajectory.append(QgsField("altitude_ft"))
        fieldsTrajectory.append(QgsField("speed_kt"))
        fieldsTrajectory.append(QgsField("wind_kt"))
  
        
        #Create Flight lines from each flightSegments
        print("Create Flight lines from each flightSegments ... ")
        trajectoryLayer.startEditing()
        ids = [f.id() for f in trajectoryLayer.getFeatures()]
        trajectoryLayer.dataProvider().deleteFeatures( ids )
        for flightSegment in fpFeatures:
            fsGeom=flightSegment.geometry()
            fsLine=fsGeom.asPolyline()
            identString=flightSegment.attributes()[0]
            altitude_ft=flightSegment.attributes()[1]
            speed_kt=flightSegment.attributes()[2]
            wind_kt=flightSegment.attributes()[3]
            rollLimit=QgsProject.instance().readNumEntry(QDConfReader.QDRONE_LABEL,QDConfReader.UAV_ROLL_ANGLE_LABEL,0)[0]
            turningRadius=self.computeTurningRadius(rollLimit, speed_kt)
            trajectoryPoints=self.generateTrajectory(fsLine,turningRadius) 
            lineFeature=QgsFeature(fieldsTrajectory,4)
            lineFeature.setAttribute(0,identString)
            lineFeature.setAttribute(1,altitude_ft)
            lineFeature.setAttribute(2,speed_kt)
            lineFeature.setAttribute(3,wind_kt)
            lineFeature.setGeometry(QgsGeometry.fromPolyline(trajectoryPoints))
            trajectoryLayer.dataProvider().addFeatures([lineFeature])
        trajectoryLayer.commitChanges()
        
        #Create buffers from flightLines
        print("Create buffers from flightLines ... ")
        lineFeatures=trajectoryLayer.getFeatures() 
        for lineSegment in lineFeatures:
            identString=lineSegment.attributes()[0]
            altitude_ft=lineSegment.attributes()[1]
            speed_kt=lineSegment.attributes()[2]
            wind_kt=lineSegment.attributes()[3] 
            impactAreaFactor=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.IMPACT_AREA_FACTOR_LABEL,"default")[0])
            pointsTabletemp=lineSegment.geometry()
            pointsTable=pointsTabletemp.asPolyline()
            for i in range(0,len(pointsTable)-1):
                fsPoint1=pointsTable[i]
                fsPoint2=pointsTable[i+1]
                groundHeightFt=self.computeAltitude_ft(fsPoint1,fsPoint2,altitude_ft,wind_kt)             
                frontBuffer=self.computeFrontBuffer(altitude_ft,speed_kt,wind_kt,0.0,impactAreaFactor)
                sideBuffer=self.computeSideBuffer(altitude_ft,speed_kt,wind_kt,0.0,impactAreaFactor)   
                fsPoint3=self.displacePoint2(fsPoint1,fsPoint2,frontBuffer)
                tempGeometry=QgsGeometry.fromPolyline([fsPoint1,fsPoint3])
                bufferedArea=tempGeometry.buffer(sideBuffer,100)
                buffSurface=bufferedArea.area()
                feat=QgsFeature(fieldsImpact,3)
                feat.setAttribute(0,identString)
                feat.setAttribute(1,buffSurface)                
                feat.setGeometry(bufferedArea)
                tempImpact.dataProvider().addFeatures([feat])
                
       #Update population Field
        print("Update population Field ... ")
        densFeatures=densLayer.getFeatures()
        buffFeatures=tempImpact.getFeatures()
        tempImpact.startEditing()
        for impactZone in buffFeatures:
            totalPopulation=0
            request=QgsFeatureRequest()    
            request.setFilterRect(impactZone.geometry().boundingBox())
            for f in densLayer.getFeatures(request):
                #FP_suppress : population=f.attributes()[4]
                #print("in densLayer")
                if f.geometry().overlaps(impactZone.geometry()):
                    #print("overlaps")
                    #if (DensityLayerType==200):
                    population=f.attributes()[4]
                    #else:
					#	population=f.attributes()[3]
						
                    totalPopulation=totalPopulation+population
                    
                    
            impactZone.setAttribute(2,totalPopulation)
            densite=1000000*totalPopulation/impactZone.attributes()[1]
            impactZone.setAttribute(3,densite)
            tempImpact.updateFeature(impactZone)
            #print("Population %d"% totalPopulation)
            #print("Densite %d"% densite)
        tempImpact.commitChanges()
        
        #Fusion des elements de tempImpact
        print("Fusion des elements de tempImpact ...")
        impactLayer.startEditing()
        ids = [f.id() for f in impactLayer.getFeatures()]
        impactLayer.dataProvider().deleteFeatures( ids )
        allFlightPlanPopulation=0
        allFlightPlanSurface=0
        print("Begin fusion...")
        for fplan in fpLayer.getFeatures():
            identString=fplan.attributes()[0]
            request=QgsFeatureRequest()
            request.setFilterExpression ('"segmentId" = \''+ identString+'\'' )
            surf=0
            population=0
            for impactZone in tempImpact.getFeatures(request):
                surf=surf+impactZone.attributes()[1]
                population=population+impactZone.attributes()[2]
                geom=impactZone.geometry() 
            #print("Population : %d"%population)
            #print("surface : %d"%surf)
            density=1000000*population/surf
            listImpactZone=[feat for feat in tempImpact.getFeatures(request)]
            feat=QgsFeature(fieldsImpact,3)
            feat.setAttribute(0,identString)
            feat.setAttribute(1,surf)
            feat.setAttribute(2,population)
            feat.setAttribute(3,density)
            allFlightPlanPopulation=allFlightPlanPopulation+population
            allFlightPlanSurface=allFlightPlanSurface+surf
            for g in tempImpact.getFeatures(request):
                geom=geom.combine(g.geometry())
            feat.setGeometry(geom)
            impactLayer.dataProvider().addFeatures([feat])            
        impactLayer.commitChanges()      
 
        alldensity=1000000*float(allFlightPlanPopulation)/float(allFlightPlanSurface)
        self.iface.messageBar().pushMessage("QDrone","Average density computed %0.0f inHbt/km2"%alldensity)
        print ("END")
        

    def runIntervisibility(self):
        # Request intervisibility height
        inputBox=QInputDialog()
        inputBox.setInputMode(QInputDialog.TextInput)
        inputBox.setLabelText("Set aircraft height for intervisibility (in ft AGL) :")
        ok=inputBox.exec_()
        altString_ft=inputBox.textValue()
        altitudeCible_m=float(altString_ft)*0.3048        
        
        #Read parameters
        refraction_coef_string=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.REFFRACTION_COEF_LABEL,"default")[0]
        grass7Path=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GRASS7_PATH_LABEL,"default")[0]
        intervisibilityFileRelPath=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.INTERVISIBILITY_FILE_LABEL,"default")[0]
        gcsAntennaHeightString=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GCS_ANTENNA_HEIGHT_M_LABEL,"default")[0]
        intervibilityFile=QgsProject.instance().readPath(intervisibilityFileRelPath)+"_"+altString_ft+"_ft.tif"
        grassBinPath=grass7Path+"/bin/"
        pathRelativeMergedDTED=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.MERGED_DTED_FILE_LABEL,"default")[0]        
        mergedDTEDAbsolutePath=QgsProject.instance().readPath(pathRelativeMergedDTED)

        gcsLat=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GCS_POSITION_LAT_LABEL,"default")[0])
        gcsLon=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.GCS_POSITION_LON_LABEL,"default")[0])
        delta_deg=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.DTED_DELTA_DEG_LABEL,"default")[0])
        delta_m=delta_deg*60*1852
        regionRes=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.INTERVISI_COMPUTATION_STEP_M_LABEL,"default")[0]
        
        #Generate grass command
        crsSrc=QgsCoordinateReferenceSystem(4326)#WGS84
        crsDest=QgsCoordinateReferenceSystem(32631) #UTM 31N
        transfo=QgsCoordinateTransform(crsSrc,crsDest)
        pt0=transfo.transform(QgsPoint(gcsLon,gcsLat))
        
        cmdLineViewshed1="\""+grassBinPath+"g.proj.exe\" -tc epsg=32631 location=projLocation"
        cmdLineViewshed2="\""+grassBinPath+"r.in.gdal\" -o input=\""+mergedDTEDAbsolutePath.replace('/','\\')+"\" output=projDTED.dt1 target=projLocation title=\"titleProjDTED\" --overwrite"
        cmdLineViewshed3="\""+grassBinPath+"g.region.exe\" n="+str(int(pt0.y()+delta_m))+" s="+str(int(pt0.y()-delta_m))+" e="+str(int(pt0.x()+delta_m))+" w="+str(int(pt0.x()-delta_m))+" res="+regionRes
              

        cmdLineViewshed="\""+grassBinPath+"r.viewshed.exe\" -c -r -b input=projDTED.dt1"
        cmdLineViewshed=cmdLineViewshed+" output=intervisi.tif coordinates="+str(pt0.x())+","+str(pt0.y())
        cmdLineViewshed=cmdLineViewshed+" observer_elevation="+gcsAntennaHeightString+" target_elevation="+str(altitudeCible_m)
        cmdLineViewshed=cmdLineViewshed+"memory=2048 max_distance="+str(delta_m)+" refraction_coeff="+refraction_coef_string
        cmdLineViewshed=cmdLineViewshed+" --overwrite"
        cmdLineViewshed4="rm "+intervibilityFile
        cmdLineViewshed5="\""+grassBinPath+"r.out.gdal\" -f input=intervisi.tif format=GTiff output=\""+intervibilityFile.replace('/','\\')+"\""
                
        print(cmdLineViewshed)
        #To be deleted
        #cmdLineViewshed="\""+grassBinPath+"r.viewshed.exe\" --help"
        
        #Configure grass execution environment
        myEnv=os.environ
        newPath=myEnv["PATH"]+grass7Path+"\\bin;"
        newPath=newPath+grass7Path+"\\etc;"
        newPath=newPath+grass7Path+"\\etc\\python;"
        newPath=newPath+grass7Path+"\\lib;"
        newPath=newPath+grass7Path+"\\extralib;"
        newPath=newPath+grass7Path+"\\msys\\bin;"
        gisRCPath=QgsApplication.prefixPath()+"/python/plugins/QDrone/projLocation/.gisRCFile"
        self.createLocationFile(gisRCPath)
        ldLibPath=grass7Path+"\\lib;"
        
        
        myEnv["PATH"]=newPath.encode('utf8')
        myEnv["GISBASE"]=grass7Path.encode('utf8')
        myEnv["GISRC"]=gisRCPath.encode('utf8')
        myEnv["LD_LIBRARY_PATH"]=ldLibPath.encode('utf8')

        #Execute command

        try:
            process1=subprocess.check_call(cmdLineViewshed1,env=myEnv)
        except:
            print("g.proj failed")
        process2=subprocess.check_call(cmdLineViewshed2,env=myEnv)
        process3=subprocess.check_call(cmdLineViewshed3,env=myEnv)
        process=subprocess.check_call(cmdLineViewshed,env=myEnv)
        try:
            #process4=subprocess.check_call(cmdLineViewshed4,env=myEnv)
            if os.path.isfile(intervibilityFile):
                os.remove(intervibilityFile)
        except:
            print("Intervisi file removing failed")
        process5=subprocess.check_call(cmdLineViewshed5,env=myEnv)
        
        #Intervisibility layer setting and loading
        redComponent=int(255*float(altString_ft)/10000)%255
        intervisiLayer=QgsRasterLayer(intervibilityFile,QFileInfo(intervibilityFile).baseName())
        colorList=[QgsColorRampShader.ColorRampItem(0,QColor(0,0,0,0)),QgsColorRampShader.ColorRampItem(1,QColor(redComponent,0,255,150))]
        myRasterShader=QgsRasterShader()
        myColorRamp=QgsColorRampShader()
        myColorRamp.setColorRampItemList(colorList)
        myColorRamp.setColorRampType(QgsColorRampShader.INTERPOLATED)
        myRasterShader.setRasterShaderFunction(myColorRamp)
        myPseudoRenderer=QgsSingleBandPseudoColorRenderer(intervisiLayer.dataProvider(),intervisiLayer.type(),myRasterShader)
        intervisiLayer.setRenderer(myPseudoRenderer)

        try:
            QgsMapLayerRegistry.instance().addMapLayer(intervisiLayer)
        except:
            print("Map Layer not added")
    
    def runSchiebelExport(self):
        # Request mapName
        inputBox=QInputDialog()
        inputBox.setInputMode(QInputDialog.TextInput)
        inputBox.setLabelText("Set Schiebel map name :")
        ok=inputBox.exec_()
        if ok:
            chartName=inputBox.textValue()
            exportPath=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.SCHIEBEL_EXPORT_PATH_LABEL,"default")[0]        
            camcopExporter=QDCamcopterExporter(self.iface.mapCanvas(),QgsProject.instance(),exportPath,chartName)
            camcopExporter.exportChart()
    
    
    def createLocationFile(self,path):
        try:
            file = open(path,'w')   # Trying to create a new file or open one
            gisdbasePath=QgsApplication.prefixPath()+"/python/plugins/QDrone/"
            file.write("GISDBASE: "+gisdbasePath.replace('/','\\')+"\r\n")
            file.write("LOCATION_NAME: projLocation\r\n")
            file.write("MAPSET: PERMANENT\r\n")
            file.write("GRASS_DB_ENCODING: utf-8\r\n")
            file.write("DEBUG: 0\r\n")
            file.write("GUI: text")
            file.close()

        except:
            print('Location file creation fail')

    
    def computeAltitude_ft(self,fsPoint1,fsPoint2,altitude_ft,wind_kt):
        pathRelativeMergedDTED=QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.MERGED_DTED_FILE_LABEL,"default")[0]        
        mergedDTEDAbsolutePath=QgsProject.instance().readPath(pathRelativeMergedDTED)
        preImpactAreaLayer=QgsVectorLayer("Polygon?crs=epsg:32631&field=id:integer","preImpact","memory")
        fieldsPreImpact=QgsFields()
        fieldsPreImpact.append(QgsField("id"))
        currentLine=QgsGeometry.fromPolyline([fsPoint1,fsPoint2])
        preBuffer=self.computeSideBuffer(altitude_ft, 0, wind_kt, 0, 1)
        
        bufferedArea=currentLine.buffer(preBuffer,100)       
        feat=QgsFeature(fieldsPreImpact,1)
        feat.setAttribute(0,0)
        feat.setGeometry(bufferedArea)
        preImpactAreaLayer.dataProvider().addFeatures([feat])
        preImpactAreaLayer.commitChanges()
        
        zonalStat=qgis.analysis.QgsZonalStatistics(preImpactAreaLayer,mergedDTEDAbsolutePath,"",1)
        zonalStat.calculateStatistics(None)
        
        #Note : preImpact should have only one feature 
        for feat2 in preImpactAreaLayer.getFeatures():
            height_m_string=feat2.attributes()[3]
            height_ft=float(height_m_string)/0.3048
        return height_ft
        
    #This function compute the size of the side Buffer.    
    def computeSideBuffer(self,altitude_ft,speed_kt,wind_kt,ground_height_ft,factor):
        # Return side buffer in meters
        # which is distance due to wind drift during fall time
        hauteur_m=(float(altitude_ft)*0.3048-float(ground_height_ft)*0.3048)
        #H=1/2gt^2 -> t=sqrt(2H/g)
        t=sqrt(2*hauteur_m/9.81);
        drift=(float(wind_kt)*0.514*t)*factor
        #print("Side Drift %0.0f"%drift)
        return drift
 
    #This function compute the size of the front Buffer.     
    def computeFrontBuffer(self,altitude_ft,speed_kt,wind_kt,ground_height_ft,factor):
        hauteur_m=(float(altitude_ft)*0.3048-float(ground_height_ft)*0.3048)
        #H=1/2gt^2 -> t=sqrt(2H/g)
        t=sqrt(2*hauteur_m/9.81);
        drift=float(speed_kt)*0.514*t*factor
        #print("Front Drift %0.0f"%drift)
        return drift

    #This function displace the second point of a give segment within a given distance in meters
    def displacePoint2(self,Point1,Point2,distance):
        x1=Point1.x()
        x2=Point2.x()
        y1=Point1.y()
        y2=Point2.y()
        longueur=sqrt((x2-x1)**2+(y2-y1)**2)
        factor=(longueur+distance)/longueur
        x3=x1+factor*(x2-x1)
        y3=y1+factor*(y2-y1)
        Point3=QgsPoint(x3,y3)
        return Point3
    
    
     #This function displace the first point in direction of point 1 of a given segment within a given distance in meters
    def displacePoint1(self,Point1,Point2,distance):
        x1=Point1.x()
        x2=Point2.x()
        y1=Point1.y()
        y2=Point2.y()
        longueur=sqrt((x2-x1)**2+(y2-y1)**2)
        factor=(distance)/longueur
        x3=x1+factor*(x2-x1)
        y3=y1+factor*(y2-y1)
        Point3=QgsPoint(x3,y3)
        return Point3
    
    def generateTrajectory(self,segmentPoints,turningRadius):
        #segmentPoints is supposed to be a list of points
        test=1
        
        #trajectory sampling calculation
        angleStepDeg=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.TRAJ_TURNING_ANGLE_STEP_DEG_LABEL,"default")[0])
        distStepMin=float(QgsProject.instance().readEntry(QDConfReader.QDRONE_LABEL,QDConfReader.SAMPLING_DIST_MIN_LABEL,"default")[0])
        distStep=max(2*tan((angleStepDeg*pi/180)/2)*turningRadius,distStepMin)
        
        if len(segmentPoints)<3:
            test=0
        else:
            for i in range(1,len(segmentPoints)-1):
                fsPoint1=segmentPoints[i-1]
                fsPoint2=segmentPoints[i]
                fsPoint3=segmentPoints[i+1]
                theta=self.computeAngle(fsPoint1, fsPoint2, fsPoint3)
                uu=self.distance(fsPoint1,fsPoint2)
                vv=self.distance(fsPoint2,fsPoint3)
                if theta==0:
                    test=0
                else:
                    anticip=turningRadius/tan(theta/2)
                    if (anticip>uu or anticip>vv):
                        test=0
        #On cree les points si necessaire
        if test: 
            trajPoints=[segmentPoints[0]]
            nbPoints=len(segmentPoints)
            for i in range(1,nbPoints-1):
                #Generate turns
                fsPoint1=segmentPoints[i-1]
                fsPoint2=segmentPoints[i]
                fsPoint3=segmentPoints[i+1]
                turnCenter=self.computeCenterOfTurn(fsPoint1, fsPoint2, fsPoint3, turningRadius)
                #Note : TBD : read thetaStep from project Property
                angleOfTurn=self.reformatAngles(self.computeAngle(fsPoint1, fsPoint2, fsPoint3)-pi)  
                if angleOfTurn>=0:
                    thetaStep=(angleStepDeg*pi/180)
                    theta0=-pi/2+self.computeAngle(QgsPoint(fsPoint1.x()+10,fsPoint1.y()), fsPoint1, fsPoint2)
                    thetaFin=pi/2+self.computeAngle(QgsPoint(fsPoint3.x()+10,fsPoint3.y()), fsPoint3, fsPoint2)

                else:
                    thetaStep=-(angleStepDeg*pi/180)
                    theta0=pi/2+self.computeAngle(QgsPoint(fsPoint1.x()+10,fsPoint1.y()), fsPoint1, fsPoint2)
                    thetaFin=-pi/2+self.computeAngle(QgsPoint(fsPoint3.x()+10,fsPoint3.y()), fsPoint3, fsPoint2)
                
                newPointList=self.computeArcPoints(turnCenter, turningRadius, theta0, thetaFin,thetaStep)
                trajPoints=trajPoints+newPointList
            trajPoints.append(segmentPoints[nbPoints-1])
            
            #Trajectory sampling
            newTrajPoints=[trajPoints[0]]
            newNbPoints=len(trajPoints)
            for i in range(0,newNbPoints-1):
                fsPoint1=trajPoints[i]
                fsPoint2=trajPoints[i+1]
                currentDistance=self.distance(fsPoint1, fsPoint2)
                if (currentDistance>1.1*distStep):
                    nbPointsToAdd=int(ceil(currentDistance/distStep)-1)
                    pointSpace=currentDistance/(nbPointsToAdd+1)
                    for j in range(1,nbPointsToAdd+1):
                        pointToAdd=self.displacePoint1(fsPoint1, fsPoint2, pointSpace*j)
                        newTrajPoints.append(pointToAdd)
                newTrajPoints.append(fsPoint2)
        else:
            newTrajPoints=segmentPoints
        
            
        return  newTrajPoints
    
    #Geo Toolbox
    def computeTurningRadius(self,rollAngleDeg,speed_kt):
        pi=3.1416
        g=9.81
        radius=((float(speed_kt)*0.514)**2)/(g*tan(pi*rollAngleDeg/180))
        return radius
    #Compute angle between two flight plan leg 1->2->3
    def distance(self,point1,point2):
        ux=point1.x()-point2.x()
        uy=point1.y()-point2.y()
        uu=sqrt(ux**2+uy**2)
        return uu
    def computeCenterOfTurn(self,point1,point2,point3,radius):
        ux=point1.x()-point2.x()
        uy=point1.y()-point2.y()
        vx=point3.x()-point2.x()
        vy=point3.y()-point2.y()
        uu=sqrt(ux**2+uy**2)
        vv=sqrt(vx**2+vy**2)       
        theta=self.computeAngle(point1, point2, point3)
        wx=ux/uu+vx/vv
        wy=uy/uu+vy/vv
        ww=sqrt(wx**2+wy**2)
        anticip=radius/tan(theta/2)
        centerX=point2.x()+sqrt(radius**2+anticip**2)*wx/ww
        centerY=point2.y()+sqrt(radius**2+anticip**2)*wy/ww
        center=QgsPoint(centerX,centerY)
        return  center        
    def computeArcPoints(self,centerPoint,radius,thetaDebut,thetaFin,thetaStep):
        arcList=[]
        #Reformat Angle
        theta0=self.reformatAngles(thetaDebut)
        theta1=self.reformatAngles(thetaFin)
        if thetaStep>0:
            if theta0>theta1:
                theta1=theta1+2*pi
        else:
            if theta0<theta1:
                theta1=theta1-2*pi
        thetaList=[theta0+thetaStep*i for i in range(0,int(floor(abs((theta1-theta0)/thetaStep))))]
        for theta in thetaList:
            newX=centerPoint.x()+radius*cos(theta)
            newY=centerPoint.y()+radius*sin(theta)
            newPoint=QgsPoint(newX,newY)
            arcList.append(newPoint)
        return arcList

    def computeAngle(self,point1,point2,point3):
        ux=point1.x()-point2.x()
        uy=point1.y()-point2.y()
        vx=point3.x()-point2.x()
        vy=point3.y()-point2.y()
        uu=sqrt(ux**2+uy**2)
        vv=sqrt(vx**2+vy**2)
        cosTheta=(ux*vx+uy*vy)/(uu*vv)
        sinTheta=(ux*vy-uy*vx)/(uu*vv)
        if sinTheta==0:
            signeTheta=0
        else:
            signeTheta=sinTheta/abs(sinTheta)
        theta=acos(cosTheta)*signeTheta
        return theta

    def reformatAngles(self,angle):
        newAngle=angle
        while(newAngle>pi):
            newAngle=newAngle-2*pi
        while(newAngle<-pi):
            newAngle=newAngle+2*pi
        return newAngle
    
    def parseDTEDFolder(self,absolutePath,extension,latDeg,lonDeg,deltaDeg):
        result=[]
        expRegFile=".*("+extension+")$"
        expRegCoord="(\d{6}(N|S)\d{7}(E|W)){4}"
        for filesList in os.walk(absolutePath):
            absolutePathforFiles=filesList[0];
            files=filesList[2];
            for myFile in files:
                if re.match(expRegFile, myFile):
                    myAbsoluteFile=absolutePathforFiles+"/"+myFile
                    #print(myAbsoluteFile)

                    dtedFile=open(myAbsoluteFile,"r")
                    firstLine=dtedFile.readline()
                    m=re.search(expRegCoord,firstLine)
                    coordinatesGroup=m.group(0)

                    coordinatesList=self.extractCoordFromPattern(coordinatesGroup)
                    dtedFile.close()

                    if self.isInFile(latDeg, lonDeg, deltaDeg, coordinatesList):
                        result.append(myAbsoluteFile)
                    #print(coordinatesList)
        #print("resultDTED")
        #print(result)
        return result
    
    def parseGeoTIFFFolder(self,absolutePath,latDeg,lonDeg,deltaDeg,geoTiffExtension,worldFileExtension,projectionExtension):  
        result=[]
        expRegFile=".*("+geoTiffExtension+")$"   
        for filesList in os.walk(absolutePath):
            absolutePathforFiles=filesList[0];
            files=filesList[2];
            for myFile in files:     
                if re.match(expRegFile, myFile):
                    myAbsoluteFile=absolutePathforFiles+"/"+myFile
                    #print(myAbsoluteFile)
                    coordinatesList=self.extractCoordFromGeoTiff(myAbsoluteFile,worldFileExtension,projectionExtension)
                    if self.isInFile(latDeg, lonDeg, deltaDeg, coordinatesList):
                        result.append(myAbsoluteFile)
        #print("resultTIF")
        #print(result)
        return result 
    
    def extractCoordFromGeoTiff(self,myAbsoluteFile,worldFileExtension,projectionExtension):
        result=[]        
        #Read image Height and Width
        img=Image.open(myAbsoluteFile)
        imageWidth,imageHeight=img.size
        
        #Parse worldFile
        worldFile=open(myAbsoluteFile[:-4]+worldFileExtension,"r")
        k=0
        for line in worldFile:
            if (k==0):
                A=float(line)
            if (k==1):
                D=float(line)
            if (k==2):
                B=float(line)
            if (k==3):
                E=float(line)
            if (k==4):
                C=float(line)
            if (k==5):
                F=float(line)                
            k=k+1
        worldFile.close()
        x0=C+min(0,A*imageWidth,B*imageHeight,A*imageWidth+B*imageHeight);
        y0=F+min(0,D*imageWidth,E*imageHeight,D*imageWidth+E*imageHeight);
        x1=C+max(0,A*imageWidth,B*imageHeight,A*imageWidth+B*imageHeight);
        y1=F+max(0,D*imageWidth,E*imageHeight,D*imageWidth+E*imageHeight);
        
        #Reproject points
        prjFile=open(myAbsoluteFile[:-4]+projectionExtension,"r")
        k=0
        for line in prjFile:
            if (k==0):
                wktLine=line   
            k=k+1
        prjFile.close()
        crsSrc=QgsCoordinateReferenceSystem(wktLine)#projection of TIF file
        crsDest=QgsCoordinateReferenceSystem(4326) #WGS84
        transfo=QgsCoordinateTransform(crsSrc,crsDest)
        
        pt0=transfo.transform(QgsPoint(x0,y0))
        pt1=transfo.transform(QgsPoint(x1,y1))
        lon0=pt0.x()
        lat0=pt0.y()
        lon1=pt1.x()
        lat1=pt1.y()
        
        result=[lat0,lat1,lon0,lon1]
        return result     
    
    def extractCoordFromPattern(self,pattern):
        #return [latmin, latmax, lonmin, lonmax]
        lat=[]
        longi=[]
        for i in range(0,4):
            lat.insert(i,self.signFromLetter(pattern[15*i+6])*(float(pattern[15*i:15*i+2])+float(pattern[15*i+2:15*i+4])/60+float(pattern[15*i+4:15*i+6])/3600))
            longi.insert(i,self.signFromLetter(pattern[15*i+14])*(float(pattern[15*i+7:15*i+10])+float(pattern[15*i+10:15*i+12])/60+float(pattern[15*i+12:15*i+14])/3600))        
        result=[min(lat),max(lat),min(longi),max(longi)]
        return result
    
    def signFromLetter(self,letter):
        result=0
        if letter=="N":
            result=1;
        if letter=="E":
            result=1;
        if letter=="W":
            result=-1;
        if letter=="S":
            result=-1;
        return result
    
    def isInFile(self,lat,lon,delta,coordinatesList):
        test=True
        if coordinatesList[0]>(lat+delta):
            test=False
        if coordinatesList[1]<(lat-delta):
            test=False
        if coordinatesList[2]>(lon+delta):
            test=False
        if coordinatesList[3]<(lon-delta):
            test=False
        return test
            
        
