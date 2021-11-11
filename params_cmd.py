#!/usr/local/sv2/jupyter/jupyter_venv/bin/python3
import json
import os
import subprocess
import sys
import glob

def get_session(jobid):
    # get the tmux session name corresponding to the jobid
    try:
        name = subprocess.check_output(['squeue','-j','{}'.format(jobid),'-O','name','--noheader'])
        return name.strip()
    except:
        return None

def gen_password():
    import string
    from random import choice
    alphabet = string.ascii_letters + string.digits
    passwd = ''.join(choice(alphabet) for i in range(8))
    return passwd

def port_pid(port):
    """
    Use lsof to determine the set of pids listening on a given port
    """
    import subprocess
    cmd = ['/usr/sbin/lsof','-Fp','-i',':{}'.format(port)]
    try:
        pids = [int(x[1:])  for x in subprocess.check_output(cmd).splitlines()]
    except:
        pids = []
    return set(pids)


def start_hterm(port,token):
    import os
    import subprocess
    import time
    env = os.environ.copy()
    env['TOKEN']=token
    env['PORT']='{}'.format(port)
    cmd = ['node','/opt/shell/shell_cmd.js']
    cmd.extend(sys.argv[1:])


    out = open(os.path.expanduser("~/.s2smux.log"),'w')
    p = subprocess.Popen(cmd,stdout=out,stderr=out,stdin=None,env=env)
    pid = p.pid
    cmd = ['/watchdog.py',str(port),str(pid),'300']
    p = subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,stdin=None)
    pids = port_pid(port)
    retry = 0
    while not pid in pids and retry < 5:
        retry = retry + 1
        time.sleep(1)
        pids = port_pid(port)
    return p

def get_free_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("",0))
    port = s.getsockname()[1]
    s.close()
    return port


token = gen_password()
port = get_free_port()
p = start_hterm(port,token)
print(json.dumps({'port':port,'token':token}))

