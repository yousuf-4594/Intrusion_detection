from tkinter import ttk
import json
import threading
import time
import subprocess
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import numpy as np

def read_json_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def monitor_json_changes(filename):
    previous_data = read_json_file(filename)
    
    while True:
        current_data = read_json_file(filename)
        
        if current_data != previous_data:
            print("JSON file content has changed:")
            update_gui(current_data) 
            update_graph(current_data) 

            previous_data = current_data
        
        time.sleep(1)

def run_lucid_program():
    command = ["python3", 
               "lucid_cnn.py",
               "--predict_live", 
               "enp0s3",
               "--model", 
               "./output/10t-10n-DOS2019-LUCID.h5",
               "--attack_net", 
               "11.0.0.0/24",
               "--victim_net",
               "10.42.0.0/24"
               ]
    subprocess.run(command)

def update_gui(data):
    time_label.config(text="Time: " + data["Time"])
    packets_label.config(text="Packets: " + str(data["Packets"]))
    samples_label.config(text="Samples: " + str(data["Samples"]))
    ddos_label.config(text="DDOS%: " + data["DDOS%"])
    accuracy_label.config(text="Accuracy: " + data["Accuracy"])
    source_label.config(text="Source: " + data["Source"])

lucid_process = None
times = []
ddos_values = []

packets_values = []
samples_values = []

def update_graph(data):
    global times, ddos_values, packets_values, samples_values
    
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
    times.append(current_time)
    ddos_values.append(float(data["DDOS%"]))
    packets_values.append(float(data["Packets"]))
    samples_values.append(float(data["Samples"]))

    # Keep only the top 12 values
    times = times[-12:]
    ddos_values = ddos_values[-12:]

    packets_values = packets_values[-12:]
    samples_values = samples_values[-12:]
    
    # Clear previous plot
    ax.clear()
    ax.plot(times, ddos_values, marker='x', linestyle='-', linewidth=1)
    ax.fill_between(times, ddos_values, color='red', alpha=0.5)   
    ax.set_xlabel('Real World Time')
    ax.set_ylabel('DDOS%')
    ax.set_title('DDoS Score')
    ax.grid(alpha=0.4)
    ax.set_xlim(times[0], times[-1])
    ax.set_ylim(-0.5, 1.5)
    plt.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='x', rotation=90)    
    canvas.draw()
    


def update_heatmap(data):
    global packets_values, samples_values
    
    heatmap_data = np.array([packets_values, samples_values])
    ax2.clear()
    ax2.imshow(heatmap_data, cmap='hot', interpolation='nearest')
    ax2.set_xticks(range(len(times)))
    ax2.set_xticklabels([])
    ax2.set_yticks(range(len(heatmap_data)))
    ax2.set_yticklabels(['P', 'S'])
    canvas2.draw()

def update_plot():
    current_data = read_json_file("results.json")
    update_graph(current_data)
    update_heatmap(current_data)
    root.after(1000, update_plot)



def restart_program():
    global lucid_process
    
    print("RESTARTING PROCESS")
    if lucid_process and lucid_process.poll() is None:
        lucid_process.terminate()
        lucid_process.wait()
    
    lucid_process = subprocess.Popen(["python3", 
                                      "lucid_cnn.py",
                                      "--predict_live", 
                                      selected_interface.get(),
                                      "--model", 
                                      "./output/10t-10n-DOS2019-LUCID.h5",
                                      "--attack_net", 
                                      "11.0.0.0/24",
                                      "--victim_net",
                                      "10.42.0.0/24"])

def shutdown_program():
    pass



root = tk.Tk()
root.title("DDoS Armour")
root.configure(bg="white") 



restart_button = tk.Button(root, text="Restart", command=restart_program)
restart_button.grid(row=0, column=0, sticky="w")

shutdown_button = tk.Button(root, text="Shutdown", command=shutdown_program)
shutdown_button.grid(row=0, column=1, sticky="e")

interface_label = tk.Label(root, text="Select Interface:", bg="white")
interface_label.grid(row=1, column=0, sticky="w")

interface_options = ["enp0s3", "eth0", "wlan0"]
selected_interface = tk.StringVar(root)
interface_dropdown = ttk.Combobox(root, textvariable=selected_interface, values=interface_options)
interface_dropdown.grid(row=1, column=1, sticky="e")
interface_dropdown.current(0)

time_label = tk.Label(root, text="Time: ", bg="white")
time_label.grid(row=2, column=0, sticky="w")

packets_label = tk.Label(root, text="Packets: ", bg="white")
packets_label.grid(row=3, column=0, sticky="w")

samples_label = tk.Label(root, text="Samples: ", bg="white")
samples_label.grid(row=4, column=0, sticky="w")

ddos_label = tk.Label(root, text="DDOS%: ", bg="white")
ddos_label.grid(row=5, column=0, sticky="w")

accuracy_label = tk.Label(root, text="Accuracy: ", bg="white")
accuracy_label.grid(row=6, column=0, sticky="w")

source_label = tk.Label(root, text="Source: ", bg="white")
source_label.grid(row=7, column=0, sticky="w")

fig = plt.figure(figsize=(6, 5))
fig.subplots_adjust(bottom=0.3)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=8, column=0, rowspan=6, columnspan=2)

fig2 = plt.figure(figsize=(2, 0.5))
canvas2 = FigureCanvasTkAgg(fig2, master=root)
canvas2.get_tk_widget().grid(row=2, column=1, rowspan=2, sticky="e")

ax = fig.add_subplot(1, 1, 1)
ax2 = fig2.add_subplot(1, 1, 1)

json_thread = threading.Thread(target=monitor_json_changes, args=("results.json",))
json_thread.start()

lucid_thread = threading.Thread(target=run_lucid_program)
lucid_thread.start()

update_plot()
root.mainloop()
