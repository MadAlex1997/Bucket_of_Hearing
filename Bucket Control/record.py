from scipy.io import wavfile
from sounddevice import rec, wait
from datetime import datetime
import json

# The following varaibles will be obtained from sensor_info.json
# seconds = 30
# sample_rate = 16000
# data_path = "../Data/"
# sensor_name = "sensor1"
with open("./sensor_info.json","r") as si:
    sidict = json.load(si.read())
    seconds = sidict["collect_duration"]
    samplerate = sidict["samplerate"]
    data_path = sidict["data_path"]
    sensor_name = sidict["sensor_name"]


def record():
    for _ in range(2):
        start_time = datetime.now().timestamp()
        recorder = rec(frames=int(seconds*samplerate), samplerate=samplerate,channels=1)
        wait()
        wavfile.write(filename=f"{data_path}{sensor_name}_{start_time}.wav",
                    rate=samplerate,
                    data = recorder
                    )

if __name__ == "__main__":
    record()