#!/usr/bin/env python
# coding: utf-8

from collections import defaultdict
import re


class Query(dict):
    linebreak = '\n'
    separator = ':'

    def read(self, path):
        with open(path, 'r') as file:
            for line in file:
                query_id, query = line.split(self.separator, 1)
                self[query_id] = query.strip()
        return self

    def write(self, path):
        with open(path, 'w') as file:
            for k in sorted(list(self.keys())):
                file.write(self.separator.join([str(k), self[k]]))
                file.write(self.linebreak)
        return self

class Relevance(dict):
    linebreak = '\n'
    separator = ' '

    def __missing__(self, query_id):
        self[query_id] = defaultdict(lambda:defaultdict(int))
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
                        file.write(self.separator.join(l))
                        file.write(self.linebreak)
        return self
