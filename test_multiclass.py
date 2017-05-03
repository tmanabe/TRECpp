#!/usr/bin/env python
# coding: utf-8

import NTCIR
import tempfile
import TREC
import unittest


class TestMulticlass(unittest.TestCase):
    def _test(self,
              source_cls,
              target_cls,
              source_path,
              target_path,
              write_dir=False):
        d = tempfile.TemporaryDirectory()
        source = source_cls().read(source_path)
        if write_dir:
            target_cls.write(source, d.name)
            source = target_cls().read(d.name + '/*.txt')
        else:
            target_cls.write(source, d.name + '/tmp.txt')
            source = target_cls().read(d.name + '/tmp.txt')
        target = target_cls().read(target_path)
        d.cleanup()
        return (source, target)

    # Note: An NTCIR.Relevance is supporsed to contain a single intent
    def test_relevance_TtoN(self):
        source = './samples/TREC_relevance.txt'
        target = './samples/NTCIR_relevance/*.txt'
        args = [TREC.Relevance, NTCIR.Relevance, source, target, True]
        self.assertEqual(*self._test(*args))

    def test_relevance_NtoT(self):
        source = './samples/NTCIR_relevance/*.txt'
        target = './samples/TREC_relevance.txt'
        args = [NTCIR.Relevance, TREC.Relevance, source, target, False]
        source, target = self._test(*args)
        self.assertEqual(source, target.single())

    def test_run_TtoN(self):
        source = './samples/TREC_run.txt'
        target = './samples/NTCIR_run/*.txt'
        args = [TREC.Run, NTCIR.Run, source, target, True]
        self.assertEqual(*self._test(*args))

    def test_run_NtoT(self):
        source = './samples/NTCIR_run/*.txt'
        target = './samples/TREC_run.txt'
        args = [NTCIR.Run, TREC.Run, source, target, False]
        self.assertEqual(*self._test(*args))


if __name__ == '__main__':
    unittest.main()
