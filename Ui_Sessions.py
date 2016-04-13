# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *
import os
import shutil
try:
    from PyQt4.QtCore import QString
except ImportError:
    QString = str

class Ui_Sessions(object):
    def setupUi(self, Sessions):
        Sessions.setObjectName("Sessions")
        self.objet_sessions = Sessions

        layout = QtGui.QFormLayout()
        layout_new = QtGui.QFormLayout()
        layout_buttons = QtGui.QFormLayout()

        self.label_select = QtGui.QLabel()
        self.label_select_text = "Selectionnez une session existante ou \"Nouvelle session\" pour créer une session :"
        self.label_select.setText(self.label_select_text.decode('utf-8'))
        layout.addRow(self.label_select)

        self.comboBox = QtGui.QComboBox()
        self.comboBox.addItem("Nouvelle session")

        directory = QtCore.QDir(QtCore.QDir.currentPath())
        directory.cdUp()
        directory.cd("apps\qgis\python\plugins\QDrone\sessions")
        list_sessions = directory.entryList(QtCore.QDir.Dirs|QtCore.QDir.NoDotAndDotDot)
        del directory
        self.comboBox.addItems(list_sessions)

        layout.addRow(self.comboBox)

        self.label_new = QtGui.QLabel()
        self.label_new_text = "Créer une nouvelle session :"
        self.label_new.setText(self.label_new_text.decode('utf-8'))
        layout_new.addRow(self.label_new)

        self.input = QtGui.QLineEdit()
        layout_new.addRow(self.input)

        self.buttonBox = QtGui.QDialogButtonBox(Sessions)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.del_button = QtGui.QPushButton("Supprimer la session")
        self.del_button.clicked.connect(self.del_session)

        Str = "Se déconnecter"
        self.deco_btn = QtGui.QPushButton(Str.decode('utf-8'))

        layout_deco_btnbox = QtGui.QFormLayout()

        layout_deco_btnbox.addRow(self.deco_btn, self.buttonBox)
        layout_buttons.addRow(self.del_button, layout_deco_btnbox)

        self.layout_principal = QtGui.QFormLayout()
        self.layout_principal.addRow(layout)
        self.layout_principal.addRow(layout_new)
        self.layout_principal.addRow(layout_buttons)

        Sessions.setLayout(self.layout_principal)
        Sessions.resize(500,0)
        Sessions.setMaximumSize(500,0)
        Sessions.setMinimumSize(500,0)

        self.retranslateUi(Sessions)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Sessions.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Sessions.reject)
        QtCore.QMetaObject.connectSlotsByName(Sessions)

    def retranslateUi(self, Sessions):
        Sessions.setWindowTitle(QtGui.QApplication.translate("Sessions", "Configuration de session", None, QtGui.QApplication.UnicodeUTF8))

    def refreshComboBox(self):
        self.comboBox.clear()
        self.comboBox.addItem("Nouvelle session")

        directory = QtCore.QDir(QtCore.QDir.currentPath())
        directory.cdUp()
        directory.cd("apps\qgis\python\plugins\QDrone\sessions")
        list_sessions = directory.entryList(QtCore.QDir.Dirs|QtCore.QDir.NoDotAndDotDot)
        del directory
        self.comboBox.addItems(list_sessions)

    def del_session(self):
        if self.comboBox.currentText() != "Nouvelle session":
            directory = QtCore.QDir(QtCore.QDir.currentPath())
            directory.cdUp()
            directory.cd("apps\qgis\python\plugins\QDrone\sessions")
            popup = QtGui.QMessageBox()

            session_name = self.comboBox.currentText()

            for layer in QgsMapLayerRegistry.instance().mapLayers().values():
              if layer.name().find("flightPlan") != -1:
                QgsMapLayerRegistry.instance().removeMapLayer( layer.id() )

            del_files_dir = QtCore.QDir(directory)
            del_files_dir.cd(session_name)
            filesList = del_files_dir.entryList()
            for i in range(len(filesList)):
                del_files_dir.remove(filesList[i])

            if directory.rmdir(session_name):
                Str = "La session " + session_name.encode('utf-8') + " a été supprimée."
                popup.setText(Str.decode('utf-8'))
            else:
                popup.setText("Impossible de supprimer la session : " + session_name + ".")
            self.refreshComboBox()
            self.objet_sessions.reject()
            popup.exec_()

    def new_session(self, name):
        directory = QtCore.QDir(QtCore.QDir.currentPath())
        directory.cdUp()
        directory.cd("apps\qgis\python\plugins\QDrone\sessions")
        success = QtCore.QDir.mkdir(directory, name)
        del directory

        return success