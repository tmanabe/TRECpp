#!/usr/bin/env python
# coding: utf-8

from test_base import _sample
from TREC import Relevance
from TREC import Run
from TRECpp.click import click
import unittest


class TestClick(unittest.TestCase):
    def test_relevance(self):
        relevance = Relevance().read(_sample('TREC_relevance.txt'))
        run = Run().read(_sample('TREC_run.txt'))
        result = click(relevance, run)
        self.assertEqual(result['1'], [])
        self.assertEqual(result['2'], [0])
        self.assertEqual(result['3'], [1, 5])
        self.assertEqual(result['4'], [1, 2, 5])
        self.assertEqual(result['5'], [2, 3, 4, 5])


if __name__ == '__main__':
    unittest.main()
