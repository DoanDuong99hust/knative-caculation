from collections import defaultdict
import re
from time import gmtime
import numpy as np
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import  os
import csv

from datetime import timezone, tzinfo

from pytz import utc

TERMINATING_STATUS = "terminating"

NULL_STATE = "empty"
WARM_STATE = "warm"
COLD_STATE = "cold"
ACTIVE_STATE = "active"
DELETE_STATE = "delete"
NULL_AFTER_DELTE = "empty:after_delete"

DEPLOY_ACTION = "cold_start"
SCALE_DOWN_ACTION = "warm:terminating"
COOLLING_DOWN_ACTION = "active:terminating"
CURL_ACTION = "cold_start:curl"
UPDATE_ACTION = "cold_start:update_config"
DELETE_ACTION = "delete:terminating"
WARM_DELETE_ACTION = "warm_delete:terminating"
COLD_DELETE_ACTION = "cold_delete"

# Raw data
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
CALCULATION_TYPE = "revert_lifecircle"
data_directory = "D:\FIL\DATN\Data\pi4\\" + data_by_day_folder + "\\" + CALCULATION_TYPE
power_data_directory = "D:\FIL\DATN\Data\pi4\power\\" + data_by_day_folder + "\\" + CALCULATION_TYPE

def get_dic_data(file_directory:str, data_type:str):
    data_pd = pd.read_csv(file_directory, sep=',', names=[TIME_SECONDS, DATE_TIME, POD_NUM, CPU_PER, RAM_PER, POD_STATE])
    data_arr = np.transpose(np.array([data_pd[POD_STATE], data_pd[data_type]]))
    dict_data = defaultdict(list)
    for key, value in data_arr:
        dict_data[key].append(value)
    data_maxtime_dic = defaultdict(list)
    for key, value in dict_data.items():
        data_maxtime_dic[key].append(max(value))
    return data_maxtime_dic

def get_power_dic_data(power_file_directory:str):
    data_pd = pd.read_csv(power_file_directory, sep=',')
    data_arr = data_pd.to_numpy()
    dict_data = defaultdict(list)
    for i in range(len(data_pd[TIME])):
        dict_data[data_pd[TIME][i]].append(data_arr[i])
    return dict_data

def format_time(dtime:str, time_of:str):
    if time_of == "power": 
        datet = datetime.datetime.strptime(re.sub("\.[0-9]*\+[0-9]*\:[0-9]*", "\t", dtime).strip(), "%Y-%m-%d %H:%M:%S").astimezone(utc)
        return datetime.datetime.strptime(re.sub("\.[0-9]*\+[0-9]*\:[0-9]*", "\t", str(datet)[:19]).strip(), "%Y-%m-%d %H:%M:%S")
    if time_of == "raw_data":
        return datetime.datetime.strptime(re.sub("\.[0-9]*\+[0-9]*\:[0-9]*", "\t", dtime).strip(), "%Y-%m-%d %H:%M:%S.%f")

def write_to_file(value,status:str, raw_data_file_name:str):
    write = csv.writer(open(power_data_directory+"\\"+power_with_status_folder+"\\"+"status_{}".format(raw_data_file_name), 'a', newline=''))
    write.writerow([value[0],value[1],value[2],value[3],status])

