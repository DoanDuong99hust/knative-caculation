import yaml
import subprocess
import main

path_capture_deploy = "/home/fil/filip/hanoi/code/capture_deploy.yaml"

def update_replicas(x: int):
#opens the capture file and updates the replica values
    try:
        with open(path_capture_deploy, "r") as yaml_file:    
            docs = list(yaml.load_all(yaml_file, Loader=yaml.SafeLoader))
            for doc in docs:
                for key, value in doc.items():
                    if value == "apps/v1":
                        doc["spec"]["replicas"] = int(x)
                        break
        with open(path_capture_deploy, 'w') as yaml_file:
            yaml.dump_all(docs, yaml_file, default_flow_style=False)
        
        main.start_master("kubectl apply -f {}".format(path_capture_deploy))
        #subprocess.run("kubectl apply -f capture_deploy.yaml", shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')

    except yaml.YAMLError as exc:
        print(exc)

def delete_pods():
    main.start_master("kubectl delete -f {}".format(path_capture_deploy))

    #subprocess.run("kubectl delete -f capture_deploy.yaml", shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
