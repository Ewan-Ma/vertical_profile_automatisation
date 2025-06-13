# -*- coding: utf-8 -*-
"""
Made by Arthur Saint Upery and Ewan Maurel
"""

import socket
from datetime import datetime
import time
import csv
import serial
import usb.core
import usb.util
import threading

class TCPClient():
    """Class for managing the TCP connection with the robot and sensors connection"""

    def __init__(self, ip, port, wind, com, vendor, product, temp, hum, co2, pres, temp2):
        """
        Executed at the begining of each program
        Initialize robot connection
        """
        # Sensor and connection settings
        self.csv_file = ""
        self.filename = ""
        self.freq = 1  # Frequency of data acquisition (Hz)

        self.ip = ip
        self.port = port
        self._socket = None
        self.ser = None  # Serial port for wind sensor
        self.dev = None  # USB device for CO2 sensor
        self.wind = wind
        self.temp = temp
        self.com = com
        self.vendor = vendor
        self.product = product
        self.hum = hum
        self.co2 = co2
        self.pres = pres
        self.temp2 = temp2

        self.nb_actual_field = 1

        # Connect to robot via TCP
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.ip, self.port))
        except Exception as e:
            raise e

        self._socket.settimeout(5)

    def connect_wind(self):
        """Initialize connection with the wind sensor via serial"""
        try:
            self.ser = serial.Serial(self.com, 115200, timeout=1)
            if self.ser is None:
                raise ValueError('Device not found.')
        except ValueError as e:
            raise e  

    def connect_co2(self):
        """Initialize connection with the CO2 sensor via USB"""
        try:
            self.dev = usb.core.find(idVendor=0x1509, idProduct=0x0A02)
            self.dev.set_configuration()
            command = '(USB(Rate 20Hz)(Sources ("CO2B um/m" "H2OB mm/m" "P kPa" "T C")))\n'
            self.dev.write(0x02, command.encode('utf-8'), timeout=1000)
        except ValueError as e:
            raise e              

    def close_socket(self):
        """Close robot and sensor connections properly"""
        if self.ser:
            self.ser.close()
        if self.dev:
            usb.util.release_interface(self.dev, 0)
        self.send("end")

    def recv(self, bufsize=255):
        """Read data from robot TCP socket"""
        response = None
        while response is None:
            try:
                response = self._socket.recv(bufsize).decode()
            except socket.timeout:
                response = "timeout"
            except Exception as e:
                raise e
            if response:
                if "\r" in response:
                    parts = response.split("\r")
                    # Return the line that includes 'done' if found
                    return next((r for r in parts if "done" in r), parts[0])
                response = None

    def send(self, cmd):
        """Send a command to the robot via TCP"""
        cmd += "\r"
        bytes_sent = self._socket.send(cmd.encode())
        return 0 if len(cmd) == bytes_sent else -1

    def stop(self):
        """Send stop command to robot"""
        self.send("stop")

    def get_wind(self, data):
        """Get wind sensor data from serial and update `data` list"""
        try:                    
            self.ser.reset_input_buffer()
            read = self.ser.readline()
            if read:
                read = read.decode(errors="ignore").strip()
                values = read.split()
                data[0] = values[5]  # e.g., wind direction U
                data[1] = values[7]  # e.g., wind direction V
                data[2] = values[9]  # e.g., wind direction W
                data[3] = values[11]  # Temperature
            return data
        except Exception:
            return data

    def get_other(self, stop_event):
        """Read continuously from CO2 USB sensor in a background thread"""
        read_values = b""
        while not stop_event.is_set():
            try:
                if self.dev is None:
                    raise ValueError("error")
                reading = self.dev.read(0x86, 64, timeout=5000)
                read_values += bytes(reading)
                if b'\n' in read_values:
                    line, read_values = read_values.split(b'\n', 1)
                    line_list = line.decode('utf-8').split('\t')
                    try:
                        self.co2_data = [
                            line_list[2],   # CO2
                            line_list[3],  # H2O
                            line_list[4],  # Pressure
                            line_list[5],  # Temp
                        ]
                    except:
                        self.co2_data = ["Error"] * 4
            except (usb.core.USBError, ValueError):
                self.dev = usb.core.find(idVendor=0x1509, idProduct=0x0A02)
                if self.dev:
                    self.dev.set_configuration()
                self.co2_data = ["Error"] * 4
    
    def acquisition(self, start):
        """Handle sensor data acquisition based on time interval"""
        response = self.recv()
        elapsed = time.time() - start
        if ("posx" in response) and elapsed >= (1/self.freq):
            now = datetime.now()
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S') + f".{int(now.microsecond/10000):02d}" #convert microsecond to centisecond
            start = time.time()
            pos = response.split(",")
            position_z = pos[3]

            data = ["Error"] * 8
            if self.temp or self.wind:
                data = self.get_wind(data)
            if self.hum or self.co2 or self.pres or self.temp2:
                data[4:] = self.co2_data

            self.write_on_file(timestamp, position_z, data)
        return response, start

    def goto(self, pos):
        """Go to Cartesian position and wait for completion"""
        msg = "goto," + ",".join(map(str, pos))
        self.send(msg)
        response = None
        while response != "goto,done":
            response = self.recv()

    def sgoto(self, pos):
        """Go slowly to Cartesian position and wait for completion
        'sgoto' = 'slow goto' (slower for measure)"""
        msg = "sgoto," + ",".join(map(str, pos))
        self.send(msg)
        response = None
        start = time.time()
        while response != "sgoto,done":
            response, start = self.acquisition(start)

    def gotoj(self, pos):
        """Go to joint position and wait for completion"""
        msg = "gotoj," + ",".join(map(str, pos))
        self.send(msg)
        response = None
        while response != "gotoj,done":
            response = self.recv()

    def sgotoj(self, pos):
        """
        Go to joint position slowly and wait for completion.
        'sgotoj' = 'slow gotoj' (slower for measure)
        """
        msg = "sgotoj," + ",".join(map(str, pos))
        self.send(msg)
        response = None
        start = time.time()
        while response != "sgotoj,done":
            response, start = self.acquisition(start)

    def get_current_posx(self):
        """Ask current Cartesian position of the tool"""
        self.send("get_current_posx")
        response = ""
        while "posx" not in response:
            response = self.recv()
        response = response.split(",")
        posx = list(map(float, response[1:-1]))
        sol_space = response[-1]
        return posx

    def write_on_file(self, timestamp, position_z, data):
        """Save acquired data to CSV"""
        row = [timestamp, position_z, self.nb_actual_field]
        if self.wind:
            row.extend(data[0:3])
        if self.temp:
            row.append(data[3])
        if self.co2:
            row.append(data[4])
        if self.hum:
            row.append(data[5])
        if self.pres:
            row.append(data[6])
        if self.temp2:
            row.append(data[7])
        try:
            with open(self.filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)
        except IOError:
            pass

    def find_start_pos(self, distance):
        """Find the starting joint position that corresponds to a TY close to 'distance'"""
        with open(self.csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            column_names = next(reader)
            try:
                index_tx = column_names.index('TY')
            except ValueError:
                exit()

            start_field = []
            for line in reader:
                try:
                    tx_val = float(line[index_tx])
                    if abs(tx_val - distance) <= 50:
                        start_field = list(map(float, line[:6]))
                except (ValueError, IndexError):
                    continue
            return start_field if start_field else exit()


    def up_down_field(self, mode, start_field, ground_level, nb_measures, callback=None):
        """
        Perform up/down movement in the field and acquire sensor data.
        'mode' can be "Continuous" or "Discontinuous"
        """
        # Start background thread for continuous CO2 reading
        stop_co2_thread = threading.Event()
        co2_thread = threading.Thread(target=self.get_other, args=(stop_co2_thread,))
        co2_thread.start()
        self.co2_data = ["Error"] * 4

        interval = ground_level / nb_measures
        start_pos = [start_field[0], 0, 10, 0, 80, 180]
        self.gotoj(start_pos)

        if mode == "Continuous":
            self.send("stream_pos")

        time.sleep(1)

        self.sgotoj(start_field)
        pos_field = self.get_current_posx()
        sign = 1
        for _ in range(2):  # up and down
            sign *= -1
            for _ in range(nb_measures):
                pos_field[2] += interval * sign
                self.sgoto(pos_field)
                if mode == "Discontinuous":
                    self.acquisition(0)
        self.sgotoj(start_pos)
        if callback:
            callback()

        if mode == "Continuous":
            self.send("stop_stream")

        # Stop CO2 reading thread
        stop_co2_thread.set()
        co2_thread.join()
        if self.dev:
            usb.util.release_interface(self.dev, 0)
