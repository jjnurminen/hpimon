# -*- coding: utf-8 -*-
"""
Talk directly to MEG system / read config files

@author: jussi

hpi freqs:
telnet localhost collector
pass homunculus122
vars hpiFreqx
"""

import os.path as op

COLLECTOR_CONF = '/neuro/dacq/setup/collector/conf/collector.defs'


def hpi_freqs_from_config():
    if op.isfile(COLLECTOR_CONF):
        
    