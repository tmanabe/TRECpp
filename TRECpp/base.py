#!/usr/bin/env python
# coding: utf-8

from collections import defaultdict
from os import mkdir
from os import path
from os import system
from shutil import which
from tempfile import TemporaryDirectory


class Query(dict):  # qID -> query
    def transpose(self):
        result = {}
        for k, v in self.items():
            assert v not in result.keys()
            result[v] = k
        return result


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


class Result(dict):  # qID -> measure -> score
    def __missing__(self, query_id):
        self[query_id] = {}
        return self[query_id]


class Ranking(list):  # dID list
    def transpose(self):
        result = []
        for _, i in sorted([(dID, i) for i, dID in enumerate(self)]):
            result.append(i)
        return result


class Run(dict):  # qID -> Ranking
    def __missing__(self, query_id):
        self[query_id] = Ranking()
        return self[query_id]

    def __setitem__(self, k, v):
        assert isinstance(v, Ranking)
        super().__setitem__(k, v)

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
                pairs = [(p, id) for id, p in id_to_penalty.items()]
                for penalty, doc_id in sorted(pairs):
                    run_O[query_id].append(doc_id)
        return run_O

    def list_urls(self, p, prefix='http://127.0.0.1:8080/', suffix=''):
        document_ids = set()
        for _, ranking in self.items():
            for document_id in ranking:
                document_ids.add(document_id)
        with open(p, 'w') as file:
            for document_id in sorted(document_ids):
                file.write(''.join([prefix, document_id, suffix]))
                file.write('\n')

    def ndeval(self, rel, opt='-c -traditional'):
        assert which('ndeval') is not None
        from TREC import Relevance as TREC_Relevance
        from TREC import Result as TREC_Result
        from TREC import Run as TREC_Run
        d = TemporaryDirectory()
        try:
            rel_path = path.join(d.name, 'rel.txt')
            run_path = path.join(d.name, 'run.txt')
            res_path = path.join(d.name, 'res.txt')
            TREC_Relevance.write(rel, rel_path)
            TREC_Run.write(self, run_path)
            args = (opt, rel_path, run_path, res_path)
            assert 0 == system('ndeval %s %s %s > %s' % args)
            res = TREC_Result().read(res_path)
        finally:
            d.cleanup()
        return res

    def NTCIREVAL(self, rel, opt='-g 4'):
        assert which('pyNTCIREVAL') is not None
        assert len(self) == len(rel)
        from NTCIR import Relevance as NTCIR_Relevance
        from NTCIR import Result as NTCIR_Result
        from NTCIR import Run as NTCIR_Run
        d = TemporaryDirectory()
        try:
            names = ['relevance', 'run', 'labeled_run', 'result']
            dirs = [path.join(d.name, n) for n in names]
            for dir in dirs:
                mkdir(dir)
            NTCIR_Relevance.write(rel, dirs[0])
            NTCIR_Run.write(self, dirs[1])
            for query_id in self.keys():
                args = [path.join(dir, query_id + '.txt') for dir in dirs[0:3]]
                args = tuple(args)
                system('pyNTCIREVAL label -r %s %s > %s' % args)
            for query_id in self.keys():
                basename = query_id + '.txt'
                args = [opt, path.join(dirs[0], basename)]
                args += [path.join(dir, basename) for dir in dirs[2:]]
                args = tuple(args)
                system('pyNTCIREVAL compute %s -r %s %s > %s' % args)
            result = NTCIR_Result().read(path.join(dirs[3], '*.txt'))
        finally:
            d.cleanup()
        return result
