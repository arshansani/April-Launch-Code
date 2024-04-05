import smbus
import logging
import time

# I2C address of the GPS module
GPS_ADDRESS = 0x42  # Update with the correct I2C address

# I2C commands
GPS_COMMAND_HOT_START = 0x01
GPS_COMMAND_WARM_START = 0x02
GPS_COMMAND_COLD_START = 0x04
GPS_COMMAND_QUERY_DATA = 0x10

# Create an I2C bus object
try:
    bus = smbus.SMBus(1)  # Use I2C bus 1
    gps_available = True
except Exception as e:
    logging.error(f"I2C initialization failed: {e}")
    gps_available = False

def gps_init(command=GPS_COMMAND_HOT_START):
    if not gps_available:
        return
    
    try:
        bus.write_byte(GPS_ADDRESS, command)
        time.sleep(1)  # Wait for initialization
    except Exception as e:
        logging.error(f"GPS initialization failed: {e}")

def gps_query_data():
    if not gps_available:
        return {}
    
    try:
        bus.write_byte(GPS_ADDRESS, GPS_COMMAND_QUERY_DATA)
        time.sleep(0.1)  # Wait for data to be available
        
        # Read data from the GPS module
        data = bus.read_i2c_block_data(GPS_ADDRESS, 0, 32)  # Read 32 bytes of data
        
        # Log the received data for debugging
        logging.debug(f"Received GPS data: {data}")
        
        # Process the received data and extract relevant information
        # Implement the parsing logic according to the module's I2C protocol
        
        # Example parsing logic (modify according to actual data format)
        latitude = float(f"{data[0]}.{data[1]}")
        longitude = float(f"{data[2]}.{data[3]}")
        altitude = float(f"{data[4]}.{data[5]}")
        
        # Return the parsed GPS data
        return {
            "Latitude": latitude,
            "Longitude": longitude,
            "Altitude": altitude
        }
    
    except Exception as e:
        logging.error(f"GPS data query failed: {e}")
        return {}

if __name__ == "__main__":
    # Initialize logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Initialize GPS module
    gps_init(GPS_COMMAND_HOT_START)
    
    try:
        while True:
            # Get GPS data
            gps_data = gps_query_data()
            
            # Print the GPS data
            print(f"Latitude: {gps_data.get('Latitude', '')}")
            print(f"Longitude: {gps_data.get('Longitude', '')}")
            print(f"Altitude: {gps_data.get('Altitude', '')}")
            print("---")
            
            time.sleep(1)  # Adjust the delay as needed
    
    except KeyboardInterrupt:
        # Clean up any resources if needed
        pass