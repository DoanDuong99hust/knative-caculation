import subprocess
from main_rebuild import *
import docker
import json
from server_constants import *

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
            writer = csv.writer(open(DATA_PULLING_IMAGE_FILE_DIRECTORY.format("knative_video_detection", str(SLEEP_TIME)), 'a'))
            writer.writerow([datetime.utcfromtimestamp(values_network_receive[0]).strftime('%Y-%m-%d %H:%M:%S'), values_per_cpu_in_use[1], values_memory[1], values_network_receive[1], values.get('status')])
        except:
            print("Error") 
    time.sleep(SLEEP_TIME)
    # print(json.dumps(line, indent=4))