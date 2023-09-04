import dearpygui.dearpygui as dpg
from obspy import read as sig_read
from scipy.signal import spectrogram, butter, lfilter
from scipy.io import wavfile
import numpy as np
import warnings
import plotly.graph_objects as go
import datetime
warnings.filterwarnings("ignore")

import array
import matplotlib.pyplot as plt


dpg.create_context()

def print_val(sender):
    print(dpg.get_value(sender))

def callback(sender, app_data):
    print("Sender: ", sender)
    print("App Data: ", app_data)
    dpg.set_value("file_name",list(app_data['selections'].keys())[0])
    dpg.set_value("file_path",list(app_data['selections'].values())[0])

def get_data(sender, app_data):
    print(app_data)
    file_path_string = dpg.get_value("file_path")
    sl1 = 0
    sl2 = 600*1000
    sl = 0
    if sender == "tslice":
        # sl = app_data
        sl1 = app_data*600*1000
        sl2 = (app_data+1)*600*1000
    
    else:
        app_data = dpg.get_value("tslice")
        # sl = app_data
        sl1 = app_data*600*1000
        sl2 = (app_data+1)*600*1000
    
    if ".wav" in file_path_string:
        fs, data = wavfile.read(file_path_string)
        length = data.shape[0] / fs
        time = np.linspace(0., length, data.shape[0])
        print(fs)
        if len(data.shape)>1:
            if data.shape[1]>1:
                data = data.mean(axis=1)
        
        data = data[sl1:sl2]
        time = time[sl1:sl2]
        
        x_arr = list(time)
        y_arr = list(data)
        dpg.set_value("file_type","WAV")
        dpg.set_value("x_array",x_arr)
        dpg.set_value("y_array",y_arr)
        dpg.set_value("fs",fs)

    else:
        try:
            collect = sig_read(file_path_string)[0]
            data = collect.data
            time = collect.times()
            data = data[sl1:sl2]
            time = time[sl1:sl2]
            x_arr = list(time)
            y_arr = list(data)
            dpg.set_value("file_type","File readable by obspy")
            dpg.set_value("x_array",x_arr)
            dpg.set_value("y_array",y_arr)
            dpg.set_value("fs",collect.stats.sampling_rate)
        except:
            dpg.set_value("file_type","Not openable by OBSPY")
            return 1

def plot_wave():
    delete_waveform()
    with dpg.window(label="Waveform",tag="Waveform",height=200,width=800,pos=[0,150],on_close=delete_waveform()):
        def create_plot():
            with dpg.plot(label="Line Series", height=-1, width=-1,parent="Waveform"):
                dpg.add_plot_legend(parent="Line Series")
                # dpg.add_drag_line(label="dline1", color=[255, 0, 0, 255], default_value=2.0, callback=print_val)
                dpg.add_plot_axis(dpg.mvXAxis, label="x",tag="xaxis_tag")
                dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="yaxis")
                sl = dpg.get_value("tslice")
                dpg.set_axis_limits("xaxis_tag", sl*600, (sl+1)*600)
                
                # series 1
                # dpg.add_line_series(x=x_arr, y=y_arr, label="series 1", parent="yaxis", tag="series_1")
                dpg.add_line_series(x=dpg.get_value("x_array"), y=dpg.get_value("y_array"), label="series 1", parent="yaxis", tag="series_1")
                # dpg.set_axis_ticks(axis="xaxis_tag",label_pairs=label_pairs)
                # create plot
        
        create_plot()
    # spectro_texture()

        
def bound(sender, app_data, user_data):
    dpg.set_axis_limits("xaxis_tag", app_data*600, (1+app_data)*600)
    dpg.set
        
def spectro(sender, app_data):
    data = np.array(dpg.get_value("y_array"))
    fs = dpg.get_value("fs")
    section = dpg.get_value("tslice")
    # data = data[section*600*int(fs):(section+1)*600*int(fs)]
    f, t, Sxx = spectrogram(data, fs)
    Sxx = np.flipud(Sxx)
    print(Sxx.shape)
    fig = go.Figure(go.Heatmap(x=t,y=f,z=10 * np.log10(Sxx)))
    fig.write_html(f"{dpg.get_value('file_name').replace('.wav','')}_{section}.html")

def plot(sender, app_data):
    get_data(sender=sender,app_data=app_data)
    plot_wave()
    spectro_texture()

