#!/usr/bin/env python
# coding: utf-8

from TRECpp.adv import TimeSeries as OriginalTimeSeries


class TimeSeries(OriginalTimeSeries):
    def read(self, path):
        with open(path, 'r') as file:
            buf = file.readlines()
        buf = [l.rstrip().split(',') for l in buf]
        measure, *rIDs = buf.pop(0)
        for i, l in enumerate(buf):
            timestamp, *scores = l
            for (rID, score) in zip(rIDs, scores):
                self[timestamp][rID][i][measure] = float(score)
        return self

    def write(self, path):
        with open(path, 'w') as file:
            measure = None
            for timestamp in sorted(self.keys()):
                rd = self[timestamp]
                rIDs = sorted(rd.keys())
                for qID in sorted(rd[rIDs[0]].keys()):
                    if measure is not None:
                        file.write(timestamp)
                    for rID in rIDs:
                        rf = rd[rID][qID]
                        if measure is None:
                            assert len(rf) == 1
                            measure = sorted(rf.keys())[0]
                            file.write(','.join([measure] + rIDs))
                            file.write('\n')
                            file.write(timestamp)
                        file.write(',')
                        file.write(str(rf[measure]))
                    file.write('\n')
