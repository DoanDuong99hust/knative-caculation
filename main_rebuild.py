from datetime import datetime
from nis import match
from pickle import TRUE
from tkinter import W
from xxlimited import Str

import requests
from constants import *
import re
import urllib.request
import json
import time
import csv
import paramiko
import pods
import sys
import threading
from multiprocessing import Event, Process
from multiprocessing.pool import ThreadPool
from pods import *
import subprocess
import os
import signal
import run_on_pi4.usbmeter as usbmeter

localdate = datetime.now()
generate_file_time = "{}_{}_{}_{}h{}".format(localdate.day, localdate.month, localdate.year, localdate.hour, localdate.minute)

POD_EXISTED = 0
WARM_CALCULATION_TIME = 0
DELETE_CALCULATION_TIME = 0
INSTANCE = ""
TARGET_VIDEO = ""
DETECTION_IMAGE = ""

finished = False
timestamps={}
jobs_status = {
    WARM_PROCESSING : True,
    COLD_TO_WARM_PROCESSING : True,
    COLD_PROCESSING : True,
    ACTIVE_PROCESSING : True,
    DELETE_PROCESSING : True}

def get_pods_existed():
    url_server_running_pod = PROMETHEUS_DOMAIN + RUNNING_PODS_QUERY
    values_running_pods=json.loads(urllib.request.urlopen(url_server_running_pod).read())["data"]["result"][0]['value'][1]
    return int(values_running_pods)

def start_master(command:str):
 
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(MASTER_HOST, username=MASTER_USERNAME, password=MASTER_PASSWORD)
    print(command)
    stdin, stdout, stderr = client.exec_command(command)

    for line in stdout:
        print (line.strip('\n'))

    client.close()

def start_pi4(command:str):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(PI_IP, username=PI_USERNAME, password=PI_PASSWORD)
    print(command)
    stdin, stdout, stderr = client.exec_command(command)

    for line in stdout:
        print (line.strip('\n'))

    client.close()

def get_data_from_api(query:str):
    url_data = PROMETHEUS_DOMAIN + query
    try:
        contents = urllib.request.urlopen(url_data).read().decode('utf-8')
        values=json.loads(contents)["data"]["result"][0]['value']
    except:
        values = -1
    return values

def is_pod_terminating():
    status = str(subprocess.run(['deployments/get_pod_status.sh', '-l'], stdout=subprocess.PIPE).stdout.decode('utf-8')).strip()
    return status == TERMINATING_STATUS

def get_prometheus_values_and_update_job(target_pods:int, job:str, repetition: int, pods_existed:int):
    values_per_cpu_in_use = get_data_from_api(VALUES_CPU_QUERY)
    values_memory = get_data_from_api(VALUES_MEMORY_QUERY)
    values_running_pods = get_data_from_api(VALUES_PODS_QUERY)

    if is_pod_terminating():
        job = job + ":terminating"
    #write values to file
    try:
        writer = csv.writer(open(DATA_PROMETHEUS_FILE_DIRECTORY.format(
            str(INSTANCE),str(target_pods),str(repetition),str(TARGET_VIDEO),str(INSTANCE),generate_file_time), 'a'))
        writer.writerow([values_running_pods[0],datetime.utcfromtimestamp(values_running_pods[0]).strftime('%Y-%m-%d %H:%M:%S'), values_running_pods[1], values_per_cpu_in_use[1], values_memory[1], job])
    except:
        print("Error") 
    # if TEST_MODE: print("Current pods: %s, target: %d" % (curr_pods, (int(target_pods)+POD_EXSISTED)))
    update_job_status(job, values_running_pods, pods_existed)

def update_job_status(job:str, values_running_pods, pods_existed):
        #+2 on target pods for the default pods
    curr_running_pods = int(values_running_pods[1])
    if COLD_JOB == job:
        if curr_running_pods > pods_existed:
            jobs_status[COLD_PROCESSING] = False
    elif COLD_TO_WARM == job:
        if curr_running_pods < pods_existed:
            jobs_status[COLD_TO_WARM_PROCESSING] = False
    elif WARM_JOB == job:
        if curr_running_pods > pods_existed:
            jobs_status[WARM_PROCESSING] = False
    elif ACTIVE_JOB == job:
        if curr_running_pods < pods_existed:
            jobs_status[ACTIVE_PROCESSING] = False

def create_request(url: str):
    print(url)
    rs_response = requests.get(url)
    print(rs_response)
    # subprocess.call(['sh','./deployments/curl.sh'])

def create_request_thread():
    video_path = "test_video/" + TARGET_VIDEO
    print("Start thread")
    threading.Thread(target=create_request, args=("http://detection.default.svc.cluster.local/{}".format(video_path),)).start()

def timestamps_to_file(target_pods:int, repetition:int):
    with open(TIMESTAMP_DATA_FILE_DIRECTORY.format(str(target_pods), str(repetition)), 'w') as f:
        for key in timestamps.keys():
            f.write("%s,%s\n"%(key,timestamps[key]))

