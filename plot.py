import dearpygui.dearpygui as dpg
from obspy import read as sig_read
from scipy.signal import spectrogram, butter, lfilter
from scipy.io import wavfile
import numpy as np
import warnings
import plotly.graph_objects as go
warnings.filterwarnings("ignore")

import array
import matplotlib.pyplot as plt


dpg.create_context()

def callback(sender, app_data):
    # print("Sender: ", sender)
    # print("App Data: ", app_data)
    dpg.set_value("file_name",list(app_data['selections'].keys())[0])
    dpg.set_value("file_path",list(app_data['selections'].values())[0])

def time_slice(sender, app_data):
    """
time_slice function

Parameters:
    sender (str): The widget sender
    app_data (int): Timeslice index 

Returns:
    sl1 (int): Start index of slice
    sl2 (int): End index of slice

Functionality:
    This function calculates the start and end indices 
    for slicing the waveform data based on the selected 
    timeslice.

    It gets the waveform length and sampling rate. 

    If triggered from tslice widget, it calculates the slice
    indices based on the timeslice index.

    Otherwise it uses the current tslice value.

    Returns the calculated start and end indices.
    """
    tlen = dpg.get_value("tlen")
    fs = dpg.get_value("fs")
    sl1 = 0
    sl2 = tlen*fs
    sl = 0
    if sender == "tslice":
        # sl = app_data
        sl1 = app_data*tlen*fs
        sl2 = (app_data+1)*tlen*fs
    
    else:
        app_data = dpg.get_value("tslice")
        # sl = app_data
        sl1 = app_data*tlen*fs
        sl2 = (app_data+1)*tlen*fs
    return int(sl1), int(sl2)

def get_data(sender, app_data):
    """
    get_data function

    Parameters:
        sender (str): The widget sender
        app_data (dict): Data passed from the widget 

    Functionality:
        This function retrieves waveform data based on user selection.

        It checks if a .wav file is selected, if so it reads the data using 
        scipy.io.wavfile.read(). 

        Otherwise it attempts to read the file with obspy using sig_read().

        It then slices the data based on the selected time interval.

        The x and y data arrays are extracted and set to DPG values to plot.
    """
    print(app_data)
    file_path_string = dpg.get_value("file_path")
        
    if ".wav" in file_path_string:
        fs, data = wavfile.read(file_path_string)
        length = data.shape[0] / fs
        time = np.linspace(0., length, data.shape[0])
        if len(data.shape)>1:
            if data.shape[1]>1:
                data = data.mean(axis=1)
        dpg.set_value("fs",fs)
        sl1, sl2 = time_slice(sender=sender, app_data=app_data)
        data = data[sl1:sl2]
        time = time[sl1:sl2]

        x_arr = list(time)
        y_arr = list(data)
        dpg.set_value("file_type","WAV")
        dpg.set_value("x_array",x_arr)
        dpg.set_value("y_array",y_arr)
        

    else:
        try:
            collect = sig_read(file_path_string)[0]
            dpg.set_value("fs",collect.stats.sampling_rate)
            data = collect.data
            time = collect.times()
            sl1, sl2 = time_slice(sender=sender, app_data=app_data)
            data = data[sl1:sl2]
            time = time[sl1:sl2]
            x_arr = list(time)
            y_arr = list(data)
            dpg.set_value("file_type","File readable by obspy")
            dpg.set_value("x_array",x_arr)
            dpg.set_value("y_array",y_arr)
            
        except:
            dpg.set_value("file_type","Not openable by OBSPY")
            return 1

def plot_wave():
    """
plot_wave function

Functionality:
    Creates a new window and plot for showing the waveform data.

    It creates a new DPG plot and adds x and y axes.

    The waveform line series is added linked to the x and y arrays.

    The x axis limits are set based on the selected time interval.
    """
    delete_waveform()
    with dpg.window(label="Waveform",tag="Waveform",height=200,width=800,pos=[0,150],on_close=delete_waveform()):
        def create_plot():
            with dpg.plot(label="Line Series", height=-1, width=-1,parent="Waveform",query=True):
                dpg.add_plot_axis(dpg.mvXAxis, label="x",tag="xaxis_tag")
                dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="yaxis")
                sl = dpg.get_value("tslice")
                tlen = dpg.get_value("tlen")
                dpg.set_axis_limits("xaxis_tag", sl*tlen, (sl+1)*tlen)
                
                # series 1
                # dpg.add_line_series(x=x_arr, y=y_arr, label="series 1", parent="yaxis", tag="series_1")
                dpg.add_line_series(x=dpg.get_value("x_array"), y=dpg.get_value("y_array"), label="series 1", parent="yaxis", tag="series_1")
                # dpg.set_axis_ticks(axis="xaxis_tag",label_pairs=label_pairs)
                # create plot
        
        create_plot()
    # spectro_texture()

        
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
    dpg.set_value("spectro_freq",list(f))
    dpg.set_value("spectro_time",list(t))
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
    
    with dpg.window(label="Spectrogram", tag="spectro", width=800, height=350,pos=[0,350],):
        # create plot
        with dpg.plot(label="Spectrogram plot",tag="s_plot", height=-1, width=-1,query=True, no_mouse_pos=True):
            # dpg.add_plot_legend()

            dpg.add_plot_axis(dpg.mvXAxis, label="Time",tag="spectro_xaxis",parent="s_plot",no_tick_labels=True)
            dpg.add_plot_axis(dpg.mvYAxis, label="Freq", tag="spectro_yaxis",parent="s_splot",no_tick_labels=True)
            
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
    dpg.add_float_vect_value(label="spectro_freq",tag="spectro_freq" ,default_value=[])
    dpg.add_float_vect_value(label="spectro_time",tag="spectro_time" ,default_value=[])

