import subprocess
import time

if __name__ == "__main__":

    warming_status_seconds = 20
    target_pods_scale = [1] 
    # target_pods = [70, 80, 90, 100]
    # for step in range(70, 120, 10):
    #    target_pods.append(step)
    repeat_time = 1
    instance = "server"
    target_video = "4K_video_59s.webm"
    for target_pod in target_pods_scale:
        for rep in range(1, repeat_time + 1, 1):
            print("Target pod: {}, Repeat time: {}/{}, Instance: {}, Target video: {}".format(target_pod,rep,repeat_time,instance,target_video))
            cmd = '/usr/bin/python3 /home/controller/knative-caculation/main_rebuild.py master {} {} {} {} {}>> log.txt'.format(
                str(target_pod), str(warming_status_seconds), str(rep), str(instance), str(target_video))
            process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
            time.sleep(15)