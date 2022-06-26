from collections import defaultdict
import csv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

target_file = "/home/controller/knative-caculation/data/server/data_prom_target_pod_1_repeat_time_1_video_4K_video_59s.webm_server_26_6_2022_2h13.csv"

def create_2D_array_data(path):
  numpy_data = (pd.read_csv(path)).to_numpy()
#   print(numpy_data)
  transpose_data = np.transpose(numpy_data)
#   print(transpose_data)

  time_period = list(transpose_data[0])
  cpu_value = list(transpose_data[4])
  test_array = np.array([time_period, cpu_value])
#   print(test_array)
  list_arr = test_array.tolist()
  # test_array.astype(int)
#   print(list_arr)
  return list_arr

# def create_dictionary(list_arr) :
#   d = defaultdict(list)
#   print(d)
#   for year, month in list_arr:
#       d[year].append(month)
#   dic = defaultdict(list)
#   for key,values in d.items():
#     if (key == 'nan') :
#       key = 0
#       key = int(ipaddress.ip_address(key))/pow(10,32)
#       dic[key].append(len(list(OrderedDict.fromkeys(values)))/120)
#     else:
#       key = int(ipaddress.ip_address(key))/pow(10,32)
#       dic[key].append(len(list(OrderedDict.fromkeys(values)))/120)
#   print(dic)
#   return dic

data = create_2D_array_data(target_file)

plt.plot(data[0],data[1])  # Matplotlib
plt.xlabel("Time")
plt.ylabel("CPU %")
# plt.title(path + " " + str(len(list_data)) + " IP")
plt.show()