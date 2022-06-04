from datetime import datetime
import urllib.request
import json
import time
import csv
import main
'''
#TODO: extend CSV File with column value of COLD/WARM/DELETE

def get_prometheus_values(target_pods:int):
    #CPU Usage
    url_cpu = "http://192.168.101.243:30000/api/v1/query?query=100-(avg%20by%20(instance,%20job)%20(irate(node_cpu_seconds_total{mode=%22idle%22,%20job=%22node_exporter_metrics%22,%20instance=%22192.168.101.14:9100%22}[30s])*100))"
    contents_cpu = urllib.request.urlopen(url_cpu).read().decode('utf-8')
    values_cpu=json.loads(contents_cpu)["data"]["result"][0]['value']

    #number of pods.
    url_pods = "http://192.168.101.243:30000/api/v1/query?query=kubelet_running_pods{kubernetes_io_hostname='pi4'}"
    contents_pods = urllib.request.urlopen(url_pods).read()
    values_pods=json.loads(contents_pods)["data"]["result"][0]['value']
    
    #write values to file
    writer = csv.writer(open("data-prometeus.csv", 'a'))
    writer.writerow([datetime.utcfromtimestamp(values_pods[0]).strftime('%Y-%m-%d %H:%M:%S'), values_pods[1], values_cpu[1]])

    #+2 on target pods for the default pods
    curr_pods = int(values_pods[1])
    print("Current pods: %s, target: %s" % (curr_pods, target_pods+2))
    if(curr_pods<(target_pods+2)): 
       
        main.add_timestamp("pods_reached", time.time())
        main.set_cold_done(True)
        test = True
        
    if(values_pods[1]==0): main.add_timestamp("pods_deleted", time.time())

'''