def calculate_cold_job(target_pods:int, repetition: int):
    print("Scenario: COLD - Started...")
    POD_EXISTED = get_pods_existed()
    while jobs_status[COLD_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, COLD_JOB, repetition, POD_EXISTED)
        time.sleep(0.5)
    print("Scenario: COLD - Ended...")

def calculate_cold_to_warm_job(target_pods:int, repetition: int):
    print("Scenario: COLD to WARM - Started...")
    POD_EXISTED = get_pods_existed()
    while jobs_status[COLD_TO_WARM_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, COLD_TO_WARM, repetition, POD_EXISTED)
        time.sleep(0.2)
    print("Scenario: COLD to WARM - Ended...")

def calculate_warm_job(target_pods:int, repetition: int):
    print("Scenario: WARM - Started...")
    POD_EXISTED = get_pods_existed()
    warm_caculation_time_count = 0
    while jobs_status[WARM_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, WARM_JOB, repetition, POD_EXISTED)
        time.sleep(0.5)
        warm_caculation_time_count = warm_caculation_time_count + 1
        if warm_caculation_time_count == int(WARM_CALCULATION_TIME):
            create_request_thread()
            get_prometheus_values_and_update_job(target_pods, WARM_JOB, repetition, POD_EXISTED)
    print("Scenario: WARM - Ended...")

def calculate_active_job(target_pods:int, repetition: int):
    print("Scenario: ACTIVE - Started...")
    POD_EXISTED = get_pods_existed()
    while jobs_status[ACTIVE_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, ACTIVE_JOB, repetition, POD_EXISTED)
        time.sleep(0.2)

def calculate_active_scale_job(target_pods:int, repetition: int):
    print("Scenario: ACTIVE SCALE - Started...")
    POD_EXISTED = get_pods_existed()
    warm_caculation_time_count = 0
    while jobs_status[WARM_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, WARM_JOB, repetition, POD_EXISTED)
        time.sleep(0.5)
        warm_caculation_time_count = warm_caculation_time_count + 1
        if warm_caculation_time_count == int(300):
            create_request_thread()
            get_prometheus_values_and_update_job(target_pods, WARM_JOB, repetition, POD_EXISTED)
    print("Scenario: ACTIVE SCALE - Ended...")

def calculate_delete_job(target_pods:int, repetition: int):
    print("Scenario: DELETE - Started...")
    POD_EXISTED = get_pods_existed()
    delete_caculation_time_count = 0
    while jobs_status[DELETE_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, DELETE_JOB, repetition, POD_EXISTED)
        time.sleep(0.5)
        delete_caculation_time_count = delete_caculation_time_count +1
        if delete_caculation_time_count == int(DELETE_CALCULATION_TIME):
            jobs_status[DELETE_PROCESSING] = False

def calculate_scale_jobs(target_pods:int, repetition: int):
    pods.update_replicas(target_pods, INSTANCE, DETECTION_IMAGE)
    calculate_cold_job(target_pods, repetition)
    calculate_warm_job(target_pods, repetition)
    calculate_active_scale_job(target_pods, repetition)
    pods.delete_pods() # delete service
    calculate_delete_job(target_pods, repetition)
    print("Measurement finished.")
    print("Saving timestamps..")
    # timestamps_to_file(target_pods, repetition)
    print("Done")
    global finished
    finished = True
    return

def calculate_jobs(target_pods:int, repetition: int):

    pods.update_replicas(target_pods, INSTANCE, DETECTION_IMAGE)
    calculate_cold_job(target_pods, repetition)
    calculate_cold_to_warm_job(target_pods, repetition)
    calculate_warm_job(target_pods, repetition)
    calculate_active_job(target_pods, repetition)
    pods.delete_pods() # delete service
    calculate_delete_job(target_pods, repetition)
    print("Measurement finished.")
    print("Saving timestamps..")
    # timestamps_to_file(target_pods, repetition)
    print("Done")
    global finished
    finished = True
    return

if __name__ == "__main__":
    
    """ 
    call: python3 main.py [COMMAND] [TARGET_PODS] [MINUTES_WARM] 
    """
    target_pods_scale = sys.argv[2]
    WARM_CALCULATION_TIME = sys.argv[3]
    DELETE_CALCULATION_TIME = sys.argv[3]
    repeat_time = sys.argv[4]
    INSTANCE = sys.argv[5]
    TARGET_VIDEO = sys.argv[6]
    DETECTION_IMAGE = sys.argv[7]
    if sys.argv[1] == "master":
        # Call to source code at pi4 
        if INSTANCE == "pi4":
            print("Start calculate power on pi4")
            p0=Process(target=start_pi4, args=(RUN_UMMETER_AT_PI4_CMD.format(target_pods_scale, repeat_time, TARGET_VIDEO, generate_file_time), ))
        print("Start calculate job on {}".format(INSTANCE))
        p1=Process(target=calculate_jobs, args=(target_pods_scale, repeat_time, ), daemon = True)
        p0.start()
        time.sleep(6)
        p1.start()
        p1.join()
        p0.join()

        # p1=Process(target=calculate_scale_jobs, args=(target_pods_scale, repeat_time, ), daemon = True)
        # p1.start()
        # p1.join()
        print("Every process is done.")

    else: print("Not recognized command")