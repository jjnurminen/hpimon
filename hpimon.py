# -*- coding: utf-8 -*-
"""


Threading:
see e.g. 
https://mayaposch.wordpress.com/2011/11/01/how-to-really-truly-use-qthreads-the-full-explanation/
https://nikolak.com/pyqt-threading-tutorial/

GIL?
data is read through socket - should release the lock

TODO:

high cpu usage - socket reads?
make sure ft buffer and dacq get started in correct order; otherwise buffer size
may not be set in dacq


data plotter widgets





@author: jussi
"""


from __future__ import print_function
import sys
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import pyqtSignal
import time
import psutil
import mne
from mne.externals import FieldTrip
import numpy as np
import scipy
from mne import pick_types
import os.path as op
import subprocess
import ast
from config import Config


DEBUG = False

def debug_print(*args):
    if DEBUG:
        print(*args)

def ft_server_pid(procname):
    """ Tries to return the PID of the server process. """
    for proc in psutil.process_iter():
        try:
            if proc.name() == procname:
                return proc.pid
        except psutil.AccessDenied:
            pass
    return None


def start_ft_server(bin, opts):
    """ bin is the executable, opts is a list of opts """
    args = [bin] + opts
    return subprocess.Popen(args)


class HPImon(QtGui.QMainWindow):

    # new signals must be defined here
    new_data = pyqtSignal()

    def __init__(self):
        super(self.__class__, self).__init__()
        self.apptitle = 'hpimon'
        # load user interface made with designer
        uic.loadUi('hpimon.ui', self)
        self.cfg = Config()
        try:
            self.cfg.read()
        except ValueError:
            self.message_dialog('No config file, creating %s with default '
                                'values. Please edit according to '
                                'your setup and restart.' %
                                self.cfg.configfile)
            self.cfg.write()
            self.close()

        """ Parse some options """
        self.cfreqs = ast.literal_eval(self.cfg.HPI_FREQS)
        self.SNR_COLORS = ast.literal_eval(self.cfg.SNR_COLORS)  # str to dict

        self.serverp = None
        if self.cfg.HOST == 'localhost' and not ft_server_pid(self.cfg.SERVER_BIN):
            debug_print('Starting server')
            self.serverp = start_ft_server(self.cfg.SERVER_PATH,
                                           self.cfg.SERVER_OPTS.split())
            if not ft_server_pid():
                raise Exception('Cannot start server')

        self.timer = QtCore.QTimer()
        self.init_widgets()

        self.ftclient = FieldTrip.Client()
        self.ftclient.connect(self.cfg.HOST, port=self.cfg.PORT)
        self.pick_mag, self.pick_grad = self.get_ch_indices()
        self.pick_meg = np.sort(np.concatenate([self.pick_mag,
                                                self.pick_grad]))
        self.nchan = len(self.pick_meg)
        self.sfreq = self.get_header_info()['sfreq']
        self.init_glm()
        self.new_data.connect(self.update_snr_display)

        self.last_sample = self.buffer_last_sample()
        
        self.timer.timeout.connect(self.poll_buffer)
        self.timer.start(self.cfg.BUFFER_POLL_INTERVAL)
        self.statusbar.showMessage(self.msg_running())


    def init_widgets(self):
        # labels
        for wnum in range(5):
            lbname = 'label_' + str(wnum + 1)
            self.__dict__[lbname].setText(str(self.cfreqs[wnum]) + ' Hz')
        # progress bars
        for wnum in range(5):
            wname = 'progressBar_' + str(wnum + 1)
            sty = '.QProgressBar {'
            sty += self.cfg.BAR_STYLE
            sty += ' }'
            self.__dict__[wname].setStyleSheet(sty)
        # stylesheets for progress bars
        self.progbar_styles = dict()
        for snr in ['good', 'ok', 'bad']:
            sty = ('QProgressBar {%s} QProgressBar::chunk { background-color: '
                   '%s; %s }' % (self.cfg.BAR_STYLE, self.SNR_COLORS[snr],
                                 self.cfg.BAR_CHUNK_STYLE))
            self.progbar_styles[snr] = sty
        # buttons
        self.btnQuit.clicked.connect(self.close)
        self.btnStop.clicked.connect(self.toggle_timer)
        
    def toggle_timer(self):
        if self.timer.isActive():
            self.statusbar.showMessage(self.msg_stopped())
            self.btnStop.setText('Start monitoring')
            self.timer.stop()
        else:
            self.statusbar.showMessage(self.msg_running())
            self.btnStop.setText('Stop monitoring')
            self.timer.start()
    
    def msg_running(self):
        return ('Running, poll interval %d ms, window %d ms' %
                (self.cfg.BUFFER_POLL_INTERVAL, self.cfg.WIN_LEN))

    def msg_stopped(self):
        return 'Stopped'

    def get_ch_indices(self):
        """ Return indices of magnetometers and gradiometers in the
        FieldTrip data matrix """
        grads, mags = [], []
        for ind, ch in enumerate(self.ftclient.getHeader().labels):
            if ch[:3] == 'MEG':
                if ch[-1] == '1':
                    mags.append(ind)
                elif ch[-1] in ['2', '3']:
                    grads.append(ind)
                else:
                    raise ValueError('Unexpected channel name: ' + ch)
        debug_print('Got %d magnetometers and %d gradiometers' %
                    (len(mags), len(grads)))
        return np.array(mags), np.array(grads)

    def get_header_info(self):
        """ Get misc info from FieldTrip header """
        return {'sfreq': self.ftclient.getHeader().fSample}

    def buffer_last_sample(self):
        """ Return number of last sample available from server. """
        return self.ftclient.getHeader().nSamples

    def poll_buffer(self):
        """ Emit a signal if new data is available in the buffer. """
        buflast = self.buffer_last_sample()
        debug_print('polling buffer, buffer last sample: %d, my last sample: %d' %
                    (buflast, self.last_sample))
        # buffer last sample can also decrease (reset) if streaming from file
        if buflast != self.last_sample:
            debug_print('poll: new data')
            self.new_data.emit()
            self.last_sample = buflast
        else:
            debug_print('poll: no new data')

    def fetch_buffer(self):
        start = self.last_sample - self.cfg.WIN_LEN + 1
        stop = self.last_sample
        debug_print('fetching buffer from %d to %d' % (start, stop))
        data = self.ftclient.getData([start, stop])
        if data is None:
            print('Warning: server returned no data')
            return None
        else:
            return data[:, self.pick_meg]

    def init_glm(self):
        """ Build general linear model for amplitude estimation """
        # get some info from fiff
        self.linefreqs = (np.arange(self.cfg.NHARM+1)+1) * self.cfg.LINE_FREQ
        # time + dc and slope terms
        t = np.arange(self.cfg.WIN_LEN) / float(self.sfreq)
        self.model = np.empty((len(t),
                               2+2*(len(self.linefreqs)+len(self.cfreqs))))
        self.model[:, 0] = t
        self.model[:, 1] = np.ones(t.shape)
        # add sine and cosine term for each freq
        allfreqs = np.concatenate([self.linefreqs, self.cfreqs])
        self.model[:, 2::2] = np.cos(2 * np.pi * t[:, np.newaxis] * allfreqs)
        self.model[:, 3::2] = np.sin(2 * np.pi * t[:, np.newaxis] * allfreqs)
        self.inv_model = scipy.linalg.pinv(self.model)

    def compute_snr(self, data):
        coeffs = np.dot(self.inv_model, data)  # nterms * nchan
        coeffs_hpi = coeffs[2+2*len(self.linefreqs):]
        resid_vars = np.var(data - np.dot(self.model, coeffs), 0)
        # get total power by combining sine and cosine terms
        # sinusoidal of amplitude A has power of A**2/2
        hpi_pow = (coeffs_hpi[0::2, :]**2 + coeffs_hpi[1::2, :]**2)/2
        # average across channel types separately
        hpi_pow_grad_avg = hpi_pow[:, self.pick_grad].mean(1)
        #hpi_pow_mag_avg = hpi_pow[:, self.pick_mag].mean(1)
        # divide average HPI power by average variance
        snr_avg_grad = hpi_pow_grad_avg / \
            resid_vars[self.pick_grad].mean()
        #snr_avg_mag = hpi_pow_mag_avg / \
        #    resid_vars[self.pick_mag].mean()
        return 10 * np.log10(snr_avg_grad)

    def update_snr_display(self):
        buf = self.fetch_buffer()
        if buf is not None:
            snr = self.compute_snr(buf)
            for wnum in range(1, 6):
                wname = 'progressBar_' + str(wnum)
                this_snr = int(np.round(snr[wnum-1]))
                self.__dict__[wname].setValue(this_snr)
                if this_snr > self.cfg.SNR_OK:
                    sty = self.progbar_styles['good']
                elif this_snr > self.cfg.SNR_BAD:
                    sty = self.progbar_styles['ok']
                else:
                    sty = self.progbar_styles['bad']
                self.__dict__[wname].setStyleSheet(sty)

    def message_dialog(self, msg):
        """ Show message with an 'OK' button. """
        dlg = QtGui.QMessageBox()
        dlg.setWindowTitle(self.apptitle)
        dlg.setText(msg)
        dlg.addButton(QtGui.QPushButton('Ok'), QtGui.QMessageBox.YesRole)
        dlg.exec_()

    def closeEvent(self, event):
        """ Confirm and close application. """
        self.timer.stop()
        # disconnect from server
        self.ftclient.disconnect()
        # if we launched the server process, kill it
        if self.serverp is not None:
            debug_print('Killing server process')
            self.serverp.kill()
        event.accept()


def main():

    app = QtGui.QApplication(sys.argv)
    hpimon = HPImon()

    hpimon.show()
    app.exec_()


if __name__ == '__main__':
    main()

