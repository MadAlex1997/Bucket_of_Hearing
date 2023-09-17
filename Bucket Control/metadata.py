import json
from sounddevice import rec, wait
from datetime import datetime
import numpy as np
import os
from time import sleep
from hashlib import sha256
# from pigps import GPS

# gps = GPS()

with open("./sensor_info.json","r") as si:
    sidict = json.load(si)
    seconds = sidict["collect_duration"]
    samplerate = sidict["samplerate"]
    data_path = sidict["data_path"]
    meta_path = sidict["meta_path"]
    sensor_name = sidict["sensor_name"]

def check_waiting():
    """
    Give a list of data files that are waiting for a meta data file to be written
    that list has the file type striped from the end 
    """
    data_waiting = os.listdir("./Data")
    data_waiting = [i for i in data_waiting if ".wav" in i]
    data_waiting = [i.replace(".wav","") for i in data_waiting]
    meta_done = os.listdir("./Meta")
    meta_done = [i for i in meta_done if ".json" in i]
    meta_done = [i.replace(".json","") for i in meta_done]
    data_waiting = [data for data in data_waiting if data not in meta_done]
    return data_waiting

def write_metadata(file):
    json_dict = sidict
    unix_time = datetime.fromtimestamp(float(file.split("_")[1]))

    # json_dict["lat"] = gps.lat
    # json_dict["lon"] = gps.lon
    
    # TODO Use numpy time diff to determine start time based on gps time and unix time
    # system_time_now = np.datetime64(datetime.now())
    # gps_time_now = np.datetime64(gps.time)
    # system_time_diff = system_time_now - np.datetime64(unix_time)
    # json_dict["start_time"] = str(gps_time_now - system_time_diff)
    
    json_dict["start_time"] = str(np.datetime64(unix_time))
    
    with open(f"{data_path}{file}.wav","rb") as hash_file:
        checksum = sha256(hash_file.read()).hexdigest()
    
    json_dict["checksum"] =checksum
    
    with open(f"{meta_path}{file}.json","w+") as jfile:
        json.dump(json_dict,jfile)
        
def metadata():
    for _ in range(5):
        data_waiting = check_waiting()
        if data_waiting:
            for file in data_waiting:
                write_metadata(file)
        else:
            # sleep(10)
            continue
if __name__ == "__main__":
    metadata()
