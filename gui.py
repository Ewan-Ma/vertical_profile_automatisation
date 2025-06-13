# -*- coding: utf-8 -*-
"""
Made by Arthur Saint Upery and Ewan Maurel
"""
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        self.app_state = "wait"
        
        super().__init__()
        self.title("Configuration complète")
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

        # ==== Variables ====
        self.save_path = ctk.StringVar()
        self.mode = ctk.StringVar(value="Continuous")
        self.freq = ctk.StringVar(value="1")
        self.nb_points = ctk.StringVar(value="1")
        self.nb_fields = ctk.StringVar(value="1")
        self.angle = ctk.StringVar(value="90")
        self.distance1 = ctk.StringVar(value="700")
        self.angle1 = ctk.StringVar(value="90")
        self.distance2 = ctk.StringVar(value="700")
        self.angle2 = ctk.StringVar(value="0")
        self.distance3 = ctk.StringVar(value="700")
        self.angle3 = ctk.StringVar(value="-90")
        self.gposition = ctk.StringVar(value="0")
        self.up_down = ctk.StringVar(value="1")
        self.repetitions = ctk.StringVar(value="1")

        self.measure_temp = ctk.BooleanVar(value=False)
        self.measure_wind = ctk.BooleanVar(value=False)
        self.measure_hum = ctk.BooleanVar(value=False)
        self.measure_co2 = ctk.BooleanVar(value=False)
        self.measure_press = ctk.BooleanVar(value=False)
        self.measure_temp2 = ctk.BooleanVar(value=False)

        # Technical settings
        self.ip_bras = ctk.StringVar(value="192.168.137.100")
        self.port_bras = ctk.StringVar(value=20002)
        self.serial_port = ctk.StringVar(value="COM6")
        self.co2_vendor = ctk.StringVar(value="1509")
        self.co2_product = ctk.StringVar(value="0A02")

        # === CSV saving file creation ===
        exe_dir = os.path.dirname(os.path.abspath(__file__))
        now = datetime.now()
        filename = now.strftime("data_%d-%m_%H%M.csv")
        self.save_path.set(os.path.join(exe_dir, filename))

        # ==== Main interface ====
        self.init_interface()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def init_interface(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=3)
        main_frame.grid_rowconfigure(1, weight=4)

        self.init_main_frame(main_frame)
        self.init_tech_frame(main_frame)
        self.init_position_frame(main_frame)

    # Layout interface settings
    def init_main_frame(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=0, rowspan=2, padx=20, pady=10, sticky="nsew")

        # Title
        ctk.CTkLabel(frame, text="📁 Data saving", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=(10, 20))

        # Saving file
        ctk.CTkEntry(frame, textvariable=self.save_path, width=400).grid(row=1, column=0, columnspan=2, padx=5)
        self.csv_button = ctk.CTkButton(frame, text="Choose a saving place", command=self.select_save_path)
        self.csv_button.grid(row=1, column=2, padx=5)

        # Fields amount
        ctk.CTkLabel(frame, text="Amount of fields :").grid(row=2, column=0, padx=5, pady=(10, 0), sticky="w")
        self.nb_fields_menu = ctk.CTkOptionMenu(frame, values=["1", "2", "3"], variable=self.nb_fields, command=self.update_fields)
        self.nb_fields_menu.grid(row=2, column=1, pady=(10, 0), sticky="w")


        # Quantities to measure
        ctk.CTkLabel(frame, text="Measured variables :").grid(row=4, column=0, columnspan=2, padx=5, pady=(10, 0), sticky="w")
        self.temp_box = ctk.CTkCheckBox(frame, text="Temperature", variable=self.measure_temp, command=self.co2_selected)
        self.temp_box.grid(row=5, column=0, padx=5, sticky="w")
        self.wind_box = ctk.CTkCheckBox(frame, text="Wind", variable=self.measure_wind, command=self.wind_selected)
        self.wind_box.grid(row=5, column=1, sticky="w")
        self.h2o_box = ctk.CTkCheckBox(frame, text="H2O", variable=self.measure_hum, command=self.co2_selected)
        self.h2o_box.grid(row=6, column=0, padx=5, pady=2, sticky="w")
        self.co2_box = ctk.CTkCheckBox(frame, text="CO2", variable=self.measure_co2, command=self.co2_selected)
        self.co2_box.grid(row=6, column=1, pady=2, sticky="w")
        self.pres_box = ctk.CTkCheckBox(frame, text="Pressure (CO2)", variable=self.measure_press, command=self.co2_selected)
        self.pres_box.grid(row=7, column=0, padx=5, sticky="w")
        self.temp2_box = ctk.CTkCheckBox(frame, text="Temperature (CO2)", variable=self.measure_temp2, command=self.co2_selected)
        self.temp2_box.grid(row=7, column=1, padx=5, sticky="w")

        # Amount of up & down and repetitions
        ctk.CTkLabel(frame, text="Amount of up & down (> 0) :").grid(row=8, column=0, padx=5, pady=(10, 0), sticky="w")
        ctk.CTkEntry(frame, textvariable=self.up_down).grid(row=8, column=1, padx=5, pady=(10, 0), sticky="w")

        ctk.CTkButton(frame, text="Estimate time", command=self.update_time).grid(row=8, column=2, padx=5, pady=(10, 0), sticky="w")

        self.rep_label = ctk.CTkLabel(frame, text="Amount of repetitions (> 0) :")
        self.rep_entry = ctk.CTkEntry(frame, textvariable=self.repetitions)
        self.rep_label.grid(row=9, column=0, padx=5, pady=(10, 0), sticky="w")
        self.rep_entry.grid(row=9, column=1, padx=5, pady=(10, 0), sticky="w")
        self.rep_label.configure(state="disabled")
        self.rep_entry.configure(state="disabled")

        self.estimate_time_text = ctk.StringVar()
        self.estimate_time_text.set("0h 0min 0s")
        self.estimate_time_label = ctk.CTkLabel(frame, textvariable = self.estimate_time_text)
        self.estimate_time_label.grid(row=9, column=2, padx=5, pady=(10, 0), sticky="we")

        # Measuring mode (continuous / discontinuous)
        ctk.CTkLabel(frame, text="Measuring mode :").grid(row=10, column=0, padx=5, pady=(10, 0), sticky="w")
        self.mode_menu = ctk.CTkOptionMenu(frame, values=["Continuous", "Discontinuous"], variable=self.mode, command=self.toggle_mode)
        self.mode_menu.grid(row=10, column=1, padx=5, pady=(10, 0), sticky="w")
        
        # Acquisition settings
        self.freq_label = ctk.CTkLabel(frame, text="Frequency (Hz) (< 10) :")
        self.freq_entry = ctk.CTkEntry(frame, textvariable=self.freq)
        self.nb_label = ctk.CTkLabel(frame, text="Amount of measures (> 0) :")
        self.nb_entry = ctk.CTkEntry(frame, textvariable=self.nb_points)
        self.freq_label.grid(row=11, column=0, padx=5, pady=(10, 0), sticky="w")
        self.freq_entry.grid(row=11, column=1, pady=(10, 0), sticky="w")
        self.nb_label.grid(row=11, column=0, padx=5, pady=(10, 0), sticky="w")
        self.nb_entry.grid(row=11, column=1, pady=(10, 0), sticky="w")
        self.nb_label.grid_remove()
        self.nb_entry.grid_remove()

        
        ctk.CTkLabel(frame, text="").grid(row=12, column=0, columnspan=2, pady=20)

        # Recording display / ground finding by the robot
        self.recording_label = ctk.CTkLabel(frame, text="● Recording in progess", text_color="red")
        self.recording_label.grid(row=12, column=0, columnspan=2, padx=5, pady=20, sticky="w")
        self.recording_label.grid_remove()

        self.finding_ground_label = ctk.CTkLabel(frame, text="● Finding ground", text_color="yellow")
        self.finding_ground_label.grid(row=12, column=0, columnspan=2, padx=5, pady=20, sticky="w")
        self.finding_ground_label.grid_remove()

        self.stop_measure_label = ctk.CTkLabel(frame, text="● Stopping in progess", text_color="red")
        self.stop_measure_label.grid(row=12, column=0, columnspan=2, padx=5, pady=20, sticky="w")
        self.stop_measure_label.grid_remove()

        self.progress_bar = ctk.CTkProgressBar(frame)
        self.progress_bar.grid(row=13, column=0, columnspan=2, padx=5, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()

        self.progress_text = ctk.StringVar()
        self.progress_text.set("0 %")
        self.progress_label = ctk.CTkLabel(frame, textvariable = self.progress_text)
        self.progress_label.grid(row=13, column=2, padx=5, pady=(0, 10), sticky="ew")
        self.progress_label.grid_remove()

        # Start & stop buttons settings and availability
        self.find_button = ctk.CTkButton(frame, text="Find Ground", fg_color="yellow", command=self.finding_ground)
        self.find_button.grid(row=14, column=0, columnspan=2, padx=5, pady=10, sticky="w")
        self.find_button.configure(state="disabled")

        self.start_button = ctk.CTkButton(frame, text="Start", fg_color="green", command=self.start_recording)
        self.start_button.grid(row=14, column=1, columnspan=2, padx=5, pady=10, sticky="w")
        self.start_button.grid_remove()

        self.stop_button = ctk.CTkButton(frame, text="Stop", fg_color="red", command=self.stop_recording)
        self.stop_button.grid(row=14, column=0, pady=10, sticky="w")
        self.stop_button.grid_remove()

        self.valid_button = ctk.CTkButton(frame, text="Update Value", fg_color="green", command=self.update)
        self.valid_button.grid(row=14, column=1, pady=10, sticky="w")
        self.valid_button.grid_remove()

    # Technical settings window layout
    def init_tech_frame(self, parent):
        tech_frame = ctk.CTkFrame(parent)
        tech_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Window label
        ctk.CTkLabel(tech_frame, text="🔧 Technical settings", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        # Robot IP adress display
        ctk.CTkLabel(tech_frame, text="Robot IP adress :").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.ip_entry = ctk.CTkEntry(tech_frame, textvariable=self.ip_bras)
        self.ip_entry.grid(row=1, column=1, padx=5, pady=5)

        # Robot communication port display
        ctk.CTkLabel(tech_frame, text="Robot comunication port  :").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.port_entry = ctk.CTkEntry(tech_frame, textvariable=self.port_bras)
        self.port_entry.grid(row=2, column=1, padx=5, pady=5)

        # Wind sensor communnication port
        self.seral_port_label = ctk.CTkLabel(tech_frame, text="Serial port wind sensor :")
        self.seral_port_label.grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.seral_port_label.grid_remove()
        self.seral_port_entry = ctk.CTkEntry(tech_frame, textvariable=self.serial_port)
        self.seral_port_entry.grid(row=3, column=1, padx=5, pady=5)
        self.seral_port_entry.grid_remove()

        # CO2 sensor identifier
        self.co2_vendor_label = ctk.CTkLabel(tech_frame, text="CO2 idVendor :")
        self.co2_vendor_label.grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.co2_vendor_label.grid_remove()
        self.co2_vendor_entry = ctk.CTkEntry(tech_frame, textvariable=self.co2_vendor)
        self.co2_vendor_entry.grid(row=4, column=1, padx=5, pady=5)
        self.co2_vendor_entry.grid_remove()

        self.co2_product_label = ctk.CTkLabel(tech_frame, text="CO2 idProduct :")
        self.co2_product_label.grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.co2_product_label.grid_remove()
        self.co2_product_entry = ctk.CTkEntry(tech_frame, textvariable=self.co2_product)
        self.co2_product_entry.grid(row=5, column=1, padx=5, pady=5)
        self.co2_product_entry.grid_remove()

        # Robot connection button and display
        self.connected_button = ctk.CTkButton(tech_frame, text="Connect", command=self.connect)
        self.connected_button.grid(row=6, column=0, padx=5, pady=10)
        self.unconnected_button = ctk.CTkButton(tech_frame, text="Unconnect", command=self.unconnect)
        self.unconnected_button.grid(row=6, column=0, padx=5, pady=10)
        self.unconnected_button.grid_remove()

        #Connection loading display
        self.connected_label = ctk.CTkLabel(tech_frame, text="● Connected", text_color="green")
        self.connected_label.grid(row=6, column=1, padx=5, sticky="we")
        self.connected_label.grid_remove()

        self.unconnected_label = ctk.CTkLabel(tech_frame, text="Not connected", text_color="red")
        self.unconnected_label.grid(row=6, column=1, padx=5, sticky="we")

    # Fields position window settings
    def init_position_frame(self, parent):
        position_frame = ctk.CTkFrame(parent)
        position_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(position_frame, text="📏 Field(s) position", font=("Arial", 16)).grid(row=0, column=0, columnspan=4, pady=10)

        # Field 1 settings
        self.position1_label = ctk.CTkLabel(position_frame, text="Position field 1 :", font=("Arial", 14))
        self.position1_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.position1_button = ctk.CTkButton(position_frame, text="Go to", command=self.goto_field1)
        self.position1_button.grid(row=1, column=2, columnspan=2, pady=(15,0), padx=10, sticky="we")
        self.position1_button.configure(state="disabled")
        self.distance1_input = ctk.CTkEntry(position_frame, textvariable=self.distance1)
        self.distance1_input.grid(row=2, column=0, padx=5, pady=5)
        self.distance1_label = ctk.CTkLabel(position_frame, text="mm,")
        self.distance1_label.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.angle1_input = ctk.CTkEntry(position_frame, textvariable=self.angle1)
        self.angle1_input.grid(row=2, column=2, padx=5, pady=5)
        self.angle1_label = ctk.CTkLabel(position_frame, text="°")
        self.angle1_label.grid(row=2, column=3, sticky="w", padx=5, pady=5)

        # Field 2 settings
        self.position2_label = ctk.CTkLabel(position_frame, text="Position field 2 :", font=("Arial", 14))
        self.position2_label.grid(row=3, column=0, sticky="e", padx=5, pady=(15,5))
        self.position2_label.grid_remove()
        self.position2_button = ctk.CTkButton(position_frame, text="Go to", command=self.goto_field2)
        self.position2_button.grid(row=3, column=2, columnspan=2, padx=10, pady=(15,0), sticky="we")
        self.position2_button.configure(state="disabled")
        self.position2_button.grid_remove()
        self.distance2_input = ctk.CTkEntry(position_frame, textvariable=self.distance2)
        self.distance2_input.grid(row=4, column=0, padx=5, pady=5)
        self.distance2_input.grid_remove()
        self.distance2_label = ctk.CTkLabel(position_frame, text="mm,")
        self.distance2_label.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        self.distance2_label.grid_remove()
        self.angle2_input = ctk.CTkEntry(position_frame, textvariable=self.angle2)
        self.angle2_input.grid(row=4, column=2, padx=5, pady=5)
        self.angle2_input.grid_remove()
        self.angle2_label = ctk.CTkLabel(position_frame, text="°")
        self.angle2_label.grid(row=4, column=3, sticky="w", padx=5, pady=5)
        self.angle2_label.grid_remove()

        # Field 3 settings
        self.position3_label = ctk.CTkLabel(position_frame, text="Position field 3 :", font=("Arial", 14))
        self.position3_label.grid(row=5, column=0, sticky="e", padx=5, pady=(15,5))
        self.position3_label.grid_remove()
        self.position3_button = ctk.CTkButton(position_frame, text="Go to", command=self.goto_field3)
        self.position3_button.grid(row=5, column=2, columnspan=2, padx=10, pady=(15,0), sticky="we")
        self.position3_button.configure(state="disabled")
        self.position3_button.grid_remove()
        self.distance3_input = ctk.CTkEntry(position_frame, textvariable=self.distance3)
        self.distance3_input.grid(row=6, column=0, padx=5, pady=5)
        self.distance3_input.grid_remove()
        self.distance3_label = ctk.CTkLabel(position_frame, text="mm,")
        self.distance3_label.grid(row=6, column=1, sticky="w", padx=5, pady=5)
        self.distance3_label.grid_remove()
        self.angle3_input = ctk.CTkEntry(position_frame, textvariable=self.angle3)
        self.angle3_input.grid(row=6, column=2, padx=5, pady=5)
        self.angle3_input.grid_remove()
        self.angle3_label = ctk.CTkLabel(position_frame, text="°")
        self.angle3_label.grid(row=6, column=3, sticky="w", padx=5, pady=5)
        self.angle3_label.grid_remove()

        #-----------------Ground-----------------#

        # Field 1 ground settings
        self.gposition_label = ctk.CTkLabel(position_frame, text="Ground Distance field 1 :", font=("Arial", 14))
        self.gposition_label.grid(row=1, column=0, sticky="we", padx=5, pady=(15,5))
        self.gposition_label.grid_remove()
        self.gposition_input = ctk.CTkEntry(position_frame, textvariable=self.gposition)
        self.gposition_input.grid(row=1, column=1, padx=5, pady=(15,5))
        self.gposition_input.grid_remove()
        self.gposition_unit = ctk.CTkLabel(position_frame, text="mm")
        self.gposition_unit.grid(row=1, column=2, sticky="w", padx=5, pady=(15,5))
        self.gposition_unit.grid_remove()
        self.gposition_button = ctk.CTkButton(position_frame, text="Go to", command=self.goto_ground_field)
        self.gposition_button.grid(row=2, column=0, padx=5, pady=5, sticky="we")
        self.gposition_button.grid_remove()
        self.gsave_button = ctk.CTkButton(position_frame, text="Save", command=self.save_ground_field)
        self.gsave_button.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="we")
        self.gsave_button.grid_remove()

        # Field 2 ground settings
        self.gposition2_label = ctk.CTkLabel(position_frame, text="Ground Distance field 2 :", font=("Arial", 14))
        self.gposition2_label.grid(row=1, column=0, sticky="we", padx=5, pady=(15,5))
        self.gposition2_label.grid_remove()

        # Field 3 ground settings
        self.gposition3_label = ctk.CTkLabel(position_frame, text="Ground Distance field 3 :", font=("Arial", 14))
        self.gposition3_label.grid(row=1, column=0, sticky="we", padx=5, pady=(15,5))
        self.gposition3_label.grid_remove()

    # File path selecting display 
    def select_save_path(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV File", "*.csv")])
        if path:
            self.save_path.set(path)

    # Measurement mode settings pannel
    def toggle_mode(self, choice):
        if choice == "Continuous":
            self.nb_label.grid_remove()
            self.nb_entry.grid_remove()
            self.freq_label.grid()
            self.freq_entry.grid()
        else:
            self.freq_label.grid_remove()
            self.freq_entry.grid_remove()
            self.nb_label.grid()
            self.nb_entry.grid()

    def update_fields(self, nb):
        nb = int(nb)
        if nb == 1:
            self.rep_label.configure(state="disabled")
            self.rep_entry.configure(state="disabled")
            self.distance2_label.grid_remove()
            self.distance2_input.grid_remove()
            self.angle2_label.grid_remove()
            self.angle2_input.grid_remove()
            self.position2_label.grid_remove()
            self.position2_button.grid_remove()
            self.distance3_label.grid_remove()
            self.distance3_input.grid_remove()
            self.angle3_label.grid_remove()
            self.angle3_input.grid_remove()
            self.position3_label.grid_remove()
            self.position3_button.grid_remove()
        elif nb == 2:
            self.rep_label.configure(state="normal")
            self.rep_entry.configure(state="normal")
            self.distance2_label.grid()
            self.distance2_input.grid()
            self.angle2_label.grid()
            self.angle2_input.grid()
            self.position2_label.grid()
            self.position2_button.grid()
            self.distance3_label.grid_remove()
            self.distance3_input.grid_remove()
            self.angle3_label.grid_remove()
            self.angle3_input.grid_remove()
            self.position3_label.grid_remove()
            self.position3_button.grid_remove()
        else:
            self.rep_label.configure(state="normal")
            self.rep_entry.configure(state="normal")
            self.distance2_label.grid()
            self.distance2_input.grid()
            self.angle2_label.grid()
            self.angle2_input.grid()
            self.position2_label.grid()
            self.position2_button.grid()
            self.distance3_label.grid()
            self.distance3_input.grid()
            self.angle3_label.grid()
            self.angle3_input.grid()
            self.position3_label.grid()
            self.position3_button.grid()
            

    def wind_selected(self):
        if self.measure_wind.get() or self.measure_temp.get():
            self.seral_port_label.grid()
            self.seral_port_entry.grid()
        else:
            self.seral_port_label.grid_remove()
            self.seral_port_entry.grid_remove()
        if self.find_button.cget("state") == "normal":
            self.unconnect()

    def co2_selected(self):
        if self.measure_co2.get() or self.measure_hum.get() or self.measure_temp2.get() or self.measure_press.get():
            self.co2_vendor_label.grid()
            self.co2_product_label.grid()
            self.co2_vendor_entry.grid()
            self.co2_product_entry.grid()
        else:
            self.co2_vendor_label.grid_remove()
            self.co2_product_label.grid_remove()
            self.co2_vendor_entry.grid_remove()
            self.co2_product_entry.grid_remove()

        if self.find_button.cget("state") == "normal":
            self.unconnect()

    def connect(self):
        self.app_state = "connect"
        com = self.serial_port.get()
        ip = self.ip_bras.get()
        port = int(self.port_bras.get())
        vendor = self.co2_vendor_entry.get()
        product = self.co2_product_entry.get()
        temp = self.measure_temp.get()
        wind = self.measure_wind.get()
        hum = self.measure_hum.get()
        co2 = self.measure_co2.get()
        pres = self.measure_press.get()
        temp2 = self.measure_temp2.get()
        self.result = [com, ip, port, vendor, product, temp, wind, hum, co2, pres, temp2]
        

    def unconnect(self):
        self.app_state = "unconnect"
        self.find_button.configure(state="disabled")
        self.position1_button.configure(state="disabled")
        self.position2_button.configure(state="disabled")
        self.position3_button.configure(state="disabled")
        self.connected_label.grid_remove()
        self.unconnected_label.grid()
        self.unconnected_button.grid_remove()
        self.connected_button.grid()

    def is_number(self, value, msg, min_val=0, max_val=float("inf")):
        try:
            val = int(value)
            if min_val <= val <= max_val:
                return True
        except:
            pass
        messagebox.showerror("Error" , f"Please enter a value between {min_val} and {max_val if max_val != float('inf') else '∞'}, for {msg}.")
        return False
    
    def goto_field1(self):
        self.app_state = "goto1"
        if self.is_number(self.distance1.get(), "distance from field n°1", 700, 1600):
            distance1 = int(self.distance1.get())
        else:
            return
        if self.is_number(self.angle1.get(), "angle of field n°1", -90, 90):
            angle1 = int(self.angle1.get())
        else:
            return
        self.result = [distance1, angle1]
        

    def goto_field2(self):
        self.app_state = "goto2"
        if self.is_number(self.distance2.get(), "distance from field n°2", 700, 1600):
            distance2 = int(self.distance2.get())
        else:
            return
        if self.is_number(self.angle2.get(), "angle of field n°2", -90, 90):
            angle2 = int(self.angle2.get())
        else:
            return
        self.result = [distance2, angle2]
        

    def goto_field3(self):
        self.app_state = "goto3"
        if self.is_number(self.distance3.get(), "distance from field n°3", 700, 1600):
            distance3 = int(self.distance3.get())
        else:
            return
        if self.is_number(self.angle3.get(), "angle of field n°3", -90, 90):
            angle3 = int(self.angle3.get())
        else:
            return
        self.result = [distance3, angle3]

    def find_ground(self, i):
        if i == 0:
            self.gposition_label.grid()
            self.gposition_input.grid()
            self.gposition_unit.grid()
            self.gposition_button.grid()
            self.gsave_button.grid()
        elif i == 1:
            self.gposition_label.grid_remove()
            self.gposition2_label.grid()
        else:
            self.gposition2_label.grid_remove()
            self.gposition3_label.grid()

    def goto_ground_field(self):
        if self.is_number(self.gposition.get(), "distance to the ground in field", -500, 0):
            gposition = int(self.gposition.get())
        else:
            return
        self.app_state = "gotoground"
        self.result = [gposition]

    def save_ground_field(self):
        if self.is_number(self.gposition.get(), "distance to the ground in field", -500, 0):
            gposition = int(self.gposition.get())
        else:
            return
        self.app_state = "saveground"
        self.result = [gposition]


    def finding_ground(self):
        nb_fields = int(self.nb_fields.get())
        if self.is_number(self.distance1.get(), "distance from field n°1", 700, 1600):
            distance1 = int(self.distance1.get())
        else:
            return
        if self.is_number(self.distance2.get(), "distance from field n°2", 700, 1600):
            distance2 = int(self.distance2.get())
        else:
            return
        if self.is_number(self.distance3.get(), "distance from field n°3", 700, 1600):
            distance3 = int(self.distance3.get())
        else:
            return
        if self.is_number(self.angle1.get(), "angle of field n°1", -90, 90):
            angle1 = int(self.angle1.get())
        else:
            return
        if self.is_number(self.angle2.get(), "angle of field n°2", -90, 90):
            angle2 = int(self.angle2.get())
        else:
            return
        if self.is_number(self.angle3.get(), "angle of field n°3", -90, 90):
            angle3 = int(self.angle3.get())
        else:
            return
        self.result = [nb_fields, distance1, distance2, distance3, angle1, angle2, angle3]
        self.find_button.grid_remove()
        self.start_button.grid()
        self.start_button.configure(state="disabled")
        self.stop_button.grid()
        self.co2_product_entry.configure(state="disabled")
        self.co2_vendor_entry.configure(state="disabled")
        self.seral_port_entry.configure(state="disabled")
        self.nb_fields_menu.configure(state="disabled")
        self.ip_entry.configure(state="disabled")
        self.port_entry.configure(state="disabled")
        self.unconnected_button.configure(state="disabled")
        self.position1_label.grid_remove()
        self.position1_button.grid_remove()
        self.distance1_input.grid_remove()
        self.distance1_label.grid_remove()
        self.angle1_input.grid_remove()
        self.angle1_label.grid_remove()
        if nb_fields >= 2:
            self.position2_label.grid_remove()
            self.position2_button.grid_remove()
            self.distance2_input.grid_remove()
            self.distance2_label.grid_remove()
            self.angle2_input.grid_remove()
            self.angle2_label.grid_remove()
        if nb_fields ==3:
            self.position3_label.grid_remove()
            self.position3_button.grid_remove()
            self.distance3_input.grid_remove()
            self.distance3_label.grid_remove()
            self.angle3_input.grid_remove()
            self.angle3_label.grid_remove()
        self.app_state = "find"
        messagebox.showinfo("Message", "Settings saved.")
        
    def start_recording(self):
        filename = self.save_path.get()
        mode = self.mode.get()
        if self.mode.get() == "Continuous":
            if self.is_number(self.freq.get(), "frequency", 0, 10):
                freq = int(self.freq.get())
            else:
                return
            nb_points = 1
        else:
            if self.is_number(self.nb_points.get(), "measurement points", 0):
                nb_points = int(self.nb_points.get())
            else:
                return
            freq = 1
        temp = self.measure_temp.get()
        wind = self.measure_wind.get()
        hum = self.measure_hum.get()
        co2 = self.measure_co2.get()
        pres = self.measure_press.get()
        temp2 = self.measure_temp2.get()
        self.result = [filename, temp, wind, hum, co2, pres, temp2, mode, nb_points, freq]
        self.nb_entry.configure(state="disabled")
        self.freq_entry.configure(state="disabled")
        self.csv_button.configure(state="disabled")
        self.temp_box.configure(state="disabled")
        self.co2_box.configure(state="disabled")
        self.wind_box.configure(state="disabled")
        self.h2o_box.configure(state="disabled")
        self.pres_box.configure(state="disabled")
        self.temp2_box.configure(state="disabled")
        self.mode_menu.configure(state="disabled")
        nb_fields = int(self.nb_fields.get())
        self.distance1_label.configure(state="disabled")
        self.distance1_input.configure(state="disabled")
        self.angle1_label.configure(state="disabled")
        self.angle1_input.configure(state="disabled")
        self.position1_label.configure(state="disabled")
        self.position1_button.configure(state="disabled")
        if nb_fields >= 2:
            self.distance2_label.configure(state="disabled")
            self.distance2_input.configure(state="disabled")
            self.angle2_label.configure(state="disabled")
            self.angle2_input.configure(state="disabled")
            self.position2_label.configure(state="disabled")
            self.position2_button.configure(state="disabled")
        if nb_fields == 3:
            self.distance3_label.configure(state="disabled")
            self.distance3_input.configure(state="disabled")
            self.angle3_label.configure(state="disabled")
            self.angle3_input.configure(state="disabled")
            self.position3_label.configure(state="disabled")
            self.position3_button.configure(state="disabled")
        self.valid_button.grid()
        self.start_button.grid_remove()
        self.progress_bar.grid()
        self.progress_bar.set(0)
        self.progress_label.grid()
        self.progress_text.set("0 %")
        self.app_state = "start"
        messagebox.showinfo("Message", "Settings saved.")

    def update_counter(self, progress):
        self.progress_bar.set(progress)
        self.progress_text.set(f"{progress * 100:.1f} %")

    def update_time(self):
        if self.is_number(self.up_down.get(), "up & down", 0):
            up_down = int(self.up_down.get())
        else:
            return
        if int(self.nb_fields.get()) > 1:
            if self.is_number(self.repetitions.get(), "repetition", 0):
                nb_rep = int(self.repetitions.get())
            else:
                return
        else:
            nb_rep = 1
        time = nb_rep * up_down * int(self.nb_fields.get()) * 30
        hours, time = divmod(time, 3600)
        minutes, seconds = divmod(time, 60)
        self.estimate_time_text.set(f"{hours}h {minutes}min {seconds}s")

    def stop_recording(self):
        if messagebox.askyesno("Stop", "Do you want to stop measuring ?"):
            if self.app_state == "find_ground":
                self.app_state = "stop_find"
            if self.app_state == "record":
                self.app_state = "stop_measure"
            if self.app_state == "wait":
                self.app_state = "stop"

    def end_recording(self):
        if self.app_state == "stop_find":
            self.start_button.grid_remove()
            if self.finding_ground_label.winfo_ismapped():
                self.finding_ground_label.grid_remove()
        if self.app_state == "stop_measure":
            self.valid_button.grid_remove()
            if self.recording_label.winfo_ismapped():
                self.recording_label.grid_remove()
        if self.app_state == "stop":
            self.start_button.grid_remove()
        self.app_state = "wait"
        self.stop_button.grid_remove()
        self.progress_bar.grid_remove()
        self.progress_label.grid_remove()
        self.find_button.grid()
        self.find_button.configure(state="normal")
        self.co2_product_entry.configure(state="normal")
        self.nb_entry.configure(state="normal")
        self.freq_entry.configure(state="normal")
        self.co2_vendor_entry.configure(state="normal")
        self.seral_port_entry.configure(state="normal")
        self.co2_product_entry.configure(state="normal")
        self.csv_button.configure(state="normal")
        self.nb_fields_menu.configure(state="normal")
        self.temp_box.configure(state="normal")
        self.co2_box.configure(state="normal")
        self.wind_box.configure(state="normal")
        self.h2o_box.configure(state="normal")
        self.pres_box.configure(state="normal")
        self.temp2_box.configure(state="normal")
        self.mode_menu.configure(state="normal")
        self.ip_entry.configure(state="normal")
        self.port_entry.configure(state="normal")
        self.unconnected_button.configure(state="normal")
        nb_fields = int(self.nb_fields.get())
        self.distance1_label.configure(state="normal")
        self.distance1_input.configure(state="normal")
        self.angle1_label.configure(state="normal")
        self.angle1_input.configure(state="normal")
        self.position1_label.configure(state="normal")
        self.position1_button.configure(state="normal")
        if nb_fields >= 2:
            self.distance2_label.configure(state="normal")
            self.distance2_input.configure(state="normal")
            self.angle2_label.configure(state="normal")
            self.angle2_input.configure(state="normal")
            self.position2_label.configure(state="normal")
            self.position2_button.configure(state="normal")
        if nb_fields == 3:
            self.distance3_label.configure(state="normal")
            self.distance3_input.configure(state="normal")
            self.angle3_label.configure(state="normal")
            self.angle3_input.configure(state="normal")
            self.position3_label.configure(state="normal")
            self.position3_button.configure(state="normal")
        self.distance1_label.grid()
        self.distance1_input.grid()
        self.angle1_label.grid()
        self.angle1_input.grid()
        self.position1_label.grid()
        self.position1_button.grid()
        if nb_fields >= 2:
            self.distance2_label.grid()
            self.distance2_input.grid()
            self.angle2_label.grid()
            self.angle2_input.grid()
            self.position2_label.grid()
            self.position2_button.grid()
        if nb_fields == 3:
            self.distance3_label.grid()
            self.distance3_input.grid()
            self.angle3_label.grid()
            self.angle3_input.grid()
            self.position3_label.grid()
            self.position3_button.grid()
        self.gposition_input.grid_remove()
        self.gposition_unit.grid_remove()
        self.gposition_button.grid_remove()
        self.gsave_button.grid_remove()
        if nb_fields == 1:
            self.gposition_label.grid_remove()
        if nb_fields == 2:
            self.gposition2_label.grid_remove()
        if nb_fields == 3:
            self.gposition3_label.grid_remove()
        self.unconnect()
        messagebox.showinfo("Stop", "End of measuring")

    def update(self):
        if self.is_number(self.up_down.get(), "up & down", 0):
            up_down = int(self.up_down.get())
        else:
            return
        if int(self.nb_fields.get()) > 1:
            if self.is_number(self.repetitions.get(), "repetition", 0):
                nb_rep = int(self.repetitions.get())
            else:
                return
        else:
            nb_rep = 1
        self.result = [up_down,nb_rep]

    def get_result(self):
        return self.result
    
    def get_actual_state(self):
        
        if self.app_state == "wait":
            if self.finding_ground_label.winfo_ismapped():
                self.finding_ground_label.grid_remove()
            if self.stop_measure_label.winfo_ismapped():
                self.stop_measure_label.grid_remove()
            if self.recording_label.winfo_ismapped():
                self.recording_label.grid_remove()

        if self.app_state == "stop_find":
            if self.finding_ground_label.winfo_ismapped():
                self.finding_ground_label.grid_remove()
                
            if self.stop_measure_label.winfo_ismapped():
                self.stop_measure_label.grid_remove()
            else:
                self.stop_measure_label.grid()
        
        if self.app_state == "stop_measure":
            if self.recording_label.winfo_ismapped():
                self.recording_label.grid_remove()

            if self.stop_measure_label.winfo_ismapped():
                self.stop_measure_label.grid_remove()
            else:
                self.stop_measure_label.grid()
        
        if self.app_state == "find_ground":
            if self.finding_ground_label.winfo_ismapped():
                self.finding_ground_label.grid_remove()
            else:
                self.finding_ground_label.grid()

        if self.app_state == "record":
            if self.recording_label.winfo_ismapped():
                self.recording_label.grid_remove()
            else:
                self.recording_label.grid()

        if self.app_state == "ground_fond":
            self.start_button.configure(state="normal")
            self.app_state = "wait"

        if self.app_state == "connected":
            self.unconnected_button.grid()
            self.connected_button.grid_remove()
            self.unconnected_label.grid_remove()
            self.connected_label.grid()
            self.find_button.configure(state="normal")
            self.position1_button.configure(state="normal")
            self.position2_button.configure(state="normal")
            self.position3_button.configure(state="normal")
            self.app_state = "wait"
        return self.app_state
    
    def on_close(self):
        self.app_state = "close"
        self.destroy()

    def connection_error(self):
        messagebox.showinfo("ERREUR", "Check if all the devices are ON or well connected")

    def error_file(self):
        messagebox.showinfo("ERREUR", "Can't open file")

    def saved_file(self, filepath):
        messagebox.showinfo("FILE SAVED", "File saved here : {0}".format(filepath))