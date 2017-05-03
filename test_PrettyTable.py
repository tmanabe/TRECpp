#!/usr/bin/env python
# coding: utf-8

from io import StringIO
from os import path
import sys
import tempfile
from test_base import _sample
import TREC
from TRECpp.PrettyTable import ComparisonResult
from TRECpp.PrettyTable import ResultDict
import unittest


class TestPrettyTable(unittest.TestCase):
    def test_cr(self):
        source = ComparisonResult().read(_sample('PrettyTable_cr.txt'))
        d = tempfile.TemporaryDirectory()
        p = path.join(d.name, 'tmp.txt')
        source.write(p, 'statistic')
        destination = ComparisonResult().read(p)
        d.cleanup()
        self.assertEqual(source, destination)

    def test_cr_print(self):
        rd = ResultDict()
        rd['k1'] = TREC.Result().read(_sample('TREC_result.txt'))
        rd['k1']['1']['alpha-nDCG@10'] = 1.0
        rd['k2'] = TREC.Result().read(_sample('TREC_result.txt'))
        rd['k2']['2']['alpha-nDCG@10'] = 1.0
        rd['k3'] = TREC.Result().read(_sample('TREC_result.txt'))
        rd['k3']['3']['alpha-nDCG@10'] = 1.0
        rd['k4'] = TREC.Result().read(_sample('TREC_result.txt'))
        rd['k4']['4']['alpha-nDCG@10'] = 1.0
        rd['k5'] = TREC.Result().read(_sample('TREC_result.txt'))
        rd['k5']['5']['alpha-nDCG@10'] = 1.0
        subject = rd.paired_t()
        with open(_sample('PrettyTable_cr.txt'), 'r') as file:
            expect = file.read()
        sys.stdout = StringIO()
        try:
            ComparisonResult.print(subject, 'statistic')
            actual = sys.stdout.getvalue()
        finally:
            sys.stdout = sys.__stdout__
        self.assertEqual(expect, actual)

    def test_rd(self):
        source = ResultDict().read(_sample('PrettyTable_rd.txt'))
        d = tempfile.TemporaryDirectory()
        p = path.join(d.name, 'tmp.txt')
        source.write(p)
        destination = ResultDict().read(p)
        d.cleanup()
        self.assertEqual(source, destination)

    def test_rd_print(self):
        rd = ResultDict()
        rd['k1'] = TREC.Result().read(_sample('TREC_result.txt'))
        rd['k2'] = TREC.Result().read(_sample('TREC_result.txt'))
        rd['k2']['amean']['alpha-nDCG@10'] = 0.123
        rd['k2']['amean']['ERR-IA@10'] = 0.345
        rd['k3'] = TREC.Result().read(_sample('TREC_result.txt'))
        rd['k3']['amean']['alpha-nDCG@10'] = 0.567
        rd['k3']['amean']['ERR-IA@10'] = 0.789
        with open(_sample('PrettyTable_rd.txt'), 'r') as file:
            expect = file.read()
        sys.stdout = StringIO()
        try:
            rd.print()
            actual = sys.stdout.getvalue()
        finally:
            sys.stdout = sys.__stdout__
        self.assertEqual(expect, actual)


if __name__ == '__main__':
    unittest.main()
