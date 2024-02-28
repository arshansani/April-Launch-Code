import logging
from sense_hat import SenseHat

sense = SenseHat()

# Set Constants
g = 9.80665  # m/s^2

def get_accelerometer_data():
    try:
        # Get accelerometer data in Gs
        acceleration = sense.get_accelerometer_raw()
        # Convert to m/s^2 and format to two decimal places
        x = round(acceleration['x'] * g, 2)  
        y = round(acceleration['y'] * g, 2)
        z = round(acceleration['z'] * g, 2)
        return {"x": x, "y": y, "z": z}
    except Exception as e:
        logging.error(f"Error reading accelerometer: {e}")
        return {"x": "", "y": "", "z": ""}

# DEPRACATED, GIVES BAD READINGS
def get_compass_data():
    try:
        # Get compass data in degrees
        north = sense.get_compass()
        return {north}
    except Exception as e:
        logging.error(f"Error reading compass: {e}")
        return ""

def get_gyroscope_data():
    try:
        # Get gyroscope data in radians per second
        gyro = sense.get_gyroscope_raw()
        # Format to two decimal places
        x = round(gyro['x'], 2)  
        y = round(gyro['y'], 2)
        z = round(gyro['z'], 2)
        return {"x": x, "y": y, "z": z}
    except Exception as e:
        logging.error(f"Error reading gyroscope: {e}")
        return {"x": "", "y": "", "z": ""}

# DEPRACATED, GIVES BAD READINGS
def get_orientation_data():
    try:
        # Get orientation data in degrees
        gyro = sense.get_orientation_degrees()
        # Format to two decimal places
        pitch = round(gyro["pitch"], 2)  
        roll = round(gyro["roll"], 2)
        yaw = round(gyro["yaw"], 2)
        return {"pitch": [pitch], "roll": roll, "yaw": yaw}
    except Exception as e:
        logging.error(f"Error reading gyroscope: {e}")
        return ""

def get_humidity():
    try:
        # Get humidity data in percentage
        humidity = sense.get_humidity()
        return humidity
    except Exception as e:
        logging.error(f"Error reading humidity: {e}")
        return ""

def get_pressure():
    try:
        # Get pressure data in millibars
        pressure = sense.get_pressure()
        if pressure == 0: # If the sensor returns 0, it's likely an error
            return ""
        return pressure
    except Exception as e:
        logging.error(f"Error reading pressure: {e}")
        return ""

def get_temperature_from_humidity():
    try:
        # Get temperature data in degrees Celsius from the humidity sensor
        temperature = round(sense.get_temperature_from_humidity(), 2)
        return temperature
    except Exception as e:
        logging.error(f"Error reading temperature: {e}")
        return ""
    
def get_temperature_from_pressure():
    try:
        # Get temperature data in degrees Celsius from the pressure sensor
        temperature = round(sense.get_temperature_from_pressure(), 2)
        if temperature == 0: # If the sensor returns 0, it's likely an error
            return ""
        return temperature
    except Exception as e:
        logging.error(f"Error reading temperature: {e}")
        return ""