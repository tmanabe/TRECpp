#!/usr/bin/env python
# coding: utf-8

from collections import defaultdict
from os import system
from shutil import which
from tempfile import TemporaryDirectory


class Query(dict):  # qID -> query
    pass


class Relevance(dict):  # qID -> iID -> dID -> relevance
    def __missing__(self, query_id):
        self[query_id] = defaultdict(lambda: defaultdict(int))
        return self[query_id]

    def compact(self):
        for query_id, remainder in self.items():
            for intent_id, d in remainder.items():
                for document_id in sorted(d.keys()):
                    if d[document_id] <= 0:
                        d.pop(document_id)
        return self

    def single(self, iID='0'):
        for query_id, remainder in self.items():
            for k in sorted(remainder.keys()):
                if k != iID:
                    remainder.pop(k)
        return self


class ProbabilisticRelevance(Relevance):
    pass


class Result(dict):  # qID -> measure -> score
    def __missing__(self, query_id):
        self[query_id] = {}
        return self[query_id]


class Run(dict):  # qID -> rank -> dID
    def __missing__(self, query_id):
        self[query_id] = []
        return self[query_id]

    def combine(run_A, run_B, alpha=0.5):
        '''Combine two runs. See [Cai+, SIGIR\'04] .'''
        run_O = Run()
        for query_id in run_A:
            if query_id in run_B:
                ranking_A, ranking_B = run_A[query_id], run_B[query_id]
                assert sorted(ranking_A) == sorted(ranking_B)
                id_to_penalty = {}
                for index, doc_id in enumerate(ranking_A):
                    rank = index + 1
                    id_to_penalty[doc_id] = alpha * rank
                for index, doc_id in enumerate(ranking_B):
                    rank = index + 1
                    id_to_penalty[doc_id] += (1 - alpha) * rank
                pairs = [(penalty, doc_id) for doc_id, penalty in id_to_penalty.items()]
                run_O[query_id] = []
                for penalty, doc_id in sorted(pairs):
                    run_O[query_id].append(doc_id)
        return run_O

    def list_urls(self, path, prefix='http://127.0.0.1:8080/', suffix=''):
        document_ids = set()
        for _, ranking in self.items():
            for document_id in ranking:
                document_ids.add(document_id)
        with open(path, 'w') as file:
            for document_id in sorted(document_ids):
                file.write(''.join([prefix, document_id, suffix]))
                file.write('\n')

    def ndeval(self, rel, opt='-c -traditional'):
        assert which('ndeval') is not None
        from TREC import Relevance as TREC_Relevance
        from TREC import Result as TREC_Result
        from TREC import Run as TREC_Run
        d = TemporaryDirectory()
        rel_path = '%s/rel.txt' % d.name
        run_path = '%s/run.txt' % d.name
        res_path = '%s/res.txt' % d.name
        TREC_Relevance.write(rel, rel_path)
        TREC_Run.write(self, run_path)
        assert 0 == system(
            'ndeval %s %s %s > %s' % (opt, rel_path, run_path, res_path))
        res = TREC_Result().read(res_path)
        d.cleanup()
        return res
