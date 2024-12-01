from datetime import datetime
import time
import board
import busio
import adafruit_mlx90640

class ThermalSensor:
    def __init__(self):
        
        self.time_period = {
            "day": list(range(8, 19)),  # Hours 8 to 18 inclusive
            "night": list(range(19, 25)) + list(range(0, 8))  # Hours 19 to 24 and 0 to 7
        }
        self.sensor = self.initialize_sensor()
    
    def initialize_sensor(self):
       
        i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)  # Create I2C bus
        mlx = adafruit_mlx90640.MLX90640(i2c)  # Initialize the sensor

        # Set refresh rate
        mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_8_HZ

        return mlx

    def get_max_allowed_temp(self):
       
        current_hour = int(datetime.now().strftime("%H"))
        if current_hour in self.time_period["day"]:
            return 38  # Max allowed temp during the day
        elif current_hour in self.time_period["night"]:
            return 30  # Max allowed temp during the night

    def read_temperature(self):
        
        frame = [0] * 768  # MLX90640 outputs 768 temperature values (24x32)
        try:
            self.sensor.getFrame(frame)
            max_temp = max(frame)  # Get the maximum temperature
        except Exception as e:
            print(f"Error reading frame: {e}")
            max_temp = None

        max_allowed_temp = self.get_max_allowed_temp()
        return max_temp, max_allowed_temp