from cmath import log
from collections import defaultdict
import csv
from email.mime import base
from math import log2
from tkinter.font import names
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import re

POD_STATE = "pod_state"
POD_STATUS = "pod_status"
TIMESTAMP = "timestamp"
STATE = "state"
TARGET_PODS = "target_pods"
REPEAT_TIME = "repeat_time"
MEAN = "mean"

data_by_day_folder = "20_7_2022"
target_folder = "pi4" 
data_directory = "D:\FIL\DATN\Data\\timestamp\\" + target_folder + "\\" + data_by_day_folder
output_data_dir = "D:\FIL\DATN\DataOptimize\\timestamp\\" + target_folder + "\\"
data_optimize_file = output_data_dir+"data_{}_{}_optimize_tmp.csv"

def remove_optimize_file(file_directory:str):
    if os.path.exists(file_directory):
      os.remove(file_directory)
    else:
        print("The file does not exist")

def get_dic_data(file_directory:str, data_type:str):
    data_pd = pd.read_csv(file_directory, sep=',', names=[POD_STATUS, TIMESTAMP, STATE])
    data_arr = np.transpose(np.array([data_pd[STATE], data_pd[data_type]]))
    dict_data = defaultdict(list)
    for key, value in data_arr:
        dict_data[key].append(value)
    data_mean_dic = defaultdict(list)
    for key, value in dict_data.items():
        data_mean_dic[key].append(max(value) - min(value))
    # cold_to_warm = {"cold_to_warm":[data_mean_dic.get("cold_to_warm")[0]-data_mean_dic.get("cold_to_warm:terminating")[0]]}
    # active = {"active":[data_mean_dic.get("active")[0]-data_mean_dic.get("active:terminating")[0]-12]}
    # data_mean_dic.update(cold_to_warm)
    # data_mean_dic.update(active)

    return data_mean_dic

def write_to_file(calculation_type:str, data_type:str, target_pod:str, repeat_time:str, key:str, value:float):
    write = csv.writer(open(data_optimize_file.format(data_type, calculation_type), 'a', newline=''))
    write.writerow([target_pod,repeat_time,key,value])

def generate_optimize_data_files(data_directory:str, calculation_type:str):
    for filename in os.listdir(data_directory+ "\\"+calculation_type):
        file_directory = os.path.join(data_directory+"\\"+calculation_type, filename)
        # checking if it is a file
        if os.path.isfile(file_directory):
            target_pod = re.search('target_pod_(.*)_repeat',file_directory).group(1)
            repeat_time = re.search('repeat_time_(.*)_video',file_directory).group(1)[0]
            print("file_directory: ", file_directory, "target_pod: ", target_pod, "repeat_time: ", repeat_time)
            for key, value in get_dic_data(file_directory, TIMESTAMP).items():
                write_to_file(calculation_type,"timestamp",target_pod,repeat_time,key,value[0])
                # data_cpu_optimize.append([target_pod,repeat_time,key,str(value[0])])

def boxplot_state(data_type:str, calculation_type:str):
    df = pd.read_csv(output_data_dir+"data_{}_{}_optimize_tmp.csv".format(data_type, calculation_type), sep=',', names=[TARGET_PODS, REPEAT_TIME, POD_STATE, MEAN])
    df = df.sort_values(by=TARGET_PODS)

    df_null = df[df[POD_STATE]=="begin"]
    df_null = df_null.sort_values(by=TARGET_PODS)

    df_cold = df[df[POD_STATE]=="cold"]
    df_cold = df_cold.sort_values(by=TARGET_PODS)

    df_warm = df[df[POD_STATE]=="warm"]
    df_warm = df_warm.sort_values(by=TARGET_PODS)

    df_active = df[df[POD_STATE]=="active"]
    df_active = df_active.sort_values(by=TARGET_PODS)

    plt.figure()

    arr = [df_null, df_warm, df_cold, df_active]
    # print(arr)
    i=0
    color = ["red", "orange", "green", "blue"]

    marker = ["v", ">", "s", "v",]

    labels = ["State:Null", "State:Warm", "State:Cold", "State:Active", ]

    # color = ["red", "orange", "yellow", "green", "blue", "violet", "black"]

    # marker = ["v", ">", "s", "v", ">", "s", "v"]

    # labels = ["Cold", "Cold to Warm", "Cold to Warm Ter", "Warm", "Active", "Active Ter" ,"Terminate"]

    for scenario in arr:
        # plt.subplot(1, 1, i+1)
        plt.subplot(1, 1, 1)

        draw_box = scenario[[TARGET_PODS, MEAN]]
        
        list_pods = np.unique(df[TARGET_PODS])
        ticks= [str(e) for e in list_pods]
        x_positions = list(range(0, len(ticks)))

        # for pod in list_pods:
        #     draw_i = draw_box[draw_box[TARGET_PODS] == pod]

        #     if(len(draw_i) != 0):
        #         plt.boxplot(draw_i[MEAN], positions=[ticks.index(str(pod))], widths=0.5, patch_artist=True, boxprops=dict(facecolor='white'))
                
        plt.xticks(x_positions, ticks)

        plt.xlabel("Number of Pods")
        plt.yscale("log")
        plt.ylabel("{} state process {} (s)".format(target_folder,data_type))
        
        if i==0:xx=1
        elif i==1: xx=1
        elif i==2: xx=2
        elif i==3: xx=3
        
        my_fitting = np.polyfit(scenario[TARGET_PODS], scenario[MEAN], 2, full=True)
        poly = np.poly1d(my_fitting[0])
        plt.plot(scenario[TARGET_PODS].astype(str), poly(scenario[TARGET_PODS]), color=color[i],  marker=marker[i], label = labels[i])

        print(my_fitting[0])
        i = i + 1

    # legend
    # handles, labels = plt.gca().get_legend_handles_labels()
    # red_patch = mpatches.Patch(color='red', label='The red data')
    plt.legend()
    result_image_dir = "result\{}\{}\{} state {}_{}.jpg"
    plt.savefig(result_image_dir.format(data_by_day_folder,target_folder,calculation_type,data_type,data_by_day_folder))
    plt.show()
    # remove_optimize_file(data_optimize_file.format(data_type))

