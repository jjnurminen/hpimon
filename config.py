# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 15:59:53 2016

@author: hus20664877
"""

import ConfigParser
import os.path as op


class Config:

    """ Init config dict with default options """
    cfg = dict()
    cfg['SERVER_PATH'] = '/home/jussi/neuromag2ft-3.0.2/bin/x86_64-pc-linux-gnu/neuromag2ft'
    cfg['SERVER_OPTS'] = ' '.join(['--file', '/home/jussi/megdata/zhdanov_andrey/160412/aud_2positions_raw.fif'])
    cfg['SERVER_BIN'] = op.split(cfg['SERVER_PATH'])[1]
    cfg['BUFFER_POLL_INTERVAL'] = '100'  # how often to poll buffer (ms)
    cfg['WINDOW_LEN'] = '200'  # how much data to use for single SNR estimate (ms)
    cfg['LINE_FREQ'] = '50'
    cfg['SNR_OK'] = '10'
    cfg['SNR_BAD'] = '-5'
    #cfg['SNR_COLORS'] = {'bad': '#f44242', 'ok': '#eff700', 'good': '#57cc2c'}
    cfg['BAR_STYLE'] = 'text-align: center;'  # style for progress bar
    cfg['BAR_CHUNK_STYLE'] = 'margin: 2px;'  # style for progress bar chunk

    def __init__(self):
        self.cfg = Config.cfg.copy()
        self.section = 'HPImon'  # global section identifier
        self.configfile = '/Temp/test.cfg'
        self.__dict__.update(self.cfg)

    def read(self):
        """ Read whole config dict from disk file. Disk file must match the dict
        object in memory. """
        parser = ConfigParser.SafeConfigParser()
        parser.optionxform = str  # make it case sensitive
        parser.read(self.configfile)
        for key in self.cfg:
            try:
                # convert to numeric values when reading
                self.cfg[key] = Config.asnum(parser.get(self.section, key))
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                raise ValueError('Invalid configuration file, please fix or delete: ' + self.configfile)
        self.__dict__.update(self.cfg)

    def write(self):
        """ Save current config dict to a disk file. """
        try:
            inifile = open(self.configfile, 'wt')
        except IOError:
            raise ValueError('Cannot open config file for writing')
        parser = ConfigParser.SafeConfigParser()
        parser.optionxform = str  # make it case sensitive
        parser.add_section(self.section)
        for key in self.cfg.keys():
            parser.set(self.section, key, str(self.cfg[key]))
        parser.write(inifile)
        inifile.close()

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


            
        
        
        
