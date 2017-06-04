#!/usr/bin/env python
# coding: utf-8

from LETOR import Relevance as Rel
from os import path
import tempfile
import unittest


class TestLETOR(unittest.TestCase):

    def test_relevance(self):
        source = Rel().read(path.join('samples', 'LETOR_relevance.txt'))
        d = tempfile.TemporaryDirectory()
        p = path.join(d.name, 'tmp.txt')
        try:
            source.write(p)
            destination = Rel().read(p)
        finally:
            d.cleanup()
        self.assertEqual(source, destination)

    def test_relevance_sort_by(self):
        original = Rel().read(path.join('samples', 'LETOR_relevance.txt'))
        self.assertEqual(
            [
                'document-1-5',
                'document-1-4',
                'document-1-3',
                'document-1-2',
                'document-1-1',
            ],
            original.sort_by(1)['1'],
        )
        self.assertEqual(
            [
                'document-2-5',
                'document-2-4',
                'document-2-3',
                'document-2-2',
                'document-2-1',
            ],
            original.sort_by(2, descending=True)['2'],
        )
        self.assertEqual(
            [
                'document-3-3',
                'document-3-4',
                'document-3-5',
            ],
            original.sort_by(3, k=3)['3'],
        )

    def test_update(self):
        original = Rel().read(path.join('samples', 'LETOR_relevance.txt'))
        actual = original.update(original)
        for qid, remainder in actual.items():
            for iid, remainder in remainder.items():
                for did, rel in remainder.items():
                    self.assertEqual(6, len(rel.feature))
                    for i in range(3):
                        self.assertEqual(
                            rel.feature[i + 1],
                            rel.feature[i + 4]
                        )


if __name__ == '__main__':
    unittest.main()
