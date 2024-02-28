# Import necessary modules here
import logging
import time
import os
import glob

# Import your own modules here
import sense_hat_sensors as shs
#import camera_operations as co
import data_writer as dw

def main():
    # Initialize logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("System Initialized...")

    # Determine the filename for this run
    filename = dw.get_next_filename()
    
    # Write to CSV
    header = ['Timestamp', 'Accelerometer X (m/s^2)', 'Accelerometer Y (m/s^2)', 'Accelerometer Z (m/s^2)', 'Gyroscope X (rad/s)', 'Gyroscope Y (rad/s)', 'Gyroscope Z (rad/s)', 'Humidity (%)', 'Pressure (mbar)', 'Temperature from Humidity (C)', 'Temperature from Pressure (C)']
    dw.write_data_to_csv(dict(zip(header, header)), filename)

    try:
        # Starting camera recording
        #co.start_camera_recording('video.h264')

        while True:
            # Gather sensor data
            sensor_data = {
                'Timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'Accelerometer X': shs.get_accelerometer_data().get('x', '') if shs.get_accelerometer_data() != "" else "",
                'Accelerometer Y': shs.get_accelerometer_data().get('y', '') if shs.get_accelerometer_data() != "" else "",
                'Accelerometer Z': shs.get_accelerometer_data().get('z', '') if shs.get_accelerometer_data() != "" else "",
                'Gyroscope X': shs.get_gyroscope_data().get('x', '') if shs.get_gyroscope_data() != "" else "",
                'Gyroscope Y': shs.get_gyroscope_data().get('y', '') if shs.get_gyroscope_data() != "" else "",
                'Gyroscope Z': shs.get_gyroscope_data().get('z', '') if shs.get_gyroscope_data() != "" else "",
                'Humidity': shs.get_humidity() if shs.get_humidity() != "" else "",
                'Pressure': shs.get_pressure() if shs.get_pressure() != "" else "",
                'Temperature from Humidity': shs.get_temperature_from_humidity() if shs.get_temperature_from_humidity() != "" else "",
                'Temperature from Pressure': shs.get_temperature_from_pressure() if shs.get_temperature_from_pressure() != "" else ""
            }

            # Write data to CSV
            dw.write_data_to_csv(sensor_data, filename)

            # For debugging: Print data every 5 seconds
            # Comment or uncomment the following lines for debugging
            print(sensor_data)
            print("\n\n")

            # Placeholder for camera recording logic
            #start_camera_recording()  # Or any other camera operation

            # Sleep for a while if needed to limit the frequency of readings
            time.sleep(3)

    except KeyboardInterrupt:
        logging.info("Program terminated by user.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

    finally:
        # Stopping camera recording and releasing resources
        #co.stop_camera_recording()
        logging.info("Program exited.")

if __name__ == "__main__":
    main()
