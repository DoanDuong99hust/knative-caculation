import subprocess
import time

from constants import SERVER_USER

if __name__ == "__main__":

    # revert_lifecircle
    calculation_type = "revert_lifecircle"
    null_cold_warm_status_seconds = 30
    target_pods_scale = [4] 
    repeat_time = 3
    instance = "pi4"

    # list video: highway.mp4, 4K_video_59s.webm, traffic_34s.webm, video.mp4
    target_video = "highway.mp4"
    detection_image = ""
    if instance == SERVER_USER:
        detection_image = "29061999/knative-video-detection@sha256:477b697dae923281790d4064a2261b8a704b38baeae904a23a3b24ee0022e87d"
    else :
        detection_image = "29061999/knative-video-detection-arm@sha256:47705b6d9561b0fe45fadf559802a8d500c32b069fd50ef0fc69e6859c34a9e3"
    for target_pod in target_pods_scale:
        for rep in range(repeat_time, repeat_time + 1, 1):
            print("Target pod: {}, Repeat time: {}/{}, Instance: {}, Target video: {}, Type: {}".format(
                target_pod,rep,repeat_time,instance,target_video,calculation_type))
            cmd = '/usr/bin/python3 /home/controller/knative-caculation/main_revert.py master {} {} {} {} {} {} {}>> log.txt'.format(
                str(target_pod), str(null_cold_warm_status_seconds), str(rep), str(instance), str(target_video), str(detection_image), str(calculation_type))
            process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)