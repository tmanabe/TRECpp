#!/usr/bin/env python
# coding: utf-8

import os
import tempfile
import TREC
import unittest


def _sample(filename):
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


if __name__ == '__main__':
    unittest.main()
