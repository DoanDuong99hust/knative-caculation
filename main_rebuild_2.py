from collections import defaultdict
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

ACTIVE_CALCULATION_TIME = 0
NULL_CALCULATION_TIME = 0
COLD_CALCULATION_TIME = 0
INSTANCE = ""
TARGET_VIDEO = ""
DETECTION_IMAGE = ""
CALCULATING_HOSTNAME = SERVER_USER
CALCULATING_INSTANCE = SERVER_IP
POD_EXISTED = 0

finished = False
timestamps={}
terminate_state = defaultdict(list)
jobs_status = {
    NULL_PROCESSING : True,
    COLD_START_PROCESSING : True,
    WARM_PROCESSING : True,
    COLD_PROCESSING : True,
    ACTIVE_PROCESSING : True,
    DELETE_PROCESSING : True}

def get_pods_existed():
    url_server_running_pod = PROMETHEUS_DOMAIN + str(RUNNING_PODS_QUERY).format(CALCULATING_HOSTNAME)
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

def get_prometheus_values_and_update_job(target_pods:int, job:str, repetition: int):
    values_per_cpu_in_use = get_data_from_api(VALUES_CPU_QUERY.format(CALCULATING_INSTANCE))
    values_memory = get_data_from_api(VALUES_MEMORY_QUERY.format(CALCULATING_INSTANCE,CALCULATING_INSTANCE,CALCULATING_INSTANCE))
    values_running_pods = get_data_from_api(VALUES_PODS_QUERY.format(CALCULATING_HOSTNAME))

    update_job_status(job, values_running_pods, target_pods)
    if is_pod_terminating():
        if WARM_STATE != job or (WARM_STATE == job and ((int(values_running_pods[1])-int(POD_EXISTED)) <= target_pods)):
            job = job + ":terminating"
            terminate_state[job].append(time.time())
    #write values to file
    try:
        writer = csv.writer(open(DATA_PROMETHEUS_FILE_DIRECTORY.format(
            str(INSTANCE),str(target_pods),str(repetition),str(TARGET_VIDEO),str(INSTANCE),generate_file_time), 'a'))
        writer.writerow([values_running_pods[0],datetime.utcfromtimestamp(values_running_pods[0]).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], values_running_pods[1], values_per_cpu_in_use[1], values_memory[1], job])
    except:
        print("Error") 
    # if TEST_MODE: print("Current pods: %s, target: %d" % (curr_pods, (int(target_pods)+POD_EXSISTED)))

def update_job_status(state:str, values_running_pods, target_pods:int):
    #+2 on target pods for the default pods
    curr_running_pods = int(values_running_pods[1])
    # print(state, values_running_pods, target_pods, POD_EXISTED)
    if COLD_START_STATE == state or "cold_start:curl" == state:
        if curr_running_pods == POD_EXISTED + target_pods:
            jobs_status[COLD_START_PROCESSING] = False
    elif WARM_STATE == state:
        if curr_running_pods == POD_EXISTED:
            jobs_status[WARM_PROCESSING] = False
    elif DELETE_JOB == state:
        if curr_running_pods == POD_EXISTED:
            jobs_status[DELETE_PROCESSING] = False

def create_request(url: str):
    rs_response = requests.get(url)
    print(rs_response.content)
    # subprocess.call(['sh','./deployments/curl.sh'])

def create_request_thread(target_pods: int):
    video_path = "test_video/" + TARGET_VIDEO
    for i in range(target_pods):
        print("Start thread :", i + 1)
        threading.Thread(target=create_request, args=("http://detection.default.svc.cluster.local/{}".format(video_path),)).start()

def timestamps_to_file(target_pods:int, repetition:int):
    print(timestamps)
    with open(DATA_TIMESTAMP_FILE_DIRECTORY.format(
        str(INSTANCE), str(target_pods), str(repetition), str(TARGET_VIDEO), str(INSTANCE), generate_file_time), 'w') as f:
        for key, value in terminate_state.items():
            timestamps[key+"_start"]=min(value)
            timestamps[key+"_end"]=max(value)

        for key in timestamps.keys():
            if "_start" in key:
                job_key = re.search('(.*)_start',key).group(1)
            if "_end" in key:
                job_key = re.search('(.*)_end',key).group(1)
            f.write("%s,%s,%s\n"%(key,timestamps[key],job_key))

def calculate_null_job(target_pods:int, repetition: int, state:str):
    print("Scenario: NULL - Started...")
    cold_calculation_time_count = 0
    while jobs_status[NULL_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, state, repetition)
        time.sleep(0.5)
        cold_calculation_time_count = cold_calculation_time_count + 0.5
        if cold_calculation_time_count == int(NULL_CALCULATION_TIME):
            jobs_status[NULL_PROCESSING] = False
    print("Scenario: NULL - Ended...")

def calculate_cold_start_job(target_pods:int, repetition: int, state:str):
    print("Scenario: COLD START - Started...")
    while jobs_status[COLD_START_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, state, repetition)
        time.sleep(0.5)
    print("Scenario: COLD START - Ended...")

