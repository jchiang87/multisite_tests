#!/usr/bin/env python
import sys
import tempfile
import time
import subprocess
import click

job_batch_id = sys.argv[1]

sub_file_contents = f"""universe = local
executable = /usr/bin/condor_tail
transfer_executable = False
arguments = -maxbytes 1048576 {job_batch_id}
output = condor_tail.$(Cluster).out
error = condor_tail.$(Cluster).out
log = condor_tail.$(Cluster).log
queue
"""

with tempfile.NamedTemporaryFile(mode="w+t", delete_on_close=False) as subfile:
    subfile.write(sub_file_contents)
    filepath = subfile.name
    subfile.close()
    command = f"condor_submit {filepath}"
    for line in subprocess.check_output(command, shell=True,
                                        encoding="utf-8").split("\n"):
        if "submitted to cluster" in line:
            cluster_id = line.strip().split()[-1]
    time.sleep(5)
    while True:
        command = f"cat condor_tail.{cluster_id}out"
        print(command)
        subprocess.check_call(command, shell=True)
        if not click.confirm("Try again?", default=False):
            break
    if click.confirm("Clean up?", default=True):
        command = f"condor_rm {cluster_id}0"
        print(command)
        try:
            subprocess.check_call(command, shell=True)
        except subprocess.CalledProcessError:
            pass
        time.sleep(3)
        command = f"rm -rf condor_tail.{cluster_id}*"
        print(command)
        subprocess.check_call(command, shell=True)
