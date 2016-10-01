#!/usr/bin/env python
# coding: utf-8

import TREC
import unittest


class TestTREC(unittest.TestCase):

    def test_query(self):
        source = TREC.Query().read('./sample_query.txt')
        source.write('./tmp_query.txt')
        destination = TREC.Query().read('./tmp_query.txt')
        self.assertEqual(source, destination)

    def test_relevance(self):
        source = TREC.Relevance().read('./sample_relevance.txt')
        source.write('./tmp_relevance.txt')
        destination = TREC.Relevance().read('./tmp_relevance.txt')
        self.assertEqual(source, destination)

    def test_run(self):
        source = TREC.Run().read('./sample_run.txt')
        source.write('./tmp_run.txt')
        destination = TREC.Run().read('./tmp_run.txt')
        self.assertEqual(source, destination)

    def test_result(self):
        source = TREC.Result().read('./sample_result.txt')
        source.write('./tmp_result.txt')
        destination = TREC.Result().read('./tmp_result.txt')
        self.assertEqual(source, destination)


if __name__ == '__main__':
    unittest.main()
