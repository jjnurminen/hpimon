# -*- coding: utf-8 -*-
"""
Default config. Will be overwritten by updates - do not edit.
Edit the user specific config file instead (location given by cfg_file below)


@author: Jussi (jnu@iki.fi)
"""

import os.path as op

cfg = dict()

# location of user specific config file
pathprefix = op.expanduser('~')
appdir = pathprefix
cfg_file = appdir + '/.hpimon.cfg'

""" These variables will be written out into config file. """

cfg['SERVER_AUTOSTART'] = 1
cfg['SERVER_PATH'] = '/home/user/neuromag2ft-3.0.2/bin/x86_64-pc-linux-gnu/neuromag2ft'
cfg['SERVER_OPTS'] = '--chunksize 500'
cfg['HOST'] = 'localhost'
cfg['PORT'] = 1972
cfg['BUFFER_POLL_INTERVAL'] = 100  # how often to poll buffer (ms)
cfg['WIN_LEN'] = 500  # how much data to use for single SNR estimate (ms)
cfg['LINE_FREQ'] = ''
cfg['HPI_FREQS'] = '[]'
cfg['NHARM'] = 5  # number of line harmonics to use
# SNR limits. Maximum (coil fixed to helmet) = ~40 dB, no HPI = ~ -22 dB
cfg['SNR_OK'] = 10  # lower than this is 'ok', higher is 'good'
cfg['SNR_BAD'] = -5  # lower than this is 'bad'
cfg['SNR_COLORS'] = {'bad': '#f44242', 'ok': '#eff700', 'good': '#57cc2c'}
cfg['BAR_STYLE'] = 'text-align: center;'  # style for progress bar
cfg['BAR_CHUNK_STYLE'] = 'margin: 2px;'  # style for progress bar chunk
cfg['COLLECTOR_CONFIG'] = '/neuro/dacq/setup/collector/conf/collector.defs'
