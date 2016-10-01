#!/usr/bin/env python
# coding: utf-8

from collections import defaultdict
import csv
import re


class Query(dict):
    linebreak = '\n'
    separator = ':'

    def read(self, path):
        with open(path, 'r') as file:
            for line in file:
                query_id, query = line.split(Query.separator, 1)
                self[query_id] = query.strip()
        return self

    def write(self, path):
        with open(path, 'w') as file:
            for k in sorted(list(self.keys())):
                file.write(Query.separator.join([str(k), self[k]]))
                file.write(Query.linebreak)
        return self


class Relevance(dict):
    linebreak = '\n'
    separator = ' '

    def __missing__(self, query_id):
        self[query_id] = defaultdict(lambda: defaultdict(int))
        return self[query_id]

    def read(self, path):
        with open(path, 'r') as file:
            for line in file:
                l = re.split('\\s+', line.strip(), 3)
                query_id, intent_id, document_id, relevance = l
                relevance = int(relevance)
                self[query_id][intent_id][document_id] = relevance
        return self

    def write(self, path):
        with open(path, 'w') as file:
            for query_id in sorted(list(self.keys())):
                from_i = self[query_id]
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
    separator = ','
    run_id = '_'

    def __missing__(self, query_id):
        self[query_id] = {}
        return self[query_id]

    def read(self, path):
        with open(path, 'r') as file:
            for d in csv.DictReader(file):
                d.pop('runid')
                query_id = d.pop('topic')
                l = self[query_id]
                for measure in d:
                    value = float(d[measure])
                    if(value != value):  # NaN
                        l[measure] = None
                    else:
                        l[measure] = value
        return self

    def write(self, path):
        fieldnames = ['runid', 'topic']
        fieldnames += list(self[list(self.keys())[0]].keys())
        with open(path, 'w', newline=Result.linebreak) as file:
            writer = csv.DictWriter(file, fieldnames)
            writer.writeheader()
            for query_id in sorted(list(self.keys())):
                d_s = self[query_id]
                d_d = {'runid': Result.run_id, 'topic': query_id}
                for measure in d_s:
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
    run_id = '_'

    def __missing__(self, query_id):
        self[query_id] = []
        return self[query_id]

    def read(self, path):
        query_id_to_pairs = defaultdict(list)
        with open(path, 'r') as file:
            for line in file:
                l = re.split('\\s+', line.strip(), 5)
                query_id, k, document_id, rank, score, s = l
                query_id_to_pairs[query_id].append([
                    -float(score),
                    document_id,
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
                rank = 1
                for document_id in document_ids:
                    l = [
                        query_id,
                        'Q0',
                        document_id,
                        str(rank),
                        str(-rank),
                        Run.run_id,
                    ]
                    file.write(Run.separator.join(l))
                    file.write(Run.linebreak)
                    rank += 1
        return self
