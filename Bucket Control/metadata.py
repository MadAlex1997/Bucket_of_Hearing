import json
from sounddevice import rec, wait
from datetime import datetime
import numpy
import os
from time import sleep
# from pigps import GPS

# gps = GPS()

with open("./sensor_info.json","r") as si:
    sidict = json.load(si.read())
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
    data_waiting = [data not in meta_done for data in data_waiting]
    return data_waiting

def write_metadata(file):
    unix_time = file.split("_")[1]

    # lat = gps.lat
    # lon = gps.lon
    # time = gps.time
    # TODO Use numpy time diff to determine start time based on gps time and unix time

    with open(f"{meta_path}{file}.json","w+") as jfile:
        pass


def metadata():
    for _ in range(5):
        data_waiting = check_waiting()
        if data_waiting:
            for file in data_waiting:
                write_metadata(file)
        else:
            sleep(10)
            continue
