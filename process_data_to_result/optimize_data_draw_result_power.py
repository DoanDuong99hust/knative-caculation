from collections import defaultdict
import csv
import datetime
from tkinter.font import names
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import re

from pytz import utc

TARGET_PODS = "target_pods"
REPEAT_TIME = "repeat_time"
MEAN = "mean"
TIME_SECONDS = "time_seconds"
DATE_TIME = "date_time"
POD_NUM = "pod_num"
CPU_PER = "cpu_%"
RAM_PER = "ram_%"
POD_STATE = "pod_state"
# Raw power data
TIME = "time"
VOLT = "Volts"
AMPE = "Amps"
WATT ="Watts"

data_by_day_folder = "20_7_2022"
power_with_status_folder = "power_with_status" 
data_directory = "D:\FIL\DATN\Data\pi4\\" + data_by_day_folder
CALCULATION_TYPE = "revert_lifecircle"
power_data_directory = "D:\FIL\DATN\Data\pi4\power\\" + data_by_day_folder + "\\" +CALCULATION_TYPE
output_data_dir = "D:\FIL\DATN\DataOptimize\\pi4\\"

data_optimize_file = output_data_dir+"data_{}_{}_optimize_tmp.csv"

def remove_optimize_file(file_directory:str):
    if os.path.exists(file_directory):
      os.remove(file_directory)
    else:
        print("The file does not exist")

def get_dic_data(file_directory:str, data_type:str):
    data_pd = pd.read_csv(file_directory, sep=',', names=[TIME, VOLT, AMPE, WATT, POD_STATE])
    data_arr = np.transpose(np.array([data_pd[POD_STATE], data_pd[data_type]]))
    dict_data = defaultdict(list)
    for key, value in data_arr:
        dict_data[key].append(value)
    data_mean_dic = defaultdict(list)
    for key, value in dict_data.items():
        data_mean_dic[key].append(sum(value)/len(value))
    return data_mean_dic

def get_mean_dic(file_directory:str, data_type:str):
    data_pd = pd.read_csv(file_directory, sep=',', names=[TIME, VOLT, AMPE, WATT, POD_STATE])
    data_arr = np.transpose(np.array([data_pd[POD_STATE], data_pd[TIME], data_pd[data_type]]))
    dict_data1 = defaultdict(list)
    for key, value1,value2 in data_arr:
        dict_data1[key].append([format_time(str(value1)).timestamp(),value2])
    data_mean_dic1 = defaultdict(list)
    for key, value in dict_data1.items():
        total_value = 0
        for index in range(1,len(value),1):
            total_value = total_value + value[index-1][1]*(value[index][0]-value[index-1][0]) # 
        data_mean_dic1[key].append(total_value/(value[len(value)-1][0]-value[0][0]))
    return data_mean_dic1
    
def write_to_file(data_type:str, target_pod:str, repeat_time:str, key:str, value:float):
    write = csv.writer(open(data_optimize_file.format(data_type, CALCULATION_TYPE), 'a', newline=''))
    write.writerow([target_pod,repeat_time,key,value])

def generate_optimize_data_files(data_directory:str):
    for filename in os.listdir(data_directory):
        file_directory = os.path.join(data_directory, filename)
        # checking if it is a file
        if os.path.isfile(file_directory):
            target_pod = re.search('target_pod_(.*)_repeat',file_directory).group(1)
            repeat_time = re.search('repeat_time_(.*)_video',file_directory).group(1)[0]
            print("file_directory: ", file_directory, "target_pod: ", target_pod, "repeat_time: ", repeat_time)
            for key, value in get_dic_data(file_directory,WATT).items():
                write_to_file("power",target_pod,repeat_time,key,float(value[0]))
                # data_cpu_optimize.append([target_pod,repeat_time,key,str(value[0])])

def boxplot_state(data_type:str):
    df = pd.read_csv(output_data_dir+"data_{}_{}_optimize_tmp.csv".format(data_type, CALCULATION_TYPE), sep=',', names=[TARGET_PODS, REPEAT_TIME, POD_STATE, MEAN])
    # df = pd.DataFrame(arr_data,columns=[TARGET_PODS, REPEAT_TIME, POD_STATE, MEAN])
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

    arr = [df_null, df_warm, df_cold]
    print(arr)
    i=0
    color = ["red", "orange", "green", "blue"]

    marker = ["v", ">", "s", "v",]

    labels = ["State:Null", "State:Warm", "State:Cold", ]

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
        # plt.yscale("log", base=10)
        plt.ylabel("PI4 state {} usage Watts".format(data_type))
        
        if i==0:xx=1
        elif i==1: xx=1
        elif i==2: xx=2
        
        my_fitting = np.polyfit(scenario[TARGET_PODS], scenario[MEAN], xx, full=True)
        poly = np.poly1d(my_fitting[0])
        plt.plot(scenario[TARGET_PODS].astype(str), poly(scenario[TARGET_PODS]), color=color[i],  marker=marker[i], label = labels[i])

        print(my_fitting[0])
        i = i + 1

    # legend
    # handles, labels = plt.gca().get_legend_handles_labels()
    # red_patch = mpatches.Patch(color='red', label='The red data')
    plt.legend()
    result_image_dir = "result\\"+data_by_day_folder+"\\{} state {}_{} log.jpg"
    plt.savefig(result_image_dir.format("pi4",data_type,data_by_day_folder))
    plt.show()
    # remove_optimize_file(data_optimize_file.format(data_type))