def calculate_warm_job(target_pods:int, repetition: int):
    print("Scenario: WARM - Started...")
    while jobs_status[WARM_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, WARM_JOB, repetition)
        time.sleep(0.5)
    print("Scenario: WARM - Ended...")

def calculate_cold_job(target_pods:int, repetition: int):
    print("Scenario: COLD - Started...")
    cold_caculation_time_count = 0
    while jobs_status[COLD_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, COLD_STATE, repetition)
        time.sleep(0.5)
        cold_caculation_time_count = cold_caculation_time_count + 0.5
        if cold_caculation_time_count == int(COLD_CALCULATION_TIME):
            jobs_status[COLD_PROCESSING] = False
    print("Scenario: COLD - Ended...")

def calculate_active_job(target_pods:int, repetition: int):
    print("Scenario: ACTIVE - Started...")
    active_calculation_time_count = 0
    while jobs_status[ACTIVE_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, ACTIVE_JOB, repetition)
        time.sleep(0.5)
        active_calculation_time_count = active_calculation_time_count + 0.5
        if active_calculation_time_count == int(ACTIVE_CALCULATION_TIME):
            pods.delete_pods()
            jobs_status[ACTIVE_PROCESSING] = False
    print("Scenario: ACTIVE - Ended...")

def calculate_delete_job(target_pods:int, repetition: int):
    print("Scenario: DELETE - Started...")
    while jobs_status[DELETE_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, DELETE_JOB, repetition)
        time.sleep(0.5)
    print("Scenario: DELETE - Ended...")

def calculate_jobs(target_pods:int, repetition: int):

    timestamps["null_start"]=time.time()
    calculate_null_job(target_pods, repetition, NULL_STATE)
    timestamps["null_end"]=time.time()

    timestamps["deploy_start"]=time.time()
    pods.update_replicas(target_pods, INSTANCE, DETECTION_IMAGE)
    timestamps["deploy_end"]=time.time()

    timestamps["coldstart_start"]=time.time()
    calculate_cold_start_job(target_pods, repetition, COLD_START_STATE)
    timestamps["coldstart_end"]=time.time()

    timestamps["warm_start"]=time.time()
    calculate_warm_job(target_pods, repetition)
    timestamps["warm_end"]=time.time()

    timestamps["cold_start"]=time.time()
    calculate_cold_job(target_pods, repetition)
    timestamps["cold_end"]=time.time()

    timestamps["curl_start"]=time.time()
    create_request_thread(target_pods)
    timestamps["curl_end"]=time.time()

    timestamps["curl_coldstart_start"]=time.time()
    jobs_status[COLD_START_PROCESSING] = True
    calculate_cold_start_job(target_pods, repetition, "cold_start:curl")
    timestamps["curl_coldstart_end"]=time.time()

    timestamps["active_start"]=time.time()
    calculate_active_job(target_pods, repetition)
    timestamps["active_end"]=time.time()

    timestamps["delete_start"]=time.time()
    calculate_delete_job(target_pods, repetition)
    timestamps["delete_end"]=time.time()

    timestamps["null_after_delete_start"]=time.time()
    jobs_status[NULL_PROCESSING] = True
    calculate_null_job(target_pods, repetition,"null:after_delete")
    timestamps["null_after_delete_end"]=time.time()

    print("Measurement finished.")
    print("Saving timestamps..")
    timestamps_to_file(target_pods, repetition)
    print("Done")
    global finished
    finished = True
    return

if __name__ == "__main__":
    
    """ 
    call: python3 main.py [COMMAND] [TARGET_PODS] [MINUTES_WARM] 
    """
    target_pods_scale = sys.argv[2]
    ACTIVE_CALCULATION_TIME = sys.argv[3]
    repeat_time = sys.argv[4]
    INSTANCE = sys.argv[5]
    TARGET_VIDEO = sys.argv[6]
    DETECTION_IMAGE = sys.argv[7]
    NULL_CALCULATION_TIME = sys.argv[8]
    COLD_CALCULATION_TIME = sys.argv[3]
    if sys.argv[1] == "master":
        # Call to source code at pi4 
        if INSTANCE == "pi4":
            print("Start calculate power on pi4")
            CALCULATING_HOSTNAME = PI4_USER
            CALCULATING_INSTANCE = PI4_IP    
            p0=Process(target=start_pi4, args=(RUN_UMMETER_AT_PI4_CMD.format(int(target_pods_scale), repeat_time, TARGET_VIDEO, generate_file_time), ))
        print("Start calculate job on {}".format(INSTANCE))
        POD_EXISTED = get_pods_existed()
        p1=Process(target=calculate_jobs, args=(int(target_pods_scale), repeat_time, ), daemon = True)
        p0.start()
        time.sleep(8)
        p1.start()
        p1.join()
        p0.join()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
        print("Every process is done.")

    else: print("Not recognized command")