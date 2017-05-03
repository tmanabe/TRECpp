#!/usr/bin/env python
# coding: utf-8

from collections import defaultdict
from TRECpp.base import Relevance
from TRECpp.base import Result
from TRECpp.base import Run


class ComparisonResult(dict):  # rID1 -> rID2 -> measure -> score
    def __missing__(self, query_id):
        self[query_id] = defaultdict(lambda: defaultdict(None))
        return self[query_id]


class ProbabilisticRelevance(Relevance):
    pass


class ResultDict(dict):  # rID -> Result
    def __setitem__(self, k, v):
        assert isinstance(v, Result)
        super().__setitem__(k, v)

    def format_by(self, format, key=None):
        if key is None:
            key = format
        for res in self.values():
            res[key] = format.format(**res)
        return self

    def paired_t(self,
                 ignore=['amean'],
                 measure='alpha-nDCG@10'):
        from scipy.stats import ttest_rel
        result = ComparisonResult()
        for rID1, r1 in self.items():
            for rID2, r2 in self.items():
                if rID1 == rID2:
                    continue
                l1, l2 = [], []
                for qID, m2s1 in r1.items():
                    if qID in ignore or measure not in m2s1 or qID not in r2:
                        continue
                    m2s2 = r2[qID]
                    if measure not in m2s2:
                        continue
                    l1.append(m2s1[measure])
                    l2.append(m2s2[measure])
                statistic, pvalue = ttest_rel(l1, l2, nan_policy='raise')
                result[rID1][rID2]['measure'] = measure
                result[rID1][rID2]['statistic'] = statistic
                result[rID1][rID2]['pvalue'] = pvalue
                result[rID1][rID2]['level'] = ''
                for lv in [0.05, 0.01, 0.001]:
                    if pvalue < lv:
                        result[rID1][rID2]['level'] += '*'
        return result


class RunDict(dict):  # rID -> Run
    def __setitem__(self, k, v):
        assert isinstance(v, Run)
        super().__setitem__(k, v)

    def ndeval(self, rel, opt='-c -traditional'):
        result = ResultDict()
        for rID, r in self.items():
            result[rID] = r.ndeval(rel, opt)
        return result

    def NTCIREVAL(self, rel, opt='-g 4'):
        result = ResultDict()
        for rID, r in self.items():
            result[rID] = r.NTCIREVAL(rel, opt)
        return result
