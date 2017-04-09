#!/usr/bin/env python
# coding: utf-8

from collections import defaultdict
import csv
from os import system
import re
from shutil import which
from tempfile import TemporaryDirectory


def validate_query_id(raw_query_id):
    candidate_query_id = re.sub(r'\D', '', raw_query_id).lstrip('0')
    return raw_query_id if candidate_query_id == '' else candidate_query_id


class Query(dict):
    linebreak = '\n'
    separator = ':'

    def read(self, path):
        with open(path, 'r') as file:
            for line in file:
                query_id, query = line.split(Query.separator, 1)
                self[query_id] = query.rstrip()
        return self

    def write(self, path):
        with open(path, 'w') as file:
            for k in sorted(list(self.keys())):
                k = validate_query_id(k)
                file.write(Query.separator.join([str(k), self[k]]))
                file.write(Query.linebreak)
        return self


class ProbabilisticRelevance(dict):
    linebreak = '\n'
    separator = ' '

    class relevance(int):
        def __new__(self,
                    relevance='0',
                    method_id='-1',
                    probability='nan'):
            self = int.__new__(self, relevance)
            self.method_id = method_id
            self.probability = float(probability)
            return self

    def __missing__(self, query_id):
        self[query_id] = defaultdict(lambda: defaultdict(self.relevance))
        return self[query_id]

    def read(self, path):
        with open(path, 'r') as file:
            for line in file:
                l = re.split('\\s+', line.strip(), 4)
                query_id, document_id = l[0:2]
                relevance = self.relevance(*l[2:])
                self[query_id]['0'][document_id] = relevance
        return self

    def write(self, path):
        with open(path, 'w') as file:
            for query_id in sorted(list(self.keys())):
                from_d = self[query_id]['0']
                query_id = validate_query_id(query_id)
                for document_id in sorted(list(from_d.keys())):
                    relevance = from_d[document_id]
                    if not isinstance(relevance, self.relevance):
                        relevance = self.relevance(relevance)
                    l = [
                        query_id,
                        document_id,
                        str(relevance),
                        relevance.method_id,
                        str(relevance.probability),
                    ]
                    file.write(ProbabilisticRelevance.separator.join(l))
                    file.write(ProbabilisticRelevance.linebreak)
        return self


class Relevance(dict):
    linebreak = '\n'
    separator = ' '

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

    def read(self, path):
        with open(path, 'r') as file:
            for line in file:
                l = re.split('\\s+', line.strip(), 3)
                query_id, intent_id, document_id, relevance = l
                try:
                    relevance = int(relevance)
                except Exception:
                    relevance = float(relevance)
                self[query_id][intent_id][document_id] = relevance
        return self

    def write(self, path):
        with open(path, 'w') as file:
            for query_id in sorted(list(self.keys())):
                from_i = self[query_id]
                query_id = validate_query_id(query_id)
                for intent_id in sorted(list(from_i.keys())):
                    from_d = from_i[intent_id]
                    for document_id in sorted(list(from_d.keys())):
                        relevance = from_d[document_id]
                        l = [
                            query_id,
                            intent_id,
                            document_id,
                            str(relevance),
                        ]
                        file.write(Relevance.separator.join(l))
                        file.write(Relevance.linebreak)
        return self


class Result(dict):
    linebreak = '\n'

    class query_id(str):
        def __new__(self, query_id, run_id='_'):
            self = str.__new__(self, validate_query_id(query_id))
            self.run_id = run_id
            return self

    def __missing__(self, query_id):
        self[query_id] = {}
        return self[query_id]

    def read(self, path):
        with open(path, 'r') as file:
            for d in csv.DictReader(file):
                query_id = Result.query_id(query_id=d.pop('topic'),
                                           run_id=d.pop('runid').rstrip())
                l = self[query_id]
                for measure in d:
                    try:
                        value = float(d[measure])
                        if(value != value):  # NaN
                            l[measure] = None
                        else:
                            l[measure] = value
                    except ValueError:
                        if d[measure] == '-1.#IND00':  # Zero division
                            l[measure] = None
                        else:
                            raise RuntimeError('TREC.Result::read:' +
                                               'Unknown value')
        return self

    def write(self, path):
        fieldnames = ['runid', 'topic']
        fieldnames += list(self[list(self.keys())[0]].keys())
        with open(path, 'w', newline=Result.linebreak) as file:
            writer = csv.DictWriter(file, fieldnames)
            writer.writeheader()
            for query_id in sorted(list(self.keys())):
                d_s = self[query_id]
                if not isinstance(query_id, Result.query_id):
                    query_id = Result.query_id(query_id)
                d_d = {'runid': query_id.run_id, 'topic': query_id}
                for measure in d_s:
                    if measure == '#':
                        continue
                    value = d_s[measure]
                    if value is None:
                        d_d[measure] = '-nan'
                    else:
                        d_d[measure] = '{0:.6f}'.format(value)
                writer.writerow(d_d)
        return self


class Run(dict):
    linebreak = '\n'
    separator = ' '

    class document_id(str):
        def __new__(self, document_id, score, key='Q0', run_id='_'):
            self = str.__new__(self, document_id)
            self.score = score
            self.key = key
            self.run_id = run_id
            return self

    def __missing__(self, query_id):
        self[query_id] = []
        return self[query_id]

    def list_urls(self, path, prefix='http://127.0.0.1:8080/', suffix=''):
        document_ids = set()
        for _, ranking in self.items():
            for document_id in ranking:
                document_ids.add(document_id)
        with open(path, 'w') as file:
            for document_id in sorted(document_ids):
                file.write(''.join([prefix, document_id, suffix]))
                file.write(Run.linebreak)

    def ndeval(self, rel, opt='-c -traditional'):
        assert which('ndeval') is not None
        d = TemporaryDirectory()
        rel_path = '%s/rel.txt' % d.name
        run_path = '%s/run.txt' % d.name
        res_path = '%s/res.txt' % d.name
        Relevance.write(rel, rel_path)
        Run.write(self, run_path)
        assert 0 == system(
            'ndeval %s %s %s > %s' % (opt, rel_path, run_path, res_path))
        res = Result().read(res_path)
        d.cleanup()
        return res

    def read(self, path):
        query_id_to_pairs = defaultdict(list)
        with open(path, 'r') as file:
            for line in file:
                l = re.split('\\s+', line.strip(), 5)
                query_id, key, document_id, rank, score, run_id = l
                query_id_to_pairs[query_id].append([
                    -float(score),
                    Run.document_id(document_id,
                                    score=score,
                                    key=key,
                                    run_id=run_id),
                ])
        for query_id in query_id_to_pairs:
            pairs = query_id_to_pairs[query_id]
            l = self[query_id]
            for pair in sorted(pairs):
                l.append(pair[-1])
        return self

    def write(self, path):
        with open(path, 'w') as file:
            for query_id in sorted(list(self.keys())):
                document_ids = self[query_id]
                query_id = validate_query_id(query_id)
                rank = 1
                for document_id in document_ids:
                    if not isinstance(document_id, Run.document_id):
                        document_id = Run.document_id(document_id,
                                                      score=float(-rank))
                    l = [
                        query_id,
                        document_id.key,
                        document_id,
                        str(rank),
                        str(document_id.score),
                        document_id.run_id,
                    ]
                    file.write(Run.separator.join(l))
                    file.write(Run.linebreak)
                    rank += 1
