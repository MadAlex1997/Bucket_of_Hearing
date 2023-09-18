from scipy.io import wavfile
# from sounddevice import rec, wait
from datetime import datetime
import numpy as np
import json
from time import sleep



with open("./sensor_info.json","r") as si:
    sidict = json.load(si)
    seconds = sidict["collect_duration"]
    samplerate = sidict["samplerate"]
    data_path = sidict["data_path"]
    sensor_name = sidict["sensor_name"]

def record_dummy():
    while True:
        start_time = datetime.now().timestamp()
        recorder = np.random.randint(low=-3000,high=3000,size=samplerate*seconds,dtype=np.int64)
        # recorder = rec(frames=int(seconds*samplerate), samplerate=samplerate,channels=1)
        # wait()
        sleep(30)
        wavfile.write(filename=f"{data_path}{sensor_name}_{start_time}.wav",
                    rate=samplerate,
                    data = recorder
                    )

# def record():
#     """
#     Record wav files and save them
#     """
#     while True:
#         start_time = datetime.now().timestamp()
#         recorder = rec(frames=int(seconds*samplerate), samplerate=samplerate,channels=1)
#         wait()
#         wavfile.write(filename=f"{data_path}{sensor_name}_{start_time}.wav",
#                     rate=samplerate,
#                     data = recorder
#                     )

# if __name__ == "__main__":
#     record()