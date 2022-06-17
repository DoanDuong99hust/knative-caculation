import subprocess
import time

if __name__ == "__main__":

    minutes = 1
    target_pods = [1]
    # target_pods = [70, 80, 90, 100]
    # for step in range(70, 120, 10):
    #    target_pods.append(step)
    reps = 1
    for target in target_pods:
        for rep in range(0, reps, 1):
            print("Target: {}, rep:{}/{}".format(target,rep,reps))
            cmd = '/usr/bin/python3 /home/controller/knative-caculation/main.py master {} {} {} >> log.txt'.format(str(target), str(minutes), str(rep))
            process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
            time.sleep(15)