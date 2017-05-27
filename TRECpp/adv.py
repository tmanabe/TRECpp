#!/usr/bin/env python
# coding: utf-8

from TRECpp.base import Relevance
from TRECpp.base import Result
from TRECpp.base import Run


class ComparisonResult(dict):  # rID1 -> rID2 -> measure -> score
    def __missing__(self, query_id):
        self[query_id] = Result()
        return self[query_id]


class ProbabilisticRelevance(Relevance):
    pass


class ResultDict(dict):  # rID -> qID -> measure -> score
    def __missing__(self, rID):
        self[rID] = Result()
        return self[rID]

    def __setitem__(self, k, v):
        assert isinstance(v, Result)
        super().__setitem__(k, v)

    def compare(self, qID='amean', measure='alpha-nDCG@10'):
        result = ComparisonResult()
        for rID1, r1 in self.items():
            for rID2, r2 in self.items():
                if rID1 == rID2:
                    continue
                res = result[rID1][rID2]
                diff = self[rID2][qID][measure] - self[rID1][qID][measure]
                res['measure'] = measure
                res['difference'] = diff
                res['percent'] = 100 * diff / self[rID2][qID][measure]
        return result

    def format_by(self, format, key=None):
        if key is None:
            key = format
        for res in self.values():
            res[key] = format.format(**res)
        return self

    def measures(self):
        result = set()
        for rID, remainder in self.items():
            for qID, remainder in remainder.items():
                for measure in remainder.keys():
                    result.add(measure)
        return result

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

    def _correlation(self, func):
        result = ComparisonResult()
        for rID0 in self.keys():
            for rID1 in self.keys():
                n = len(self[rID0].keys())
                assert n == len(self[rID1].keys())
                total_corr, total_p = 0.0, 0.0
                for qID in self[rID0].keys():
                    tau, p = func(
                        self[rID0][qID].transpose(),
                        self[rID1][qID].transpose(),
                        nan_policy='raise',
                    )
                    total_corr += tau
                    total_p += p
                result[rID0][rID1]['correlation'] = total_corr / n
                result[rID0][rID1]['pvalue'] = total_p / n
        return result

    def kendalltau(self):
        from scipy.stats import kendalltau
        return self._correlation(kendalltau)

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

    def spearmanr(self):
        from scipy.stats import spearmanr
        return self._correlation(spearmanr)


class TimeSeries(dict):  # timestamp -> ResultDict
    def __missing__(self, timestamp):
        self[timestamp] = ResultDict()
        return self[timestamp]

    def __setitem__(self, k, v):
        assert isinstance(v, ResultDict)
        super().__setitem__(k, v)

    def paired_t(self, sep='-'):
        measure, grand_rd, result = None, ResultDict(), ResultDict()
        # Original: rID -> qID -> measure -> score
        # Here: timestamp -> statistic -> pID (ranking pair ID) -> value
        timestamps = sorted(self.keys())
        for timestamp in timestamps:
            rd = self[timestamp]
            for rID, remainder in rd.items():
                for qID, remainder in remainder.items():
                    if measure is None:
                        assert len(remainder) == 1
                        measure = sorted(remainder.keys())[0]
                    score = remainder[measure]
                    qID = sep.join([timestamp, str(qID)])
                    grand_rd[rID][qID][measure] = score
            co_result = grand_rd.paired_t([], measure)  # No ignorance
            for rID1, remainder in co_result.items():
                for rID2, remainder in remainder.items():
                    pID = sep.join([rID1, rID2])
                    for stat, value in remainder.items():
                        result[timestamp][stat][pID] = value
        return result
