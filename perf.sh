#!/usr/bin/env bash

LOSS_LEVELS="00 05 10 20 40"
LATENCY="10"
DEVICE="lo"

mkdir results

for LEVEL in $LOSS_LEVELS ; do
    ./loss.sh -d $DEVICE -l $LATENCY -p $LEVEL up
    tests/performance.py > "results/pl_${LEVEL}_perf.txt"
    ./loss.sh -d $DEVICE -l $LATENCY -p $LEVEL down
done

