# Import necessary modules here
import threading
import logging
import time

# Import your own modules here
import camera_module as camera
import sense_hat_module as sh
import data_writer as dw
import thermocouple_module as tc

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Write Header to CSV
    sensor_filename = dw.get_next_filename('sensor_data_{}.csv')
    header = ['Timestamp', 'Accelerometer X (m/s^2)', 'Accelerometer Y (m/s^2)', 'Accelerometer Z (m/s^2)', 'Gyroscope X (rad/s)', 'Gyroscope Y (rad/s)', 'Gyroscope Z (rad/s)', 'Humidity (%)', 'Pressure (mbar)', 'Temperature from Humidity (C)', 'Temperature from Pressure (C)', 'Thermocouple Temperature (C)']
    dw.write_data_to_csv(dict(zip(header, header)), sensor_filename)

    # Record in 5-minute segments for a total of 3 hours, ensuring at least 1 GB of free space
    # Start video recording in a separate thread
    video_filename = dw.get_next_filename('video_{}')
    video_args = (video_filename, 30, 10800, False, 1)
    video_thread = threading.Thread(target=camera.record_video, args=(video_args))
    video_thread.start()
    
    # Print a message to the console
    print("System Initialized...")

    try:
        while True:
            # Gather sensor data
            sensor_data = {
                'Timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'Accelerometer X': sh.get_accelerometer_data().get('x', '') if sh.get_accelerometer_data() != "" else "",
                'Accelerometer Y': sh.get_accelerometer_data().get('y', '') if sh.get_accelerometer_data() != "" else "",
                'Accelerometer Z': sh.get_accelerometer_data().get('z', '') if sh.get_accelerometer_data() != "" else "",
                'Gyroscope X': sh.get_gyroscope_data().get('x', '') if sh.get_gyroscope_data() != "" else "",
                'Gyroscope Y': sh.get_gyroscope_data().get('y', '') if sh.get_gyroscope_data() != "" else "",
                'Gyroscope Z': sh.get_gyroscope_data().get('z', '') if sh.get_gyroscope_data() != "" else "",
                'Humidity': sh.get_humidity() if sh.get_humidity() != "" else "",
                'Pressure': sh.get_pressure() if sh.get_pressure() != "" else "",
                'Temperature from Humidity (C)': sh.get_temperature_from_humidity() if sh.get_temperature_from_humidity() != "" else "",
                'Temperature from Pressure (C)': sh.get_temperature_from_pressure() if sh.get_temperature_from_pressure() != "" else "",
                'Thermocouple Temperature (C)': tc.get_thermocouple_data() if tc.get_thermocouple_data() != "" else ""
            }

            # Write data to CSV
            dw.write_data_to_csv(sensor_data, sensor_filename)

            # Debugging
            logging.debug(f"{sensor_data} \n\n")

            # Sleep for a while if needed to limit the frequency of readings
            time.sleep(3)

    except KeyboardInterrupt:
        logging.info("Program terminated by user.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

    finally:
        # Stop the video recording
        camera.stop_recording()
        video_thread.join()
        logging.info("Program exited.")

if __name__ == "__main__":
    while True:
        logging.info("Starting main program...")
        main()
        logging.error("Main program exited. Restarting...")