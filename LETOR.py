# coding: utf-8

from glob import glob
import os
from TRECpp.base import Relevance as BaseRelevance
from TRECpp.base import Run


class LETOR(dict):
    def read(self, directory_path):
        directory_path = directory_path.rstrip(os.sep)
        pattern = os.path.join(directory_path, '**', 'Fold1')
        for fold1_path in glob(pattern, recursive=True):
            dataset_path = fold1_path.rsplit(os.sep, 1)[0]
            self[dataset_path] = DataSet().read(dataset_path)
        return self


class DataSet(dict):
    def read(self, directory_path):
        directory_path = directory_path.rstrip(os.sep)
        for i in [1, 2, 3, 4, 5]:
            path = os.path.join(directory_path, 'Fold%i' % i)
            self[i] = Fold().read(path)
        return self


class Fold(object):
    __slots__ = ['test', 'train', 'vali']

    def generate_all(self):
        result = Relevance()
        for slot in Fold.__slots__:
            result.update(getattr(self, slot))
        return result

    def read(self, directory_path):
        directory_path = directory_path.rstrip(os.sep)
        for slot in Fold.__slots__:
            setattr(self, slot, Relevance())
            R = getattr(self, slot)
            for path in glob(os.path.join(directory_path, slot + '*')):
                R.read(path)
        return self


class Relevance(BaseRelevance):

    class relevance(int):
        def __eq__(self, other):
            return (
                super() and
                self.feature == other.feature and
                self.meta == other.meta
            )

        def __new__(self, line):
            body, meta = line.split('#', 1)
            l = body.rstrip().split(' ')
            self = int.__new__(self, l.pop(0))
            self.feature, self.meta = {}, {}
            self.meta['qid'] = l[0].split(':', 1)[-1]
            for s in l[1:]:
                k, v = s.split(':', 1)
                if v == 'NULL':
                    v = '-inf'
                self.feature[int(k)] = float(v)
            l = meta.rstrip().split(' ')
            for i in range(len(l) // 3):
                assert l[3 * i + 1] == '='
                self.meta[l[3 * i]] = l[3 * i + 2]
            return self

    def sort_by(self, feature_index, descending=False, k=-1):
        def f(docid):
            return docid_to_rel[docid].feature[feature_index]
        result = Run()
        for qid in self:
            docid_to_rel = self[qid]['0']
            l = [docid for docid in docid_to_rel]
            l.sort(key=f)
            if descending:
                l.reverse()
            if k == -1:
                k = len(l)
            result[qid] += l[:k]
        return result

    def read(self, path):
        with open(path, 'r') as file:
            for line in file:
                relevance = self.relevance(line)
                qid = relevance.meta.pop('qid')
                docid = relevance.meta.pop('docid')
                self[qid]['0'][docid] = relevance
        return self

    def update(self, other, offset=None):
        if offset is None:
            k1 = list(self.keys())[0]
            k2 = list(self[k1]['0'].keys())[0]
            offset = len(self[k1]['0'][k2].feature)
        for qid, remainder in self.items():
            for docid, merger in remainder['0'].items():
                mergee = other[qid]['0'][docid]
                for k in sorted(mergee.feature.keys()):
                    merger.feature[offset + k] = mergee.feature[k]
        return self

    def write(self, path):
        with open(path, 'w') as file:
            for qid in sorted(self.keys()):
                remainder = self[qid]
                for docid in sorted(remainder['0'].keys()):
                    rel = remainder['0'][docid]
                    meta = {'docid': docid}
                    if hasattr(rel, 'meta'):
                        meta.update(rel.meta)
                    file.write(str(rel))
                    file.write(' ')
                    file.write('qid')
                    file.write(':')
                    file.write(qid)
                    file.write(' ')
                    if hasattr(rel, 'feature'):
                        for k in sorted(rel.feature.keys()):
                            file.write(str(k))
                            file.write(':')
                            file.write(str(rel.feature[k]))
                            file.write(' ')
                    file.write('#')
                    for k in sorted(meta.keys()):
                        file.write(k)
                        file.write(' ')
                        file.write('=')
                        file.write(' ')
                        file.write(meta[k])
                        file.write(' ')
                    file.write('\n')
