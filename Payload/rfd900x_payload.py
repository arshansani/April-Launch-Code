import time
import random
import logging
import threading
from pymavlink import mavutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Configure the serial connection
serial_port = '/dev/ttyUSB0'  # Replace with the appropriate USB port
baud_rate = 57600  # Set the baud rate according to your RFD900x configuration

# Create a MAVLink connection
mav = mavutil.mavlink_connection(serial_port, baud=baud_rate)

heartbeat_interval = 1  # Interval in seconds for sending heartbeat messages

# Function to send a heartbeat
def send_heartbeat():
    # Create and send a heartbeat message
    heartbeat_msg = mavutil.mavlink.MAVLink_heartbeat_message(
        mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,  # MAV_TYPE
        mavutil.mavlink.MAV_AUTOPILOT_GENERIC,  # Autopilot type
        0,  # MAV_MODE
        0,  # Custom mode
        mavutil.mavlink.MAV_STATE_ACTIVE,  # System status
        2  # MAVLink version (set to 2 for MAVLink 2)
    )

    # Log the contents of the heartbeat message
    logging.debug("Heartbeat Message Contents:")
    logging.debug(f" MAV_TYPE: {heartbeat_msg.type}")
    logging.debug(f" Autopilot: {heartbeat_msg.autopilot}")
    logging.debug(f" Base Mode: {heartbeat_msg.base_mode}")
    logging.debug(f" Custom Mode: {heartbeat_msg.custom_mode}")
    logging.debug(f" System Status: {heartbeat_msg.system_status}")
    logging.debug(f" MAVLink Version: {heartbeat_msg.mavlink_version}")
    
    # Send the heartbeat message
    mav.mav.send(heartbeat_msg)
    logging.info("Heartbeat message sent.")

# Function to send data
def send_data(data):
    timestamp = int(time.time() * 1000) % (2**32)
    data_list = list(data.values())
    num_vectors = (len(data_list) + 2) // 3  # Calculate the number of vectors needed
    
    for i in range(num_vectors):
        start_index = i * 3
        end_index = min(start_index + 3, len(data_list))
        vector_data = data_list[start_index:end_index]

        # Pad the vector with zeros if it has less than 3 elements
        while len(vector_data) < 3:
            vector_data.append(0.0)

        mav.mav.debug_vect_send(
            name=f"Data_Vector_{i}".encode(),
            time_usec=timestamp,
            x=vector_data[0],
            y=vector_data[1],
            z=vector_data[2]
        )

    logging.info("Data sent.")

# Communication loop
def communication_loop():
    while True:
        try:
            # Send a heartbeat message at regular intervals
            if int(time.time()) % heartbeat_interval == 0:
                logging.debug("Sending heartbeat...")
                send_heartbeat()

            # Check if a message has been received
            msg = mav.recv_match(blocking=False)
            if msg:
                logging.info(f"Received message: {msg.get_type()}")
                logging.debug(f"Message contents: {msg.to_dict()}")
            else:
                logging.debug("No message received.")

        except Exception as e:
            logging.error(f"Error: {e}")

        # Wait for a short interval before the next iteration
        time.sleep(0.1)

# Main loop
def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Test data
    test_data = {
        'Timestamp': '2023-06-08 12:34:56',
        'Accelerometer_X': 1.23,
        'Accelerometer_Y': 4.56,
        'Accelerometer_Z': 7.89,
        'Gyroscope_X': 10.11,
        'Gyroscope_Y': 12.13,
        'Gyroscope_Z': 14.15,
        'Humidity': 50.0,
        'Pressure': 1013.25,
        'Temperature_Humidity': 25.5,
        'Temperature_Pressure': 26.0,
        'Temperature_Thermocouple': 27.5,
        'Latitude': '30.2672',
        'Longitude': '-97.7431',
        'Altitude': '0.0',
        'Speed': '0.0',
        'Heading': '0.0'
    }

    # Start the communication loop
    comm_thread = threading.Thread(target=communication_loop)
    comm_thread.start()

    # Send test data
    send_data(test_data)

    # Wait for a few seconds before exiting
    time.sleep(5)

if __name__ == "__main__":
    main()