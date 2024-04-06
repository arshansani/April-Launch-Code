import time
import logging
from pymavlink import mavutil
from data_writer_ground import get_next_filename, write_data_to_csv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

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

# Callback function to handle received messages
def handle_message(msg):
    global data, received_vectors

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
            data['Accelerometer X (m/s^2)'] = msg.x
            data['Accelerometer Y (m/s^2)'] = msg.y
            data['Accelerometer Z (m/s^2)'] = msg.z
        elif received_vectors == 1:
            data['Gyroscope X (rad/s)'] = msg.x
            data['Gyroscope Y (rad/s)'] = msg.y
            data['Gyroscope Z (rad/s)'] = msg.z
        elif received_vectors == 2:
            data['Humidity (%)'] = msg.x
            data['Pressure (mbar)'] = msg.y
            data['Temperature from Humidity (C)'] = msg.z
        elif received_vectors == 3:
            data['Temperature from Pressure (C)'] = msg.x
            data['Thermocouple Temperature (C)'] = msg.y

        received_vectors += 1

        # Check if all four vectors have been received
        if received_vectors == 4:
            # Record the assembled data to CSV file
            logging.info(f"Data received: {data}")
            write_data_to_csv(data, filename)
            received_vectors = 0
            
            # Reset the data dictionary for the next set of vectors
            data = {}

    else:
        logging.warning("Unknown message type received: %s", msg.get_type())

# Main loop
def main():
    heartbeat_timeout = 5  # Heartbeat timeout in seconds
    last_heartbeat_time = time.time()
    heartbeat_warning_timeout = 10  # Heartbeat warning timeout in seconds
    last_heartbeat_warning = time.time()
    heartbeat_status = "OK"

    while True:
        try:
            # Check if a message has been received
            msg = mav.recv_match(blocking=False)
            if msg:
                if msg.get_type() == 'HEARTBEAT':
                    last_heartbeat_time = time.time()
                    heartbeat_status = "OK"
                handle_message(msg)
            else:
                logging.debug("No message received.")

            # Check for heartbeat timeout
            current_time = time.time()
            if current_time - last_heartbeat_time > heartbeat_timeout:
                # Handle the heartbeat timeout condition here
                # For example, you can reconnect, send a request for heartbeat, or perform any other necessary actions
                heartbeat_status = "TIMEOUT"
                if current_time - last_heartbeat_warning > heartbeat_warning_timeout:
                    logging.info(f"Heartbeat timeout! No heartbeat received for {round(current_time-last_heartbeat_time, 0)} seconds.")
                    last_heartbeat_warning = current_time

        except KeyboardInterrupt:
            logging.info("Keyboard interrupt received. Exiting...")
            break

        except Exception as e:
            logging.error(f"Error: {e}")

        # Wait for a short interval before the next iteration
        time.sleep(0.001)

    # Close the MAVLink connection when done
    mav.close()

if __name__ == "__main__":
    main()