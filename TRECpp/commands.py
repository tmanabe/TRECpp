#!/usr/bin/env python
# coding: utf-8

from argparse import ArgumentParser as AP
from os import path
from TREC import Relevance
from TREC import Result
from TREC import Run
from TRECpp.adv import RunDict


def ndeval():
    ap = AP(
        description='Batch-ndeval TREC runs.'
    )
    ap.add_argument('relevance',
                    help='A TREC relevance file',
                    metavar='relevance',
                    type=str,
                    )
    ap.add_argument('results_dir',
                    help='A dir for TREC evaluation result files',
                    metavar='results_dir',
                    type=str,
                    )
    ap.add_argument('runs',
                    help='TREC run files',
                    metavar='run',
                    nargs='+',
                    type=str,
                    )
    ap = ap.parse_args()
    rd = RunDict()
    for run in ap.runs:
        rd[run] = Run().read(run)
    rel = Relevance().read(ap.relevance)
    for run, result in rd.ndeval(rel).items():
        base_name = path.basename(run)
        Result.write(result, path.join(ap.results_dir, base_name))
