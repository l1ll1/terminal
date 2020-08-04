#!/usr/bin/python3
import json
import os
import subprocess
import sys
import glob

def get_session(jobid):
    # get the tmux session name corresponding to the jobid
    #name = subprocess.check_output(['squeue','-j','{}'.format(jobid),'-O','name','--noheader'])
    cmd = ['ssh','localhost','-o','StrictHostKeyChecking=no','tmux','list-sessions']
    try:
        #sessions = subprocess.check_output(['squeue','-j','{}'.format(jobid),'-O','name','--noheader'])
        sessions = subprocess.check_output(cmd)
        lines = sessions.splitlines()
        if len(lines) == 1:
            return sessions.splitlines()[0].split(b':')[0]
        else:
            print(sessions)
            raise Exception("Can't identify the correct session")
    except subprocess.CalledProcessError as e:
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
    cmd = ['/usr/bin/lsof','-Fp','-i',':{}'.format(port)]
    try:
        pids = [int(x[1:])  for x in subprocess.check_output(cmd).splitlines()]
    except:
        pids = []
    return set(pids)


def start_hterm(port,session,token):
    import os
    import subprocess
    import time
    cmd = ['node','/opt/shell/tmux.js']
    env = os.environ.copy()
    env['TOKEN']=token
    env['PORT']='{}'.format(port)
    if session is not None:
        env['SESSION']=session

    out = open(os.path.expanduser("~/.s2smux.log"),'w')
    p = subprocess.Popen(cmd,stdout=out,stderr=out,stdin=None,env=env)
    pid = p.pid
    cmd = ['/watchdog.py',str(port),str(pid),'300']
    subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=None,stdin=None)
    pids = port_pid(port)
    retry = 0
    while not pid in pids and retry < 5:
        retry = retry + 1
        time.sleep(1)
        pids = port_pid(port)
        



def get_free_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("",0))
    port = s.getsockname()[1]
    s.close()
    return port

jobid = sys.argv[1]

token = gen_password()
port = get_free_port()
session = get_session(jobid)
try:
    start_hterm(port,session,token)
except Exception as e:
    print(json.dumps({'error': '{}'.format(e)}))
    sys.exit(1)
print(json.dumps({'port':port,'token':token}))