def boxplot_action(data_type:str):
    df = pd.read_csv(output_data_dir+"data_{}_{}_optimize_tmp.csv".format(data_type, CALCULATION_TYPE), sep=',', names=[TARGET_PODS, REPEAT_TIME, POD_STATE, MEAN])
    # df = pd.DataFrame(arr_data,columns=[TARGET_PODS, REPEAT_TIME, POD_STATE, MEAN])
    df = df.sort_values(by=TARGET_PODS)

    df_deploy = df[df[POD_STATE]=="cold_start"]
    df_deploy = df_deploy.sort_values(by=TARGET_PODS)

    df_scale_down = df[df[POD_STATE]=="warm:terminating"]
    df_scale_down = df_scale_down.sort_values(by=TARGET_PODS)

    df_curl = df[df[POD_STATE]=="cold_start:curl"]
    df_curl = df_curl.sort_values(by=TARGET_PODS)

    df_delete = df[df[POD_STATE]=="delete:terminating"]
    df_delete = df_delete.sort_values(by=TARGET_PODS)

    # Revert Actions
    df_warm_curl = df[df[POD_STATE]=="cold_start:curl"]
    df_warm_curl = df_warm_curl.sort_values(by=TARGET_PODS)

    df_cooling = df[df[POD_STATE]=="active:terminating"]
    df_cooling = df_cooling.sort_values(by=TARGET_PODS)

    df_update = df[df[POD_STATE]=="cold_start:update_config"]
    df_update = df_update.sort_values(by=TARGET_PODS)

    df_warm_delete = df[df[POD_STATE]=="warm_delete:terminating"]
    df_warm_delete = df_warm_delete.sort_values(by=TARGET_PODS)

    df_cold_delete = df[df[POD_STATE]=="cold_delete"]
    df_cold_delete = df_cold_delete.sort_values(by=TARGET_PODS)

    plt.figure()

    arr = []
    labels = []
    if CALCULATION_TYPE == "life_circle":
        arr = [df_deploy, df_scale_down, df_curl,]
        labels = ["Action:Deploying", "Action:Scaling down", "Action:Curling"]
    else:
        arr = [df_warm_curl, df_update, df_warm_delete, df_cold_delete]
        labels = ["Action:WarmCurling", "Action:Updating", "Action:Warm deleting", "Action:Cold deleting"]
    print(arr[1], arr[2])
    i=0
    color = ["red","green", "blue","orange" ,]

    marker = ["v", ">", "s", "v", ">", "s", "v"]

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
        # plt.yscale("log", base=10)
        plt.ylabel("PI4 {} action {} usage Watts".format(CALCULATION_TYPE,data_type))
        
        if i==0:xx=1
        elif i==1: xx=1
        elif i==2: xx=2
        
        my_fitting = np.polyfit(scenario[TARGET_PODS], scenario[MEAN], 3, full=True)
        poly = np.poly1d(my_fitting[0])
        plt.plot(scenario[TARGET_PODS].astype(str), poly(scenario[TARGET_PODS]), color=color[i],  marker=marker[i], label = labels[i])

        print(my_fitting[0])
        i = i + 1

    # legend
    # handles, labels = plt.gca().get_legend_handles_labels()
    # red_patch = mpatches.Patch(color='red', label='The red data')
    plt.legend()
    # result_image_dir = "result\\"+data_by_day_folder+"\\{} action {}_{} log.jpg"
    # plt.savefig(result_image_dir.format("pi4",data_type,data_by_day_folder))
    result_image_dir = "result\{}\{}\{}_{}_action_{}_{}.jpg"
    plt.savefig(result_image_dir.format(data_by_day_folder,CALCULATION_TYPE,"pi4",CALCULATION_TYPE,data_type,data_by_day_folder))
    plt.show()
    remove_optimize_file(data_optimize_file.format(data_type, CALCULATION_TYPE))

def format_time(dtime:str):
    return datetime.datetime.strptime(dtime, "%Y-%m-%d %H:%M:%S.%f+07:00")
if __name__=='__main__':
    generate_optimize_data_files(power_data_directory+"\\"+power_with_status_folder)
    # boxplot_state("power")
    boxplot_action("power")