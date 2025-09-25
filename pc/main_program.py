# -*- coding: utf-8 -*-
"""
Made by Arthur Saint Upery and Ewan Maurel
"""

# Importing local modules
import gui                    # Custom module handling the graphical interface
import robot_control          # Custom module handling robot communications

# Importing required modules
import threading              # For running parallel tasks
import os                     # For file path management
import sys                    # To check system-specific parameters
import time                   # For delays and timestamps
import csv                    # For writing results to a CSV file

# Function to get the correct path for embedded resources (PyInstaller compatibility)
def resource_path(rel_path):
    """Return absolute path to resource, works for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, rel_path)
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, rel_path)

# Thread function to continuously check the application state
def get_state(stop_event):
    global actual_state
    while not stop_event.is_set():
        time.sleep(1)
        actual_state = app.get_actual_state()

# Thread function to get real-time feedback values (number of up-downs and repetitions)
def get_live_result(stop_live):
    global meas_time
    while not stop_live.is_set():
        time.sleep(1)
        live_param = app.get_result()
        meas_time = live_param[0] * 60 #in second

# Initialize variables
csv_file = resource_path("max_positions.csv")
actual_state = "wait"
app = gui.App()

meas_time = 30
start_time = time.time()

# Start thread to monitor app state
stop_thread = threading.Event()
state = threading.Thread(target=get_state, args=(stop_thread,))
state.start()

stop_thread_live = threading.Event()

# Main logic that handles robot connection, positioning, and measurements
def main_program(stop_event):
    global actual_state, meas_time, start_time, stop_thread_live, nb_fields
    robot = None
    filename = None
    live = None
    initial_posej = [0,0,140,0,-50,180]  # Robot's home pose

    # Internal function to update progress in the GUI
    def update_gui_counter():
        global meas_time, start_time
        progress = (time.time() - start_time)/meas_time
        if actual_state != "close":
            app.update_counter(progress)

    while not stop_event.is_set():
        time.sleep(1)

        # Handle connection to the robot
        if actual_state == "connect":
            app.app_state = "wait"
            actual_state = "wait"
            param = app.get_result()  # Retrieve connection parameters
            com, ip, port, vendor, product = param[:5]
            temp, pres, wind, hum, co2, intern_co2 = param[5:11]

            try:
                robot = robot_control.TCPClient(ip, port, wind, com, vendor, product, temp, hum, co2, pres, intern_co2)
                robot.send("Hello")
                response = robot.recv()  # Check if connection works
                if temp or pres or wind:
                    robot.connect_wind()
                if hum or co2 or intern_co2:
                    robot.connect_co2()
                app.app_state = "connected"
                robot.csv_file = csv_file
            except:
                if robot:
                    robot.close_socket()
                app.connection_error()

        # Handle disconnection
        if actual_state == "unconnect":
            app.app_state = "wait"
            actual_state = "wait"
            if robot:
                robot.stop()
                time.sleep(0.1)
                robot.close_socket()

        # Handle positioning commands
        if actual_state in ["goto1", "goto2", "goto3"]:
            param = app.get_result()
            distance = param[0]
            start_field = robot.find_start_pos(distance)
            start_field[0] = param[1]
            robot.gotoj(start_field)
            app.app_state = "wait"

        # Start a full measurement process
        if actual_state == "find":
            app.app_state = "find_ground"
            actual_state = "find_ground"
            param = app.get_result()
            
            #Repositioning to the starting position
            robot.gotoj(initial_posej)

            ground_level = []
            start_fields = []
            nb_fields = param[0]
            distances = param[1:4]
            angles = param[4:7]
            for i in range(nb_fields):
                app.find_ground(i)
                start_field = robot.find_start_pos(distances[i])
                start_field[0] = angles[i]
                start_fields.append(start_field)
                robot.gotoj(start_field)
                start_field_xyz = robot.get_current_posx()

                while actual_state not in ["stop_find","saveground","close"]:
                    time.sleep(1)
                    if actual_state == "gotoground":
                        app.app_state = "find_ground"
                        actual_state = "find_ground"
                        ground_distance = app.get_result()
                        arm_position = robot.get_current_posx()
                        arm_position[2] = ground_distance[0]
                        robot.goto(arm_position)

                if actual_state == "saveground":
                    app.app_state = "find_ground"
                    actual_state = "find_ground"
                    ground_distance = app.get_result()
                    ground_level.append(start_field_xyz[2] - ground_distance[0])
                    robot.goto(start_field_xyz)
                else:
                    break

            if actual_state == "find_ground":
                app.app_state = "ground_fond"
                actual_state = "ground_fond"
                
            robot.gotoj(initial_posej)

        if actual_state == "start":
            start_time = time.time()

            param = app.get_result()
            # Start thread to update live feedback values
            live = threading.Thread(target=get_live_result, args=(stop_thread_live,))
            live.start()

            # Extract measurement parameters
            filename, temp, pres, wind, hum, co2, intern_co2 = param[:7]
            mode = param[7]
            nb_points = param[8]
            robot.freq = param[9]
            app.update() #for meas_time
            time.sleep(1)
            

            row = ['Time', 'Position','Field number']
            row2 = ['X','X','X']
            if wind:
                row.extend(['Wind (U)', 'Wind (V)', 'Wind (W)','Magnetic'])
                row2.extend([wind,wind,wind,wind])
            if temp:
                row.append('Temperature')
                row2.append(temp)
            if pres:
                row.append('Pressure')
                row2.append(pres)
            if co2:
                row.append('CO2')
                row2.append(co2)
            if hum:
                row.append('Humidity')
                row2.append(hum)
            if intern_co2:
                row.extend(['Pressure CO2','Temperature CO2'])
                row2.extend([intern_co2,intern_co2])

            row.append('Mode')
            row2.append(mode)
            if mode == "Continuous":
                row.append('Frequency')
                row2.append(robot.freq)
            else:
                row.append('Number of points')
                row2.append(nb_points)

            # Write CSV header
            try:
                with open(filename, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(row)
                    writer.writerow(row2)
            except IOError:
                app.error_file()

            robot.filename = filename

            # Measurement loop
            app.app_state = "record"
            actual_state = "record"
            while True:
                elapsed = time.time() - start_time
                if elapsed >= meas_time:
                    break

                if actual_state not in ["stop_measure", "close"]:
                    for j in range(nb_fields):
                        if actual_state not in ["stop_measure", "close"]:
                            robot.nb_actual_field = j + 1
                            robot.up_down_field(mode, start_fields[j], ground_level[j], nb_points, callback=update_gui_counter)
                        else:
                            break
                else:
                    break

            # End of measurements
            robot.gotoj(initial_posej)
            app.saved_file(os.path.abspath(filename))
            filename = None
            stop_thread_live.set()
            live.join()
            if actual_state != "close":
                app.app_state = "stop_measure"
                actual_state = "stop_measure"
                app.end_recording()

        # Handle stop event during measurement
        if actual_state in ["stop_measure","stop_find","stop"]:
            stop_thread_live.set()
            if live:
                live.join()
            app.end_recording()

        # Handle app closure and resource cleanup
        if actual_state == "close":
            actual_state = "wait"
            if robot:
                robot.send("stop_stream")
                time.sleep(0.1)
                robot.stop()
                time.sleep(0.1)
                robot.close_socket()
            if live:
                stop_thread_live.set()
                live.join()
            stop_thread.set()
            actual_state = "unconnect"

# Start the main control program thread
prog = threading.Thread(target=main_program, args=(stop_thread,))
prog.start()

# Launch GUI mainloop (blocking call until GUI is closed)
app.mainloop()


# Clean up threads when GUI is closed

state.join()
prog.join()
