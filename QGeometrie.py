# -*- coding: utf-8 -*-
"""


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

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt4.QtGui import QAction, QIcon
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.gui import *
from owslib.crs import Crs

from math import *
import math
#from pathlib import Path




class QGeometrie:


    def __init__(self,project):
        self.project=project
        self.pathConfFile=""

    #def processReading(self,path):
    
    	
		
    #Compute angle between two flight plan leg 1->2->3
    def distance(self,point1,point2):
        ux=point1.x()-point2.x()
        uy=point1.y()-point2.y()
        uu=sqrt(ux**2+uy**2)
        return uu
        

    def rotationVecteur(self, vect1, angle):		
		x1 = vect1.x()
		y1 = vect1.y()
		x2 = x1*cos(angle)-y1*sin(angle)
		y2 = x1*sin(angle)+y1*cos(angle)
		vect2 = QgsPoint(x2,y2)
		return vect2 
		
    def vecteurUnitaire(self, Point1, Point2):
		dist = self.distance(Point1, Point2)
		if (dist!=0) :
			x = (Point2.x() - Point1.x())/dist
			y = (Point2.y() - Point1.y())/dist
		else :
			x = 1
			y = 1
		
		U = QgsPoint(x,y)
		return U 
		
		
    def deplacePointSuivantVecteur(self, Point1, Vecteur, distance):
		x2 = Point1.x()+distance*Vecteur.x()
		y2 = Point1.y()+distance*Vecteur.y()
		Pt2 = QgsPoint(x2,y2)
		
		return Pt2 


    #This function displace the second point of a give segment within a given distance in meters
    def displacePoint2(self,Point1,Point2,distance):
		x1=Point1.x()
		x2=Point2.x()
		y1=Point1.y()
		y2=Point2.y()
#		longueur=sqrt((x2-x1)**2+(y2-y1)**2)
		longueur=math.sqrt(Point1.sqrDist(Point2))
		factor=(longueur+distance)/longueur
		x3=x1+factor*(x2-x1)
		y3=y1+factor*(y2-y1)
		Point3=QgsPoint(x3,y3)
		return Point3
		
    def displacePointAngle(self,Point1,Point2,distance, angle):
		
		u = self.vecteurUnitaire(Point1,Point2)
		v = self.rotationVecteur(u,angle)
		
		Point3 = self.deplacePointSuivantVecteur(Point1,v,distance)
		return Point3
		
    
    def generateTrajectory(self,segmentPoints,turningRadius):
        #segmentPoints is supposed to be a list of points
        test=1
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
                    thetaStep=(10*pi/180)
                    theta0=-pi/2+self.computeAngle(QgsPoint(fsPoint1.x()+10,fsPoint1.y()), fsPoint1, fsPoint2)
                    thetaFin=pi/2+self.computeAngle(QgsPoint(fsPoint3.x()+10,fsPoint3.y()), fsPoint3, fsPoint2)

                else:
                    thetaStep=-(10*pi/180)
                    theta0=pi/2+self.computeAngle(QgsPoint(fsPoint1.x()+10,fsPoint1.y()), fsPoint1, fsPoint2)
                    thetaFin=-pi/2+self.computeAngle(QgsPoint(fsPoint3.x()+10,fsPoint3.y()), fsPoint3, fsPoint2)
                
                newPointList=self.computeArcPoints(turnCenter, turningRadius, theta0, thetaFin,thetaStep)
                trajPoints=trajPoints+newPointList
            trajPoints.append(segmentPoints[nbPoints-1])
        else:
            trajPoints=segmentPoints
        return  trajPoints
    
    #Geo Toolbox
    def computeTurningRadius(self,rollAngleDeg,speed_kt):
        pi=3.1416
        g=9.81
        radius=((float(speed_kt)*0.514)**2)/(g*tan(pi*rollAngleDeg/180))
        return radius
        

    
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
        
        
        





    
    
   

    
    
    
    
    
