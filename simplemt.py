# -*- coding: utf-8 -*-
"""

Single-threaded version:
ok but buffer updates may take too long (few hundred ms for 0,5 s buffer?)


Multithreaded version:
see e.g. https://nikolak.com/pyqt-threading-tutorial/

separate worker thread (data fetch)
use of timer?




@author: jussi
"""


from __future__ import print_function
import sys
from PyQt4 import QtGui, QtCore, uic
import time
import psutil
import mne
from mne.realtime import FieldTripClient




class DataFetchThread(QtCore.QThread):

    data_rdy = QtCore.pyqtSignal(object) 
 
    def __init__(self, rtclient):
        QtCore.QThread.__init__(self)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_snr_display)
        self.timer.start(1000)
        
    def run(self):
 
       

class HPImon(QtGui.QMainWindow):

    def __init__(self):
        super(self.__class__, self).__init__()
        # load user interface made with designer
        uic.loadUi('hpimon.ui', self)

        datathread = DataFetchThread()
        datathread.data_rdy.connect(self.on_buffer_read)

        self.btnQuit.clicked.connect(self.close)


    def update_snr_display(self, data):
        self.label_1.setText(str(hash(data)))

    def on_buffer_read(self, data):
        self.update_snr_display(data)

    def closeEvent(self, event):
        """ Confirm and close application. """
        self.timer.stop()
        self.rtclient.ft_client.disconnect()
        event.accept()

def main():

    app = QtGui.QApplication(sys.argv)
    hpimon = HPImon()

    hpimon.show()
    app.exec_()


if __name__ == '__main__':
    main()

