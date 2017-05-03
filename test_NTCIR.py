#!/usr/bin/env python
# coding: utf-8

import NTCIR
import tempfile
import unittest


class TestNTCIR(unittest.TestCase):

    def _test(self, cls, pattern):
        d = tempfile.TemporaryDirectory()
        source = cls().read(pattern)
        source.write(d.name)
        destination = cls().read(d.name + '/*.txt')
        d.cleanup()
        return (source, destination)

    def test_relevance(self):
        pattern = './samples/NTCIR_relevance/*.txt'
        self.assertEqual(*self._test(NTCIR.Relevance, pattern))

    def test_run(self):
        pattern = './samples/NTCIR_run/*.txt'
        self.assertEqual(*self._test(NTCIR.Run, pattern))

    def test_result(self):
        pattern = './samples/NTCIR_result/*.txt'
        self.assertEqual(*self._test(NTCIR.Result, pattern))


if __name__ == '__main__':
    unittest.main()
