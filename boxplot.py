import csv
import pandas as pd
import matplotlib.pyplot as plt

avr_prometheus = {
    "cold":[],
    "warm":[],
    "delete":[]
}
cold = []
warm = []
delete = []

with open('./data/data-prometeus.csv') as csvfile:
    data_prometheus = csv.DictReader(csvfile, fieldnames=['timestamp', 'pods', 'cpu', 'job'])
    for row in data_prometheus:
        if row['job'] == 'cold':
            cold.append(float(row['cpu']))
            print(row)
        elif row['job'] == 'warm':
            warm.append(float(row['cpu']))
        elif row['job'] == 'delete':
            delete.append(float(row['cpu']))

avr_cold = sum(cold) / len(cold)
avr_warm = sum(warm) / len(warm)
avr_delete = sum(delete) / len(delete)

print("Cold: {}, Warm: {}, Delete:{}".format(avr_cold, avr_warm, avr_delete))


plt.boxplot(delete)
plt.yscale('log')
plt.show()
""" with open('./data/timestamps.csv') as csvfile:
    data_timestamps = csv.DictReader(csvfile, fieldnames=['job', 'timestamp'])
    for row in data_timestamps:
        print(row)
    
 """

#Excel file
""" df = pd.read_excel('./data/UM25C.xlsx', sheet_name=None, header=1)
print(df)
 """