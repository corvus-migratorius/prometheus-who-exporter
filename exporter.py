#!/usr/bin/env python3

import subprocess
import time

who_up = 0  # exporter status 1 - working, 0 - dead
who_active = {}  # users active sessions

def parse_who_output(output):
    """
    "who -u" output parsing  
    """
    active_sessions = {}
    for line in output.splitlines():
        rows = line.split()
        username = rows[0]
        idle_time = rows[3]
        if idle_time == '.':
            active_sessions[username] = active_sessions.get(username, 0) + 1
    return active_sessions

def update_metrics():
    """
    Update metrics function
    """
    global who_up, who_active
    try:
        result = subprocess.run(['who', '-u'], capture_output=True, text=True)
        if result.returncode == 0:
            who_up = 1
            
            who_active = parse_who_output(result.stdout)
        else:
            who_up = 0
    except Exception as e:
        print(f"Error: {e}")
        who_up = 0

if __name__ == '__main__':
    while True:
        update_metrics()
        time.sleep(5) 

