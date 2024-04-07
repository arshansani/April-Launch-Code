import serial
from ublox_gps import UbloxGps

# Initialize serial connection
serial_port = serial.Serial('/dev/ttyACM1', baudrate=9600, timeout=1)
gps = UbloxGps(serial_port)

def get_data():
    try:
        raw_data = gps.geo_coords()
        latitude = float(raw_data.lat)
        longitude = float(raw_data.lon)
        altitude = float(raw_data.height)/1000
        speed = float(raw_data.gSpeed)/1000
        heading = raw_data.headMot

        data = {
            'Latitude': latitude,
            'Longitude': longitude,
            'Altitude': altitude,
            'Speed': speed,
            'Heading': heading
        }
        return data
    except (ValueError, IOError) as err:
        print(err)
        return None, None, None

def get_time():
    try:
        gps_time = gps.date_time()
        time = ("UTC Time {}:{}:{}".format(gps_time.hour, gps_time.min, gps_time.sec))
        return time
    except (ValueError, IOError) as err:
        print(err)
        return None

def main():
    try:
        print("Listening for UBX Messages.")
        while True:
            data = get_data()
            #time_data = get_time()

            print(f"Latitude: {data.get('Latitude')}, Longitude: {data.get('Longitude')}, Altitude: {data.get('Altitude')}, Speed: {data.get('Speed')}, Heading: {data.get('Heading')}")
            #print(f"Time: {time_data}")

    finally:
        serial_port.close()

if __name__ == "__main__":
    main()