def boxplot_action(data_type:str, calculation_type:str):
    df = pd.read_csv(output_data_dir+"data_{}_{}_optimize_tmp.csv".format(data_type,calculation_type), sep=',', names=[TARGET_PODS, REPEAT_TIME, POD_STATE, MEAN])
    df = df.sort_values(by=TARGET_PODS)

    df_deploy = df[df[POD_STATE]=="coldstart"]
    df_deploy = df_deploy.sort_values(by=TARGET_PODS)

    df_scale_down = df[df[POD_STATE]=="warm:terminating"]
    df_scale_down = df_scale_down.sort_values(by=TARGET_PODS)

    df_curl = df[df[POD_STATE]=="curl_coldstart"]
    df_curl = df_curl.sort_values(by=TARGET_PODS)

    df_delete = df[df[POD_STATE]=="delete:terminating"]
    df_delete = df_delete.sort_values(by=TARGET_PODS)

    # Revert Actions
    df_warm_curl = df[df[POD_STATE]=="curl_coldstart"]
    df_warm_curl = df_warm_curl.sort_values(by=TARGET_PODS)

    df_cooling = df[df[POD_STATE]=="active:terminating"]
    df_cooling = df_cooling.sort_values(by=TARGET_PODS)

    df_update = df[df[POD_STATE]=="update_config_coldstart"]
    df_update = df_update.sort_values(by=TARGET_PODS)

    df_warm_delete = df[df[POD_STATE]=="warm_delete:terminating"]
    df_warm_delete = df_warm_delete.sort_values(by=TARGET_PODS)

    df_cold_delete = df[df[POD_STATE]=="cold_delete"]
    df_cold_delete = df_cold_delete.sort_values(by=TARGET_PODS)

    plt.figure()

    arr = []
    labels = []
    if calculation_type == "life_circle":
        arr = [df_deploy, df_scale_down, df_curl, df_delete]
        labels = ["Action:Deploying", "Action:Scaling down", "Action:Curling", "Action:Force delete", ]
    else:
        arr = [df_warm_curl, df_cooling, df_update, df_warm_delete]
        labels = ["Action:WarmCurling", "Action:Cooling", "Action:Updating", "Action:Warm deleting"]
    print(arr[1], arr[2])
    i=0
    color = ["red","violet", "green", "blue","orange" ,]

    marker = ["v", ">", "s", "v", ">", "s", "v"]


    # color = ["red", "orange", "yellow", "green", "blue", "violet", "black"]

    # marker = ["v", ">", "s", "v", ">", "s", "v"]

    # labels = ["Cold", "Cold to Warm", "Cold to Warm Ter", "Warm", "Active", "Active Ter" ,"Terminate"]

    for scenario in arr:
        # plt.subplot(1, 1, i+1)
        plt.subplot(1, 1, 1)
        
        list_pods = np.unique(df[TARGET_PODS])
        ticks= [str(e) for e in list_pods]
        x_positions = list(range(0, len(ticks)))
                
        plt.xticks(x_positions, ticks)

        plt.xlabel("Number of Pods")
        plt.yscale("log", base=2)
        plt.ylabel("{} action process {} (s)".format(target_folder,data_type))
        
        if i==0:xx=1
        elif i==1: xx=1
        elif i==2: xx=2
        elif i==3: xx=3
        
        my_fitting = np.polyfit(scenario[TARGET_PODS], scenario[MEAN], 3, full=True)
        poly = np.poly1d(my_fitting[0])
        plt.plot(scenario[TARGET_PODS].astype(str), poly(scenario[TARGET_PODS]), color=color[i],  marker=marker[i], label = labels[i])

        print(my_fitting[0])
        i = i + 1

    # legend
    # handles, labels = plt.gca().get_legend_handles_labels()
    # red_patch = mpatches.Patch(color='red', label='The red data')
    plt.legend()
    result_image_dir = "result\{}\{}\{}_{}_action_{}_{}.jpg"
    plt.savefig(result_image_dir.format(data_by_day_folder,calculation_type,target_folder,calculation_type,data_type,data_by_day_folder))
    plt.show()
    remove_optimize_file(data_optimize_file.format(data_type, calculation_type))

if __name__=='__main__':
    generate_optimize_data_files(data_directory, "revert_lifecircle")
    # boxplot_state("timestamp")
    boxplot_action("timestamp", "revert_lifecircle")
