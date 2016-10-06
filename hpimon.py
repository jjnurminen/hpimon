# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 09:03:58 2016

@author: jussi
"""


from __future__ import print_function
import sys
from PyQt4 import QtGui, QtCore, uic
import time


class HPImon(QtGui.QMainWindow):

    def __init__(self):
        super(self.__class__, self).__init__()
        # load user interface made with designer
        uic.loadUi('hpimon.ui', self)

        self.btnQuit.clicked.connect(self.close)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
    
    
    def update(self):
        self.label_1.setText(str(time.clock()))


def main():

    app = QtGui.QApplication(sys.argv)
    hpimon = HPImon()

    hpimon.show()
    app.exec_()


if __name__ == '__main__':
    main()

