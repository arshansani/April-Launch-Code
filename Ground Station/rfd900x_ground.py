import time
import logging
from pymavlink import mavutil
from data_writer_ground import get_next_filename, write_data_to_csv
from flask import Flask, jsonify, request
from threading import Thread

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

app = Flask(__name__)

# Configure the serial connection
serial_port = 'COM6'  # Replace with the appropriate COM port
baud_rate = 57600  # Set the baud rate according to your RFD900x configuration

# Create a MAVLink connection
mav = mavutil.mavlink_connection(serial_port, baud=baud_rate)

# Get the next file name
filename = get_next_filename("data_{}.csv")

# Write the header to the CSV file
header = ['Timestamp', 'Accelerometer X (m/s^2)', 'Accelerometer Y (m/s^2)', 'Accelerometer Z (m/s^2)', 'Gyroscope X (rad/s)', 'Gyroscope Y (rad/s)', 'Gyroscope Z (rad/s)', 'Humidity (%)', 'Pressure (mbar)', 'Temperature from Humidity (C)', 'Temperature from Pressure (C)', 'Thermocouple Temperature (C)']
write_data_to_csv(dict(zip(header, header)), filename)

# Initialize variables to store the received data
data = {}
received_vectors = 0

# Global variables to store the most recent data and heartbeat status
most_recent_data = {}
most_recent_heartbeat_status = "OK"

# Callback function to handle received messages
def handle_message(msg):
    global most_recent_data, data, received_vectors

    if msg.get_type() == 'HEARTBEAT':
        logging.debug("Heartbeat received!")
        logging.debug("Message contents: %s", msg.to_dict())
    elif msg.get_type() == 'DEBUG_VECT':
        logging.info("Debug vector received!")
        logging.debug("Message contents: %s", msg.to_dict())

        # Extract the relevant data from the message
        # Vectors can only contain 3 values, so we need to keep track of which vector we are receiving
        if received_vectors == 0:
            data['Timestamp'] = msg.time_usec
            data['Accelerometer_X'] = msg.x
            data['Accelerometer_Y'] = msg.y
            data['Accelerometer_Z'] = msg.z
        elif received_vectors == 1:
            data['Gyroscope_X'] = msg.x
            data['Gyroscope_Y'] = msg.y
            data['Gyroscope_Z'] = msg.z
        elif received_vectors == 2:
            data['Humidity'] = msg.x
            data['Pressure'] = msg.y
            data['Temperature_Humidity'] = msg.z
        elif received_vectors == 3:
            data['Temperature_Pressure'] = msg.x
            data['Temperature_Thermocouple'] = msg.y
            data['Latitude'] = msg.z
        elif received_vectors == 4:
            data['Longitude'] = msg.x
            data['Altitude'] = msg.y
            data['Speed'] = msg.z
        elif received_vectors == 5:
            data['Heading'] = msg.x

        received_vectors += 1

        # Check if all four vectors have been received
        if received_vectors == 6:
            # Record the assembled data to CSV file
            logging.info(f"Data received: {data}")
            write_data_to_csv(data, filename)
            received_vectors = 0
            
            # Update the most recent data
            most_recent_data = data

            # Reset the data dictionary for the next set of vectors
            data = {}

    else:
        logging.warning("Unknown message type received: %s", msg.get_type())

# Main loop
def main():
    global most_recent_data, most_recent_heartbeat_status

    heartbeat_timeout = 5  # Heartbeat timeout in seconds
    last_heartbeat_time = time.time()
    heartbeat_warning_timeout = 10  # Heartbeat warning timeout in seconds
    last_heartbeat_warning_time = time.time()

    while True:
        try:
            # Check if a message has been received
            msg = mav.recv_match(blocking=False)
            if msg:
                if msg.get_type() == 'HEARTBEAT':
                    last_heartbeat_time = time.time()
                    most_recent_heartbeat_status = "OK"
                handle_message(msg)
            else:
                logging.debug("No message received.")

            # Check for heartbeat timeout
            current_time = time.time()
            if current_time - last_heartbeat_time > heartbeat_timeout:
                # Handle the heartbeat timeout condition here
                # For example, you can reconnect, send a request for heartbeat, or perform any other necessary actions
                most_recent_heartbeat_status = "TIMEOUT"
                if current_time - last_heartbeat_warning_time > heartbeat_warning_timeout:
                    logging.info(f"Heartbeat timeout! No heartbeat received for {round(current_time-last_heartbeat_time, 0)} seconds.")
                    last_heartbeat_warning_time = current_time

        except KeyboardInterrupt:
            logging.info("Keyboard interrupt received. Exiting...")
            break

        except Exception as e:
            logging.error(f"Error: {e}")

        # Wait for a short interval before the next iteration
        time.sleep(0.001)

    # Close the MAVLink connection when done
    mav.close()

# API route to get the most recent data
@app.route('/api/data', methods=['GET'])
def get_most_recent_data():
    global most_recent_data, most_recent_heartbeat_status
    response_data = {
        'Timestamp': most_recent_data.get('Timestamp', 0),
        'Accelerometer_X': most_recent_data.get('Accelerometer_X', 0),
        'Accelerometer_Y': most_recent_data.get('Accelerometer_Y', 0),
        'Accelerometer_Z': most_recent_data.get('Accelerometer_Z', 0),
        'Gyroscope_X': most_recent_data.get('Gyroscope_X', 0),
        'Gyroscope_Y': most_recent_data.get('Gyroscope_Y', 0),
        'Gyroscope_Z': most_recent_data.get('Gyroscope_Z', 0),
        'Humidity': most_recent_data.get('Humidity', 0),
        'Pressure': most_recent_data.get('Pressure', 0),
        'Temperature_Humidity': most_recent_data.get('Temperature_Humidity', 0),
        'Temperature_Pressure': most_recent_data.get('Temperature_Pressure', 0),
        'Temperature_Thermocouple': most_recent_data.get('Temperature_Thermocouple', 0),
        'Latitude': most_recent_data.get('Latitude', 0),
        'Longitude': most_recent_data.get('Longitude', 0),
        'Altitude': most_recent_data.get('Altitude', 0),
        'Speed': most_recent_data.get('Speed', 0),
        'Heading': most_recent_data.get('Heading', 0),
        'Heartbeat_Status': most_recent_heartbeat_status
    }
    logging.info(f"Data Sent: {response_data}")
    return response_data

def run_flask_app():
    app.run()

if __name__ == "__main__":
    # Start the Flask app in a separate thread
    flask_thread = Thread(target=run_flask_app)
    flask_thread.start()

    main()