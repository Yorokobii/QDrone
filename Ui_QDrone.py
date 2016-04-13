# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

class Ui_QDrone(object):
    def setupUi(self, QDrone):
        QDrone.setObjectName("QDrone")
        QDrone.resize(400, 300)
        QDrone.setMaximumSize(400, 300)
        QDrone.setMinimumSize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(QDrone)
        self.buttonBox.setGeometry(QtCore.QRect(20, 260, 361, 20))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(QDrone)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), QDrone.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), QDrone.reject)
        QtCore.QMetaObject.connectSlotsByName(QDrone)

    def retranslateUi(self, QDrone):
        QDrone.setWindowTitle(QtGui.QApplication.translate("QDrone", "QDrone", None, QtGui.QApplication.UnicodeUTF8))
