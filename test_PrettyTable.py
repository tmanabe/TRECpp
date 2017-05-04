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
    def _test(self, cls, file_name):
        source = cls().read(_sample(file_name))
        d = tempfile.TemporaryDirectory()
        try:
            p = path.join(d.name, 'tmp.txt')
            source.write(p)
            destination = cls().read(p)
        finally:
            d.cleanup()
        return (source, destination)

    def test_cr(self):
        self.assertEqual(*self._test(
            ComparisonResult,
            'PrettyTable_cr.txt'
        ))

    def test_cr_print(self):
        rd = ResultDict()
        rd['k0'] = TREC.Result().read(_sample('TREC_result.csv'))
        rd['k1'] = TREC.Result().read(_sample('TREC_result_1.csv'))
        rd['k2'] = TREC.Result().read(_sample('TREC_result_2.csv'))
        subject = rd.paired_t()
        with open(_sample('PrettyTable_cr.txt'), 'r') as file:
            expect = file.read()
        sys.stdout = StringIO()
        try:
            ComparisonResult.print(subject)
            actual = sys.stdout.getvalue()
        finally:
            sys.stdout = sys.__stdout__
        self.assertEqual(expect, actual)

    def test_rd(self):
        self.assertEqual(*self._test(
            ResultDict,
            'PrettyTable_rd.txt'
        ))

    def test_rd_print(self):
        rd = ResultDict()
        rd['k0'] = TREC.Result().read(_sample('TREC_result.csv'))
        rd['k1'] = TREC.Result().read(_sample('TREC_result_1.csv'))
        rd['k2'] = TREC.Result().read(_sample('TREC_result_2.csv'))
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
