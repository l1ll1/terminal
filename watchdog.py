#!/usr/bin/python3
import psutil
import sys
import time
import os
import signal

# A simple watchdog program. If the program (pid) isn't connected after <n> seconds (on the given port)
# kill it.
# This means we will clean up programs that either
# a) weren't connected to witing <n> seconds
# b) were connected to, but have since been disconnected for 60 seconds

def connected(port):
    nc = psutil.net_connections()
    for c in nc:
        if c.laddr.port == port:
            try:
                rport = c.raddr.port
                if rport is not None:
                    return True
            except:
                pass
    return False

def kill_pid(pid):
    try:
        os.kill(pid,signal.SIGINT)
    except Exception as e:
        pass

def running(pid):
    return psutil.pid_exists(pid)

port = int(sys.argv[1])
pid = int(sys.argv[2])
interval = int(sys.argv[3])
while True:
    time.sleep(interval)
    if not connected(port):
        kill_pid(pid)
        time.sleep(1)
    if not running(pid):
        exit(0)


