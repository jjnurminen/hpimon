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
#COLLECTOR_CONF = '/tmp/collector.defs'


def hpi_freqs_from_config():
    """ Read HPI frequencies from collector setup file """
    if not op.isfile(COLLECTOR_CONF):
        return None
    else:
        freqs = []
        with open(COLLECTOR_CONF, 'r') as f:
            flines = f.read().splitlines()
        for line in flines:
            lit = line.split()
            if len(lit) > 1:
                if lit[0][:7] == 'hpiFreq':
                    freqs.append(float(lit[1]))
        return freqs
        