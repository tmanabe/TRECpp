#!/usr/bin/env python
# coding: utf-8

from setuptools import setup


setup(name='TRECpp',
      version='0.0.6',
      packages=['TRECpp'],
      py_modules=['LETOR', 'NTCIR', 'RankLib', 'TREC'],
      entry_points='''
          [console_scripts]
          TRECpp_compare = TRECpp.commands:compare
          TRECpp_correlation = TRECpp.commands:correlation
          TRECpp_format = TRECpp.commands:format
          TRECpp_ndeval = TRECpp.commands:ndeval
          TRECpp_t_test = TRECpp.commands:t_test
          TRECpp_timeseries = TRECpp.commands:timeseries
      ''')
