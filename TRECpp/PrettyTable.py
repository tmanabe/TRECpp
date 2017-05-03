#!/usr/bin/env python
# coding: utf-8

from prettytable import PrettyTable
from re import split
from TRECpp.adv import ComparisonResult as OriginalComparisonResult
from TRECpp.adv import ResultDict as OriginalResultDict


class ComparisonResult(OriginalComparisonResult):
    def _print(self, measure, digits):
        header = [measure] + sorted(self.keys())
        table = PrettyTable(header)
        table.align = 'r'
        for row_key in sorted(self.keys()):
            l = [row_key]
            for column_key in sorted(self.keys()):
                if row_key == column_key:
                    l.append('')
                    continue
                v = self[row_key][column_key][measure]
                if isinstance(v, float):
                    l.append('%%.%if' % digits % v)
                else:
                    l.append(str(v))
            table.add_row(l)
        return table

    def print(self, measure, digits=3):
        print(ComparisonResult._print(self, measure, digits))

    def read(self, path):
        with open(path, 'r') as file:
            buf = file.readlines()
        buf = [split(r'\s*\|\s*', l)[1:-1] for l in buf]
        measure, *column_keys = buf[1]
        for bu in buf[3:-1]:
            row_key, *b = bu
            assert len(column_keys) == len(b)
            for column_key, v in zip(column_keys, b):
                if v == '':
                    continue
                try:
                    v = int(v)
                except ValueError:
                    try:
                        v = float(v)
                    except ValueError:
                        v = str(v)
                self[row_key][column_key][measure] = v
        return self

    def write(self, path, measure, digits=3):
        table = ComparisonResult._print(self, measure, digits)
        with open(path, 'w') as file:
            file.write(str(table))
        return self


class ResultDict(OriginalResultDict):
    def _print(self, query_id, measures, digits):
        header = [query_id] + measures
        table = PrettyTable(header)
        table.align = 'r'
        for rID in sorted(self.keys()):
            l = [rID]
            for measure in measures:
                v = self[rID][query_id][measure]
                if isinstance(v, float):
                    l.append('%%.%if' % digits % v)
                else:
                    l.append(str(v))
            table.add_row(l)
        return table

    def print(self,
              query_id='amean',
              measures=['alpha-nDCG@10', 'ERR-IA@10'],
              digits=3):
        print(ResultDict._print(self, query_id, measures, digits))

    def read(self, path):
        with open(path, 'r') as file:
            buf = file.readlines()
        buf = [split(r'\s*\|\s*', l)[1:-1] for l in buf]
        query_id, *measures = buf[1]
        for bu in buf[3:-1]:
            rID, *b = bu
            assert len(measures) == len(b)
            for measure, v in zip(measures, b):
                if v == '':
                    continue
                try:
                    v = int(v)
                except ValueError:
                    try:
                        v = float(v)
                    except ValueError:
                        v = str(v)
                self[rID][query_id][measure] = v
        return self

    def write(self,
              path,
              query_id='amean',
              measures=['alpha-nDCG@10', 'ERR-IA@10'],
              digits=3):
        table = ResultDict._print(self, query_id, measures, digits)
        with open(path, 'w') as file:
            file.write(str(table))
        return self
