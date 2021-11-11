#!/bin/bash
rm ~/.strudel2_params.txt
while [ -f ~/.strudel2_params.txt ]; do sleep 1; done
nohup srun -O /params_noexit.py $1 >log 2>&1 &
while [ ! -f ~/.strudel2_params.txt ]; do sleep 1; done
cat ~/.strudel2_params.txt

