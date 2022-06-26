import time
import urllib.request
import docker
import json
import csv
from datetime import datetime
from server_constants import *

localdate = datetime.now()
generate_file_time = "{}_{}_{}_{}h{}".format(localdate.day, localdate.month, localdate.year, localdate.hour, localdate.minute)

def get_data_from_api(query:str):
    url_data = PROMETHEUS_DOMAIN + query
    try:
        contents = urllib.request.urlopen(url_data).read().decode('utf-8')
        values=json.loads(contents)["data"]["result"][0]['value']
    except:
        values = -1
    return values

client = docker.APIClient(base_url='unix://var/run/docker.sock')
for line in client.pull(IMAGE_NAME, stream=True, decode=True):
    values = dict(line)
    print(values.get('status'))
    if values.get('status') != STATUS_PULL_COMPLETE:
        values_network_receive = get_data_from_api(VALUES_NETWORK_RECEIVE_QUERY)
        values_per_cpu_in_use = get_data_from_api(VALUES_CPU_QUERY)
        values_memory = get_data_from_api(VALUES_MEMORY_QUERY)
        #write values to file
        try:
            writer = csv.writer(open(DATA_PULLING_IMAGE_FILE_DIRECTORY.format("knative_video_detection", str(SLEEP_TIME),generate_file_time), 'a'))
            writer.writerow([values_network_receive[0],datetime.utcfromtimestamp(values_network_receive[0]).strftime('%Y-%m-%d %H:%M:%S'), values_per_cpu_in_use[1], values_memory[1], values_network_receive[1], values.get('status')])
        except:
            print("Error") 
    time.sleep(SLEEP_TIME)
    # print(json.dumps(line, indent=4))
