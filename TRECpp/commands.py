#!/usr/bin/env python
# coding: utf-8

from argparse import ArgumentParser as AP
from os import path
from TREC import Relevance
from TREC import Result
from TREC import Run
from TRECpp.adv import RunDict
from TRECpp.csv import TimeSeries
from TRECpp.PrettyTable import ComparisonResult
from TRECpp.PrettyTable import ResultDict


def compare():
    ap = AP(
        description='Compare TREC results.'
    )
    ap.add_argument('--digits', '-d',
                    default=3,
                    help='Number of digits to be shown',
                    metavar='int',
                    type=int,
                    )
    ap.add_argument('--measure', '-m',
                    default='alpha-nDCG@10',
                    help='Evaluation measure',
                    metavar='measure',
                    type=str,
                    )
    ap.add_argument('--queryID', '-q',
                    default='amean',
                    help='Query ID or statistic to be shown',
                    metavar='ID',
                    type=str,
                    )
    ap.add_argument('--statistic', '-s',
                    default='difference',
                    help='Statistic to be shown, difference or percent',
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
    cr = rd.compare(qID=ap.queryID, measure=ap.measure)
    ComparisonResult.print(cr, measure=ap.statistic, digits=ap.digits)


def format():
    ap = AP(
        description='Format TREC results.'
    )
    ap.add_argument('--digits', '-d',
                    default=3,
                    help='Number of digits to be shown',
                    metavar='int',
                    type=int,
                    )
    ap.add_argument('--measures', '-m',
                    default=['alpha-nDCG@10', 'ERR-IA@10', 'MAP-IA'],
                    help='Evaluation measures',
                    metavar='measure',
                    nargs='+',
                    type=str,
                    )
    ap.add_argument('--queryID', '-q',
                    default='amean',
                    help='Query ID or statistic to be shown',
                    metavar='ID',
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
    rd.print(query_id=ap.queryID, measures=ap.measures, digits=ap.digits)


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


def timeseries():
    ap = AP(
        description='Sweep paird t-test for time series results.'
    )
    ap.add_argument('--digits', '-d',
                    default=3,
                    help='Number of digits to be shown',
                    metavar='int',
                    type=int,
                    )
    ap.add_argument('--hyphen', '-y',
                    default='-',
                    help='Separator of two ranking IDs',
                    metavar='str',
                    type=str,
                    )
    ap.add_argument('result',
                    help='A file of time series of results',
                    metavar='result',
                    type=str,
                    )
    ap.add_argument('--statistic', '-s',
                    default='pvalue',
                    help='Statistic to be shown',
                    metavar='statistic',
                    type=str,
                    )
    ap = ap.parse_args()
    rd = TimeSeries().read(ap.result).paired_t(sep=ap.hyphen)
    for timestamp, result in rd.items():
        for statistic, remainder in result.items():
            for pID in sorted(remainder.keys()):
                rID0, rID1 = pID.split(sep=ap.hyphen)
                if rID1 <= rID0:
                    remainder.pop(pID)
    ResultDict.print(
        rd,
        query_id=ap.statistic,
        measures=sorted(rd.measures()),
        digits=ap.digits
    )
