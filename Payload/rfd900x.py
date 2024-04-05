import time
from pymavlink import mavutil

# Configure the serial connection
serial_port = '/dev/ttyUSB0'  # Replace with the appropriate USB port
baud_rate = 9600  # Set the baud rate according to your RFD900x configuration

# Create a MAVLink connection
mav = mavutil.mavlink_connection(serial_port, baud=baud_rate)

# Function to send a heartbeat
def send_heartbeat():
    # Create and send a heartbeat message
    heartbeat_msg = mavutil.mavlink.MAVLink_heartbeat_message(
        mavutil.mavlink.MAV_TYPE_GCS,  # MAV_TYPE
        mavutil.mavlink.MAV_AUTOPILOT_INVALID,  # Autopilot type
        0,  # MAV_MODE
        0,  # Custom mode
        mavutil.mavlink.MAV_STATE_ACTIVE,  # System status
        3  # MAVLink version (set to 3 for MAVLink 2)
    )
    mav.mav.send(heartbeat_msg)

# Function to send sample data
def send_sample_data():
    # Create and send sample data using MAVLink messages
    mav.mav.debug_send(
        time_boot_ms=int(time.time() * 1000),
        ind=1,
        value=3.14
    )

    mav.mav.named_value_float_send(
        time_boot_ms=int(time.time() * 1000),
        name=b'Sample Data',
        value=42.0
    )

    print("Sample data sent.")

# Main loop
while True:
    try:
        # Send a heartbeat every second
        send_heartbeat()
        print("Heartbeat sent.")

        # Send sample data every 5 seconds
        # if int(time.time()) % 5 == 0:
        #     send_sample_data()
        #     print("Sample data sent.")

    except Exception as e:
        print(f"Error: {e}")

    # Wait for a short interval before the next iteration
    time.sleep(0.1)

# Close the MAVLink connection when done
mav.close()