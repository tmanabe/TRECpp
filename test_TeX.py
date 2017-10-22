#!/usr/bin/env python
# coding: utf-8

from filecmp import cmp
from os import path
import tempfile
from test_base import _sample
from TRECpp import PrettyTable
from TRECpp import TeX
import unittest


class TestTeX(unittest.TestCase):
    def test_cr(self):
        source_name = 'PrettyTable_cr.txt'
        source = PrettyTable.ComparisonResult().read(_sample(source_name))
        d = tempfile.TemporaryDirectory()
        try:
            p = path.join(d.name, 'tmp.txt')
            TeX.ComparisonResult.write(source, p)
            self.assertTrue(cmp(_sample('TeX_cr.tex'), p))
        finally:
            d.cleanup()

    def test_rd(self):
        source_name = 'PrettyTable_rd.txt'
        source = PrettyTable.ResultDict().read(_sample(source_name))
        d = tempfile.TemporaryDirectory()
        try:
            p = path.join(d.name, 'tmp.txt')
            TeX.ResultDict.write(source, p)
            self.assertTrue(cmp(_sample('TeX_rd.tex'), p))
        finally:
            d.cleanup()


if __name__ == '__main__':
    unittest.main()
