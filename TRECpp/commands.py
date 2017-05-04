#!/usr/bin/env python
# coding: utf-8

from argparse import ArgumentParser as AP
from os import path
from TREC import Relevance
from TREC import Result
from TREC import Run
from TRECpp.adv import RunDict
from TRECpp.adv import ResultDict
from TRECpp.PrettyTable import ComparisonResult


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

def t_test():
    ap = AP(
        description='Batch-t-test TREC results.'
    )
    ap.add_argument('--digits', '-d',
                    default=3,
                    help='Number of digits to be shown',
                    metavar='int',
                    type=int,
                    )
    ap.add_argument('--ignore', '-i',
                    default=['amean'],
                    help='Query IDs to be ignored',
                    metavar='qID',
                    nargs='+',
                    type=str,
                    )
    ap.add_argument('--measure', '-m',
                    default='alpha-nDCG@10',
                    help='Evaluation measure',
                    metavar='measure',
                    type=str,
                    )
    ap.add_argument('--statistic', '-s',
                    default='pvalue',
                    help='Statistic to be shown',
                    metavar='statistic',
                    type=str,
                    )
    ap.add_argument('results',
                    help='TREC result files',
                    metavar='result',
                    nargs='+',
                    type=str,
                    )
    ap = ap.parse_args()
    rd = ResultDict()
    for result in ap.results:
        rd[result] = Result().read(result)
    cr = rd.paired_t(ignore=ap.ignore, measure=ap.measure)
    ComparisonResult.print(cr, measure=ap.statistic, digits=ap.digits)
