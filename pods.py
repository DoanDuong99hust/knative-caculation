import yaml
import subprocess
import main_rebuild

path_capture_deploy = "deployments/object-detection.yaml"
def update_replicas(x: int):
#opens the capture file and updates the replica values
    try:
        with open(path_capture_deploy, "r") as yaml_file:    
            docs = list(yaml.load_all(yaml_file, Loader=yaml.SafeLoader))
            for doc in docs:
                for key, value in doc.items():
                    if value == "serving.knative.dev/v1":
                        doc["spec"]["template"]["metadata"]["annotations"]["autoscaling.knative.dev/min-scale"] = str(x)
                        break
        with open(path_capture_deploy, 'w') as yaml_file:
            yaml.dump_all(docs, yaml_file, default_flow_style=False)
        main_rebuild.start_master("kubectl apply -f {}".format(path_capture_deploy))
        print("Service deployed")
        #subprocess.run("kubectl apply -f capture_deploy.yaml", shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')

    except yaml.YAMLError as exc:
        print(exc)
    
def delete_pods():
    main_rebuild.start_master("kubectl delete -f {}".format(path_capture_deploy))

    #subprocess.run("kubectl delete -f capture_deploy.yaml", shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
