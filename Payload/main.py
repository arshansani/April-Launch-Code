# Import necessary modules here
import threading
import logging
import time
import random

# Import your own modules here
import camera_module as camera
import sense_hat_module as sh
import data_writer as dw
import thermocouple_module as tc
import rfd900x_payload as rfd900x
import gps_module as gps

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Write Header to CSV
    sensor_filename = dw.get_next_filename('sensor_data_{}.csv')
    header = ['Timestamp', 'Accelerometer X (m/s^2)', 'Accelerometer Y (m/s^2)', 'Accelerometer Z (m/s^2)', 'Gyroscope X (rad/s)', 'Gyroscope Y (rad/s)', 'Gyroscope Z (rad/s)', 'Humidity (%)', 'Pressure (mbar)', 'Temperature from Humidity (C)', 'Temperature from Pressure (C)', 'Thermocouple Temperature (C)', 'Latitude', 'Longitude', 'Altitude (m)', 'Speed (m/s)', 'Heading']
    dw.write_data_to_csv(dict(zip(header, header)), sensor_filename)

    # Record in 15-minute segments for a total of 3 hours, ensuring at least 1 GB of free space
    # Start video recording in a separate thread
    video_filename = dw.get_next_filename('video_{}')
    video_args = (video_filename, 900, 10800, False, 1)
    video_thread = threading.Thread(target=camera.record_video, args=(video_args))
    video_thread.start()
    
    # Start the communication loop in a separate thread
    comm_thread = threading.Thread(target=rfd900x.communication_loop)
    comm_thread.start()

    # Print a message to the console
    logging.info("System Initialized...")

    try:
        while True:
            # Gather sensor data
            gps_data = gps.get_data()

            sensor_data = {
                'Timestamp': int(time.time() * 1000) % (2**32),
                'Accelerometer_X': sh.get_accelerometer_data().get('x', '') if sh.get_accelerometer_data() != "" else "",
                'Accelerometer_Y': sh.get_accelerometer_data().get('y', '') if sh.get_accelerometer_data() != "" else "",
                'Accelerometer_Z': sh.get_accelerometer_data().get('z', '') if sh.get_accelerometer_data() != "" else "",
                'Gyroscope_X': sh.get_gyroscope_data().get('x', '') if sh.get_gyroscope_data() != "" else "",
                'Gyroscope_Y': sh.get_gyroscope_data().get('y', '') if sh.get_gyroscope_data() != "" else "",
                'Gyroscope_Z': sh.get_gyroscope_data().get('z', '') if sh.get_gyroscope_data() != "" else "",
                'Humidity': sh.get_humidity() if sh.get_humidity() != "" else "",
                'Pressure': sh.get_pressure() if sh.get_pressure() != "" else "",
                'Temperature_Humidity': sh.get_temperature_from_humidity() if sh.get_temperature_from_humidity() != "" else "",
                'Temperature_Pressure': sh.get_temperature_from_pressure() if sh.get_temperature_from_pressure() != "" else "",
                'Temperature_Thermocouple': tc.get_thermocouple_data() if tc.get_thermocouple_data() != "" else "",
                'Latitude': gps_data.get('Latitude', '') if gps_data != "" else "",
                'Longitude': gps_data.get('Longitude', '') if gps_data != "" else "",
                'Altitude': gps_data.get('Altitude', '') if gps_data != "" else "",
                'Speed': gps_data.get('Speed', '') if gps_data != "" else "",
                'Heading': gps_data.get('Heading', '') if gps_data != "" else ""
            }

            # Write data to CSV
            dw.write_data_to_csv(sensor_data, sensor_filename)

            # Debugging
            logging.debug(f"{sensor_data} \n\n")

            # Send data to Ground Station
            try:
                rfd900x.send_data(sensor_data)
            except Exception as e:
                logging.error(f"Error sending data: {e}")

            # Sleep for a while if needed to limit the frequency of readings
            time.sleep(3)

    except KeyboardInterrupt:
        logging.info("Program terminated by user.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

    finally:
        # Stop the video recording
        #camera.stop_recording()
        video_thread.join()
        logging.info("Program exited.")

if __name__ == "__main__":
    while True:
        logging.info("Starting main program...")
        main()
        logging.error("Main program exited. Restarting...")