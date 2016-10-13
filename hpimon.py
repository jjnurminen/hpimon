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

-nb: FieldTripClient can register callbacks - no need for polling :O


TODO:


config reader
disk writer for debugging
float widgets for adjusting freqs
data plotter widgets
assemble ui dynamically (arbitrary number of freqs)?
threading?





@author: jussi
"""


from __future__ import print_function
import sys
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import pyqtSignal
import time
import psutil
import mne
from mne.realtime import FieldTripClient
import numpy as np
import scipy
from mne import pick_types
import os.path as op
import subprocess


SERVER_PATH = '/home/jussti/neuromag2ft-3.0.2/bin/x86_64-pc-linux-gnu/neuromag2ft'
SERVER_OPTS = ['--file', '/home/jussi/megdata/zhdanov_andrey/160412/aud_2positions_raw.fif']
SERVER_BIN = op.split(SERVER_PATH)[1]
BUFFER_POLL_INTERVAL = 10  # how often to poll buffer (ms)
WINDOW_LEN = 200  # how much data to use for single SNR estimate (ms)
LINE_FREQ = 50
SNR_OK = 10
SNR_BAD = -5
SNR_COLORS = {'bad': '#f44242', 'ok': '#eff700', 'good': '#57cc2c'}
BAR_STYLE = 'text-align: center;'  # style for progress bar
BAR_CHUNK_STYLE = 'margin: 2px;'  # style for progress bar chunk

        

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

    # new signals must be defined here
    new_data = pyqtSignal()

    def __init__(self):
        super(self.__class__, self).__init__()
        # load user interface made with designer

        self.buflen = WINDOW_LEN
        self.n_harmonics = 5
        self.cfreqs = [83.0, 143.0, 203.0, 263.0, 323.0]
        self.cfreqs = [293.0, 307.0, 314.0, 321.0, 327.5]
        self.cfreqs = [293.0, 307.0, 314.0, 321.0, 335.5]

        self.serverp = None
        if not ft_server_pid():
            print('Starting server')
            self.serverp = start_ft_server()
            if not ft_server_pid():
                raise Exception('Cannot start server')

        uic.loadUi('hpimon.ui', self)

        # init widgets
        # labels
        for wnum in range(5):
            lbname = 'label_' + str(wnum + 1)
            self.__dict__[lbname].setText(str(self.cfreqs[wnum]) + ' Hz')
        # progress bar
        for wnum in range(5):
            wname = 'progressBar_' + str(wnum + 1)
            sty = '.QProgressBar {'
            sty += BAR_STYLE
            sty += ' }'
            self.__dict__[wname].setStyleSheet(sty)
                    
                    

        self.btnQuit.clicked.connect(self.close)
        self.rtclient = FieldTripClient(host='localhost', port=1972,
                                        tmax=150, wait_max=10)

        #self.rtclient.register_receive_callback(got_buffer)

        self.rtclient.__enter__()
        self.info = self.rtclient.get_measurement_info()
        #self.rtclient.start_receive_thread(10)
        self.init_glm()

        # which channels to get from the buffer
        self.pick_buf = mne.pick_types(self.info, meg=True, eeg=False,
                                       eog=False, stim=False)
        self.pick_meg = pick_types(self.info, meg=True, exclude=[])
        self.pick_mag = pick_types(self.info, meg='mag', exclude=[])
        self.pick_grad = pick_types(self.info, meg='grad', exclude=[])
        self.nchan = len(self.pick_meg)

        self.new_data.connect(self.update_snr_display)

        self.last_sample = self.buffer_last_sample()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.poll_buffer)
        self.timer.start(BUFFER_POLL_INTERVAL)


        

    def buffer_last_sample(self):
        """ Return number of last sample available from server. """
        return self.rtclient.ft_client.getHeader().nSamples

    def poll_buffer(self):
        """ Emit a signal if new data is available in the buffer. """
        buflast = self.buffer_last_sample()
        print('polling buffer, buffer last sample: %d, my last sample: %d' %
                (buflast, self.last_sample))
        # buffer last sample can also decrease (reset) if streaming from file
        if buflast != self.last_sample:
            self.new_data.emit()
            self.last_sample = buflast

    def fetch_buffer(self):
        return self.rtclient.get_data_as_epoch(n_samples=self.buflen,
                                               picks=self.pick_buf)
        # directly from ft_Client - do not construct Epochs object
        #start = self.last_sample - self.buflen + 1
        #stop = self.last_sample
        #return self.rtclient.ft_client.getData([start, stop]).transpose()

    def init_glm(self):
        """ Build general linear model for amplitude estimation """
        # get some info from fiff
        sfreq = self.info['sfreq']
        linefreq = self.info['line_freq']  # not in FieldTrip header
        linefreq = LINE_FREQ
        self.linefreqs = (np.arange(self.n_harmonics + 1) + 1) * linefreq
        # time + dc and slope terms
        t = np.arange(self.buflen) / float(sfreq)
        self.model = np.empty((len(t), 2+2*(len(self.linefreqs)+len(self.cfreqs))))
        self.model[:, 0] = t
        self.model[:, 1] = np.ones(t.shape)
        # add sine and cosine term for each freq
        allfreqs = np.concatenate([self.linefreqs, self.cfreqs])
        self.model[:, 2::2] = np.cos(2 * np.pi * t[:, np.newaxis] * allfreqs)
        self.model[:, 3::2] = np.sin(2 * np.pi * t[:, np.newaxis] * allfreqs)
        self.inv_model = scipy.linalg.pinv(self.model)

    def compute_snr(self, data):
        snr_avg_grad = np.zeros(len(self.cfreqs))
        hpi_pow_grad = np.zeros(len(self.cfreqs))
        snr_avg_mag = np.zeros(len(self.cfreqs))
        resid_vars = np.zeros(self.nchan)
        coeffs = np.dot(self.inv_model, data)  # nterms * nchan
        coeffs_hpi = coeffs[2+2*len(self.linefreqs):]
        resid_vars = np.var(data - np.dot(self.model, coeffs), 0)
        # get total power by combining sine and cosine terms
        # sinusoidal of amplitude A has power of A**2/2
        hpi_pow = (coeffs_hpi[0::2, :]**2 + coeffs_hpi[1::2, :]**2)/2
        # average across channel types separately
        hpi_pow_grad_avg = hpi_pow[:, self.pick_grad].mean(1)
        hpi_pow_mag_avg = hpi_pow[:, self.pick_mag].mean(1)
        # divide average HPI power by average variance
        snr_avg_grad = hpi_pow_grad_avg / \
            resid_vars[self.pick_grad].mean()
        snr_avg_mag = hpi_pow_mag_avg / \
            resid_vars[self.pick_mag].mean()
        return 10 * np.log10(snr_avg_grad)

    def snr_color(self, snr):
        """ Return progress bar stylesheet according to SNR """
        sty = 'QProgressBar {' + BAR_STYLE + '} '
        sty += 'QProgressBar::chunk { background-color: '
        if snr > SNR_OK:
            sty += SNR_COLORS['good']
        elif snr > SNR_BAD:
            sty += SNR_COLORS['ok']
        else:
            sty += SNR_COLORS['bad']
        sty += '; '
        sty += BAR_CHUNK_STYLE
        sty += ' }'
        return sty
        
    def update_snr_display(self):
        buf = self.fetch_buffer()
        data = buf.get_data()[0,:,:].transpose()
        snr = self.compute_snr(data)
        for wnum in range(1,6):
            wname = 'progressBar_' + str(wnum)
            this_snr = int(np.round(snr[wnum-1]))
            self.__dict__[wname].setValue(this_snr)
            self.__dict__[wname].setStyleSheet(self.snr_color(this_snr))


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

