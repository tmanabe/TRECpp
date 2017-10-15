#!/usr/bin/env python
# coding: utf-8

from TRECpp.base import Ranking
from TRECpp.base import Run as BaseRun


class RunBuilder(dict):
    def __missing__(self, qid):
        self[qid] = {}
        return self[qid]

    def add_bigger(self, qid, did, score):
        self[qid][did] = max(self[qid].get(did, float('-inf')), score)

    def build(self, run):
        for qid, d in self.items():
            run[qid] = Ranking.generate(d)
        self.clear()
        return run


class Run(BaseRun):
    def read(self, dids_path, qid_score_pairs_path):
        lines = open(dids_path).readlines()
        dids = [l.rsplit(' ', 1)[-1].rstrip() for l in lines]
        lines = open(qid_score_pairs_path).readlines()
        pairs = []
        for l in lines:
            qid, _, score = l.strip().split('\t', 2)
            score = float(score)
            pairs.append((qid, score))
        assert len(dids) == len(pairs)
        builder = RunBuilder()
        for did, (qid, score) in zip(dids, pairs):
            builder.add_bigger(qid, did, score)
        return (builder.build(self))
