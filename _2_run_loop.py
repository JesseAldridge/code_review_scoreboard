import subprocess, time

import secrets

while True:
    for line in secrets.command_lines:
        subprocess.call(line.split())
    # Run every 2 weeks
    time.sleep(60 * 60 * 24 * 7 * 2)
