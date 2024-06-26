import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import ImageDraw
import time
import datetime
import messagebox
from tkintermapview import TkinterMapView
import requests
from queue import Queue
from threading import Thread
import math

_URL = "http://localhost:5000/api/data"
data_queue = Queue()

def api_call_thread():
    # Thread function to make API calls and retrieve data.
    while True:
        try:
            response = requests.get(_URL)
            if response.status_code == 200:
                data = response.json()
                print(f"Data retrieved: {data}")
                data_queue.put(data)
            else:
                print(f"Error retrieving data from API. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving data from API: {str(e)}")
        
        time.sleep(1)  # Adjust the delay between API calls as needed

class TelemetryUI:
    def __init__(self, master):
        # Initialize the TelemetryUI class.
    
        # Initialize constants
        self.time_initial = time.time() # initial time
        self.ground_station = [31.854900, -97.729055]  # Launch location coordinates

        # Initialize data variables
        self.mission_duration = 0 # initial mission duration
        self.data_time = []  # Initialize list to store time data for plotting
        self.data_time.append(self.mission_duration)
        self.acceleration = (0,0,0)
        self.gyroscope = (0,0,0)
        self.humidity = 0
        self.pressure = 0
        self.temperature_humidity = 0
        self.temperature_pressure = 0
        self.temperature_thermocouple = 0
        self.coordinates = self.ground_station  # Initial coordinates
        self.altitude = 0  # Initial altitude
        self.altitude_data = []  # Initialize list to store altitude data for plotting
        self.altitude_data.append(self.altitude)
        self.speed = 0
        self.heading = 0
        self.heartbeat = "TIMEOUT"
        self.rssi = 0

        # Initialize variables
        self.polling_rate = 1000  # Polling rate in ms
        self.blink_event = None
        self.is_blinking = False

        # Create the UI
        self.master = master
        master.title("Telemetry UI")
        master.state('zoomed')  # Maximize the window

        # Create widgets
        self.polling_rate_label = ttk.Label(master, text="Polling Rate (Seconds):")
        self.polling_rate_entry = ttk.Entry(master)
        self.polling_rate_value = ttk.Label(master, text=str(self.polling_rate/1000))
        self.update_button = ttk.Button(master, text="Update", command=self.update_polling_rate)
        self.raw_data_label = ttk.Label(master, text="Raw Data:")
        self.raw_data_text = tk.Text(master, height=14, width=50)
        self.map_label = ttk.Label(master, text="Map:")
        self.map_frame = TkinterMapView(master, width=800, height=600, corner_radius=0)
        self.altitude_label = ttk.Label(master, text="Altitude Log:")
        self.altitude_figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.altitude_plot = self.altitude_figure.add_subplot(111)
        self.altitude_canvas = FigureCanvasTkAgg(self.altitude_figure, master)
        self.heartbeat_label = ttk.Label(master, text="Heartbeat Status:")
        self.heartbeat_status = ttk.Label(master, text="", font=("Arial", 14))
        self.heartbeat_indicator = ttk.Label(master, text="●", font=("Arial", 24, "bold"))
        self.cutdown_button = tk.Button(master, text="CUTDOWN", command=self.confirm_cutdown, bg="red", fg="white", font=("Arial", 14, "bold"))
        self.mission_status_label = ttk.Label(master, text="MISSION IN PROGRESS", foreground="green")
        self.compass_widget = CompassWidget(master, size=200, max_speed=50)
        self.compass_label = ttk.Label(master, text="Heading:")
        self.velocity_label = ttk.Label(master, text="Velocity: 0 m/s")
        self.heading_label = ttk.Label(master, text="Heading: 0°")

        # Layout widgets
        self.polling_rate_label.grid(row=0, column=0, sticky="w", padx=3, pady=10)
        self.polling_rate_entry.grid(row=0, column=1, padx=5)
        self.update_button.grid(row=0, column=2, padx=5)
        self.polling_rate_value.grid(row=0, column=3, sticky="w")
        self.raw_data_label.grid(row=1, column=0, sticky="w", pady=(20, 0), padx=3)
        self.raw_data_text.grid(row=2, column=0, columnspan=4, sticky="n", padx=5)
        self.heartbeat_label.grid(row=5, column=0, sticky="w", padx=3, pady=(10, 0))
        self.heartbeat_status.grid(row=5, column=1, sticky="w", pady=(10, 0))
        self.heartbeat_indicator.grid(row=5, column=2, sticky="w", pady=(10, 0), padx=(10, 0))
        self.cutdown_button.grid(row=6, column=1, padx=5, pady=(10, 0), sticky="s")
        self.mission_status_label.grid(row=7, column=1, padx=5, pady=(0, 10), sticky="n")
        self.map_label.grid(row=0, column=4, sticky="w", padx=(20, 0))
        self.map_frame.grid(row=1, column=4, rowspan=4, sticky="nsew", padx=(20, 0))
        self.altitude_label.grid(row=5, column=4, sticky="w", padx=(20, 0))
        self.altitude_canvas.get_tk_widget().grid(row=6, column=4, sticky="nsew", padx=(20, 0))
        self.compass_widget.grid(row=4, column=0, columnspan=2, padx=5, pady=(0, 10))
        self.compass_label.grid(row=3, column=0, sticky="w", padx=3, pady=(10, 0))
        self.velocity_label.grid(row=4, column=3, sticky="w", padx=(10, 0))
        self.heading_label.grid(row=4, column=2, sticky="w", padx=(10, 0))
        
        # Configure grid weights
        master.grid_rowconfigure(2, weight=1)
        master.grid_rowconfigure(6, weight=1)
        master.grid_columnconfigure(4, weight=1)

        # Create the map
        self.create_map()

        # Start the background thread for API calls
        api_thread = Thread(target=api_call_thread, daemon=True)
        api_thread.start()

        # Start periodic updates
        self.poll_data()

    def pull_data(self):
        # Pull data from the data queue and update data variables.
        while not data_queue.empty():
            data = data_queue.get()

            self.mission_duration = (time.time() - self.time_initial) / 60
            self.data_time.append(self.mission_duration)
            self.acceleration = (round(data["Accelerometer_X"],2), round(data["Accelerometer_Y"],2), round(data["Accelerometer_Z"],2))
            self.gyroscope = (round(data["Gyroscope_X"],2), round(data["Gyroscope_Y"],2), round(data["Gyroscope_Z"],2))
            self.humidity = round(data["Humidity"],0)
            self.pressure = round(data["Pressure"],0)
            self.temperature_humidity = round(data["Temperature_Humidity"],0)
            self.temperature_pressure = round(data["Temperature_Pressure"],0)
            self.temperature_thermocouple = round(data["Temperature_Thermocouple"],0)
            self.coordinates = (round(data["Latitude"],6), round(data["Longitude"],6))
            self.altitude = round(data["Altitude"] * 3.28084,0)
            self.altitude_data.append(self.altitude)
            self.speed = round(data["Speed"],2)
            self.heading = round(data["Heading"],2)
            self.heartbeat = data["Heartbeat_Status"]
            self.rssi = data["RSSI"]

        # Implement the logic to pull data from the rfd900x_ground.py
        # Generate random data for demonstration purposes
        '''
        self.mission_duration = (time.time() - self.time_initial) / 60
        self.data_time.append(self.mission_duration)
        self.acceleration = (round(random.uniform(-10.0, 10.0),2), round(random.uniform(-10.0, 10.0),2), round(random.uniform(-10.0, 10.0),2))
        self.gyroscope = (round(random.uniform(-5.0, 5.0),2), round(random.uniform(-5.0, 5.0),2), round(random.uniform(-5.0, 5.0),2))
        self.humidity = random.randint(0, 100)
        self.pressure = random.randint(900, 1100)
        self.temperature_humidity = random.uniform(20.0, 30.0)
        self.temperature_pressure = random.uniform(20.0, 30.0)
        self.temperature_thermocouple = random.uniform(-50.0, 30.0)
        self.coordinates = (random.uniform(28.0, 34.0), random.uniform(-104.0, -96.0))
        self.altitude = random.randint(0, 1000)
        self.altitude_data.append(self.altitude)

        self.heartbeat = "TIMEOUT"
        '''

    def update_raw_display(self):
        # Update the raw data display with the latest data.
        self.raw_data_text.delete(1.0, tk.END)
        self.raw_data_text.insert(tk.END, f"Mission Duration (mins): {round(self.mission_duration,1)}\n")
        self.raw_data_text.insert(tk.END, f"Time: {datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.raw_data_text.insert(tk.END, f"RSSI: {self.rssi} dBi\n")
        self.raw_data_text.insert(tk.END, f"Acceleration: {self.acceleration}\n")
        self.raw_data_text.insert(tk.END, f"Gyroscope: {self.gyroscope}\n")
        self.raw_data_text.insert(tk.END, f"Humidity (Internal): {self.humidity}%\n")
        self.raw_data_text.insert(tk.END, f"Pressure (Internal): {self.pressure} mbar\n")
        self.raw_data_text.insert(tk.END, f"Temperature (Internal): {round(self.temperature_humidity,2)} C\n")
        self.raw_data_text.insert(tk.END, f"Temperature (External): {round(self.temperature_thermocouple,2)} C\n")
        self.raw_data_text.insert(tk.END, f"Coordinates: {round(self.coordinates[0],6)}, {round(self.coordinates[1],6)}\n")
        self.raw_data_text.insert(tk.END, f"Altitude: {round(self.altitude,0)} ft\n")
        self.raw_data_text.insert(tk.END, f"Speed: {round(self.speed,2)} m/s\n")
        self.raw_data_text.insert(tk.END, f"Heading: {round(self.heading,2)}°\n")
    
    def update_map_display(self):
        # Update the map display with the latest marker positions.
        try:
            # Update the marker positions
            if self.ground_station_marker is not None:
                self.ground_station_marker.set_position(self.ground_station[0], self.ground_station[1])
            if self.balloon_marker is not None:
                self.balloon_marker.set_position(self.coordinates[0], self.coordinates[1])
            print("Map markers updated")
        except Exception as e:
            print(f"Error updating map display: {str(e)}")

    def update_altitude_log_display(self):
        # Update the altitude log display with the latest altitude data.
        # Clear the previous plot
        self.altitude_plot.clear()

        # Plot the altitude data
        self.altitude_plot.plot(self.data_time, self.altitude_data)
        self.altitude_plot.set_xlabel('Mission Time (m)')
        self.altitude_plot.set_ylabel('Altitude (ft)')
        self.altitude_plot.set_title('Altitude Log')

        # Refresh the altitude canvas
        self.altitude_canvas.draw()

    def update_polling_rate(self):
        # Update the polling rate based on the user input.
        try:
            self.polling_rate = int(self.polling_rate_entry.get())*1000
            self.polling_rate_value.config(text=str(self.polling_rate / 1000))
        except ValueError:
            pass

    def create_map(self):
        # Create the map with markers for the ground station and balloon.
        try:
            # Calculate the center coordinates between ground_station and coordinates
            center_lat = (self.ground_station[0] + self.coordinates[0]) / 2
            center_lon = (self.ground_station[1] + self.coordinates[1]) / 2
            
            # Set the map center and zoom level
            self.map_frame.set_position(center_lat, center_lon)
            self.map_frame.set_zoom(10)
            print("Map created")
            
            # Add markers for ground_station and coordinates
            self.ground_station_marker = self.map_frame.set_marker(self.ground_station[0], self.ground_station[1], text='Ground Station', marker_color_circle='red')
            self.balloon_marker = self.map_frame.set_marker(self.coordinates[0], self.coordinates[1], text='Balloon', marker_color_circle='blue')
            print("Markers added to the map")
        except Exception as e:
            print(f"Error creating map: {str(e)}")

    def poll_data(self):
        # Poll data and update displays periodically.

        # Update data
        self.pull_data()

        # Update displays
        self.update_raw_display()
        self.update_map_display()
        self.update_altitude_log_display()
        self.update_heartbeat_display(self.heartbeat)
        self.compass_widget.update_compass(self.heading, self.speed)
        self.heading_label.config(text=f"Heading: {self.heading}°")
        self.velocity_label.config(text=f"Velocity: {self.speed} m/s")

        # Schedule the next update based on the polling rate
        self.master.after(self.polling_rate, self.poll_data)

    def confirm_cutdown(self):
        # Confirm cutdown action with a dialog box.
        confirm = messagebox.askyesno("Warning: Confirm Cutdown", "Are you sure you want to initiate the cutdown?")
        if confirm == True:
            self.initiate_cutdown()

    def initiate_cutdown(self):
        # Implement the logic to initiate the cutdown
        response = requests.post('http://localhost:5000/api/cutdown')
        print(response.text)
        # Add your cutdown implementation here
        self.mission_status_label.config(text="MISSION TERMINATED", foreground="red")

    def update_heartbeat_display(self, status):
        if status == "OK":
            self.heartbeat_status.config(text=status, foreground="green")
            self.heartbeat_indicator.config(foreground="green")
            self.heartbeat_indicator.after_cancel(self.blink_event)
            self.is_blinking = False
        else:
            self.heartbeat_status.config(text=status, foreground="red")
            if not self.is_blinking:
                self.is_blinking = True
                self.blink_heartbeat_indicator()

    def blink_heartbeat_indicator(self):
        if self.is_blinking:
            current_color = self.heartbeat_indicator.cget("foreground")
            if str(current_color) == "red":
                self.heartbeat_indicator.config(foreground="gray95")
            else:
                self.heartbeat_indicator.config(foreground="red")
            self.blink_event = self.heartbeat_indicator.after(500, self.blink_heartbeat_indicator)

class CompassWidget(tk.Canvas):
    def __init__(self, master, size=200, max_speed=50, *args, **kwargs):
        super().__init__(master, width=size, height=size, *args, **kwargs)
        self.size = size
        self.max_speed = max_speed
        self.heading = 0
        self.speed = 0

    def update_compass(self, heading, speed):
        self.heading = heading
        self.speed = speed
        self.draw_compass()

    def draw_compass(self):
        self.delete("all")
        center_x = self.size // 2
        center_y = self.size // 2
        radius = self.size // 2 - 10

        # Draw compass circle
        self.create_oval(10, 10, self.size - 10, self.size - 10, outline="black", width=2)
        self.create_oval(center_x - 5, center_y - 5, center_x + 5, center_y + 5, fill="black")

        # Draw cardinal directions
        self.create_text(center_x, 20, text="N", font=("Arial", 12, "bold"))
        self.create_text(center_x, self.size - 20, text="S", font=("Arial", 12, "bold"))
        self.create_text(20, center_y, text="W", font=("Arial", 12, "bold"))
        self.create_text(self.size - 20, center_y, text="E", font=("Arial", 12, "bold"))

        # Set minimum arrow length
        min_arrow_length = 20

        # Calculate arrow length based on velocity
        arrow_length = min_arrow_length + (self.speed / self.max_speed) * (radius - min_arrow_length)

        # Calculate arrow end point
        arrow_end_x = center_x + arrow_length * math.sin(math.radians(self.heading))
        arrow_end_y = center_y - arrow_length * math.cos(math.radians(self.heading))

        # Draw velocity arrow
        self.create_line(center_x, center_y, arrow_end_x, arrow_end_y, fill="red", arrow="last", width=4)

root = tk.Tk()
ui = TelemetryUI(root)
root.mainloop()