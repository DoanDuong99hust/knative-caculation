import os
import subprocess

path_src = "/home/fil/filip/hanoi/code/data"
path_dst = "/home/fil/hanoi/code/data"

for file in os.listdir(path_src):
    cmd ="sudo scp {}/{} fil@192.168.101.43:{}/{}".format(path_src, file, path_dst, file)
    print(cmd)
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
