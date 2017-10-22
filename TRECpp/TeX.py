#!/usr/bin/env python
# coding: utf-8

from TRECpp.adv import ComparisonResult as OriginalComparisonResult
from TRECpp.adv import ResultDict as OriginalResultDict


class ComparisonResult(OriginalComparisonResult):
    def write(self, path, measure='pvalue', digits=3):
        with open(path, 'w') as file:
            keys = sorted(self.keys())
            alignment = '|'.join(['c'] * (len(keys) + 1))
            file.write('\\begin{tabular}{%s} \\hline\n' % alignment)
            file.write(' & '.join([measure] + keys) + ' \\\\ \\hline\\hline\n')
            for row_key in keys:
                file.write(row_key)
                for column_key in keys:
                    file.write(' & ')
                    if row_key == column_key:
                        continue
                    v = self[row_key][column_key][measure]
                    if isinstance(v, float):
                        file.write('%%.%if' % digits % v)
                    else:
                        file.write(str(v))
                file.write(' \\\\ \hline\n')
            file.write('\\end{tabular}\n')
        return self


class ResultDict(OriginalResultDict):
    def write(self,
              path,
              query_id='amean',
              measures=['alpha-nDCG@10', 'ERR-IA@10'],
              digits=3):
        with open(path, 'w') as file:
            rIDs = sorted(self.keys())
            alignment = '|'.join(['c'] * (len(measures) + 1))
            file.write('\\begin{tabular}{%s} \\hline\n' % alignment)
            file.write(' & '.join([query_id] + measures) + ' \\\\ \\hline\\hline\n')
            for rID in rIDs:
                file.write(rID)
                for measure in measures:
                    file.write(' & ')
                    v = self[rID][query_id][measure]
                    if isinstance(v, float):
                        file.write('%%.%if' % digits % v)
                    else:
                        file.write(str(v))
                file.write(' \\\\ \hline\n')
            file.write('\\end{tabular}\n')
        return self
