# Bucket_of_Hearing
An open-source DearPyGui application for acoustic analysis
* Opens wav files and anything that Obspy can open
* Look at data in 10-minute chunks
* Spectrogram the data
## It is still very early in development
* I need to clean up the interface once I am done testing
* I need to add more control over the spectrogram
   Likely will build in tagging and annotations
   Maybe a Doppler calculator
# Installation
* clone repository
* create venv
* pip install -r requirements.txt
# Instructions
* using venv run plot.py
* open file
* plot
* Select time interval
* spectrogram opens a window with a spectrogram image
* Set filter parameters and click on the type of filter
