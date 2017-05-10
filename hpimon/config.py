# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 13:14:16 2017

@author: hus20664877
"""


import ConfigParser
import ast
import os.path as op
from pkg_resources import resource_filename


# default config
cfg_template = resource_filename(__name__, 'default.cfg')
# user specific config
homedir = op.expanduser('~')
cfg_user = homedir + '/.hpimon.cfg'


class Section(object):
    """ Holds data for sections """
    pass


class ExtConfigParser(object):
    """ Extends SafeConfigParser by:
    1) providing attribute access as extconfigparser.section.item
    2) attributes (as above) are stored as Python types, with autoconversion by
    the ast module
    Currently read-only (i.e. no API for setting config values)
    """

    def __init__(self):
        self._parser = ConfigParser.SafeConfigParser()
        self._parser.read(cfg_template)
        self._defaultparser = self._parser
        self._update_attrs()
        # don't read the user config here,
        # to avoid triggering exceptions on import

    def _update_attrs(self):
        """ Update attributes according to current parser object. Overwrites
        existing attributes. Does not delete attributes which don't have a
        new value. """
        for section in self._parser.sections():
            if section not in self.__dict__:
                self.__dict__[section] = Section()
            cfgtxt = self._parser._sections[section]
            cfg = self._untextify(cfgtxt)
            self.__dict__[section].__dict__.update(cfg)

    def _read_user(self):
        if not op.isfile(cfg_user):
            raise IOError('User config file does not exist')
        newparser = ConfigParser.SafeConfigParser()
        newparser.read(cfg_user)
        # validate sections and keys (not yet values)
        extras = (set(newparser.sections()) -
                  set(self._defaultparser.sections()))
        if extras:
            raise ValueError('Invalid sections in config file: %s'
                             % list(extras))
        for section in newparser.sections():
            extrak = (set(newparser._sections[section].keys()) -
                      set(self._defaultparser._sections[section].keys()))
            if extrak:
                raise ValueError('Invalid keys in config file: %s' %
                                 list(extrak))
        self._parser = newparser
        self._update_attrs()

    def _write(self, file):
        cfg = open(file, 'wt')
        self._parser.write(cfg)
        cfg.close()

    def _write_user(self):
        self._write(cfg_user)

    @staticmethod
    def _untextify(di):
        """ Converts textual dict values into Python types """
        return {key: ast.literal_eval(val) for key, val in di.items()
                if key != '__name__'}

""" Provide a singleton config instance, so it doesn't have to be instantiated
separately by every caller module """
cfg = ExtConfigParser()
