import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import folium
import io
import base64
from PIL import Image, ImageTk, ImageDraw
import time
import datetime
import random
import messagebox
import tkinterweb
import webbrowser
from tkintermapview import TkinterMapView

class TelemetryUI:
    def __init__(self, master):
        # Initialize variables
        self.time_initial = time.time() # initial time
        self.ground_station = [30.2672, -97.7431]  # Austin, TX coordinates
        self.coordinates = self.ground_station  # Initial coordinates
        self.polling_rate = 1000  # Polling rate in ms
        self.altitude_data = []  # List to store altitude data for plotting
        self.data_time = []  # List to store time data for plotting

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
        self.heartbeat_status = ttk.Label(master, text="OK", foreground="green")
        self.cutdown_button = tk.Button(master, text="CUTDOWN", command=self.confirm_cutdown, bg="red", fg="white", font=("Arial", 14, "bold"))
        self.mission_status_label = ttk.Label(master, text="MISSION IN PROGRESS", foreground="green")
        
        # Layout widgets
        self.polling_rate_label.grid(row=0, column=0, sticky="w", padx=3, pady=10)
        self.polling_rate_entry.grid(row=0, column=1, padx=5)
        self.update_button.grid(row=0, column=2, padx=5)
        self.polling_rate_value.grid(row=0, column=3, sticky="w")
        self.raw_data_label.grid(row=1, column=0, sticky="w", pady=(20, 0), padx=3)
        self.raw_data_text.grid(row=2, column=0, columnspan=4, sticky="n", padx=5)
        self.heartbeat_label.grid(row=3, column=0, sticky="w", padx=3, pady=(10, 0))
        self.heartbeat_status.grid(row=3, column=1, sticky="w", pady=(10, 0))
        self.cutdown_button.grid(row=6, column=1, padx=5, pady=(10, 0), sticky="s")
        self.mission_status_label.grid(row=7, column=1, padx=5, pady=(0, 10), sticky="n")
        self.map_label.grid(row=0, column=4, sticky="w", padx=(20, 0))
        self.map_frame.grid(row=1, column=4, rowspan=4, sticky="nsew", padx=(20, 0))
        self.altitude_label.grid(row=5, column=4, sticky="w", padx=(20, 0))
        self.altitude_canvas.get_tk_widget().grid(row=6, column=4, sticky="nsew", padx=(20, 0))

        # Configure grid weights
        master.grid_rowconfigure(2, weight=1)
        master.grid_rowconfigure(6, weight=1)
        master.grid_columnconfigure(4, weight=1)

        # Create the map
        self.create_map()

        # Start periodic updates
        self.poll_data()

    def pull_data(self):
        # Implement the logic to pull data from the rfd900x_ground.py
        # Generate random data for demonstration purposes
        self.mission_duration = (time.time() - self.time_initial) / 60
        self.data_time.append(self.mission_duration)
        self.acceleration = (round(random.uniform(-10.0, 10.0),2), round(random.uniform(-10.0, 10.0),2), round(random.uniform(-10.0, 10.0),2))
        self.gyroscope = (round(random.uniform(-5.0, 5.0),2), round(random.uniform(-5.0, 5.0),2), round(random.uniform(-5.0, 5.0),2))
        self.humidity = random.randint(0, 100)
        self.pressure = random.randint(900, 1100)
        self.temperature_humidity = random.uniform(20.0, 30.0)
        self.temperature_pressure = random.uniform(20.0, 30.0)
        self.temperature_external = random.uniform(-50.0, 30.0)
        self.coordinates = (random.uniform(28.0, 34.0), random.uniform(-104.0, -96.0))
        self.altitude = random.randint(0, 1000)
        self.altitude_data.append(self.altitude)

        self.heartbeat = "OK"

    def update_raw_display(self):
        # ground_station data for demonstration
        self.raw_data_text.delete(1.0, tk.END)
        self.raw_data_text.insert(tk.END, f"Mission Duration (mins): {round(self.mission_duration,1)}\n")
        self.raw_data_text.insert(tk.END, f"Time: {datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.raw_data_text.insert(tk.END, f"Acceleration: X: {self.acceleration}\n")
        self.raw_data_text.insert(tk.END, f"Gyroscope: {self.gyroscope}\n")
        self.raw_data_text.insert(tk.END, f"Humidity (Internal): {self.humidity}%\n")
        self.raw_data_text.insert(tk.END, f"Pressure (Internal): {self.pressure} mbar\n")
        self.raw_data_text.insert(tk.END, f"Temperature (Internal): {round(self.temperature_humidity,2)} C\n")
        self.raw_data_text.insert(tk.END, f"Temperature (External): {round(self.temperature_external,2)} C\n")
        self.raw_data_text.insert(tk.END, f"Coordinates: {round(self.coordinates[0],6)}, {round(self.coordinates[1],6)}\n")
        self.raw_data_text.insert(tk.END, f"Altitude: {round(self.altitude,6)} ft\n")
    
    def update_map_display(self):
        try:
            # Update the marker positions
            self.map_frame.delete_all_marker()
            self.map_frame.set_marker(self.ground_station[0], self.ground_station[1], text='Ground Station', marker_color_circle='red')
            self.map_frame.set_marker(self.coordinates[0], self.coordinates[1], text='Balloon', marker_color_circle='blue')
            print("Map markers updated")
        except Exception as e:
            print(f"Error updating map display: {str(e)}")

    def update_altitude_log_display(self):
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
        try:
            self.polling_rate = int(self.polling_rate_entry.get())*1000
            self.polling_rate_value.config(text=str(self.polling_rate / 1000))
        except ValueError:
            pass

    def create_map(self):
        try:
            # Calculate the center coordinates between ground_station and coordinates
            center_lat = (self.ground_station[0] + self.coordinates[0]) / 2
            center_lon = (self.ground_station[1] + self.coordinates[1]) / 2
            
            # Set the map center and zoom level
            self.map_frame.set_position(center_lat, center_lon)
            self.map_frame.set_zoom(10)
            print("Map created")
            
            # Add markers for ground_station and coordinates
            self.map_frame.set_marker(self.ground_station[0], self.ground_station[1], text='Ground Station', marker_color_circle='red')
            self.map_frame.set_marker(self.coordinates[0], self.coordinates[1], text='Balloon', marker_color_circle='blue')
            print("Markers added to the map")
        except Exception as e:
            print(f"Error creating map: {str(e)}")

    def calculate_map_coordinates(self, location):
        # Implement the logic to calculate the coordinates on the map based on the location
        # Replace with the appropriate calculations based on the Texas map dimensions and coordinates
        # Example implementation:
        map_width = 800
        map_height = 600
        lat_range = (25.0, 37.0)  # Approximate latitude range of Texas
        lon_range = (-107.0, -93.0)  # Approximate longitude range of Texas

        lat, lon = location
        x = int((lon - lon_range[0]) / (lon_range[1] - lon_range[0]) * map_width)
        y = int((lat_range[1] - lat) / (lat_range[1] - lat_range[0]) * map_height)
        return x, y

    def draw_marker(self, image, x, y, color):
        # Implement the logic to draw a marker on the map image at the specified coordinates
        draw = ImageDraw.Draw(image)
        marker_size = 10
        draw.ellipse((x - marker_size, y - marker_size, x + marker_size, y + marker_size), fill=color)

    def poll_data(self):
        # Update data
        self.pull_data()

        # Update displays
        self.update_raw_display()
        self.update_map_display()
        self.update_altitude_log_display()
        self.update_heartbeat_display(self.heartbeat)

        # Schedule the next update based on the polling rate
        self.master.after(self.polling_rate, self.poll_data)

    def confirm_cutdown(self):
        confirm = messagebox.askyesno("Warning: Confirm Cutdown", "Are you sure you want to initiate the cutdown?")
        if confirm == True:
            self.initiate_cutdown()

    def initiate_cutdown(self):
        # Implement the logic to initiate the cutdown
        print("Cutdown initiated!")
        # Add your cutdown implementation here
        self.mission_status_label.config(text="MISSION TERMINATED", foreground="red")

    def update_heartbeat_display(self, status):
        if status == "OK":
            self.heartbeat_status.config(text=status, foreground="green")
        else:
            self.heartbeat_status.config(text=status, foreground="red")

root = tk.Tk()
ui = TelemetryUI(root)
root.mainloop()