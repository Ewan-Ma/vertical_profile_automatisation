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
import queue

class TCPClient():
    """Class for managing the TCP connection with the robot and sensors connection"""

    def __init__(self, ip, port, wind, com, vendor, product, temp, hum, co2, pres, intern_co2):
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
        self.intern_co2 = intern_co2

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
            self.ser.write(b'\x03hide S\rhide D\rhide Pitch\rhide Roll\routputrate 20\rexit\r')
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

    def get_data(self, stop_event):
        read_values = b""
        while not stop_event.is_set():

            """Read continuously wind sensor data from serial and update `data` list in a background threadGet"""
            try:
                read = self.ser.readline()
                if read:
                    read = read.decode(errors="ignore").strip()
                    values = read.split()
                    self.wind_data = [values[1], # e.g., wind direction U
                            values[3], # e.g., wind direction V
                            values[5], # e.g., wind direction W
                            values[13], # Magnetic
                            values[7], # Temperature
                            values[11]] # Pressure
            except Exception:
                self.wind_data = ["Error"] * 6

            """Read continuously from CO2 USB sensor in a background thread"""
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
                            line_list[5],  # Temperature
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
        timea = time.time()
        elapsed = timea - start
        if ("posx" in response) and elapsed >= (1/self.freq):
            now = datetime.now()
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S') + f".{int(now.microsecond/10000):02d}" #convert microsecond to centisecond
            start = timea
            pos = response.split(",")
            position_z = pos[3]

            row = [timestamp, position_z, self.nb_actual_field]
            
            if self.wind:
                row.extend(self.wind_data[0:4])
            if self.temp:
                row.append(self.wind_data[4])
            if self.pres:
                row.append(self.wind_data[5])
            if self.co2:
                row.append(self.co2_data[0])
            if self.hum:
                row.append(self.co2_data[1])
            if self.intern_co2:
                row.extend(self.co2_data[2:4])
            self.data_queue.put(row)

        return response, start
    
    def csv_writer_thread(self):
        buffer = []
        while not self.stop_writing.is_set() or not self.data_queue.empty():
            try:
                item = self.data_queue.get(timeout=0.1)
                buffer.append(item)
            except queue.Empty:
                pass

            if len(buffer) >= 100:
                self.flush_to_csv(buffer)
                buffer.clear()

        # final flush if necessary
        if buffer:
            self.flush_to_csv(buffer)

    def flush_to_csv(self, rows):
        try:
            with open(self.filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(rows)
        except IOError:
            pass            

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
        stop_data_thread = threading.Event()
        data_thread = threading.Thread(target=self.get_data, args=(stop_data_thread,))
        data_thread.start()
        self.wind_data = ["Error"] * 6
        self.co2_data = ["Error"] * 4

        # Start background thread for writing in csv file
        self.data_queue = queue.Queue()
        self.stop_writing = threading.Event()
        self.writer_thread = threading.Thread(target=self.csv_writer_thread, daemon=True)
        self.writer_thread.start()

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
        stop_data_thread.set()
        data_thread.join()
        if self.dev:
            usb.util.release_interface(self.dev, 0)

        # Stop csv file writing thread
        self.stop_writing.set()
        self.writer_thread.join()
