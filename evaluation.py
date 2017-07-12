#!/usr/bin/env python
"""
Horn Concerto - Evaluation for inference.
Author: Tommaso Soru <tsoru@informatik.uni-leipzig.de>
Version: 0.0.1
Usage:
    Use test endpoint (DBpedia)
    > python evaluation.py <TEST_SET> <INFERRED_TRIPLES>
"""
import sys
from joblib import Parallel, delayed
import numpy as np
import multiprocessing

reload(sys)
sys.setdefaultencoding("utf-8")

VERSION = "0.0.1"

############################### ARGUMENTS ################################
num_cores = multiprocessing.cpu_count()
print "Cores: ", num_cores

TEST_SET = sys.argv[1]
INFERRED = sys.argv[2]

test = list()

def evaluate(t):
    # corrupted
    t_triple = t.split(' ')
    corr_obj = "{} {}".format(t_triple[0], t_triple[1])
    corr_sub = "{} {}".format(t_triple[1], t_triple[2])
    # print "corr_obj=", corr_obj
    # print "corr_sub=", corr_sub
    pos = 1
    with open(INFERRED) as f:
        for line in f:
            line = line[:-1].split('\t')
            if t == line[1]:
                return pos
            triple = line[1].split(' ')
            if corr_obj in line[1]:
                # print "\t" + line[1]
                # filter out if true
                if not line[1] in test:
                    pos += 1            
            elif corr_sub in line[1]:
                # print "\t" + line[1]
                # filter out if true
                if not line[1] in test:
                    pos += 1
            
    return None

# index test set
with open(TEST_SET) as f:
    for line in f:
        line = line[:-1].split(' ')
        test.append(line[0] + " " + line[1] + " " + line[2])

def range_test(t):
    h1 = 0
    h3 = 0
    h10 = 0
    rr = 0
    pos = evaluate(t)
    print "{}\n\t{}".format(t, pos)
    if pos is None:
        rr += 1.0 / len(test)
        return rr, 0, 0, 0
    rr = 1.0 / pos
    if pos <= 1:
        h1 = 1
    if pos <= 3:
        h3 = 1
    if pos <= 10:
        h10 = 1
    # if n % 50 == 0:
    #     mrr = rr / n
    #     hitsAt1 = float(h1) / n
    #     hitsAt3 = float(h3) / n
    #     hitsAt10 = float(h10) / n
    #     print "MRR = {}".format(mrr)
    #     print "Hits@1 = {}".format(hitsAt1)
    #     print "Hits@3 = {}".format(hitsAt3)
    #     print "Hits@10 = {}".format(hitsAt10)
    return rr, h1, h3, h10

rr, h1, h3, h10 = 0, 0, 0, 0

STEP = 50

for i in range(len(test)):
    if i % STEP == 0:
        start = i / STEP
        result = Parallel(n_jobs=num_cores)(delayed(range_test)(t=t) for t in test[i:i+STEP])
        rr, h1, h3, h10 = np.sum(result, axis=0) + (rr, h1, h3, h10)
        n = i + STEP
        mrr = rr / n
        hitsAt1 = float(h1) / n
        hitsAt3 = float(h3) / n
        hitsAt10 = float(h10) / n
        print "adding range {} to {}".format(i, i+STEP)
        print "|test| = {}".format(n)
        print "MRR = {}".format(mrr)
        print "Hits@1 = {}".format(hitsAt1)
        print "Hits@3 = {}".format(hitsAt3)
        print "Hits@10 = {}".format(hitsAt10)

# add remainder
result = Parallel(n_jobs=num_cores)(delayed(range_test)(t=t) for t in test[STEP*(len(test)/STEP):])
rr, h1, h3, h10 = np.sum(result, axis=0) + (rr, h1, h3, h10)
print "adding range {} to {}".format(STEP*(len(test)/STEP), "END")

mrr = rr / len(test)
hitsAt1 = float(h1) / len(test)
hitsAt3 = float(h3) / len(test)
hitsAt10 = float(h10) / len(test)
print "\nFINAL RESULTS"
print "|test| = {}".format(len(test))
print "MRR = {}".format(mrr)
print "Hits@1 = {}".format(hitsAt1)
print "Hits@3 = {}".format(hitsAt3)
print "Hits@10 = {}".format(hitsAt10)