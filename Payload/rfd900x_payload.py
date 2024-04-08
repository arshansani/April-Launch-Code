import time
import random
import logging
import threading
from pymavlink import mavutil

# Configure the serial connection
serial_port = '/dev/ttyUSB0'  # Replace with the appropriate USB port
baud_rate = 57600  # Set the baud rate according to your RFD900x configuration

# Create a MAVLink connection
mav = mavutil.mavlink_connection(serial_port, baud=baud_rate)

heartbeat_interval = 1  # Interval in seconds for sending heartbeat messages
cutdown_status = False  # Status of the cutdown mechanism

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
            name=f"Vector_{i}".encode(),
            time_usec=timestamp,
            x=vector_data[0],
            y=vector_data[1],
            z=vector_data[2]
        )

    logging.info("Data sent.")

# Communication loop
def communication_loop():
    global cutdown_status
    while True:
        try:
            # Send a heartbeat message at regular intervals
            if int(time.time()) % heartbeat_interval == 0:
                logging.debug("Sending heartbeat...")
                send_heartbeat()

            # Check if a message has been received
            msg = mav.recv_match(blocking=False)
            if msg:
                if msg.get_type() == "DEBUG_VECT":
                    logging.info(f"Received debug vector: {msg.name}")
                    if msg.name == "Cutdown":
                        logging.warning("Activating cutdown mechanism...")
                        cutdown_status = True
                        logging.warning("Cutdown mechanism activated!")
                logging.info(f"Received message: {msg.get_type()}")
                logging.debug(f"Message contents: {msg.to_dict()}")
            else:
                logging.debug("No message received.")

        except Exception as e:
            logging.error(f"Error: {e}")

        # Wait for a short interval before the next iteration
        time.sleep(1)

# Function to get the status of the cutdown mechanism
def get_cutdown_status():
    global cutdown_status
    return cutdown_status

# Main loop
def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Start the communication loop
    comm_thread = threading.Thread(target=communication_loop)
    comm_thread.start()

    while True:
        # Test data
        test_data = {
            'Timestamp': int(time.time() * 1000) % (2**32),
            'Accelerometer_X': random.uniform(-10, 10),
            'Accelerometer_Y': random.uniform(-10, 10),
            'Accelerometer_Z': random.uniform(-10, 10),
            'Gyroscope_X': random.uniform(-5, 5),
            'Gyroscope_Y': random.uniform(-5, 5),
            'Gyroscope_Z': random.uniform(-5, 5),
            'Humidity': random.uniform(20, 80),
            'Pressure': random.uniform(900, 1100),
            'Temperature_Humidity': random.uniform(10, 40),
            'Temperature_Pressure': random.uniform(10, 40),
            'Temperature_Thermocouple': random.uniform(-50, 40),
            'Latitude': random.uniform(28.0, 34.0),
            'Longitude': random.uniform(-104.0, -96.0),
            'Altitude': random.uniform(0, 100000),
            'Speed': random.uniform(0, 10),
            'Heading': random.uniform(0, 360)
        }

        # Send test data
        send_data(test_data)

        # Wait for a few seconds before exiting
        time.sleep(5)

if __name__ == "__main__":
    main()