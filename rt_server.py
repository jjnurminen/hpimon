# -*- coding: utf-8 -*-
"""
Manage the rt server.

@author: jussi (jnu@iki.fi)
"""

import psutil
import subprocess


def rt_server_pid(procname):
    """ Tries to return the PID of the server process. """
    for proc in psutil.process_iter():
        try:
            if proc.name() == procname:
                return proc.pid
        except psutil.AccessDenied:
            pass
    return None


def start_rt_server(bin, opts):
    """ bin is the executable, opts is a list of opts """
    args = [bin] + opts
    return subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)


def stop_rt_server(serverp):
    """ Stops our own instance of the server. """
    if serverp is not None:
        serverp.terminate()
