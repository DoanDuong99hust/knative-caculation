import os
import yaml
import subprocess
from constants import *
import main_rebuild
from run_on_pi4.pi4_constants import SLASH

path_file_deploy = "/home/controller/knative-caculation/deployments/object-detection.yaml"
def update_replicas(target_pods_scale: int, instance: str, detection_image: str):
#opens the capture file and updates the replica values
    try:
        with open(path_file_deploy, "r") as yaml_file:    
            docs = list(yaml.load_all(yaml_file, Loader=yaml.SafeLoader))
            for doc in docs:
                for key, value in doc.items():
                    if value == "serving.knative.dev/v1":
                        doc["spec"]["template"]["metadata"]["annotations"]["autoscaling.knative.dev/max-scale"] = str(target_pods_scale)
                        doc["spec"]["template"]["spec"]["nodeSelector"]["kubernetes.io/hostname"] = str(instance)
                        doc["spec"]["template"]["spec"]["containers"][0]["image"] = str(detection_image)
                        break
        with open(path_file_deploy, 'w') as yaml_file:
            yaml.dump_all(docs, yaml_file, default_flow_style=False)
        subprocess.call('echo {} | sudo -S kubectl apply -f {}'.format(MASTER_PASSWORD, path_file_deploy), shell=True)
        # main_rebuild.start_master("kubectl apply -f {}".format(path_capture_deploy))
        print("Service deployed")
        #subprocess.run("kubectl apply -f capture_deploy.yaml", shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')

    except yaml.YAMLError as exc:
        print(exc)
    
def delete_pods():
    subprocess.call('echo {} | sudo -S kubectl delete -f {}'.format(MASTER_PASSWORD, path_file_deploy), shell=True)
    # main_rebuild.start_master("kubectl delete -f {}".format(path_capture_deploy))

    #subprocess.run("kubectl delete -f capture_deploy.yaml", shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')