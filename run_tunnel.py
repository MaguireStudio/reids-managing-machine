import pty
import os
import subprocess
import time

def start_tunnel():
    master, slave = pty.openpty()
    p = subprocess.Popen(
        ["ssh", "-o", "StrictHostKeyChecking=no", "-R", "80:localhost:8000", "nokey@localhost.run"],
        stdin=slave, stdout=slave, stderr=slave, close_fds=True
    )
    os.close(slave)
    
    start_time = time.time()
    while time.time() - start_time < 15:
        try:
            output = os.read(master, 1024).decode('utf-8')
            if output.strip():
                print(output)
        except OSError:
            break
        time.sleep(0.5)

start_tunnel()