if __name__=='__main__':
    for filename in os.listdir(data_directory):
        file_directory = os.path.join(data_directory, filename)
        power_file_directory = os.path.join(power_data_directory, filename.replace("_prom_","_power_"))
        # checking if it is a file
        if os.path.isfile(file_directory):
            power_dic_data = get_power_dic_data(power_file_directory)
            status_dic_data = get_dic_data(file_directory, DATE_TIME)
            for key, value in power_dic_data.items():
                power_date = format_time(key,"power")
                if CALCULATION_TYPE == "life_circle":
                    if status_dic_data.get(NULL_STATE) is not None and power_date <= format_time(status_dic_data.get(NULL_STATE)[0],"raw_data"):
                        write_to_file(value[0], NULL_STATE, filename)
                        continue
                    if status_dic_data.get(DEPLOY_ACTION) is not None and power_date <= format_time(status_dic_data.get(DEPLOY_ACTION)[0],"raw_data"):
                        write_to_file(value[0], DEPLOY_ACTION, filename)
                        continue
                    if status_dic_data.get(WARM_STATE) is not None and power_date <= format_time(status_dic_data.get(WARM_STATE)[0],"raw_data"):
                        write_to_file(value[0], WARM_STATE, filename)
                        continue
                    if status_dic_data.get(SCALE_DOWN_ACTION) is not None and power_date <= format_time(status_dic_data.get(SCALE_DOWN_ACTION)[0],"raw_data"):
                        write_to_file(value[0], SCALE_DOWN_ACTION, filename)
                        continue
                    if power_date <= format_time(status_dic_data.get(COLD_STATE)[0],"raw_data"):
                        write_to_file(value[0], COLD_STATE, filename)
                        continue
                    if power_date <= format_time(status_dic_data.get(CURL_ACTION)[0],"raw_data"):
                        write_to_file(value[0], CURL_ACTION, filename)
                        continue
                    if power_date <= format_time(status_dic_data.get(ACTIVE_STATE)[0],"raw_data"):
                        write_to_file(value[0], ACTIVE_STATE, filename)
                        continue
                    if power_date <= format_time(status_dic_data.get(DELETE_ACTION)[0],"raw_data"):
                        write_to_file(value[0], DELETE_ACTION, filename)
                        continue
                    if status_dic_data.get(DELETE_STATE) is not None and power_date <= format_time(status_dic_data.get(DELETE_STATE)[0],"raw_data"):
                        write_to_file(value[0], DELETE_STATE, filename)
                        continue
                    if power_date <= format_time(status_dic_data.get(NULL_AFTER_DELTE)[0],"raw_data"):
                        write_to_file(value[0], NULL_AFTER_DELTE, filename)
                        continue
                else:
                    if status_dic_data.get(NULL_STATE) is not None and power_date <= format_time(status_dic_data.get(NULL_STATE)[0],"raw_data"):
                        write_to_file(value[0], NULL_STATE, filename)
                        continue
                    if status_dic_data.get(DEPLOY_ACTION) is not None and power_date <= format_time(status_dic_data.get(DEPLOY_ACTION)[0],"raw_data"):
                        write_to_file(value[0], DEPLOY_ACTION, filename)
                        continue
                    if status_dic_data.get(WARM_STATE) is not None and power_date <= format_time(status_dic_data.get(WARM_STATE)[0],"raw_data"):
                        write_to_file(value[0], WARM_STATE, filename)
                        continue
                    if status_dic_data.get(CURL_ACTION) is not None and power_date <= format_time(status_dic_data.get(CURL_ACTION)[0],"raw_data"):
                        write_to_file(value[0], CURL_ACTION, filename)
                        continue
                    if status_dic_data.get(ACTIVE_STATE) is not None and power_date <= format_time(status_dic_data.get(ACTIVE_STATE)[0],"raw_data"):
                        write_to_file(value[0], ACTIVE_STATE, filename)
                        continue
                    if status_dic_data.get(COOLLING_DOWN_ACTION) is not None and power_date <= format_time(status_dic_data.get(COOLLING_DOWN_ACTION)[0],"raw_data"):
                        write_to_file(value[0], COOLLING_DOWN_ACTION, filename)
                        continue
                    if status_dic_data.get(COLD_STATE) is not None and power_date <= format_time(status_dic_data.get(COLD_STATE)[0],"raw_data"):
                        write_to_file(value[0], COLD_STATE, filename)
                        continue
                    if status_dic_data.get(UPDATE_ACTION) is not None and power_date <= format_time(status_dic_data.get(UPDATE_ACTION)[0],"raw_data"):
                        write_to_file(value[0], UPDATE_ACTION, filename)
                        continue
                    if status_dic_data.get(WARM_DELETE_ACTION) is not None and power_date <= format_time(status_dic_data.get(WARM_DELETE_ACTION)[0],"raw_data"):
                        write_to_file(value[0], WARM_DELETE_ACTION, filename)
                        continue
                    if status_dic_data.get("warm_to_cold") is not None and power_date <= format_time(status_dic_data.get("warm_to_cold")[0],"raw_data"):
                        write_to_file(value[0], "warm_to_cold", filename)
                        continue
                    if status_dic_data.get("warm_to_cold:terminating") is not None and power_date <= format_time(status_dic_data.get("warm_to_cold:terminating")[0],"raw_data"):
                        write_to_file(value[0], "warm_to_cold:terminating", filename)
                        continue
                    if status_dic_data.get(COLD_DELETE_ACTION) is not None and power_date <= format_time(status_dic_data.get(COLD_DELETE_ACTION)[0],"raw_data"):
                        write_to_file(value[0], COLD_DELETE_ACTION, filename)
                        continue
