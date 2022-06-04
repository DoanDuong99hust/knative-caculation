from datetime import datetime
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
import subprocess
import os
import signal
import usbmeter

url_pods = "http://192.168.101.243:30000/api/v1/query?query=kubelet_running_pods{kubernetes_io_hostname='server06'}"
values_pods_t=json.loads(urllib.request.urlopen(url_pods).read())["data"]["result"][0]['value'][1]
DEFAULT_PODS=int(values_pods_t)

PI_IP = "192.168.101.70"
TEST_MODE = False

finished = False
timestamps={}
jobs_status = {
    "warm_done" : False,
    "cold_done" : False,
    "delete_done": False}

def start_master(command:str):
 
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('192.168.101.243', username='fil', password='1')
    print(command)
    stdin, stdout, stderr = client.exec_command(command)

    for line in stdout:
        print (line.strip('\n'))

    client.close()

def get_prom_pod_time(values:dict, target_pods:int, repetition: int):
    success = False
    url_time = "http://192.168.101.243:30000/api/v1/query?query=kube_pod_status_phase{namespace='capture',job='Kubernetes'}"
    raw = urllib.request.urlopen(url_time).read()
    output = json.loads(raw)

    for pod in output["data"]["result"]:
        try:
            pod_name = pod['metric']['pod']
            if pod_name in values.keys():
                phase = pod['metric']['phase']
                status = pod['value'][1]
                if(str(values[pod_name][0]) == "0" and phase == "Pending" and status == "1"):
                    values[pod_name][0] = pod['value'][0]
                    print("Pending!")
                elif(str(values[pod_name][1]) == "0" and phase == "Running" and status == "1"):
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
        writer = csv.writer(open("/home/luongtrann/hanoi/code/data/pod_start_time_{}_{}.csv".format(str(target_pods), str(repetition)), 'w'))
        for key, value in values.items():
            writer.writerow([key, value])
        success = True
    # else:
    #     #print("Condition is not satisfied.")
    #     print(len(values))
    #     print("require: " + str(target_pods))
    #     print(values)
    return success, values
def get_data_from_api(query:str, instance:str):
    url_data = "http://192.168.101.243:30000/api/v1/query?query=" + query
    try:
        contents = urllib.request.urlopen(url_data).read().decode('utf-8')
        values=json.loads(contents)["data"]["result"][0]['value']
    except:
        values = -1
    return values
    
def get_prometheus_values(target_pods:int, job:str, repetition: int):
    
    #CPU Usage
    url_cpu = "http://192.168.101.243:30000/api/v1/query?query=100-(avg%20by%20(instance,%20job)%20(irate(node_cpu_seconds_total{mode=%22idle%22,%20job=%22node_exporter_metrics%22,%20instance=%22192.168.101.72:9100%22}[30s])*100))"
    try:
        contents_cpu = urllib.request.urlopen(url_cpu).read().decode('utf-8')
        values_cpu=json.loads(contents_cpu)["data"]["result"][0]['value']
    except:
        values_cpu = "-1"
    #number of pods.
    url_pods = "http://192.168.101.243:30000/api/v1/query?query=kubelet_running_pods{kubernetes_io_hostname='server06'}"
    try:
        contents_pods = urllib.request.urlopen(url_pods).read()
        values_pods=json.loads(contents_pods)["data"]["result"][0]['value']
    except:
        values_pods="-1"
    #memory status
    url_memory = "http://192.168.101.243:30000/api/v1/query?query=(node_memory_MemTotal_bytes{job='node_exporter_metrics',instance='192.168.101.72:9100'}-node_memory_MemAvailable_bytes{job='node_exporter_metrics',instance='192.168.101.72:9100'})/(1024*1024)"
    try:
        contents_memory = urllib.request.urlopen(url_memory).read()
        values_memory=json.loads(contents_memory)["data"]["result"][0]['value']
    except:
        values_memory = "-1"

    #write values to file
    try:
        writer = csv.writer(open("/home/luongtrann/hanoi/code/data/server/data-prometheus_{}_{}_server.csv".format(str(target_pods), str(repetition)), 'a'))
        writer.writerow([datetime.utcfromtimestamp(values_pods[0]).strftime('%Y-%m-%d %H:%M:%S'), values_pods[1], values_cpu[1], values_memory[1], job])
    except:
        print("Error") 
    #+2 on target pods for the default pods
    curr_pods = int(values_pods[1])
    if TEST_MODE: print("Current pods: %s, target: %d" % (curr_pods, (int(target_pods)+DEFAULT_PODS)))
    if(curr_pods>=(int(target_pods)+DEFAULT_PODS)): 
       jobs_status["cold_done"] = True
       jobs_status["delete_done"] = False
        
    elif(curr_pods==DEFAULT_PODS): 
        jobs_status["delete_done"] = True

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
    timestamps["cold_start"]= time.time()
    while not jobs_status["cold_done"]:
        get_prometheus_values(target_pods, "cold", repetition)
        time.sleep(1)
    timestamps["cold_end"]= time.time()

    time.sleep(15)

    print("Scenario: WARM - Started...")
    timestamps["warm_start"]= time.time()
    warm_endtime = time.time()+(60*int(minutes)) #5min x 60
    while warm_endtime-time.time() > 0:
        get_prometheus_values(target_pods, "warm", repetition)
        time.sleep(1)
    jobs_status["warm_done"] = True
    timestamps["warm_end"]= time.time()

    #time.sleep(30) # there is no point to sleep here
        
    print("Scenario: DELETE - Started...")
    timestamps["delete_start"]= time.time()
    pods.delete_pods()
    while not jobs_status["delete_done"]:
        get_prometheus_values(target_pods, "delete", repetition)
        time.sleep(1)
        if jobs_status["delete_done"]:
            timestamps["pods_deleted"]= time.time()
            for i in range(0, 5, 1):
                get_prometheus_values(target_pods, "delete_after", repetition)
                time.sleep(1)
            timestamps["pods_deleted_after"]= time.time()

    #time.sleep(30) # there is no point to sleep here

    print("Measurement finished.")
    print("Saving timestamps..")
    timestamps_to_file(target_pods, repetition)
    print("Done")
    global finished
    finished = True
    return

def start_ummeter(target_pods: int, rep: int, time:int):
    cmd = '/usr/bin/python3 /home/luongtrann/usbmeter/usbmeter --addr 00:16:A5:00:0F:65 --out /home/luongtrann/hanoi/code/data_ummeter/data_ummeter_{}_{} --time {}'.format(target_pods, rep, time)
    s = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)

def timestamps_to_file(target_pods:int, repetition:int):
    with open('/home/luongtrann/hanoi/code/data/server/timestamps_{}_{}_server.csv'.format(str(target_pods), str(repetition)), 'w') as f:
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
        cmd = '/usr/bin/python3 /home/fil/filip/hanoi/code/main.py changevalue {} {} {}'.format(str(target_pods), str(minutes), str(rep))
        start_master(cmd)
        #p3=Process(target=start_measurement_prometheus_time, args=(target_pods, rep, ), daemon = True)
        p2=Process(target=start_measurement_prometheus, args=(minutes, target_pods, rep, ), daemon = True)
        p1=Process(target=usbmeter.main, args=(target_pods, rep, minutes, ), daemon = True)
        #p3.start()
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        #p3.join()
        print("Every process is done.")
    elif sys.argv[1] == "changevalue":
        usbmeter.main(target_pods, rep, minutes, )

    else: print("Not recognized command")