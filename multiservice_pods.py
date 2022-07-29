import os
from pydoc import doc
import yaml
import subprocess
from constants import *
import main_rebuild
from run_on_pi4.pi4_constants import SLASH

path_file_deploy = "/home/controller/knative-caculation/multiservice_deployments/detection_origin.yaml"
path_file_output = "/home/controller/knative-caculation/multiservice_deployments/multi_detection.yaml"

def update_replicas(target_pods_scale: int, instance: str, detection_image: str):
#opens the capture file and updates the replica values
    try:  
        new_deployment = []
        for target_pod in range(0, target_pods_scale, 1):
            docs = list(yaml.load_all(open(path_file_deploy, "r"), Loader=yaml.SafeLoader))
            for doc in docs:
                for key, value in doc.items():
                    if value == "serving.knative.dev/v1":
                        doc["metadata"]["name"] = "detection"+str(target_pod+1)
                        doc["spec"]["template"]["spec"]["nodeSelector"]["kubernetes.io/hostname"] = str(instance)
                        doc["spec"]["template"]["spec"]["containers"][0]["image"] = str(detection_image)
                        break
                new_deployment.insert(target_pod,doc)

        with open(path_file_output, 'w') as yaml_file:
            yaml.dump_all(new_deployment, yaml_file, default_flow_style=False)
    except yaml.YAMLError as exc:
        print(exc)

def config_replicas(target_pods_scale: int, instance: str, detection_image: str):
    #opens the capture file and updates the replica values
    try:  
        new_deployment = []
        for target_pod in range(0, target_pods_scale, 1):
            docs = list(yaml.load_all(open(path_file_deploy, "r"), Loader=yaml.SafeLoader))
            for doc in docs:
                for key, value in doc.items():
                    if value == "serving.knative.dev/v1":
                        doc["metadata"]["name"] = "detection"+str(target_pod+1)
                        doc["spec"]["template"]["spec"]["nodeSelector"]["kubernetes.io/hostname"] = str(instance)
                        doc["spec"]["template"]["spec"]["containers"][0]["image"] = str(detection_image)
                        doc["spec"]["template"]["metadata"]["annotations"]["autoscaling.knative.dev/window"] = str(50+target_pods_scale)+"s"
                        break
                new_deployment.insert(target_pod,doc)

        with open(path_file_output, 'w') as yaml_file:
            yaml.dump_all(new_deployment, yaml_file, default_flow_style=False)
    except yaml.YAMLError as exc:
        print(exc)

def deploy_pods():
    subprocess.call('echo {} | sudo -S kubectl apply -f {}'.format(MASTER_PASSWORD, path_file_output), shell=True)
    print("Service deployed")

def delete_pods():
    subprocess.call('echo {} | sudo -S kubectl delete -f {}'.format(MASTER_PASSWORD, path_file_output), shell=True)
    print("Service deleted")
  