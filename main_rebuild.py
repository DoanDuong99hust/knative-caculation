from datetime import datetime
from nis import match
from pickle import TRUE
from tkinter import W
from constants import *
import re
import urllib.request
import json
import time
import csv
import paramiko
import pods
import getfiles
import sys
import threading
from multiprocessing import Event, Process
from multiprocessing.pool import ThreadPool
from pods import *
import subprocess
import os
import signal
import usbmeter

POD_EXISTED = 0
WARM_CALCULATION_TIME = 0
DELETE_CALCULATION_TIME = 0

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

def get_data_from_api(query:str):
    url_data = PROMETHEUS_DOMAIN + query
    try:
        contents = urllib.request.urlopen(url_data).read().decode('utf-8')
        values=json.loads(contents)["data"]["result"][0]['value']
    except:
        values = -1
    return values

def get_prometheus_values_and_update_job(target_pods:int, job:str, repetition: int, pods_existed:int):
    values_per_cpu_in_use = get_data_from_api(VALUES_CPU_QUERY)
    values_memory = get_data_from_api(VALUES_MEMORY_QUERY)
    values_running_pods = get_data_from_api(VALUES_PODS_QUERY)
    #write values to file
    try:
        writer = csv.writer(open(DATA_PROMETHEUS_AT_SERVER_FILE_DIRECTORY.format(str(target_pods), str(repetition)), 'a'))
        writer.writerow([datetime.utcfromtimestamp(values_running_pods[0]).strftime('%Y-%m-%d %H:%M:%S'), values_running_pods[1], values_per_cpu_in_use[1], values_memory[1], job])
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

def create_request():
    subprocess.call(['sh', './curl.sh'])

def timestamps_to_file(target_pods:int, repetition:int):
    with open(TIMESTAMP_DATA_FILE_DIRECTORY.format(str(target_pods), str(repetition)), 'w') as f:
        for key in timestamps.keys():
            f.write("%s,%s\n"%(key,timestamps[key]))

def calculate_cold_job(target_pods:int, repetition: int):
    print("Scenario: COLD - Started...")
    POD_EXISTED = get_pods_existed()
    while jobs_status[COLD_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, COLD_JOB, repetition, POD_EXISTED)
        time.sleep(1)
    print("Scenario: COLD - Ended...")

def calculate_cold_to_warm_job(target_pods:int, repetition: int):
    print("Scenario: COLD to WARM - Started...")
    POD_EXISTED = get_pods_existed()
    while jobs_status[COLD_TO_WARM_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, COLD_TO_WARM, repetition, POD_EXISTED)
        time.sleep(1)
    print("Scenario: COLD to WARM - Ended...")

def calculate_warm_job(target_pods:int, repetition: int):
    print("Scenario: WARM - Started...")
    POD_EXISTED = get_pods_existed()
    warm_caculation_time_count = 0
    while jobs_status[WARM_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, WARM_JOB, repetition, POD_EXISTED)
        time.sleep(1)
        warm_caculation_time_count = warm_caculation_time_count + 1
        if warm_caculation_time_count == int(WARM_CALCULATION_TIME):
            create_request()
            get_prometheus_values_and_update_job(target_pods, WARM_JOB, repetition, POD_EXISTED)
    print("Scenario: WARM - Ended...")

def calculate_active_job(target_pods:int, repetition: int):
    print("Scenario: ACTIVE - Started...")
    POD_EXISTED = get_pods_existed()
    while jobs_status[ACTIVE_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, ACTIVE_JOB, repetition, POD_EXISTED)
        time.sleep(1)

def calculate_delete_job(target_pods:int, repetition: int):
    print("Scenario: DELETE - Started...")
    POD_EXISTED = get_pods_existed()
    delete_caculation_time_count = 0
    while jobs_status[DELETE_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, DELETE_JOB, repetition, POD_EXISTED)
        time.sleep(1)
        delete_caculation_time_count = delete_caculation_time_count +1
        if delete_caculation_time_count == int(DELETE_CALCULATION_TIME):
            jobs_status[DELETE_PROCESSING] = False

def calculate_jobs(target_pods:int, repetition: int):

    pods.update_replicas(target_pods)
    calculate_cold_job(target_pods, repetition)
    calculate_cold_to_warm_job(target_pods, repetition)
    calculate_warm_job(target_pods, repetition)
    calculate_active_job(target_pods, repetition)
    pods.delete_pods() # delete service
    calculate_delete_job(target_pods, repetition)
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
    target_pods = sys.argv[2]
    WARM_CALCULATION_TIME = sys.argv[3]
    DELETE_CALCULATION_TIME = sys.argv[3]
    rep = sys.argv[4]
    if sys.argv[1] == "master":
        #Update replicas
        # cmd = UPDATE_REPLICAS_CMD.format(str(target_pods), str(WARM_CALCULATION_TIME), str(rep))
        # start_master(cmd)
        # pods.update_replicas(target_pods)
        p2=Process(target=calculate_jobs, args=(target_pods, rep, ), daemon = True)
        # p1=Process(target=usbmeter.main, args=(target_pods, rep, WARM_CALCULATION_TIME, ), daemon = True)
        # p1.start()
        p2.start()
        # p1.join()
        p2.join()
        print("Every process is done.")
    elif sys.argv[1] == "changevalue":
        usbmeter.main(target_pods, rep, WARM_CALCULATION_TIME, )

    else: print("Not recognized command")