#!/usr/bin/env python
# coding: utf-8

from glob import glob
import os
import re
from TRECpp.base import Relevance as BaseRelevance
from TRECpp.base import Result as BaseResult
from TRECpp.base import Run as BaseRun


def path2qid(path):
    return path.rsplit(os.sep)[-1].rsplit('.')[0]


class Relevance(BaseRelevance):
    def read(self, pattern):
        for path in glob(pattern):
            query_id = path2qid(path)
            with open(path, 'r') as f:
                for line in f:
                    l = re.split('\\s+', line.rstrip(), 1)
                    document_id, relevance = l
                    relevance = relevance.lstrip('L')
                    try:
                        relevance = int(relevance)
                    except Exception:
                        relevance = float(relevance)
                    self[query_id]['0'][document_id] = relevance
        return self

    def write(self, dir, ext='txt'):
        dir = dir.rstrip(os.sep)
        for query_id in sorted(self.keys()):
            path = os.path.join(dir, query_id + '.' + ext)
            with open(path, 'w') as f:
                items = self[query_id]['0'].items()
                items = [(did, 'L' + str(rel)) for (did, rel) in items]
                for pair in sorted(items):
                    f.write(' '.join(pair) + '\n')
        return self


class Result(BaseResult):
    class measure(str):
        def __new__(self, measure, idx):
            self = str.__new__(self, measure)
            self.idx = idx
            return self

    def __missing__(self, query_id):
        super().__missing__(query_id)
        sharp = Result.measure('#', -1)
        self[query_id][sharp] = []
        return self[query_id]

    def read(self, pattern):
        for path in glob(pattern):
            query_id = path2qid(path)
            with open(path, 'r') as f:
                index = 0
                for line in f:
                    if line[0:2] == ' #':
                        self[query_id]['#'].append(line.rstrip())
                    else:
                        l = re.split(r'=\s+', line.strip(), 1)
                        measure, score = l
                        measure = Result.measure(measure, index)
                        index += 1
                        self[query_id][measure] = float(score)
        return self

    def write(self, dir, ext='txt'):
        dir = dir.rstrip(os.sep)
        for query_id in sorted(self.keys()):
            path = os.path.join(dir, query_id + '.' + ext)
            with open(path, 'w') as f:
                l = list(self[query_id].items())
                l.sort(key=lambda p: p[0].idx if hasattr(p[0], 'idx') else 0)
                for measure, score in l:
                    if measure == '#':
                        for comment in score:
                            f.write(comment + '\n')
                    else:
                        line = ' ' + measure + '='
                        line = line.ljust(21)
                        line += '%05f' % score + '\n'
                        f.write(line)
        return self


class Run(BaseRun):
    def read(self, pattern):
        for path in glob(pattern):
            query_id = path2qid(path)
            with open(path, 'r') as f:
                for line in f:
                    self[query_id].append(line.rstrip())
        return self

    def write(self, dir, ext='txt'):
        dir = dir.rstrip(os.sep)
        for query_id in sorted(self.keys()):
            path = os.path.join(dir, query_id + '.' + ext)
            with open(path, 'w') as f:
                for document_id in self[query_id]:
                    f.write(document_id + '\n')
        return self
