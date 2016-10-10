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


-ft buffer updates at its own interval
-poll buffer every x ms (x = 100 ms?)
-send signal if buffer updated




@author: jussi
"""


from __future__ import print_function
import sys
from PyQt4 import QtGui, QtCore, uic
import time
import psutil
import mne
from mne.realtime import FieldTripClient
import numpy as np
import scipy
from mne import pick_types
import os.path as op
import subprocess


SERVER_PATH = '/home/jussi/neuromag2ft-3.0.2/bin/x86_64-pc-linux-gnu/neuromag2ft'
SERVER_OPTS = ['--file', '/home/jussi/Dropbox/jn_multimodal01_raw.fif']
SERVER_BIN = op.split(SERVER_PATH)[1]


def ft_server_pid():
    """ Tries to return the PID of the server process. """
    for proc in psutil.process_iter():
        try:
            if proc.name() == SERVER_BIN:
                return proc.pid
        except psutil.AccessDenied:
            pass
    return None


def start_ft_server():
    args = [SERVER_PATH] + SERVER_OPTS
    return subprocess.Popen(args)


class HPImon(QtGui.QMainWindow):

    def __init__(self):
        super(self.__class__, self).__init__()
        # load user interface made with designer

        self.buflen = 500
        self.n_harmonics = 5
        self.cfreqs = [83.0, 143.0, 203.0, 263.0, 323.0]

        self.serverp = None
        if not ft_server_pid():
            print('Starting server')
            self.serverp = start_ft_server()
            if not ft_server_pid():
                raise Exception('Cannot start server')

        uic.loadUi('hpimon.ui', self)

        self.btnQuit.clicked.connect(self.close)
        self.rtclient = FieldTripClient(host='localhost', port=1972,
                                        tmax=150, wait_max=10)
        self.rtclient.__enter__()
        self.info = self.rtclient.get_measurement_info()
        self.init_glm()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_snr_display)
        self.timer.start(500)

    def init_glm(self):
        """ Build general linear model for amplitude estimation """
        # get some info from fiff
        sfreq = self.info['sfreq']
        linefreq = self.info['line_freq']
        linefreq = 50
        linefreqs = (np.arange(self.n_harmonics + 1) + 1) * linefreq

        self.pick_meg = pick_types(self.info, meg=True, exclude=[])
        self.pick_mag = pick_types(self.info, meg='mag', exclude=[])
        self.pick_grad = pick_types(self.info, meg='grad', exclude=[])
        self.nchan = len(self.pick_meg)

        # create general linear model for the data
        t = np.arange(self.buflen) / float(sfreq)
        model = np.empty((len(t), 2+2*(len(linefreqs)+len(self.cfreqs))))
        model[:, 0] = t
        model[:, 1] = np.ones(t.shape)
        # add sine and cosine term for each freq
        allfreqs = np.concatenate([linefreqs, self.cfreqs])
        model[:, 2::2] = np.cos(2 * np.pi * t[:, np.newaxis] * allfreqs)
        model[:, 3::2] = np.sin(2 * np.pi * t[:, np.newaxis] * allfreqs)
        self.model = model
        self.inv_model = scipy.linalg.pinv(model)

    def compute_snr(self):
        # drop last buffer to avoid overrun
        self.snr_avg_grad = np.zeros([len(self.cfreqs), 1])
        hpi_pow_grad = np.zeros([len(self.cfreqs), 1])
        self.snr_avg_mag = np.zeros([len(self.cfreqs), 1])
        resid_vars = np.zeros([self.nchan, 1])

        coeffs = np.dot(self.inv_model, self.data)
        coeffs_hpi = coeffs[2+2*len(self.linefreqs):]
        resid_vars[:, 1] = np.var(self.data - np.dot(self.model, coeffs), 0)
        # get total power by combining sine and cosine terms
        # sinusoidal of amplitude A has power of A**2/2
        hpi_pow = (coeffs_hpi[0::2, :]**2 + coeffs_hpi[1::2, :]**2)/2
        hpi_pow_grad[:, 1] = hpi_pow[:, self.pick_grad].mean(1)
        # divide average HPI power by average variance
        self.snr_avg_grad[:, 1] = hpi_pow_grad[:, 1] / \
            resid_vars[self.pick_grad, 1].mean()
        self.snr_avg_mag[:, 1] = hpi_pow[:, self.pick_mag].mean(1) / \
            resid_vars[self.pick_mag, 1].mean()

    def update_snr_display(self):
        self.server_read()
        #self.compute_snr()
        self.label_1.setText('moi')
        #self.label_1.setText(str(self.snr_avg_mag))

    def server_read(self):
        picks = mne.pick_types(self.info, meg='grad', eeg=False, eog=True,
                               stim=False, include=[])
        self.data = self.rtclient.get_data_as_epoch(n_samples=self.buflen,
                                                    picks=picks)

    def closeEvent(self, event):
        """ Confirm and close application. """
        self.timer.stop()
        # disconnect from server
        self.rtclient.ft_client.disconnect()
        # if we launched the server process, kill it
        if self.serverp is not None:
            print('Killing server process')
            self.serverp.kill()
        event.accept()


def main():

    app = QtGui.QApplication(sys.argv)
    hpimon = HPImon()

    hpimon.show()
    app.exec_()


if __name__ == '__main__':
    main()

