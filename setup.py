#!/usr/bin/env python
# coding: utf-8

from setuptools import setup


setup(name='TRECpp',
      version='0.0.3',
      packages=['TRECpp'],
      py_modules=['NTCIR', 'TREC'],
      entry_points='''
        [console_scripts]
        TRECpp_ndeval = TRECpp.commands:ndeval
        TRECpp_t_test = TRECpp.commands:t_test
      ''')
