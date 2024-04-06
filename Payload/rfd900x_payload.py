import time
import random
import logging
from pymavlink import mavutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Configure the serial connection
serial_port = '/dev/ttyUSB0'  # Replace with the appropriate USB port
baud_rate = 57600  # Set the baud rate according to your RFD900x configuration

# Create a MAVLink connection
mav = mavutil.mavlink_connection(serial_port, baud=baud_rate)

main_interval = 1  # Time in seconds to wait between iterations of the main loop
heartbeat_interval = 1  # Interval in seconds for sending heartbeat messages
transmit_interval = 5  # Interval in seconds for transmitting data

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

# Function to send sample data
def send_sample_data():
    # Create sample data
    timestamp = int(time.time() * 1000) % (2**32)
    acc_x = random.uniform(-10, 10)
    acc_y = random.uniform(-10, 10)
    acc_z = random.uniform(-10, 10)
    gyro_x = random.uniform(-5, 5)
    gyro_y = random.uniform(-5, 5)
    gyro_z = random.uniform(-5, 5)
    humidity = random.uniform(20, 80)
    pressure = random.uniform(900, 1100)
    temp_humidity = random.uniform(10, 40)
    temp_pressure = random.uniform(10, 40)
    thermocouple_temp = random.uniform(10, 40)

    # Create and send sample data using MAVLink_debug_vect_message
    data = [acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, humidity, pressure, temp_humidity, temp_pressure, thermocouple_temp]
    mav.mav.debug_vect_send(
        name=b'SensorData',
        time_usec=timestamp,
        x=data[0],
        y=data[1],
        z=data[2]
    )
    mav.mav.debug_vect_send(
        name=b'SensorData',
        time_usec=timestamp,
        x=data[3],
        y=data[4],
        z=data[5]
    )
    mav.mav.debug_vect_send(
        name=b'SensorData',
        time_usec=timestamp,
        x=data[6],
        y=data[7],
        z=data[8]
    )
    mav.mav.debug_vect_send(
        name=b'SensorData',
        time_usec=timestamp,
        x=data[9],
        y=data[10],
        z=0.0
    )
    logging.info("Sample data sent.")
    logging.info("")

# Main loop
def main():
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

            # Send data at regular intervals
            if int(time.time()) % transmit_interval == 0:
                logging.info("")
                logging.debug("Sending data...")
                send_sample_data()

        except Exception as e:
            logging.error(f"Error: {e}")

        # Wait for a short interval before the next iteration
        time.sleep(main_interval)

# Close the MAVLink connection when done
mav.close()

if __name__ == "__main__":
    main()