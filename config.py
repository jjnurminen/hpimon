# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 15:59:53 2016

@author: hus20664877
"""

import ConfigParser
import os.path as op


class Config:
    """ Configuration class for hpimon. Config values are read accessible as
    instance attributes or keys, but must be set using keys. """

    """ Init config dict with default options """
    cfg = dict()
    cfg['SERVER_PATH'] = '/home/jussi/neuromag2ft-3.0.2/bin/x86_64-pc-linux-gnu/neuromag2ft'
    cfg['SERVER_OPTS'] = '--file /home/jussi/megdata/zhdanov_andrey/160412/aud_2positions_raw.fif'
    cfg['SERVER_BIN'] = op.split(cfg['SERVER_PATH'])[1]
    cfg['HOST'] = 'localhost'
    cfg['PORT'] = 1972
    cfg['BUFFER_POLL_INTERVAL'] = 300  # how often to poll buffer (ms)
    cfg['WIN_LEN'] = 300  # how much data to use for single SNR estimate (ms)
    cfg['LINE_FREQ'] = 50
    cfg['HPI_FREQS'] = '[293.0, 307.0, 314.0, 321.0, 328.0]'
    cfg['NHARM'] = 5
    # SNR limits. Maximum (coil fixed to helmet) = ~40 dB, no HPI = ~ -22 dB
    cfg['SNR_OK'] = 10  # lower than this is 'ok', higher is 'good'
    cfg['SNR_BAD'] = -5  # lower than this is 'bad'
    cfg['SNR_COLORS'] = "{'bad': '#f44242', 'ok': '#eff700', 'good': '#57cc2c'}"
    cfg['BAR_STYLE'] = 'text-align: center;'  # style for progress bar
    cfg['BAR_CHUNK_STYLE'] = 'margin: 2px;'  # style for progress bar chunk

    def __init__(self):
        self.cfg = Config.cfg.copy()
        self.section = 'hpimon'  # global section identifier for ConfigParser
        self.configfile = op.expanduser('~') + '/.hpimon.cfg'
        self.parser = ConfigParser.SafeConfigParser()
        self.parser.optionxform = str  # make it case sensitive
        self.parser.add_section(self.section)
        self.__dict__.update(self.cfg)  # make values accessible as attributes

    def read(self):
        """ Read whole config dict from disk file. """
        if not op.isfile(self.configfile):
            raise ValueError('No config file')
        self.parser.read(self.configfile)
        for key in self.cfg:
            try:
                # convert to numeric values when reading
                self.cfg[key] = Config.asnum(self.parser.get(self.section, key))
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                raise ValueError('Invalid configuration file, please fix or delete: ' + self.configfile)
        self.__dict__.update(self.cfg)

    def write(self):
        """ Save current config to a disk file. """
        try:
            inifile = open(self.configfile, 'wt')
        except IOError:
            raise ValueError('Cannot open config file for writing')
        for key in self.cfg.keys():
            self.parser.set(self.section, key, str(self.cfg[key]))
        self.parser.write(inifile)
        inifile.close()

    def __getitem__(self, key):
        return self.cfg[key]

    def __setitem__(self, key, val):
        self.cfg[key] = val
        self.__dict__.update(self.cfg)  # make values accessible as attributes

    @staticmethod
    def asnum(str):
        """ Return str as a number if possible, else return str. """
        try:
            return int(str)
        except ValueError:
            try:
                return float(str)
            except ValueError:
                return str


            
        
        
        
