#!/usr/bin/env python
# coding: utf-8

import os
import tempfile
from test_base import _sample
import TRECpp.csv
import unittest


class TestCSV(unittest.TestCase):

    def _test(self, cls, filename):
        source = cls().read(_sample(filename))
        d = tempfile.TemporaryDirectory()
        p = os.path.join(d.name, 'tmp.txt')
        source.write(p)
        destination = cls().read(p)
        d.cleanup()
        return (source, destination)

    def test_timeseries(self):
        self.assertEqual(*self._test(
            TRECpp.csv.TimeSeries,
            'csv_timeseries.csv'
        ))


if __name__ == '__main__':
    unittest.main()
