#!/usr/bin/env python
# coding: utf-8

import NTCIR
import os
import tempfile
import TREC
from TRECpp.base import Ranking
import unittest


def _sample(filename):
    if 'NTCIR' in filename:
        return os.path.join('samples', filename, '*.txt')
    else:
        return os.path.join('samples', filename)


class TestBase(unittest.TestCase):
    def test_flake8(self):
        self.assertEqual(0, os.system('flake8 . --ignore D,E241'))

    def test_query_transpose(self):
        original = TREC.Query().read(_sample('TREC_query.txt'))
        actual = original.transpose()
        self.assertEqual(5, len(actual))
        for qID, q in original.items():
            self.assertTrue(q in actual.keys())
            self.assertEqual(qID, actual[q])

    def test_relevance_compact(self):
        with open(_sample('TREC_relevance_compact.txt')) as f:
            expect = f.read()
        rel = TREC.Relevance().read(_sample('TREC_relevance.txt'))
        d = tempfile.TemporaryDirectory()
        p = os.path.join(d.name, 'tmp.txt')
        rel.compact()
        rel.write(p)
        with open(p) as f:
            actual = f.read()
        d.cleanup()
        self.assertEqual(expect, actual)

    def test_relevance_single(self):
        subject = TREC.Relevance().read(_sample('TREC_relevance.txt'))
        subject.single('1')
        for query_id, remainder in subject.items():
            self.assertEqual(1, len(remainder))
            self.assertEqual('1', list(remainder.keys())[0])

    def test_ranking_generate(self):
        d = {
            'dID0': -1.0,
            'dID1': 0.0,
            'dID2': 0.0,
            'dID3': 1.0,
        }
        actual = Ranking.generate(d)
        self.assertEqual(['dID3', 'dID1', 'dID2', 'dID0'], actual)

    def test_ranking_transpose(self):
        original = Ranking()
        original += ['dID2', 'dID0', 'dID1', 'dID3']
        actual = original.transpose()
        self.assertEqual([1, 2, 0, 3], actual)

    def test_run_combine(self):
        r = TREC.Run().read(_sample('TREC_run.txt'))
        self.assertEqual(r, r.combine(r, alpha=0.0))
        self.assertEqual(r, r.combine(r, alpha=0.1))
        self.assertEqual(r, r.combine(r))
        self.assertEqual(r, r.combine(r, alpha=0.9))
        self.assertEqual(r, r.combine(r, alpha=1.0))

    def test_run_list_urls(self):
        with open(_sample('others_urllist.txt')) as f:
            expect = f.read()
        r = TREC.Run().read(_sample('TREC_run.txt'))
        d = tempfile.TemporaryDirectory()
        p = os.path.join(d.name, 'tmp.txt')
        r.list_urls(p)
        with open(p) as f:
            actual = f.read()
        d.cleanup()
        self.assertEqual(expect, actual)

    def test_run_ndeval(self):
        rel = TREC.Relevance().read(_sample('TREC_relevance.txt'))
        run = TREC.Run().read(_sample('TREC_run.txt'))
        expect = TREC.Result().read(_sample('TREC_result.csv'))
        actual = run.ndeval(rel)
        self.assertEqual(expect, actual)

    def test_run_NTCIREVAL(self):
        rel = TREC.Relevance().read(_sample('TREC_relevance.txt'))
        run = TREC.Run().read(_sample('TREC_run.txt'))
        expect = NTCIR.Result().read(_sample('NTCIR_result'))
        actual = run.NTCIREVAL(rel)
        self.assertEqual(expect, actual)


if __name__ == '__main__':
    unittest.main()
