import logging
import board
import digitalio
import adafruit_max31856

# Initialize the SPI bus and the chip select pin
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)  # Adjust the pin if needed

# Create an instance of the MAX31856 class
try:
    max31856 = adafruit_max31856.MAX31856(spi, cs)
    thermocouple_available = True
except Exception as e:
    logging.error(f"MAX31856 initialization failed: {e}")
    thermocouple_available = False

def get_thermocouple_data():
    if not thermocouple_available:
        return ""
    
    try:
        # Get the temperature in degrees Celsius
        temperature = max31856.temperature
        return round(temperature, 2)
    except Exception as e:
        logging.error(f"Error reading thermocouple: {e}")
        return ""
    
if __name__ == "__main__":
    # Test the thermocouple module
    temperature = get_thermocouple_data()
    print("Thermocouple temperature:", temperature)