from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import time

class Worker(QThread):
  iprogress = 0
  progress = pyqtSignal(int)

  def __init__(self):
    QThread.__init__(self)

  def __del__(self):
    self.wait()

  def run(self):
    for i in range(100000):
      self.iprogress = self.iprogress + 1
      self.progress.emit(self.iprogress)