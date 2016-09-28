#!/usr/bin/env python
# coding: utf-8

class Query(dict):
    linebreak = '\n'
    separator = ':'

    def read(self, path):
        with open(path, 'r') as file:
            for line in file:
                key, value = line.split(self.separator, 1)
                self[int(key)] = value.rstrip(self.linebreak)
        return self

    def write(self, path):
        with open(path, 'w') as file:
            for k in sorted(list(self.keys())):
                file.write(self.separator.join([str(k), self[k]]))
                file.write(self.linebreak)
        return self
