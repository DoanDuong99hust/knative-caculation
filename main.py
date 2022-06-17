from datetime import datetime
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
from multiprocessing import Process
from multiprocessing.pool import ThreadPool
from pods import *
import subprocess
import os
import signal
import usbmeter

url_pods = PROMETHEUS_DOMAIN + RUNNING_PODS_QUERY
values_pods_t=json.loads(urllib.request.urlopen(url_pods).read())["data"]["result"][0]['value'][1]
DEFAULT_PODS=int(values_pods_t)

finished = False
timestamps={}
jobs_status = {
    WARM_DONE_STATUS : False,
    COLD_DONE_STATUS : False,
    DELETE_DONE_STATUS: False}

def start_master(command:str):
 
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(MASTER_HOST, username=MASTER_USERNAME, password=MASTER_PASSWORD)
    print(command)
    stdin, stdout, stderr = client.exec_command(command)

    for line in stdout:
        print (line.strip('\n'))

    client.close()

def get_prom_pod_time(values:dict, target_pods:int, repetition: int):
    success = False
    url_time = PROMETHEUS_DOMAIN + POD_STATUS_PHASE_QUERY
    raw = urllib.request.urlopen(url_time).read()
    output = json.loads(raw)

    for pod in output["data"]["result"]:
        try:
            pod_name = pod['metric']['pod']
            if pod_name in values.keys():
                phase = pod['metric']['phase']
                status = pod['value'][1]
                if(str(values[pod_name][0]) == "0" and phase == PENDING_STATUS and status == "1"):
                    values[pod_name][0] = pod['value'][0]
                    print("Pending!")
                elif(str(values[pod_name][1]) == "0" and phase == RUNNING_STATUS and status == "1"):
                    values[pod_name][1] = pod['value'][0]
                    values[pod_name][2] = datetime.utcfromtimestamp(float( values[pod_name][1]) - float(values[pod_name][0])).strftime('%H:%M:%S:%f')
                    print("Running!")
                else:
                    dummy = 0
            else:
                # initialize the values
                values[pod_name] = ["0", "0", "0"]
        except Exception as e:
            print(e)
            continue

    if len(values) == int(target_pods) and (not any ("0" in x for x in list(values.values()))):
        writer = csv.writer(open(POD_START_TIME_DATA_FILE_DIRECTOR.format(str(target_pods), str(repetition)), 'w'))
        for key, value in values.items():
            writer.writerow([key, value])
        success = True
    # else:
    #     #print("Condition is not satisfied.")
    #     print(len(values))
    #     print("require: " + str(target_pods))
    #     print(values)
    return success, values
def get_data_from_api(query:str):
    url_data = PROMETHEUS_DOMAIN + query
    try:
        contents = urllib.request.urlopen(url_data).read().decode('utf-8')
        values=json.loads(contents)["data"]["result"][0]['value']
    except:
        values = -1
    return values
    
def get_prometheus_values(target_pods:int, job:str, repetition: int):
    
    values_cpu = get_data_from_api(VALUES_CPU_QUERY)
    values_pods = get_data_from_api(VALUES_PODS_QUERY)
    values_memory = get_data_from_api(VALUES_MEMORY_QUERY)
    #write values to file
    try:
        writer = csv.writer(open(DATA_PROMETHEUS_AT_SERVER_FILE_DIRECTORY.format(str(target_pods), str(repetition)), 'a'))
        writer.writerow([datetime.utcfromtimestamp(values_pods[0]).strftime('%Y-%m-%d %H:%M:%S'), values_pods[1], values_cpu[1], values_memory[1], job])
    except:
        print("Error") 
    #+2 on target pods for the default pods
    curr_pods = int(values_pods[1])
    if TEST_MODE: print("Current pods: %s, target: %d" % (curr_pods, (int(target_pods)+DEFAULT_PODS)))
    if(curr_pods>=(int(target_pods)+DEFAULT_PODS)): 
       jobs_status[COLD_DONE_STATUS] = True
       jobs_status[DELETE_DONE_STATUS] = False
        
    elif(curr_pods==DEFAULT_PODS): 
        jobs_status[DELETE_DONE_STATUS] = True

