import dearpygui.dearpygui as dpg
from obspy import read as sig_read
from scipy.signal import spectrogram
from scipy.io import wavfile
import numpy as np
import warnings
import plotly.graph_objects as go

warnings.filterwarnings("ignore")

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

    if ".wav" in file_path_string:
        fs, data = wavfile.read(file_path_string)
        if data.shape[1]>1:
            data = data.mean(axis=1)
        length = data.shape[0] / fs
        time = np.linspace(0., length, data.shape[0])
        x_arr = list(time)
        y_arr = list(data)
        dpg.set_value("file_type","WAV")
        dpg.set_value("x_array",x_arr)
        dpg.set_value("y_array",y_arr)
        dpg.set_value("fs",fs)

    else:
        try:
            collect = sig_read(file_path_string)[0]
            x_arr = list(collect.times())
            y_arr = list(collect.data)
            dpg.set_value("file_type","WAV")
            dpg.set_value("x_array",x_arr)
            dpg.set_value("y_array",y_arr)
            dpg.set_value("fs",collect.stats.sampling_rate)
        except:
            dpg.set_value("file_type","Not openable by OBSPY")
            return 1
    

    with dpg.window(label="Waveform",height=200,width=800,pos=[0,100],on_close=delete_waveform()):
        def create_plot():
            with dpg.plot(label="Line Series", height=-1, width=-1,parent="Waveform"):
                dpg.add_plot_legend(parent="Line Series")
                # dpg.add_drag_line(label="dline1", color=[255, 0, 0, 255], default_value=2.0, callback=print_val)
                dpg.add_plot_axis(dpg.mvXAxis, label="x",tag="xaxis_tag")
                dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="yaxis")
                dpg.set_axis_limits("xaxis_tag", 0, 600)
                # series 1
                # dpg.add_line_series(x=x_arr, y=y_arr, label="series 1", parent="yaxis", tag="series_1")
                dpg.add_line_series(x=dpg.get_value("x_array"), y=dpg.get_value("y_array"), label="series 1", parent="yaxis", tag="series_1")
                # create plot
        
        create_plot()
        
def bound(sender, app_data, user_data):
    dpg.set_axis_limits("xaxis_tag", app_data*600, (1+app_data)*600)
        
def spectro(sender, app_data):
    data = np.array(dpg.get_value("y_array"))
    fs = dpg.get_value("fs")
    section = dpg.get_value("tslice")
    data = data[section*600*int(fs):(section+1)*600*int(fs)]
    f, t, Sxx = spectrogram(data, fs)
    fig = go.Figure(go.Heatmap(x=t,y=f,z=10 * np.log10(Sxx)))
    fig.write_html(f"{dpg.get_value('file_name').replace('.wav','')}_{section}.html")


def delete_waveform():
    if dpg.does_item_exist("Waveform"):
        dpg.hide_item("Waveform")
        dpg.delete_item("Waveform")
        dpg.delete_item("Line Series")
        dpg.delete_item("x")
        dpg.delete_item("yaxis")
        dpg.delete_item("series_1")



with dpg.file_dialog(directory_selector=False, show=False, callback=callback, file_count=3, tag="file_dialog_tag", width=700 ,height=400):
    dpg.add_file_extension("", color=(255, 150, 150, 255))
    dpg.add_file_extension(".*")
    dpg.add_file_extension(".wav", color=(255, 255, 0, 255))

with dpg.value_registry():
    dpg.add_string_value(label="file_path",tag="file_path",default_value="")
    dpg.add_float_vect_value(label="y_array",tag="y_array",default_value=[1.0 for i in range(100)])
    dpg.add_float_vect_value(label="x_array",tag="x_array",default_value=[1.0 for i in range(100)])
    dpg.add_float_value(label="fs",tag="fs",default_value=0.0)

with dpg.window(label="Tutorial", width=800, height=100):
    
    dpg.add_button(label="File Selector", callback=lambda: dpg.show_item("file_dialog_tag"))
    dpg.add_text(label="file_name",default_value="No file loaded",tag="file_name")
    dpg.add_text(label="file_type",default_value="No file loaded",tag="file_type")
    dpg.add_button(label="Plot Waveform", callback=get_data)
    dpg.add_input_int(label="Time Slice",tag="tslice",default_value=0,callback=bound)
    dpg.add_button(label="Spectrogram",callback=spectro)

dpg.show_metrics()
dpg.create_viewport(title='Custom Title',height=300,width=800)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()