#!/usr/bin/env python
# coding: utf-8

import RankLib
import unittest


class TestRankLib(unittest.TestCase):
    def test_run_builder_missing(self):
        actual = RankLib.RunBuilder()
        actual['dummy']['dummy'] = 12.3

    def test_run_builder_add_bigger(self):
        actual = RankLib.RunBuilder()
        actual.add_bigger('dummy', 'dummy', 45.6)
        actual.add_bigger('dummy', 'dummy', 12.3)
        self.assertEqual(45.6, actual['dummy']['dummy'])

    def test_run_builder_build(self):
        actual = RankLib.RunBuilder()
        actual['qID0']['dID0'] = 1.2
        actual['qID0']['dID1'] = 3.4
        actual['qID1']['dID0'] = 7.8
        actual['qID1']['dID1'] = 5.6
        result = actual.build(RankLib.Run())
        self.assertEqual(0, len(actual))
        self.assertEqual(['dID1', 'dID0'], result['qID0'])
        self.assertEqual(['dID0', 'dID1'], result['qID1'])

    def test_run_read_1(self):
        actual = RankLib.Run().read('./samples/RankLib_half_run_1.txt',
                                    './samples/RankLib_half_run_1.tsv')
        self.assertEqual(1, len(actual))
        self.assertTrue('1' in actual)
        self.assertEqual(1, len(actual['1']))
        self.assertEqual('clueweb09-en0010-57-32932', actual['1'][0])

    def test_run_read_2(self):
        actual = RankLib.Run().read('./samples/RankLib_half_run_2.txt',
                                    './samples/RankLib_half_run_2.tsv')
        self.assertEqual(2, len(actual))
        self.assertTrue('qID0' in actual)
        self.assertEqual(2, len(actual['qID0']))
        self.assertEqual('456', actual['qID0'][0])
        self.assertEqual('123', actual['qID0'][1])
        self.assertTrue('qID1' in actual)
        self.assertEqual(2, len(actual['qID1']))
        self.assertEqual('123', actual['qID1'][0])
        self.assertEqual('456', actual['qID1'][1])


if __name__ == '__main__':
    unittest.main()
