#!/bin/bash
env
ssh -t localhost -o StrictHostKeyChecking=no tmux new-session -d -s $SLURM_JOBID bash
# determine the process id of the tmux server
pid=$( /bin/ps x | /bin/grep -i "[t]mux new-session -d -s" | sed 's/^\ *//' | cut -f 1 -d " " )
echo $pid
ps x
# Sleep until the tmux server exits
while [ -e /proc/$pid ]; do sleep 5; done
