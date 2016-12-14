# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 15:50:55 2016

@author: jussi
"""

from setuptools import setup


setup(name='hpimon',
      version='0.1',
      description='Continuous HPI monitor for Elekta MEG systems',
      author='Jussi Nurminen',
      author_email='jnu@iki.fi',
      license='MIT',
      url='https://github.com/jjnurminen/hpimon',
      include_package_data=True,
      entry_points={
          'gui_scripts': ['hpimon = hpimon.hpimon:main']
      })
