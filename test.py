from time import sleep
from main_rebuild import *
from datetime import datetime
from subprocess import call  
import requests  
import threading
import re
import string

pwd='1'
cmd='kubectl apply -f /home/controller/knative-caculation/deployments/nginx-pod.yaml'
video_path = "/test_video/highway.mp4"
HELLO = "hello = {{'{}'}}"

timestamps = {}
terminate_state = defaultdict(list)

def create_request(url: str):
    print(url)
    rs_response = requests.get(url)
    print(rs_response.content)
    # subprocess.call(['sh','./deployments/curl.sh'])

def create_request_thread(target_pods: int):
    video_path = "test_video/" + "highway.mp4"
    for i in range(target_pods):
        print("Start thread :", i)
        threading.Thread(target=create_request, args=("http://detection.default.svc.cluster.local/{}".format(video_path),)).start()

def exec(command:str):
    subprocess.call('echo {} | sudo -S {}'.format(pwd, command), shell=True)

def get_pod_status():
    return str(subprocess.run(['deployments/get_pod_status.sh', '-l'], stdout=subprocess.PIPE).stdout.decode('utf-8')).strip()
    
    # print(re.search('\n(.*)\n', str(result)))
    # return re.search('(.*)', str(result))

def get_pods_existed():
    timestamps["start"]=time.time()
    url_server_running_pod = PROMETHEUS_DOMAIN + RUNNING_PODS_QUERY.format(CALCULATING_HOSTNAME)
    timestamps["end"]=time.time()
    # values_running_pods=json.loads(urllib.request.urlopen(url_server_running_pod).read())["data"]["result"][0]['value'][1]
    # return int(values_running_pods)

def is_pod_terminating():
    status = str(subprocess.run(['deployments/get_pod_status.sh', '-l'], stdout=subprocess.PIPE).stdout.decode('utf-8')).strip()
    return status == TERMINATING_STATUS 

if __name__=="__main__":
    dic = {'null_start': 1657816053.7551966, 'null_end': 1657816091.3298736, 
    'deploy_start': 1657816091.3298864, 'deploy_end': 1657816091.5891926, 
    'coldstart_start': 1657816091.5892005, 'coldstart_end': 1657816094.9746792, 
    'warm_start': 1657816094.974699, 'warm_end': 1657816165.2664602, 
    'curl_start': 1657816170.2689419, 'curl_end': 1657816170.2775478, 
    'active_start': 1657816170.2775507, 'active_end': 1657816211.002524, 
    'delete_start': 1657816211.0025284, 'delete_end': 1657816244.8949406}
    for key in dic.keys():
        if "_start" in key:
            job_key = re.search('(.*)_start',key).group(1)
        if "_end" in key:
            job_key = re.search('(.*)_end',key).group(1)
        print(job_key)