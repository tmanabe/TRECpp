#!/usr/bin/env python
# coding: utf-8

import NTCIR
from test_base import _sample
import TREC
from TRECpp.adv import ResultDict
from TRECpp.adv import RunDict
import unittest


class TestAdv(unittest.TestCase):
    def test_red_setitem(self):
        rd = ResultDict()
        rd['dummy'] = NTCIR.Result()
        rd['dummy'] = TREC.Result()
        try:
            rd['dummy'] = TREC.Run()
            raise
        except AssertionError:
            pass

    def test_red_compare(self):
        rd = ResultDict()
        rd['k0'] = TREC.Result().read(_sample('TREC_result.csv'))
        rd['k1'] = TREC.Result().read(_sample('TREC_result_1.csv'))
        rd['k2'] = TREC.Result().read(_sample('TREC_result_2.csv'))
        actual = rd.compare()
        self.assertAlmostEqual(0.047283, actual['k0']['k1']['difference'])
        self.assertAlmostEqual(0.056221, actual['k0']['k2']['difference'])
        self.assertAlmostEqual(0.008938, actual['k1']['k2']['difference'])
        self.assertAlmostEqual(-0.047283, actual['k1']['k0']['difference'])
        self.assertAlmostEqual(-0.056221, actual['k2']['k0']['difference'])
        self.assertAlmostEqual(-0.008938, actual['k2']['k1']['difference'])
        self.assertAlmostEqual(7.0037372, actual['k0']['k1']['percent'])
        self.assertAlmostEqual(8.2188557, actual['k0']['k2']['percent'])
        self.assertAlmostEqual(1.3066315, actual['k1']['k2']['percent'])
        self.assertAlmostEqual(-7.5312028, actual['k1']['k0']['percent'])
        self.assertAlmostEqual(-8.9548411, actual['k2']['k0']['percent'])
        self.assertAlmostEqual(-1.3239304, actual['k2']['k1']['percent'])

    def test_red_format_by(self):
        rd = ResultDict()
        rd['k0'] = NTCIR.Result()
        rd['k0']['alpha'] = 1.234
        rd['k0']['beta'] = 'abcde'
        rd['k1'] = NTCIR.Result()
        rd['k1']['alpha'] = 5.678
        rd['k1']['beta'] = 'fghij'
        rd.format_by('{alpha} ({beta})', 'gamma')
        self.assertEqual('1.234 (abcde)', rd['k0']['gamma'])
        self.assertEqual('5.678 (fghij)', rd['k1']['gamma'])

    def test_red_paired_t(self):
        rd = ResultDict()
        rd['k0'] = TREC.Result().read(_sample('TREC_result.csv'))
        rd['k1'] = TREC.Result().read(_sample('TREC_result_1.csv'))
        rd['k2'] = TREC.Result().read(_sample('TREC_result_2.csv'))
        actual = rd.paired_t()
        self.assertAlmostEqual(actual['k0']['k1']['pvalue'], 0.195121644)
        self.assertAlmostEqual(actual['k1']['k0']['pvalue'], 0.195121644)
        self.assertAlmostEqual(actual['k0']['k2']['pvalue'], 0.232938664)
        self.assertAlmostEqual(actual['k2']['k0']['pvalue'], 0.232938664)
        self.assertAlmostEqual(actual['k1']['k2']['pvalue'], 0.437758437)
        self.assertAlmostEqual(actual['k2']['k1']['pvalue'], 0.437758437)
        self.assertAlmostEqual(
            actual['k0']['k1']['statistic'],
            -actual['k1']['k0']['statistic']
        )
        self.assertAlmostEqual(
            actual['k0']['k2']['statistic'],
            -actual['k2']['k0']['statistic']
        )
        self.assertAlmostEqual(
            actual['k1']['k2']['statistic'],
            -actual['k2']['k1']['statistic']
        )
        self.assertEqual(actual['k0']['k1']['level'], '')
        self.assertEqual(actual['k1']['k0']['level'], '')
        self.assertEqual(actual['k0']['k2']['level'], '')
        self.assertEqual(actual['k2']['k0']['level'], '')
        self.assertEqual(actual['k1']['k2']['level'], '')
        self.assertEqual(actual['k2']['k1']['level'], '')

    def test_rud_setitem(self):
        rd = RunDict()
        rd['dummy'] = NTCIR.Run()
        rd['dummy'] = TREC.Run()
        try:
            rd['dummy'] = TREC.Result()
            raise
        except AssertionError:
            pass

    def test_rud_ndeval(self):
        rd = RunDict()
        rd['k0'] = TREC.Run().read(_sample('TREC_run.txt'))
        rd['k1'] = TREC.Run().read(_sample('TREC_run_1.txt'))
        rd['k2'] = TREC.Run().read(_sample('TREC_run_2.txt'))
        rel = TREC.Relevance().read(_sample('TREC_relevance.txt'))
        expect = TREC.Result().read(_sample('TREC_result.csv'))
        actual = rd.ndeval(rel)['k0']
        self.assertEqual(expect, actual)
        expect = TREC.Result().read(_sample('TREC_result_1.csv'))
        actual = rd.ndeval(rel)['k1']
        self.assertEqual(expect, actual)
        expect = TREC.Result().read(_sample('TREC_result_2.csv'))
        actual = rd.ndeval(rel)['k2']
        self.assertEqual(expect, actual)

    def test_rud_NTCIREVAL(self):
        rd = RunDict()
        rd['k0'] = TREC.Run().read(_sample('TREC_run.txt'))
        rd['k1'] = TREC.Run().read(_sample('TREC_run_1.txt'))
        rd['k2'] = TREC.Run().read(_sample('TREC_run_2.txt'))
        rel = NTCIR.Relevance().read(_sample('NTCIR_relevance'))
        expect = NTCIR.Result().read(_sample('NTCIR_result'))
        actual = rd.NTCIREVAL(rel)['k0']
        self.assertEqual(expect, actual)


if __name__ == '__main__':
    unittest.main()
