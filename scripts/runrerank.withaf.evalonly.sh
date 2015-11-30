#!/bin/bash
NUMS="0.00001 0.0001 0.001 0.01 0.05 0.1 0.5 1 5 10 50 100"

for NUM in $NUMS
do
	python rerank_refactored.py --language $1 --subdirectory withAffixFeatsNoAffixCands/ --config_file rerankll.m3ps.evalonly.config --l1 $NUM --l2 $NUM
done