with dpg.window(label="Controls",tag="Controls", width=800, height=100):
    with dpg.menu_bar():  
        dpg.add_button(label="File", callback=lambda: dpg.show_item("file_dialog_tag"))
        dpg.add_button(label="Plot", tag="plot",  callback=plot)
        dpg.add_button(label="Waveform", tag="wave",  callback=plot_wave)
        dpg.add_button(label="Spectrogram",callback=spectro_texture)
    with dpg.group(horizontal=True):
        dpg.add_text(label="file_name",default_value="No file loaded",tag="file_name")
        dpg.add_text(label="file_type",default_value="No file loaded",tag="file_type")
    dpg.add_input_int(label="Time interval size (S)",tag="tlen",width=100,default_value=600, min_value=0, min_clamped=True,)
    dpg.add_input_int(label="Time Slice",tag="tslice",width=100,default_value=0, min_value=0, min_clamped=True, callback=plot)

with dpg.window(label="Filters",tag="filters",width=300,height=130, pos=[225,20]):
    with dpg.group(horizontal=True):
        dpg.add_listbox(tag="filter_select",items=["No Filter","Low Pass","Band Pass", "High Pass","Wind"],width=100,num_items=5,callback=apply_filter)
        with dpg.group():
            dpg.add_input_float(label="Low pass <",tag="lp_val",width=100)
            with dpg.group():
                dpg.add_input_float(label="Band pass >",tag="bp_low",width=100)
                dpg.add_input_float(label="Band pass <",tag="bp_high",width=100)
        
            dpg.add_input_float(label="High pass >",tag="hp_val",width=100)

def retreive_query():
    if dpg.is_plot_queried("s_plot"):
        x_1, x_2, y_1, y_2 = np.array(dpg.get_plot_query_area("s_plot"))
        tlen = dpg.get_value("tlen")
        tstart = dpg.get_value("tslice")*tlen
        tend = tstart + tlen
        f = np.array(dpg.get_value("spectro_freq"))
        t = np.array(dpg.get_value("spectro_time"))
        time_corrected = np.linspace(tstart,tend,t.shape[0])
        # freq_corrected = np.linspace(tstart,tend,f.shape[0])
        # print(f)
        t1 = time_corrected[int(x_1)]
        t2 = time_corrected[int(x_2)]
        f1 = f[int(y_1)]
        f2 = f[int(y_2)]
        dpg.set_value("text",str(f"from times {t1} to {t2} and {f1} to {f2} Hz"))

def spectro_mouse_pos():
    if dpg.does_item_exist("s_plot"):
        if dpg.is_item_hovered("s_plot"):
            x, y = dpg.get_plot_mouse_pos()
            tlen = dpg.get_value("tlen")
            tstart = dpg.get_value("tslice")*tlen
            tend = tstart + tlen
            f = np.array(dpg.get_value("spectro_freq"))
            t = np.array(dpg.get_value("spectro_time"))
            time_corrected = np.linspace(tstart,tend,t.shape[0])
            try:
                t1 = time_corrected[int(x)]
                f1 = f[int(y)]
                dpg.set_value("plot_mouse",f"{t1} s, {f1} Hz")
            except:
                dpg.set_value("plot_mouse","Hover the spectrogram")
            
        else:
            dpg.set_value("plot_mouse","Hover the spectrogram")
    else:
        dpg.set_value("plot_mouse","Hover the spectrogram")
with dpg.window(label="Annotations"):
    dpg.add_button(label="Get Query",callback=retreive_query)
    dpg.add_text(tag="text",default_value="Queried")
    dpg.add_text(tag="plot_mouse",default_value="")

dpg.show_metrics()
dpg.create_viewport(title='Custom Title',height=300,width=800)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Controls",True)
# dpg.start_dearpygui()
dpg.set_viewport_vsync(True)
while dpg.is_dearpygui_running():
    # insert here any code you would like to run in the render loop
    # you can manually stop by using stop_dearpygui()
    
    # dpg.set_value("plot_mouse",str(dpg.get_plot_mouse_pos()))
    spectro_mouse_pos()
    # print("this will run every frame")
    dpg.render_dearpygui_frame()
dpg.destroy_context()
