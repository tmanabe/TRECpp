#!/usr/bin/env python
# coding: utf-8

import os
import tempfile
from test_ import _sample
import TREC
import unittest


class TestTREC(unittest.TestCase):
    def _test(self, cls, filename):
        source = cls().read(_sample(filename))
        d = tempfile.TemporaryDirectory()
        p = os.path.join(d.name, 'tmp.txt')
        source.write(p)
        destination = cls().read(p)
        d.cleanup()
        return (source, destination)

    def test_validate_query_id(self):
        self.assertEqual('123', TREC.validate_query_id('123'))
        self.assertEqual('123', TREC.validate_query_id('0123'))
        self.assertEqual('123', TREC.validate_query_id('OLQ-0123'))
        self.assertEqual('amean', TREC.validate_query_id('amean'))

    def test_query(self):
        self.assertEqual(*self._test(TREC.Query, 'TREC_query.txt'))

    def test_probabilistic_relevance(self):
        cls = TREC.ProbabilisticRelevance
        path = 'TREC_probabilistic_relevance.txt'
        self.assertEqual(*self._test(cls, path))

    def test_relevance(self):
        cls = TREC.Relevance
        path = 'TREC_relevance.txt'
        self.assertEqual(*self._test(cls, path))

    def test_run(self):
        self.assertEqual(*self._test(TREC.Run, 'TREC_run.txt'))

    def test_result(self):
        self.assertEqual(*self._test(TREC.Result, 'TREC_result.txt'))


if __name__ == '__main__':
    unittest.main()
