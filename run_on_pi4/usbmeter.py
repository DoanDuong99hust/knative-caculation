#!/usr/bin/python3

# sudo systemctl start bluetooth
# echo "power on" | bluetoothctl

import collections
import struct
import sys
import argparse
import datetime
import time
import pickle
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange
from bluetooth import *
import csv


# Process socket data from USB meter and extract volts, amps etc.
def processdata(d):

    data = {}

    data["Volts"] = struct.unpack(">h", d[2 : 3 + 1])[0] / 1000.0  # volts
    data["Amps"] = struct.unpack(">h", d[4 : 5 + 1])[0] / 10000.0  # amps
    data["Watts"] = struct.unpack(">I", d[6 : 9 + 1])[0] / 1000.0  # watts
    data["temp_C"] = struct.unpack(">h", d[10 : 11 + 1])[0]  # temp in C
    data["temp_F"] = struct.unpack(">h", d[12 : 13 + 1])[0]  # temp in F

    utc_dt = datetime.datetime.now(datetime.timezone.utc)  # UTC time
    dt = utc_dt.astimezone()  # local time
    data["time"] = dt

    g = 0
    for i in range(16, 95, 8):
        ma, mw = struct.unpack(">II", d[i : i + 8])  # mAh,mWh respectively
        gs = str(g)
        data[gs + "_mAh"] = ma
        data[gs + "_mWh"] = mw
        g += 1

    data["data_line_pos_volt"] = struct.unpack(">h", d[96: 97 + 1])[0] / 100.0
    data["data_line_neg_volt"] = struct.unpack(">h", d[98: 99 + 1])[0] / 100.0
    data["resistance"] = struct.unpack(">I", d[122: 125 + 1])[0] / 10.0  # resistance
    return data


def main(target_pods: int, repetition: int, time_analysis: int):
    
    try:
        addr = '00:16:A5:00:0F:65'
        sock = BluetoothSocket(RFCOMM)
        res = sock.connect((addr, 1))
    except:
        print("Having some problems to connect to the UMMETER")
        # Automagically find USB meter
        nearby_devices = discover_devices(lookup_names=True)

        for v in nearby_devices:
            if "UM25C" in v[1]:
                print("Found", v[0])
                addr = v[0]
                break

        if addr is None:
            print("No address provided", file=sys.stderr)
            quit()

        service_matches = find_service(address=addr)

        if len(service_matches) == 0:
            print("No services found for address ", addr, file=sys.stderr)
            quit()

        first_match = service_matches[0]
        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"]

        if host is None or port is None:
            print("Host or port not specified", file=sys.stderr)
            quit()

        sock = BluetoothSocket(RFCOMM)
        print('connecting to "{}" on {}:{}'.format(name, host, port))
        res = sock.connect((host, port))

    with open("data_usbmeter_{}_{}.csv".format(str(target_pods), str(repetition)), 'a+') as f:
        writer = csv.writer(f)
        writer.writerow(["time", "Volts", "Amps", "Watts"])
        leng = 20
        volts = collections.deque(maxlen=leng)
        currents = collections.deque(maxlen=leng)
        watts = collections.deque(maxlen=leng)
        times = collections.deque(maxlen=leng)    
        
        d = b""

        endtime = time.time()+(60*int(time_analysis)+240) #[m]->[s] + 45s for cold and delete
        while endtime-time.time() > 0:
            # Send request to USB meter
            sock.send((0xF0).to_bytes(1, byteorder="big"))

            d += sock.recv(130)

            if len(d) != 130:
                continue

            data = processdata(d)
            volts.append(data["Volts"])
            currents.append(data["Amps"])
            watts.append(data["Watts"])
            times.append(data["time"])
        
            #print("%s: %fV %fA %fW" % (data["time"], data["Volts"], data["Amps"], data["Watts"]))

            
            writer.writerow([data["time"], data["Volts"], data["Amps"], data["Watts"]])

            d = b""
            time.sleep(0.1)

        print('Closed')
        sock.close()
    return True

if __name__ == "__main__":
    main(sys.argv[1],sys.argv[2],sys.argv[3])