def start_measurement_prometheus_time(target_pods: int, repetition: int):
    pod_start_status = False # variable for Kien function
    values = {} # variable for Kien function
    if(int(target_pods) < 5):
        return
    while pod_start_status != True:
        pod_start_status, values = get_prom_pod_time(values, target_pods, repetition)
        time.sleep(0.2)
    return

def start_measurement_prometheus(minutes: int, target_pods: int, repetition: int):
    '''
    minutes: defines the time to measure the warm scenario
    '''
    print("Scenario: COLD - Started...")
    timestamps[COLD_START_STATUS]= time.time()
    while not jobs_status[COLD_DONE_STATUS]:
        get_prometheus_values(target_pods, "cold", repetition)
        time.sleep(1)
    timestamps[COLD_END_STATUS]= time.time()

    time.sleep(15)

    print("Scenario: WARM - Started...")
    timestamps[WARM_START_STATUS]= time.time()
    warm_endtime = time.time()+(60*int(minutes)) #5min x 60
    while warm_endtime-time.time() > 0:
        get_prometheus_values(target_pods, "warm", repetition)
        time.sleep(1)
    jobs_status[WARM_DONE_STATUS] = True
    timestamps[WARM_END_STATUS]= time.time()

    #time.sleep(30) # there is no point to sleep here
        
    print("Scenario: DELETE - Started...")
    timestamps[DELETE_START_STATUS]= time.time()
    pods.delete_pods()
    while not jobs_status[DELETE_DONE_STATUS]:
        get_prometheus_values(target_pods, "delete", repetition)
        time.sleep(1)
        if jobs_status[DELETE_DONE_STATUS]:
            timestamps["pods_deleted"]= time.time()
            for i in range(0, 5, 1):
                get_prometheus_values(target_pods, "delete_after", repetition)
                time.sleep(1)
            timestamps[POD_DELETE_AFTER_STATUS]= time.time()

    #time.sleep(30) # there is no point to sleep here

    print("Measurement finished.")
    print("Saving timestamps..")
    timestamps_to_file(target_pods, repetition)
    print("Done")
    global finished
    finished = True
    return

def start_ummeter(target_pods: int, rep: int, time:int):
    cmd = START_UMMETER_CMD.format(target_pods, rep, time)
    s = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)

def timestamps_to_file(target_pods:int, repetition:int):
    with open(TIMESTAMP_DATA_FILE_DIRECTORY.format(str(target_pods), str(repetition)), 'w') as f:
        for key in timestamps.keys():
            f.write("%s,%s\n"%(key,timestamps[key]))
    
if __name__ == "__main__":
    
    """ 
    call: python3 main.py [COMMAND] [TARGET_PODS] [MINUTES_WARM] 
    """
    target_pods = sys.argv[2]
    minutes = sys.argv[3]
    rep = sys.argv[4]
    if sys.argv[1] == "master":
        #Update replicas
        cmd = UPDATE_REPLICAS_CMD.format(str(target_pods), str(minutes), str(rep))
        start_master(cmd)
        p0=Process(target=update_replicas, args=rep, daemon=True)
        #p3=Process(target=start_measurement_prometheus_time, args=(target_pods, rep, ), daemon = True)
        p2=Process(target=start_measurement_prometheus, args=(minutes, target_pods, rep, ), daemon = True)
        p1=Process(target=usbmeter.main, args=(target_pods, rep, minutes, ), daemon = True)
        #p3.start()
        p0.start()
        p1.start()
        p2.start()
        p0.join()
        p1.join()
        p2.join()
        #p3.join()
        print("Every process is done.")
    elif sys.argv[1] == "changevalue":
        usbmeter.main(target_pods, rep, minutes, )

    else: print("Not recognized command")