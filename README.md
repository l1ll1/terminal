This container runs code derived from 
https://osc.github.io/ood-documentation/master/applications/shell.html

When starting the program as a batch job, it simply submits a tmux new-session
When connecting to the program, 
it:

a) picks an unused port
b) generates a random token for authenticaion
c) runs a command like ssh localhost tmux attach-session <sessionid>
d) proxys that command onto the unused port
e) watches (using lsof) for connections to the port. if its been disconnected for 5 minutes it shuts down the proxy
f) prints out the port and token in json format

Because the proxy is inside the container, but the tmux server is outside we have to do a bit ssh localhost
When doing this we supress operations relating to SSHKnowHosts (beacuse localhost is rarely the same localhost)

Debugging:
----------

1) Check that you can start a tmux session via echo "module load singularity\nsingularity exec term.sif /start" | sbatch This is what strudel2 does

2) Find out which node your tmux is running on, login, singularity shell term.sif

3) Inside the singularity shell, try executing /params. Check that it gives json output. Check that it starts node /opt/shell/tmux.js and watchdog.py

4) Create an SSH tunnel to the port specified. Open the URL localhost:<port>/tmux?token=<token>
