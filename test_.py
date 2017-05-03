#!/usr/bin/env python
# coding: utf-8

import NTCIR
import os
import tempfile
import TREC
import unittest


def _sample(filename):
    if 'NTCIR' in filename:
        return os.path.join('samples', filename, '*.txt')
    else:
        return os.path.join('samples', filename)


class TestBase(unittest.TestCase):
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
        expect = TREC.Result().read(_sample('TREC_result.txt'))
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
