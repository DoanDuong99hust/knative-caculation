from collections import defaultdict
import csv
from tkinter.font import names
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import re

TARGET_PODS = "target_pods"
REPEAT_TIME = "repeat_time"
MEAN = "mean"
TIME_SECONDS = "time_seconds"
DATE_TIME = "date_time"
POD_NUM = "pod_num"
CPU_PER = "cpu_%"
RAM_PER = "ram_%"
POD_STATE = "pod_state"

folder = "pi4"
data_by_day_folder = "8_7_2022"
data_directory = "D:\FIL\DATN\Data\\"+folder
output_data_dir = "D:\FIL\DATN\DataOptimize\\"+folder+"\\"

data_cpu_optimize = []
data_ram_optimize = []

def get_dic_data(file_directory:str, data_type:str):
    data_pd = pd.read_csv(file_directory, sep=',', names=[TIME_SECONDS, DATE_TIME, POD_NUM, CPU_PER, RAM_PER, POD_STATE])
    data_arr = np.transpose(np.array([data_pd[POD_STATE], data_pd[data_type]]))
    dict_data = defaultdict(list)
    for key, value in data_arr:
        dict_data[key].append(value)
    data_mean_dic = defaultdict(list)
    for key, value in dict_data.items():
        data_mean_dic[key].append(sum(value)/len(value))
    return data_mean_dic

def write_to_file(filename:str, data_type:str, target_pod:str, repeat_time:str, key:str, value:float):
    write = csv.writer(open(output_data_dir+"data_{}_optimize_tmp.csv".format(data_type,filename), 'a', newline=''))
    write.writerow([target_pod,repeat_time,key,value])

def generate_optimize_data_files(data_directory:str):
    for filename in os.listdir(data_directory):
        file_directory = os.path.join(data_directory, filename)
        # checking if it is a file
        if os.path.isfile(file_directory):
            target_pod = re.search('target_pod_(.*)_repeat',file_directory).group(1)
            repeat_time = re.search('repeat_time_(.*)_video',file_directory).group(1)[0]
            print("file_directory: ", file_directory, "target_pod: ", target_pod, "repeat_time: ", repeat_time)
            for key, value in get_dic_data(file_directory, CPU_PER).items():
                write_to_file(filename,CPU_PER,target_pod,repeat_time,key,float(value[0]))
                # data_cpu_optimize.append([target_pod,repeat_time,key,str(value[0])])
            for key, value in get_dic_data(file_directory, RAM_PER).items():
                write_to_file(filename,RAM_PER,target_pod,repeat_time,key,float(value[0]))
                # data_ram_optimize.append([target_pod,repeat_time,key,str(value[0])])
def boxplot(arr_data,data_type:str):
    df = pd.read_csv(output_data_dir+"data_{}_optimize_tmp.csv".format(data_type), sep=',', names=[TARGET_PODS, REPEAT_TIME, POD_STATE, MEAN])
    # df = pd.DataFrame(arr_data,columns=[TARGET_PODS, REPEAT_TIME, POD_STATE, MEAN])
    df = df.sort_values(by=TARGET_PODS)

    df_cold = df[df[POD_STATE]=="cold"]
    df_cold = df_cold.sort_values(by=TARGET_PODS)

    df_cold_to_warm = df[df[POD_STATE]=="cold_to_warm"]
    df_cold_to_warm = df_cold_to_warm.sort_values(by=TARGET_PODS)

    df_cold_to_warm_ter = df[df[POD_STATE]=="cold_to_warm:terminating"]
    df_cold_to_warm_ter = df_cold_to_warm_ter.sort_values(by=TARGET_PODS)

    df_warm = df[df[POD_STATE]=="warm"]
    df_warm = df_warm.sort_values(by=TARGET_PODS)

    df_active = df[df[POD_STATE]=="active"]
    df_active = df_active.sort_values(by=TARGET_PODS)

    df_active_ter = df[df[POD_STATE]=="active:terminating"]
    df_active_ter = df_active_ter.sort_values(by=TARGET_PODS)

    df_delete = df[df[POD_STATE]=="delete"]
    df_delete = df_delete.sort_values(by=TARGET_PODS)

    plt.figure()

    arr = [df_cold, df_cold_to_warm, df_warm, df_active, df_delete]
    i=0
    color = ["red", "orange", "green", "blue", "black"]

    marker = ["v", ">", "s", "v", ">",]

    labels = ["Cold", "Cold to Warm", "Warm", "Active" ,"Terminate"]

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

        for pod in list_pods:
            draw_i = draw_box[draw_box[TARGET_PODS] == pod]

            if(len(draw_i) != 0):
                plt.boxplot(draw_i[MEAN], positions=[ticks.index(str(pod))], widths=0.5, patch_artist=True, boxprops=dict(facecolor='white'))
                
        plt.xticks(x_positions, ticks)

        plt.xlabel("Number of Pods")
        plt.ylabel("{} {} usage ".format(folder,data_type))
        
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
    plt.show()
if __name__=='__main__':
    generate_optimize_data_files(data_directory+"\\"+data_by_day_folder)
    boxplot(data_cpu_optimize,CPU_PER)
    boxplot(data_ram_optimize,RAM_PER)
