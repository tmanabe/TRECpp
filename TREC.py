#!/usr/bin/env python
# coding: utf-8

from collections import defaultdict
import csv
import re
from TRECpp.adv import ProbabilisticRelevance as BaseProbabilisticRelevance
from TRECpp.base import Query as BaseQuery
from TRECpp.base import Relevance as BaseRelevance
from TRECpp.base import Result as BaseResult
from TRECpp.base import Run as BaseRun


def validate_query_id(raw_query_id):
    candidate_query_id = re.sub(r'\D', '', raw_query_id).lstrip('0')
    return raw_query_id if candidate_query_id == '' else candidate_query_id


class Query(BaseQuery):
    def read(self, path):
        with open(path, 'r') as file:
            for line in file:
                query_id, query = line.split(':', 1)
                self[query_id] = query.rstrip()
        return self

    def write(self, path):
        with open(path, 'w') as file:
            for k in sorted(list(self.keys())):
                k = validate_query_id(k)
                file.write(':'.join([str(k), self[k]]))
                file.write('\n')
        return self


class ProbabilisticRelevance(BaseProbabilisticRelevance):
    class relevance(int):
        def __new__(self,
                    relevance='0',
                    method_id='-1',
                    probability='nan'):
            self = int.__new__(self, relevance)
            self.method_id = method_id
            self.probability = float(probability)
            return self

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
                    file.write(' '.join(l))
                    file.write('\n')
        return self


class Relevance(BaseRelevance):
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
                        file.write(' '.join(l))
                        file.write('\n')
        return self


class Result(BaseResult):
    class query_id(str):
        def __new__(self, query_id, run_id='_'):
            self = str.__new__(self, validate_query_id(query_id))
            self.run_id = run_id
            return self

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
        with open(path, 'w', newline='\n') as file:
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


class Run(BaseRun):
    class document_id(str):
        def __new__(self, document_id, score, key='Q0', run_id='_'):
            self = str.__new__(self, document_id)
            self.score = score
            self.key = key
            self.run_id = run_id
            return self

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
                    if isinstance(doc_id, Run.document_id):
                        doc_id = Run.document_id(
                            doc_id,
                            -(len(run_O[query_id]) + 1))
                    run_O[query_id].append(doc_id)
        return run_O

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
                    file.write(' '.join(l))
                    file.write('\n')
                    rank += 1