def spectro_texture():
    delete_spectrogram()
    data = np.array(dpg.get_value("y_array"))
    fs = dpg.get_value("fs")
    section = dpg.get_value("tslice")
    # data = data[section*600*int(fs):(section+1)*600*int(fs)]
    f, t, Sxx = spectrogram(data, fs)
    Sxx = np.flipud(Sxx)
    Sxx = 10 * np.log10(Sxx)
    texture_data = []
    for i in Sxx.reshape(1,-1):
        texture_data+=list(plt.colormaps['viridis'](i/Sxx.max()))

    texture_data = np.array(texture_data).reshape(1,-1)[0]
    raw_data = array.array('f', texture_data)
    # raw_data = np.array(texture_data).reshape(1,-1) 
    with dpg.texture_registry(tag="text_reg", show=False):
        dpg.add_raw_texture(width=Sxx.shape[1], 
                            height=Sxx.shape[0], 
                            default_value=raw_data, 
                            format=dpg.mvFormat_Float_rgba, 
                            tag="texture_tag")
    
    with dpg.window(label="Spectrogram", tag="spectro", width=800, height=350,pos=[0,350]):
        # create plot
        with dpg.plot(label="Spectrogram plot",tag="s_plot", height=-1, width=-1):
            dpg.add_plot_legend()

            dpg.add_plot_axis(dpg.mvXAxis, label="Time",tag="spectro_xaxis",parent="s_plot")
            dpg.add_plot_axis(dpg.mvYAxis, label="Freq", tag="spectro_yaxis",parent="s_splot")
            
                # series 1
            dpg.add_image_series(texture_tag="texture_tag",
                                 bounds_min=(0,0),
                                 bounds_max=(Sxx.shape[1],Sxx.shape[0]), 
                                 label="series 3", 
                                 parent="spectro_yaxis", 
                                 tag="spectro_series")
            # dpg.add_heat_series(x=10*np.log10(Sxx.reshape((1,-1))),rows=len(t),cols=len(f), label="series 2", parent="yaxis2", tag="series_2")

def apply_filter(sender, app_data):
    # reset filtering by getting the data
    app_data = dpg.get_value("filter_select")
    get_data(sender, app_data)
    if app_data == "No Filter":
        plot_wave()
        spectro_texture()
        return 0
    else:
        filter_name = app_data
        filter_dict = {"Low Pass":{"type":"lowpass","value":dpg.get_value("lp_val")},
                       "Band Pass":{"type":"bandpass","value":(dpg.get_value("bp_low"),dpg.get_value("bp_high"))}, 
                       "High Pass":{"type":"highpass","value":dpg.get_value("hp_val")},
                       "Wind":{"type":"highpass","value":1}}
    filter_params = filter_dict[filter_name]
    b,a = butter(N=4,Wn=filter_params["value"],btype=filter_params["type"],fs=dpg.get_value("fs"))
    y_arr = lfilter(b=b,a=a,x=np.array(dpg.get_value("y_array")))
    dpg.set_value("y_array",list(y_arr))
    plot_wave()
    spectro_texture()


 
    

def delete_waveform():
    if dpg.does_item_exist("Waveform"):
        dpg.hide_item("Waveform")
        dpg.delete_item("Waveform")
        dpg.delete_item("Line Series")
        dpg.delete_item("x")
        dpg.delete_item("yaxis")
        dpg.delete_item("series_1")

def delete_spectrogram():
    if dpg.does_item_exist("spectro"):
        dpg.hide_item("spectro")
        dpg.delete_item("spectro")
        dpg.delete_item("s_plot")
        dpg.delete_item("text_reg")
        dpg.delete_item("texture_tag")
        dpg.delete_item("x")
        dpg.delete_item("spectro_yaxis")
        dpg.delete_item("spectro_series")


with dpg.file_dialog(directory_selector=False,
                      show=False,
                      callback=callback, 
                      file_count=3, 
                      tag="file_dialog_tag", 
                      width=700 ,height=400):
    dpg.add_file_extension("", color=(255, 150, 150, 255))
    dpg.add_file_extension(".*")
    dpg.add_file_extension(".wav", color=(255, 255, 0, 255))




with dpg.value_registry():
    dpg.add_string_value(label="file_path",tag="file_path",default_value="")
    dpg.add_float_vect_value(label="y_array",tag="y_array",default_value=[1.0 for i in range(100)])
    dpg.add_float_vect_value(label="x_array",tag="x_array",default_value=[1.0 for i in range(100)])
    dpg.add_float_value(label="fs",tag="fs",default_value=0.0)

with dpg.window(label="Controls",tag="Controls", width=800, height=100):
    with dpg.menu_bar():  
        dpg.add_button(label="File", callback=lambda: dpg.show_item("file_dialog_tag"))
        dpg.add_button(label="Plot", tag="plot",  callback=plot)
        dpg.add_button(label="Waveform", tag="wave",  callback=plot_wave)
        dpg.add_button(label="Spectrogram",callback=spectro_texture)
    with dpg.group(horizontal=True):
        dpg.add_text(label="file_name",default_value="No file loaded",tag="file_name")
        dpg.add_text(label="file_type",default_value="No file loaded",tag="file_type")
    
    dpg.add_input_int(label="Time Slice",tag="tslice",width=100,default_value=0,callback=plot)

with dpg.window(label="Filters",tag="filters",width=300,height=130, pos=[225,20]):
    with dpg.group(horizontal=True):
        dpg.add_listbox(tag="filter_select",items=["No Filter","Low Pass","Band Pass", "High Pass","Wind"],width=100,num_items=5,callback=apply_filter)
        with dpg.group():
            dpg.add_input_float(label="Low pass <",tag="lp_val",width=100)
            with dpg.group():
                dpg.add_input_float(label="Band pass >",tag="bp_low",width=100)
                dpg.add_input_float(label="Band pass <",tag="bp_high",width=100)
        
            dpg.add_input_float(label="High pass >",tag="hp_val",width=100)
        

dpg.show_metrics()
dpg.create_viewport(title='Custom Title',height=300,width=800)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Controls",True)
dpg.start_dearpygui()
dpg.destroy_context()