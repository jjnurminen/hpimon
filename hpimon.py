# -*- coding: utf-8 -*-
"""

Single-threaded version:
ok but buffer updates may take too long (few hundred ms for 0,5 s buffer?)


Multithreaded version:
see e.g. 
https://mayaposch.wordpress.com/2011/11/01/how-to-really-truly-use-qthreads-the-full-explanation/
https://nikolak.com/pyqt-threading-tutorial/

separate worker thread (data fetch)
use of timer?


GIL?
data is read through socket - should release the lock





@author: jussi
"""


from __future__ import print_function
import sys
from PyQt4 import QtGui, QtCore, uic
import time
import psutil
import mne
from mne.realtime import FieldTripClient


def ft_server_pid():
    """ Tries to return the PID of the ftserver process. """
    PROCNAME = "neuromag2ft"
    for proc in psutil.process_iter():
        try:
            if proc.name() == PROCNAME:
                return proc.pid
        except psutil.AccessDenied:
            pass
    return None


def start_ft_server():
    pass

        

class HPImon(QtGui.QMainWindow):

    def __init__(self):
        super(self.__class__, self).__init__()
        # load user interface made with designer
        uic.loadUi('hpimon.ui', self)

        self.btnQuit.clicked.connect(self.close)

        self.rtclient = FieldTripClient(host='localhost', port=1972,
                                        tmax=150, wait_max=10)
        self.rtclient.__enter__()
        self.info = self.rtclient.get_measurement_info()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_snr_display)
        self.timer.start(1000)


    def update_snr_display(self):
        self.server_read()
        self.label_1.setText(str(hash(self.data)))


    def server_read(self):
        n_samples = 1024
        picks = mne.pick_types(self.info, meg='grad', eeg=False, eog=True,
                               stim=False, include=[])
        self.data = self.rtclient.get_data_as_epoch(n_samples=n_samples,
                                                    picks=picks)

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

